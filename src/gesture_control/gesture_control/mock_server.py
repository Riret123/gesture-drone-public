"""Loopback-only mock telemetry server; never connects to ROS or hardware."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json


def telemetry() -> dict:
    return dict(schema=1, mock=True, age=0., mode='SIMULATED LOITER', battery=78.,
                deadman=False, acks=['MOCK: hold=OK', 'MOCK: no flight commands sent'])


def handler(root: Path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            routes = {'/': 'dashboard/index.html', '/quest': 'quest/index.html'}
            if self.path == '/telemetry':
                body = json.dumps(telemetry()).encode('utf-8')
                content_type = 'application/json'
            elif self.path in routes:
                body = (root / routes[self.path]).read_bytes()
                content_type = 'text/html; charset=utf-8'
            elif self.path == '/telemetry_ui.js':
                body = (root / 'dashboard/telemetry.js').read_bytes()
                content_type = 'application/javascript; charset=utf-8'
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass
    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--port', type=int, default=8081)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(args.root.resolve()))
    try:
        print('Mock dashboard at http://127.0.0.1:' + str(server.server_port))
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
