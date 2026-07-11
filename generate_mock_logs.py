"""Mock log stream generator for SentinelX security daemon.

Simulates automated SSH brute-force actions and authorization confirmations
by formatting classic syslog patterns to local target destinations.
"""

import os
import random
import time
from datetime import datetime

# Read environmental configuration paths dynamically
LOG_FILE = os.environ.get("SENTINELX_LOG_PATH", "core/tests/fixtures/auth_small.log")

USERS = ["root", "admin", "user1", "git", "ubuntu", "guest", "dbuser"]
IPS = ["192.168.1.105", "10.0.0.42", "198.51.100.12", "203.0.113.88", "185.190.140.5"]

print(f"Starting standard mock log stream engine. Feeding into: {LOG_FILE}")
print("Press Ctrl+C to terminate generator instance.")

# Initialize the stream destination file clean on startup lifecycle runs
os.makedirs(os.path.dirname(os.path.abspath(LOG_FILE)), exist_ok=True)
with open(LOG_FILE, "w") as f:
    f.write("")

try:
    while True:
        # Format matching standard traditional Syslog patterns: 'Jul 11 21:30:15'
        timestamp = datetime.now().strftime("%b %e %H:%M:%S")
        ip = random.choice(IPS)
        user = random.choice(USERS)
        port = random.randint(30000, 65000)

        event_choice = random.choices(
            ["failed", "invalid", "accepted"],
            weights=[60, 20, 20],
            k=1
        )[0]

        if event_choice == "failed":
            log_line = f"{timestamp} localhost sshd[2201]: Failed password for {user} from {ip} port {port} ssh2\n"
        elif event_choice == "invalid":
            log_line = f"{timestamp} localhost sshd[2201]: Invalid user {user} from {ip} port {port}\n"
        else:
            log_line = f"{timestamp} localhost sshd[2201]: Accepted password for {user} from {ip} port {port} ssh2\n"

        with open(LOG_FILE, "a") as f:
            f.write(log_line)
            f.flush()

        print(f"Dispatched: {log_line.strip()}")
        time.sleep(random.uniform(0.5, 1.5))

except KeyboardInterrupt:
    print("\nLog streaming generation halted gracefully.")