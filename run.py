from core.watcher import follow
from core.parser  import parse_line
from core.alerts  import AlertEngine

LOG_FILE = "/var/log/auth.log"

# severity → what symbol to show
ICONS = {
    "info":     "[  INFO  ]",
    "warning":  "[WARNING ]",
    "critical": "[CRITICAL]",
}

if __name__ == "__main__":
    engine = AlertEngine()

    for line in follow(LOG_FILE):

        parsed = parse_line(line)

        # line didn't match anything we care about — skip it
        if parsed is None:
            continue

        alert = engine.process(parsed)

        # engine decided this event isn't worth reporting yet
        if alert is None:
            continue

        icon = ICONS[alert["severity"]]
        print(f"{icon} {alert['timestamp']}  "
              f"IP: {alert['ip']:<16} "
              f"User: {alert['username']:<12} "
              f"{alert['message']}")