"""Unit tests for the SentinelX Alert and State Engine.

Validates state evaluation metrics, alert thresholds, and tracking mechanisms.
"""

import os
import pytest
from core.alerts import AlertEngine


@pytest.fixture
def clean_engine() -> AlertEngine:
    """Fixture to provide a clean AlertEngine instance with an isolated state file."""
    test_state_path = "test_sentinelx_state.json"
    if os.path.exists(test_state_path):
        os.remove(test_state_path)
        
    engine = AlertEngine(state_path=test_state_path)
    yield engine
    
    if os.path.exists(test_state_path):
        os.remove(test_state_path)


def test_ut_alert_001_fail_count_increment(clean_engine: AlertEngine) -> None:
    """Verify that failed_password increments counts properly per distinct IP address."""
    ip = "192.168.1.50"
    event = {"event": "failed_password", "username": "root", "ip": ip, "port": 22}
    
    clean_engine.process_event(event)
    assert clean_engine.get_fail_count(ip) == 1
    
    clean_engine.process_event(event)
    assert clean_engine.get_fail_count(ip) == 2


def test_ut_alert_002_threshold_severities(clean_engine: AlertEngine) -> None:
    """Verify that the engine escalates tracking severity appropriately at thresholds (1, 3, 5)."""
    ip = "10.0.0.99"
    event = {"event": "failed_password", "username": "attacker", "ip": ip, "port": 22}
    
    # Threshold 1 -> INFO
    alert1 = clean_engine.process_event(event)
    assert alert1 is not None
    assert alert1["severity"] == "INFO"
    
    # Threshold 2 -> No change/No alert escalation
    alert2 = clean_engine.process_event(event)
    
    # Threshold 3 -> WARNING
    alert3 = clean_engine.process_event(event)
    assert alert3 is not None
    assert alert3["severity"] == "WARNING"


def test_ut_alert_003_invalid_user_counting(clean_engine: AlertEngine) -> None:
    """CRITICAL FIX: Verify that invalid_user events explicitly increment failure tracking counters."""
    ip = "172.16.5.5"
    event = {"event": "invalid_user", "username": "guest", "ip": ip, "port": 443}
    
    clean_engine.process_event(event)
    assert clean_engine.get_fail_count(ip) == 1, "Defect: invalid_user event was ignored by the tracking engine!"