"""Integration tests verifying state recovery across engine lifecycles."""

import os
from core.alerts import AlertEngine


def test_it_restart_001_state_recovery() -> None:
    """Verify that a newly instantiated engine loads historical counts correctly."""
    test_state = "integration_test_state.json"
    if os.path.exists(test_state):
        os.remove(test_state)

    # Lifecycle 1: Instantiate engine and record an attack signature
    engine_v1 = AlertEngine(state_path=test_state)
    event = {"event": "failed_password", "username": "admin", "ip": "10.10.10.10", "timestamp": "Jul 11 20:00:00"}
    engine_v1.process_event(event)
    
    assert engine_v1.get_fail_count("10.10.10.10") == 1
    del engine_v1  # Destroy instance context explicitly

    # Lifecycle 2: Spin up a new engine instance pointing to the same file
    engine_v2 = AlertEngine(state_path=test_state)
    assert engine_v2.get_fail_count("10.10.10.10") == 1, "State persistence loss detected across engine restart!"

    if os.path.exists(test_state):
        os.remove(test_state)