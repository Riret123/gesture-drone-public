# English / Russian technical glossary

Translation status: technical draft; no independent fluent safety review yet.

| English | Russian | Meaning in this repository |
| --- | --- | --- |
| request | запрос | desired action, not proof it happened |
| acknowledgement | подтверждение обработки запроса | service result, not verified maneuver completion |
| arming | арминг / разрешение работы двигателей | potentially hazardous flight-controller state |
| hold | удержание позиции | live bridge requests LOITER; prerequisites still matter |
| deadman | кнопка удержания разрешения | separate offline input lease concept, not continuous open palm |
| stale data | устаревшие данные | received evidence older than the policy permits |
| frame | система координат | coordinate convention; distinguish video frame: кадр |
| geofence | геозона | offline boundary policy here; no live protection claim |
| mock telemetry | искусственная телеметрия | fixture output, not aircraft measurement |
| toy simulation | упрощённая модель | limited model without validated vehicle dynamics |
| fail closed | отклонить при недостоверных данных | reject unsafe authorization, not guaranteed aircraft safety |
| precision landing | точная посадка | proposed marker-based process; hardware precision unverified |

Translation rule: preserve request, offline, mock and unverified distinctions. Never translate a proposed safeguard as a proven protection. Hardware instructions require qualified human confirmation before use.

Round 02 correction: Unicode was lost in the first PowerShell pipeline write. This file was rewritten through the patch tool and checked for actual Cyrillic code points. Encoding checks cannot establish translation quality.
