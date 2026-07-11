"""Stress tests verifying queue durability under tight processing iteration loads."""

import queue
from core.parser import parse_line


def test_str_pipeline_001_concurrency_load() -> None:
    """Blast the parsing pipeline processing loop with rapid data input streams."""
    data_queue: queue.Queue = queue.Queue()
    payload = "Jul 11 20:40:00 host sshd[1]: Failed password for root from 8.8.8.8 port 22 ssh2"
    
    for _ in range(1000):
        parsed = parse_line(payload)
        if parsed:
            data_queue.put(parsed)
            
    assert data_queue.qsize() == 1000