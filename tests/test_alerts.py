import time
import pytest
import os
import json
from unittest.mock import patch
from core.alerts import AlertEngine, load_state, save_state

@pytest.fixture
def base_config():
    return {
        'thresholds': {
            'info': 1,
            'warning': 3,
            'critical': 5
        },
        'reset_after': 2,      # low for testing reset
        'alert_cooldown': 100,  # high to test suppression
        'state_file': None
    }

def test_alert_thresholds_transition(base_config):
    engine = AlertEngine(base_config)
    
    # 1. First failure -> Info
    parsed_1 = {"event": "failed_password", "ip": "1.1.1.1", "username": "admin", "timestamp": "2026-06-28T12:00:00"}
    alert_1 = engine.process(parsed_1)
    assert alert_1 is not None
    assert alert_1["severity"] == "info"
    assert "Failed login attempt" in alert_1["message"]
    
    # 2. Second failure -> None (cooldown suppresses it)
    parsed_2 = {"event": "failed_password", "ip": "1.1.1.1", "username": "admin", "timestamp": "2026-06-28T12:00:01"}
    alert_2 = engine.process(parsed_2)
    assert alert_2 is None
    assert engine.fail_info["1.1.1.1"]["count"] == 2
    
    # Let's bypass cooldown for testing transitions by mocking time or resetting last_alert
    engine.last_alert["1.1.1.1"] = 0.0  # Force allow alert
    parsed_3 = {"event": "invalid_user", "ip": "1.1.1.1", "username": "admin", "timestamp": "2026-06-28T12:00:02"}
    alert_3 = engine.process(parsed_3)
    assert alert_3 is not None
    assert alert_3["severity"] == "warning"
    assert "Repeated failures — 3 attempts" in alert_3["message"]

    engine.last_alert["1.1.1.1"] = 0.0  # Force allow alert
    # 4th failure (no transition change, warning threshold is 3, critical is 5)
    parsed_4 = {"event": "failed_password", "ip": "1.1.1.1", "username": "admin", "timestamp": "2026-06-28T12:00:03"}
    alert_4 = engine.process(parsed_4)
    assert alert_4 is not None
    assert alert_4["severity"] == "warning"  # Still warning
    
    engine.last_alert["1.1.1.1"] = 0.0  # Force allow alert
    # 5th failure -> Critical
    parsed_5 = {"event": "failed_password", "ip": "1.1.1.1", "username": "admin", "timestamp": "2026-06-28T12:00:04"}
    alert_5 = engine.process(parsed_5)
    assert alert_5 is not None
    assert alert_5["severity"] == "critical"
    assert "Brute force attack detected — 5 failures" in alert_5["message"]

def test_alert_cooldown_suppression(base_config):
    engine = AlertEngine(base_config)
    parsed = {"event": "failed_password", "ip": "2.2.2.2", "username": "root", "timestamp": "2026-06-28T12:00:00"}
    
    # First alert allowed
    assert engine.process(parsed) is not None
    
    # Second alert suppressed by cooldown
    assert engine.process(parsed) is None
    
    # Move time forward past cooldown
    with patch('time.time', return_value=time.time() + 101):
        assert engine.process(parsed) is not None

def test_reset_after_window(base_config):
    engine = AlertEngine(base_config)
    parsed = {"event": "failed_password", "ip": "3.3.3.3", "username": "root", "timestamp": "2026-06-28T12:00:00"}
    
    # First failure
    engine.process(parsed)
    assert engine.fail_info["3.3.3.3"]["count"] == 1
    
    # Move time past reset_after (2 seconds)
    with patch('time.time', return_value=time.time() + 3):
        # Reset cooldown to allow output alert
        engine.last_alert["3.3.3.3"] = 0.0
        alert = engine.process(parsed)
        assert alert is not None
        # Count should reset to 1
        assert engine.fail_info["3.3.3.3"]["count"] == 1
        assert alert["severity"] == "info"

def test_successful_login_alert(base_config):
    engine = AlertEngine(base_config)
    parsed_success = {"event": "accepted_password", "ip": "4.4.4.4", "username": "user1", "timestamp": "2026-06-28T12:00:00"}
    
    alert = engine.process(parsed_success)
    assert alert is not None
    assert alert["severity"] == "info"
    assert "Successful login as 'user1'" in alert["message"]

def test_state_persistence(tmp_path):
    state_file = str(tmp_path / "test_state.json")
    config = {
        'thresholds': {'info': 1, 'warning': 3, 'critical': 5},
        'reset_after': 3600,
        'alert_cooldown': 0,
        'state_file': state_file
    }
    
    # Initialize engine and generate some failures
    engine = AlertEngine(config)
    parsed = {"event": "failed_password", "ip": "5.5.5.5", "username": "root", "timestamp": "2026-06-28T12:00:00"}
    
    # First failure
    engine.process(parsed)
    
    # Verify state file was created and contains the correct counts
    assert os.path.exists(state_file)
    with open(state_file, "r") as f:
        data = json.load(f)
        assert "5.5.5.5" in data["fail_info"]
        assert data["fail_info"]["5.5.5.5"]["count"] == 1
        
    # Create a new engine loading the same state file
    engine2 = AlertEngine(config)
    assert engine2.fail_info["5.5.5.5"]["count"] == 1
    
    # Process another failure under new engine
    engine2.process(parsed)
    assert engine2.fail_info["5.5.5.5"]["count"] == 2
    
    # Verify it updated state file
    with open(state_file, "r") as f:
        data2 = json.load(f)
        assert data2["fail_info"]["5.5.5.5"]["count"] == 2
