#_1 app.py
#_2 SentinelX - Failed Login Detector import re from collections import defaultdict

import re
from collections import defaultdict

log_file = "/var/log/auth.log"


def show_recent_logs():
    with open(log_file, "r") as file:
        lines = file.readlines()[-10:]

        print("\nLast 10 log entries:\n")

        for line in lines:
            print(line.strip())


def detect_failed_logins():
    failed_attempts = defaultdict(int)

    with open(log_file, "r") as file:
        for line in file:

            if "Failed password" in line:
                match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)

                if match:
                    ip = match.group(1)
                    failed_attempts[ip] += 1

    print("\nSentinelX Security Report\n")

    if not failed_attempts:
        print("No failed login attempts detected.")

    else:
        for ip, count in failed_attempts.items():
            print(f"IP: {ip} | Attempts: {count}")

            if count >= 5:
                print("⚠ Possible brute force attack detected")


show_recent_logs()
detect_failed_logins()