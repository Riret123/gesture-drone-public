#!/usr/bin/env bash
# Переключает wlan0 из клиентского Wi-Fi (uawifi) в режим точки доступа
# Drone_Network. НЕ запускать автоматически откуда-либо — только руками,
# когда сознательно готов(а) на время потерять текущее Wi-Fi-подключение
# (SSH/RDP по Wi-Fi оборвутся). См. README.md.
#
# Запуск: sudo ./switch_to_ap.sh [-y]
#   -y — не спрашивать подтверждения (для скриптов/автоматизации)

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Нужны права root: sudo ./switch_to_ap.sh" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IFACE=wlan0
AP_IP=192.168.4.1
AP_CIDR="${AP_IP}/24"
HOSTAPD_CONF="$SCRIPT_DIR/hostapd-drone.conf"
DNSMASQ_CONF="$SCRIPT_DIR/dnsmasq-drone.conf"
HOSTAPD_PID=/run/hostapd-drone.pid
DNSMASQ_PID=/run/dnsmasq-drone.pid

if [ "${1:-}" != "-y" ]; then
  echo "=== Переключение $IFACE в режим точки доступа Drone_Network ==="
  echo "ВНИМАНИЕ: это оборвёт текущее Wi-Fi подключение (uawifi/UAWiFi) —"
  echo "SSH и RDP сессии, идущие через Wi-Fi, отключатся прямо сейчас."
  echo "Продолжай, только если физически рядом с платой или есть Ethernet"
  echo "как запасной путь входа."
  echo
  read -r -p "Продолжить? (yes/[no]): " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Отменено."
    exit 0
  fi
fi

echo "-> Отключаю $IFACE от NetworkManager..."
nmcli device set "$IFACE" managed no || true
sleep 1

echo "-> Поднимаю $IFACE со статическим IP $AP_CIDR..."
ip link set "$IFACE" down
ip addr flush dev "$IFACE"
ip link set "$IFACE" up
ip addr add "$AP_CIDR" dev "$IFACE"

echo "-> Останавливаю прошлые hostapd/dnsmasq этого проекта, если остались..."
[ -f "$HOSTAPD_PID" ] && kill "$(cat "$HOSTAPD_PID")" 2>/dev/null || true
[ -f "$DNSMASQ_PID" ] && kill "$(cat "$DNSMASQ_PID")" 2>/dev/null || true
rm -f "$HOSTAPD_PID" "$DNSMASQ_PID"
sleep 1

echo "-> Запускаю hostapd (SSID Drone_Network)..."
hostapd -B -P "$HOSTAPD_PID" "$HOSTAPD_CONF"

echo "-> Запускаю dnsmasq (DHCP $AP_IP)..."
dnsmasq --conf-file="$DNSMASQ_CONF" --pid-file="$DNSMASQ_PID"

echo
echo "=== Готово: точка доступа поднята ==="
echo "  SSID:     Drone_Network"
echo "  Пароль:   CHANGE_ME_BEFORE_USE (см. network/hostapd-drone.conf)"
echo "  IP платы: $AP_IP"
echo "  Видео:    http://$AP_IP:8080/  (video_stream_server.py должен быть запущен отдельно)"
echo
echo "Вернуться в обычный режим: sudo ./switch_to_client.sh"
