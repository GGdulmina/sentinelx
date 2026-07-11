"""Unit tests verifying thread-safe queue bound restrictions."""

import queue
import pytest


def test_ut_queue_001_bound_overflow() -> None:
    """Verify that the communication queue strictly enforces maxsize limits."""
    # Mimic the production maxsize strategy
    event_queue: queue.Queue = queue.Queue(maxsize=10)

    # Fill the queue up to its configuration limits
    for i in range(10):
        event_queue.put({"event": "failed_password", "ip": f"1.1.1.{i}"}, block=False)

    assert event_queue.full() is True

    # Attempting to insert another record immediately must raise a queue.Full exception
    with pytest.raises(queue.Full):
        event_queue.put({"event": "failed_password", "ip": "9.9.9.9"}, block=False)