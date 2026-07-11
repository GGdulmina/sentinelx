"""Alert engine for SentinelX.

Tracks failed and invalid authentication events per remote IP address, manages 
time-based escalation thresholds, and orchestrates state persistence.
"""

import json
import logging
import os
import time
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def load_state(state_file: Optional[str]) -> Tuple[Dict[str, Any], Dict[str, float], Dict[str, str]]:
    """Load fail_info, last_alert, and last_severity metrics from a JSON state file.

    Args:
        state_file: Path targeting the source JSON state persistence index.

    Returns:
        A tuple containing three dictionaries: fail_info mappings, 
        last_alert tracking metrics, and last_severity tracking metrics.
    """
    if not state_file or not os.path.exists(state_file):
        return {}, {}, {}
    try:
        with open(state_file, "r") as f:
            data = json.load(f)
            fail_info = data.get("fail_info", {})
            last_alert = data.get("last_alert", {})
            last_severity = data.get("last_severity", {})
            logger.info("Successfully loaded system persistence state metrics.")
            return fail_info, last_alert, last_severity
    except Exception as e:
        logger.error(f"Error loading system state index: {e}")
        return {}, {}, {}


def save_state(state_file: Optional[str], fail_info: Dict[str, Any], 
               last_alert: Dict[str, float], last_severity: Dict[str, str]) -> None:
    """Save failure tracking metrics and state maps atomically to disk.

    Args:
        state_file: Destination target system path for the persistent index.
        fail_info: Dictionary containing failure counters per client IP.
        last_alert: Cooldown lookup mapping keeping track of notification timestamps.
        last_severity: Historical tracking mapping of historical alert severities.
    """
    if not state_file:
        return
    try:
        temp_file = f"{state_file}.tmp"
        with open(temp_file, "w") as f:
            json.dump({
                "fail_info": dict(fail_info),
                "last_alert": dict(last_alert),
                "last_severity": dict(last_severity)
            }, f, indent=2)
        os.replace(temp_file, state_file)
        logger.debug("State tracking metrics saved atomically to local storage.")
    except Exception as e:
        logger.error(f"Error executing state serialization sequence: {e}")


class AlertEngine:
    """Tracks malicious authentication failure telemetry and handles escalations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, state_path: Optional[str] = None) -> None:
        """Initialize tracking dimensions and load structural configuration metadata.

        Args:
            config: Key-value dictionary containing custom threshold limits.
            state_path: Alternative string path providing direct test isolation paths.
        """
        self.config = config or {}
        
        self.thresholds: Dict[str, int] = self.config.get('thresholds', {
            'info': 1,
            'warning': 3,
            'critical': 5
        })
        self.reset_after: int = self.config.get('reset_after', 86400)
        self.alert_cooldown: int = self.config.get('alert_cooldown', 300)
        
        self.state_file: Optional[str] = state_path or self.config.get('state_file')

        # Load historical execution state bounds
        fail_info, last_alert, last_severity = load_state(self.state_file)

        self.fail_info: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'count': 0, 'first_seen': 0.0})
        for ip, info in fail_info.items():
            self.fail_info[ip] = info

        self.last_alert: Dict[str, float] = defaultdict(float)
        for ip, ts in last_alert.items():
            self.last_alert[ip] = ts

        self.last_severity: Dict[str, str] = defaultdict(str)
        for ip, sev in last_severity.items():
            self.last_severity[ip] = sev

    def _should_alert(self, ip: str, severity: str, now: float) -> bool:
        """Evaluate if notifications for an IP address should bypass or respect cooldown.

        Args:
            ip: Target source string representation of the client system.
            severity: The evaluated severity tier for the current event.
            now: Floating point epoch timestamp of active event arrival.

        Returns:
            Boolean declaring whether notification throttling is bypassed or clear.
        """
        # CRITICAL SECTOR: If severity has escalated, bypass temporal cooldown limits
        if severity != self.last_severity.get(ip, ""):
            self.last_alert[ip] = now
            self.last_severity[ip] = severity
            return True

        last = self.last_alert.get(ip, 0.0)
        if now - last >= self.alert_cooldown:
            self.last_alert[ip] = now
            self.last_severity[ip] = severity
            return True
        return False

    def get_fail_count(self, ip: str) -> int:
        """Retrieve current baseline event counters tracked against an IP vector."""
        return self.fail_info[ip]['count']

    def process_event(self, parsed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming parsed authorization metrics and evaluate threat postures."""
        event: str = parsed.get("event", "")
        ip: str = parsed.get("ip", "")
        now: float = time.time()
        alert: Optional[Dict[str, Any]] = None

        # Handle successful authorization confirmations
        if event == "accepted_password":
            if self._should_alert(ip, "INFO", now):
                alert = self._make_alert("INFO", ip, parsed, f"Successful login as '{parsed.get('username')}'")
                save_state(self.state_file, self.fail_info, self.last_alert, self.last_severity)
            return alert

        # Filter outside attack context tracks
        if event not in ("failed_password", "invalid_user"):
            return None

        info = self.fail_info[ip]
        
        # Evaluate window reset policies
        if info['first_seen'] and (now - info['first_seen'] > self.reset_after):
            logger.info(f"Resetting failure window bounds for IP asset: {ip}")
            info['count'] = 0
            info['first_seen'] = now

        if info['count'] == 0:
            info['first_seen'] = now

        info['count'] += 1
        count: int = info['count']

        # Determine structural alerting bounds
        if count >= self.thresholds.get("critical", 5):
            severity = "CRITICAL"
            message = f"Brute force attack detected — {count} failures"
        elif count >= self.thresholds.get("warning", 3):
            severity = "WARNING"
            message = f"Repeated failures — {count} attempts"
        else:
            severity = "INFO"
            message = "Failed login attempt"

        # Check for alert dispatch with severity validation logic
        if self._should_alert(ip, severity, now):
            alert = self._make_alert(severity, ip, parsed, message)
            
        save_state(self.state_file, self.fail_info, self.last_alert, self.last_severity)
        return alert

    def _make_alert(self, severity: str, ip: str, parsed: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Construct a standardized alert payload dictionary."""
        return {
            "severity":  severity,
            "ip":        ip,
            "username":  parsed.get("username", "unknown"),
            "timestamp": parsed.get("timestamp", ""),
            "message":   message
        }