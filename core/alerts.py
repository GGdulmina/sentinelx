import time
import json
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

def load_state(state_file: str) -> tuple[dict, dict]:
    """
    Load fail_info and last_alert from a JSON state file.
    Returns (fail_info, last_alert) dicts.
    """
    if not state_file or not os.path.exists(state_file):
        return {}, {}
    try:
        with open(state_file, "r") as f:
            data = json.load(f)
            fail_info = data.get("fail_info", {})
            last_alert = data.get("last_alert", {})
            logger.info(f"Successfully loaded state from {state_file}")
            return fail_info, last_alert
    except Exception as e:
        logger.error(f"Error loading state from {state_file}: {e}")
        return {}, {}

def save_state(state_file: str, fail_info: dict, last_alert: dict):
    """
    Save fail_info and last_alert to a JSON state file atomically.
    """
    if not state_file:
        return
    try:
        # Save atomically by writing to a temporary file and renaming it
        temp_file = state_file + ".tmp"
        with open(temp_file, "w") as f:
            json.dump({
                "fail_info": dict(fail_info),
                "last_alert": dict(last_alert)
            }, f, indent=2)
        os.replace(temp_file, state_file)
        logger.debug(f"Atomically saved state to {state_file}")
    except Exception as e:
        logger.error(f"Error saving state to {state_file}: {e}")

class AlertEngine:
    """
    Tracks failed attempts per IP and decides severity.
    Includes state persistence to prevent loss across restarts.
    """

    def __init__(self, config: dict):
        """
        Initialize with configuration dict.
        Expected keys:
          - thresholds: dict with 'info', 'warning', 'critical' counts
          - reset_after: seconds after which to reset failure count for an IP (default 86400)
          - alert_cooldown: minimum seconds between alerts for same IP (default 300)
          - state_file: file path for persistence (default: None)
        """
        self.config = config
        self.thresholds = config.get('thresholds', {
            'info': 1,
            'warning': 3,
            'critical': 5
        })
        self.reset_after = config.get('reset_after', 86400)
        self.alert_cooldown = config.get('alert_cooldown', 300)
        self.state_file = config.get('state_file')

        # Load persisted state if configured
        fail_info, last_alert = load_state(self.state_file)

        # Store for each IP: {'count': int, 'first_seen': float}
        self.fail_info = defaultdict(lambda: {'count': 0, 'first_seen': 0.0})
        for ip, info in fail_info.items():
            self.fail_info[ip] = info

        # Store last alert time per IP to enforce cooldown
        self.last_alert = defaultdict(float)
        for ip, t in last_alert.items():
            self.last_alert[ip] = t

    def _should_alert(self, ip: str) -> bool:
        """Check if enough time has passed since last alert for this IP."""
        now = time.time()
        last = self.last_alert.get(ip, 0.0)
        if now - last >= self.alert_cooldown:
            self.last_alert[ip] = now
            return True
        return False

    def process(self, parsed: dict) -> dict | None:
        """
        Takes a parsed event dict.
        Returns an alert dict if the event is worth reporting,
        None if it's not interesting or suppressed by cooldown.
        """
        event = parsed["event"]
        ip = parsed["ip"]
        now = time.time()

        # 1. Successful login
        # We always report this if cooldown allows.
        if event == "accepted_password":
            if self._should_alert(ip):
                alert = self._make_alert("info", ip, parsed, f"Successful login as '{parsed['username']}'")
                save_state(self.state_file, self.fail_info, self.last_alert)
                return alert
            return None

        # 2. Failed logins and invalid user attempts
        if event not in ("failed_password", "invalid_user"):
            return None

        # Get or initialize info for this IP
        info = self.fail_info[ip]
        
        # If first_seen is old beyond reset_after, reset the count
        if info['first_seen'] and (now - info['first_seen'] > self.reset_after):
            logger.info(f"Resetting failure count window for IP {ip} (reached reset_after window)")
            info['count'] = 0
            info['first_seen'] = now

        # If this is the first failure in the window, set first_seen
        if info['count'] == 0:
            info['first_seen'] = now

        # Increment failure count
        info['count'] += 1
        count = info['count']

        # Decide severity based on count
        if count >= self.thresholds["critical"]:
            severity = "critical"
            message = f"Brute force attack detected — {count} failures"
        elif count >= self.thresholds["warning"]:
            severity = "warning"
            message = f"Repeated failures — {count} attempts"
        else:
            severity = "info"
            message = f"Failed login attempt"

        # Check if we should alert (cooldown)
        if self._should_alert(ip):
            alert = self._make_alert(severity, ip, parsed, message)
            save_state(self.state_file, self.fail_info, self.last_alert)
            return alert
        
        # Save state even if we didn't alert, to keep the failure count persisted
        save_state(self.state_file, self.fail_info, self.last_alert)
        return None

    def _make_alert(self, severity: str, ip: str,
                    parsed: dict, message: str) -> dict:
        return {
            "severity":  severity,
            "ip":        ip,
            "username":  parsed["username"],
            "timestamp": parsed["timestamp"],
            "message":   message
        }