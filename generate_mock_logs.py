import time
import random
from datetime import datetime

LOG_FILE = "mock_auth.log"

USERS = ["root", "admin", "user1", "git", "ubuntu", "guest", "dbuser"]
IPS = ["192.168.1.105", "10.0.0.42", "198.51.100.12", "203.0.113.88", "185.190.140.5"]

print(f"Starting mock log generator. Writing to {LOG_FILE}...")
print("Press Ctrl+C to stop.")

# Truncate/create the file fresh
with open(LOG_FILE, "w") as f:
    f.write("")

# Keep track of simulated attempts to make brute force realistic
failed_attempts = {}

try:
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        ip = random.choice(IPS)
        user = random.choice(USERS)
        port = random.randint(30000, 65000)

        # Decide event type:
        # If an IP starts failing, let's generate multiple failures to trigger the AlertEngine thresholds (3 warning, 5 critical)
        event_choice = random.choices(
            ["failed", "invalid", "accepted"],
            weights=[60, 20, 20],
            k=1
        )[0]

        if event_choice == "failed":
            log_line = f"{timestamp}.{random.randint(100000, 999999)}-05:00 localhost sshd[2201]: Failed password for {user} from {ip} port {port} ssh2\n"
        elif event_choice == "invalid":
            log_line = f"{timestamp}.{random.randint(100000, 999999)}-05:00 localhost sshd[2201]: Invalid user {user} from {ip} port {port}\n"
        else:
            log_line = f"{timestamp}.{random.randint(100000, 999999)}-05:00 localhost sshd[2201]: Accepted password for {user} from {ip} port {port} ssh2\n"

        with open(LOG_FILE, "a") as f:
            f.write(log_line)
            f.flush()

        print(f"Generated: {log_line.strip()}")
        time.sleep(random.uniform(0.5, 2.0))

except KeyboardInterrupt:
    print("\nGenerator stopped.")
