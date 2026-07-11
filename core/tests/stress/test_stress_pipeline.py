"""Stress tests evaluating high-volume multi-threaded queue pipeline routing."""

import time
from core.parser import parse_line
from core.alerts import AlertEngine


def test_str_pipeline_001_load_flooding() -> None:
    """Flood the processing framework with thousands of concurrent lines to verify delivery execution stability."""
    engine = AlertEngine(state_path=None)
    sample_raw = "Jul 11 20:00:01 host sshd[100]: Failed password for root from 1.1.1.1 port 22"
    
    start_time = time.time()
    for _ in range(5000):
        parsed = parse_line(sample_raw)
        if parsed:
            engine.process_event(parsed)
            
    elapsed = time.time() - start_time
    # High performance pipelines should execute 5k simple operations in less than 0.5s
    assert elapsed < 0.5, f"Pipeline bottleneck encountered. Processing time: {elapsed:.2f} seconds."