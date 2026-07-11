"""Memory leak verification module for SentinelX.

Profiles memory stability across deep processing allocations using sys allocation counters.
"""

import gc
import sys
from core.alerts import AlertEngine


def test_str_mem_001_leak_detection() -> None:
    """Verify engine memory footprint remains structurally stable under cyclical allocations."""
    # Force a baseline collection run
    gc.collect()
    
    engine = AlertEngine(state_path=None) # Keep strictly in memory, no disk I/O side effects
    base_event = {"event": "failed_password", "username": "bot", "ip": "1.2.3.4", "timestamp": "now"}
    
    # Warmsup loop allocation tracking
    for _ in range(100):
        engine.process_event(base_event)
        
    gc.collect()
    baseline_objects = len(gc.get_objects())
    
    # Process an aggressive block of cyclical events targeting the matching data space
    for i in range(1000):
        cyclical_event = {"event": "failed_password", "username": "bot", "ip": f"10.0.0.{i % 10}", "timestamp": "now"}
        engine.process_event(cyclical_event)
        
    gc.collect()
    post_stress_objects = len(gc.get_objects())
    
    # Enforce standard delta thresholds. Lingering reference counts should be effectively flat.
    object_drift = post_stress_objects - baseline_objects
    assert object_drift < 50, f"Potential memory leak detected: Structural footprint increased by {object_drift} objects!"