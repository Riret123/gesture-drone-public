#!/usr/bin/env bash
# Возвращает wlan0 из режима точки доступа Drone_Network обратно в
# обычный клиентский Wi-Fi (профиль NetworkManager "UAWiFi"). Если ты
# сейчас подключен(а) именно через Drone_Network (а не по Ethernet) —
# эта команда тоже оборвёт текущую сессию, точно так же как
# switch_to_ap.sh. См. README.md.
#
# Запуск: sudo ./switch_to_client.sh [-y]
#   -y — не спрашивать подтверждения (для скриптов/автоматизации)

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Нужны права root: sudo ./switch_to_client.sh" >&2
  exit 1
fi

IFACE=wlan0
CLIENT_CONNECTION="UAWiFi"
HOSTAPD_PID=/run/hostapd-drone.pid
DNSMASQ_PID=/run/dnsmasq-drone.pid

if [ "${1:-}" != "-y" ]; then
  echo "=== Возврат $IFACE в клиентский режим ($CLIENT_CONNECTION) ==="
  echo "Если сейчас подключен(а) через Drone_Network — эта сессия оборвётся."
  read -r -p "Продолжить? (yes/[no]): " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Отменено."
    exit 0
  fi
fi

echo "-> Останавливаю hostapd/dnsmasq..."
[ -f "$HOSTAPD_PID" ] && kill "$(cat "$HOSTAPD_PID")" 2>/dev/null || true
[ -f "$DNSMASQ_PID" ] && kill "$(cat "$DNSMASQ_PID")" 2>/dev/null || true
rm -f "$HOSTAPD_PID" "$DNSMASQ_PID"
pkill -f "hostapd -B -P $HOSTAPD_PID" 2>/dev/null || true
sleep 1

echo "-> Снимаю статический IP, возвращаю $IFACE под NetworkManager..."
ip addr flush dev "$IFACE"
nmcli device set "$IFACE" managed yes
sleep 2

echo "-> Поднимаю соединение $CLIENT_CONNECTION..."
if ! nmcli connection up "$CLIENT_CONNECTION"; then
  echo "Не удалось автоматически поднять '$CLIENT_CONNECTION'."
  echo "Проверь вручную: nmcli device wifi list; nmcli connection up $CLIENT_CONNECTION"
fi

echo
echo "Текущий IP $IFACE:"
ip -4 addr show dev "$IFACE" | grep inet || echo "  (пока не получен — подожди пару секунд: ip addr show $IFACE)"
