from collections import defaultdict


# How many failures before we escalate the severity
THRESHOLDS = {
    "info":     1,
    "warning":  3,
    "critical": 5,
}


class AlertEngine:
    """
    Tracks failed attempts per IP and decides severity.
    Think of it as a memory that gets more alarmed
    the more it sees the same IP failing.
    """

    def __init__(self):
        # defaultdict means if a key doesn't exist yet,
        # it automatically starts at 0 instead of crashing
        self.fail_counts = defaultdict(int)

    def process(self, parsed: dict) -> dict | None:
        """
        Takes a parsed event dict.
        Returns an alert dict if the event is worth reporting,
        None if it's not interesting.
        """
        event = parsed["event"]
        ip    = parsed["ip"]

        # successful login — always report this
        if event == "accepted_password":
            return self._make_alert("info", ip, parsed,
                                    f"Successful login as '{parsed['username']}'")

        # we only count failed_password, not invalid_user
        # (they come from the same attempt — avoid double counting)
        if event != "failed_password":
            return None

        # increment this IP's failure count
        self.fail_counts[ip] += 1
        count = self.fail_counts[ip]

        # decide severity based on count
        if count >= THRESHOLDS["critical"]:
            severity = "critical"
            message  = f"Brute force attack detected — {count} failures"
        elif count >= THRESHOLDS["warning"]:
            severity = "warning"
            message  = f"Repeated failures — {count} attempts"
        else:
            severity = "info"
            message  = f"Failed login attempt"

        return self._make_alert(severity, ip, parsed, message)

    def _make_alert(self, severity: str, ip: str,
                    parsed: dict, message: str) -> dict:
        return {
            "severity":  severity,
            "ip":        ip,
            "username":  parsed["username"],
            "timestamp": parsed["timestamp"],
            "message":   message,
        }