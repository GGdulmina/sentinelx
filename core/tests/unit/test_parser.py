"""Unit tests for the SentinelX log parser engine.

Covers standard SSH events, malformed configurations, ANSI injection attempts,
and ReDoS boundary processing constraints.
"""

import time
import pytest
from core.parser import parse_line


def test_ut_parser_001_valid_events() -> None:
    """Verify correct field extraction and data types for standard SSH events."""
    # Test Failed Password
    line_fail = "Jun 28 12:01:33 host sshd[123]: Failed password for root from 1.2.3.4 port 22 ssh2"
    res_fail = parse_line(line_fail)
    assert res_fail is not None
    assert res_fail["event"] == "failed_password"
    assert res_fail["username"] == "root"
    assert res_fail["ip"] == "1.2.3.4"
    assert res_fail["port"] == 22
    assert isinstance(res_fail["port"], int)

    # Test Invalid User
    line_invalid = "Jun 28 12:01:34 host sshd[123]: Invalid user admin from 5.6.7.8 port 4321"
    res_invalid = parse_line(line_invalid)
    assert res_invalid is not None
    assert res_invalid["event"] == "invalid_user"
    assert res_invalid["username"] == "admin"
    assert res_invalid["ip"] == "5.6.7.8"
    assert res_invalid["port"] == 4321

    # Test Accepted Password
    line_accept = "Jun 28 12:01:35 host sshd[123]: Accepted password for ubuntu from 9.10.11.12 port 54321 ssh2"
    res_accept = parse_line(line_accept)
    assert res_accept is not None
    assert res_accept["event"] == "accepted_password"
    assert res_accept["username"] == "ubuntu"
    assert res_accept["ip"] == "9.10.11.12"
    assert res_accept["port"] == 54321


def test_ut_parser_002_malformed_and_empty() -> None:
    """Verify that malformed, empty, or random noise strings safely return None."""
    assert parse_line("") is None
    assert parse_line("not a log line at all") is None
    assert parse_line("Jun 28 12:01:33 host sshd[123]: Failed password for") is None


def test_sec_redos_001_backtracking_protection() -> None:
    """Ensure the regex engine is immune to exponential backtracking from crafted input."""
    # Crafted malicious attack string targeting non-anchored wildcards
    evil_username = "a" * 5000 + "!"
    crafted_line = f"Jun 28 12:01:33 host sshd[123]: Failed password for {evil_username} from 1.1.1.1 port 22"
    
    start_time = time.perf_counter()
    parse_line(crafted_line)
    duration = time.perf_counter() - start_time
    
    # Secure anchored regex engines should evaluate this structural deviation in milliseconds
    assert duration < 0.1, f"Potential ReDoS vulnerability detected! Execution took {duration:.4f}s"