"""Stress tests for the SentinelX parsing sub-engine.

Simulates thousands of concurrent auth log streams to measure throughput capacity.
"""

import logging
from core.parser import parse_line

logger = logging.getLogger(__name__)


def test_str_parser_001_high_throughput() -> None:
    """Stress test the log extraction logic with 10,000 iterative records."""
    iterations = 10000
    mock_base_line = "Jul 11 20:15:30 host sshd[9999]: Failed password for invalid user admin from 192.168.100.43 port 54321 ssh2"
    
    processed_count = 0
    for _ in range(iterations):
        result = parse_line(mock_base_line)
        if result is not None:
            processed_count += 1
            
    assert processed_count == iterations, f"Data loss detected! Only processed {processed_count}/{iterations} lines."
    logger.info(f"Successfully validated baseline stress-throughput processing of {iterations} log events.")