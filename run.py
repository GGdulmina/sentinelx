import os
import sys
import signal
import queue
import threading
import logging
from datetime import datetime

from config import load_config
from core.watcher import follow
from core.parser import parse_line
from core.alerts import AlertEngine
from core.privileges import drop_privileges

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("sentinelx")

def format_timestamp(timestamp_str: str, target_format: str) -> str:
    """Format timestamp into a user-specified datetime representation."""
    if not target_format:
        return timestamp_str
    try:
        # Try ISO 8601
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime(target_format)
    except ValueError:
        try:
            # Try Syslog format (e.g. Jun 28 12:02:26)
            # Since syslog doesn't have a year, we assume the current year
            dt = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
            dt = dt.replace(year=datetime.now().year)
            return dt.strftime(target_format)
        except ValueError:
            return timestamp_str

def main():
    """Main application entry point."""
    # Load configuration
    config = load_config()
    
    # CLI argument override
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.endswith(('.yaml', '.yml')):
            logger.info(f"Loading custom configuration from: {arg}")
            config = load_config(arg)
        else:
            logger.info(f"Overriding log path to: {arg}")
            config['log_paths'] = [arg]

    # Signal handler for graceful shutdown
    def shutdown_handler(signum, frame):
        sig_name = signal.Signals(signum).name
        logger.info(f"Received {sig_name}. Shutting down SentinelX gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Drop privileges if running as root
    drop_privileges(config.get('run_as_user', 'nobody'), config.get('run_as_group', 'nogroup'))

    # Initialize the Alert Engine
    engine = AlertEngine(config)

    # Setup thread-safe queue and start watcher threads
    line_queue = queue.Queue()
    
    def watcher_worker(path):
        try:
            for line in follow(path):
                line_queue.put(line)
        except Exception as e:
            logger.error(f"Watcher thread for {path} encountered an error: {e}")

    log_paths = config.get('log_paths', [])
    if not log_paths:
        logger.error("No log files configured to monitor. Exiting.")
        sys.exit(1)

    logger.info(f"Starting log watchers for paths: {log_paths}")
    for path in log_paths:
        t = threading.Thread(target=watcher_worker, args=(path,), daemon=True)
        t.start()

    # Output formatting settings
    output_format = config.get('output_format', {})
    icons = output_format.get('icons', {
        "info": "[  INFO  ]",
        "warning": "[WARNING ]",
        "critical": "[CRITICAL]"
    })
    col_widths = output_format.get('column_widths', {
        "ip": 16,
        "username": 12
    })
    date_format = output_format.get('date_format', "")
    
    ip_width = col_widths.get('ip', 16)
    user_width = col_widths.get('username', 12)

    # Main processing loop
    logger.info("SentinelX monitoring active. Press Ctrl+C to stop.")
    while True:
        try:
            # Block on queue with a timeout to allow signals to be handled on main thread
            try:
                line = line_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            parsed = parse_line(line)
            if parsed is None:
                continue

            alert = engine.process(parsed)
            if alert is None:
                continue

            icon = icons.get(alert["severity"], f"[{alert['severity'].upper()}]")
            timestamp = format_timestamp(alert['timestamp'], date_format)
            
            print(f"{icon} {timestamp}  "
                  f"IP: {alert['ip']:<{ip_width}} "
                  f"User: {alert['username']:<{user_width}} "
                  f"{alert['message']}", flush=True)

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Shutting down...")
            break
        except Exception as e:
            logger.error(f"Error processing log entry: {e}")

if __name__ == "__main__":
    main()