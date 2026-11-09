#!/usr/bin/env python3
"""Простой MJPEG-видеосервер с /dev/video0 для полевых тестов без интернета.

Отдаёт HTML-страницу просмотра на "/" и сам поток кадров (multipart
MJPEG, m-jpeg over HTTP) на "/stream" — открывается напрямую в любом
браузере тегом <img src="/stream">, дополнительных плагинов/WebRTC-
сигнализации не требует. Работает независимо от того, в каком режиме
Wi-Fi сейчас находится плата (клиент uawifi или точка доступа
Drone_Network) — сервер просто слушает 0.0.0.0:PORT на всех интерфейсах.

Запуск:
    source ai_env/bin/activate
    python3 video_stream_server.py [--port 8080] [--camera 0]
        [--width 640] [--height 480] [--fps 15] [--quality 80]

Проверка без браузера:
    curl -s http://<IP>:8080/snapshot -o /tmp/frame.jpg   # один кадр
    curl -sN http://<IP>:8080/stream | head -c 2000       # начало потока
"""

import argparse
import math
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cv2

BOUNDARY = 'frame'
VIEWER_HTML_PATH = Path(__file__).resolve().parent / 'viewer.html'


class SharedCamera:
    """Один VideoCapture на всех клиентов, чтобы не открывать /dev/video0
    по разу на каждое подключение браузера."""

    def __init__(self, index, width, height, fps, max_age=2.0):
        if (isinstance(max_age, bool) or not isinstance(max_age, (int, float))
                or not math.isfinite(max_age) or max_age <= 0):
            raise ValueError('max_age must be finite and positive')
        self._max_age = max_age
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError(f'Не удалось открыть камеру (индекс {index})')
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

        self._lock = threading.Lock()
        self._frame = None
        self._frame_time = None
        self._frame_count = 0
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        while self._running:
            ok, frame = self.cap.read()
            if not ok:
                with self._lock:
                    self._frame = self._frame_time = None
                time.sleep(0.05)
                continue
            with self._lock:
                self._frame = frame
                self._frame_time = time.monotonic()
                self._frame_count += 1

    def get_frame(self):
        with self._lock:
            if (self._frame is None or self._frame_time is None
                    or not 0 <= time.monotonic() - self._frame_time < self._max_age):
                return None
            return self._frame.copy()

    def is_fresh(self):
        with self._lock:
            return (self._frame is not None and self._frame_time is not None
                    and 0 <= time.monotonic() - self._frame_time < self._max_age)

    @property
    def frame_count(self):
        with self._lock:
            return self._frame_count

    def stop(self):
        self._running = False
        self._thread.join(timeout=2)
        self.cap.release()


def make_handler(camera, jpeg_quality, fps):
    frame_interval = 1.0 / fps

    class Handler(BaseHTTPRequestHandler):

        def log_message(self, fmt, *args):
            # компактный лог вместо стандартного многословного формата
            print(f'[video_stream_server] {self.address_string()} - {fmt % args}')

        def do_GET(self):
            if self.path == '/' or self.path.startswith('/index'):
                self._serve_html()
            elif self.path.startswith('/stream'):
                self._serve_stream()
            elif self.path.startswith('/snapshot'):
                self._serve_snapshot()
            elif self.path.startswith('/healthz'):
                self._serve_health()
            else:
                self.send_error(404, 'Not Found')

        def _serve_html(self):
            body = VIEWER_HTML_PATH.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_health(self):
            fresh = camera.is_fresh()
            body = f'fresh={fresh} frames_captured={camera.frame_count}\n'.encode()
            self.send_response(200 if fresh else 503)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_snapshot(self):
            frame = camera.get_frame()
            if frame is None:
                self.send_error(503, 'Camera not ready')
                return
            ok, jpg = cv2.imencode(
                '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
            if not ok:
                self.send_error(500, 'Encode failed')
                return
            data = jpg.tobytes()
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _serve_stream(self):
            self.send_response(200)
            self.send_header(
                'Content-Type',
                f'multipart/x-mixed-replace; boundary={BOUNDARY}')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.end_headers()
            try:
                while True:
                    frame = camera.get_frame()
                    if frame is None:
                        time.sleep(0.05)
                        continue
                    ok, jpg = cv2.imencode(
                        '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
                    if not ok:
                        continue
                    data = jpg.tobytes()
                    self.wfile.write(f'--{BOUNDARY}\r\n'.encode())
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(data)}\r\n\r\n'.encode())
                    self.wfile.write(data)
                    self.wfile.write(b'\r\n')
                    time.sleep(frame_interval)
            except (BrokenPipeError, ConnectionResetError, socket.error):
                pass  # клиент закрыл вкладку/обновил страницу — это нормально

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--frame-max-age', type=float, default=2.0)
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--width', type=int, default=640)
    parser.add_argument('--height', type=int, default=480)
    parser.add_argument('--fps', type=int, default=15)
    parser.add_argument('--quality', type=int, default=80)
    args = parser.parse_args()

    if (not math.isfinite(args.frame_max_age) or args.frame_max_age <= 0
            or args.fps <= 0 or args.width <= 0 or args.height <= 0
            or args.camera < 0 or not 1 <= args.quality <= 100
            or not 1 <= args.port <= 65535):
        parser.error('require positive fps/dimensions, camera >= 0, quality 1..100, port 1..65535')
    camera = SharedCamera(args.camera, args.width, args.height, args.fps, args.frame_max_age)
    server = None
    try:
        handler = make_handler(camera, args.quality, args.fps)
        server = ThreadingHTTPServer((args.host, args.port), handler)
        print(f'video_stream_server: http://{args.host}:{args.port}/')
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if server is not None:
            server.server_close()
        camera.stop()



if __name__ == '__main__':
    main()
