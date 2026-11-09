# Local development dashboard

From repository root with `src/gesture_control` on PYTHONPATH run
`python -B -m gesture_control.mock_server`. Open http://127.0.0.1:8081 or /quest.
No build step, dependencies or ROS needed. The server binds loopback only, serves
two explicit pages and `/telemetry`, and never proxies arbitrary paths.

Telemetry schema: mock boolean, age seconds since sample at producer, mode string,
battery percent, deadman boolean, acks array of service-result strings. UI clears
telemetry on unavailable/stale data and uses textContent for external text.
The mock emits fixed synthetic values and clearly labels them. A real read-only
ROS adapter is not supplied; the dashboard cannot subscribe to ROS topics directly.
Do not expose this development HTTP server publicly. Browser/Quest QA remains manual.
