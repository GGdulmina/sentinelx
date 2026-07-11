"""Unit tests verifying the operational streaming mechanics of the log watcher follow generator."""

import os
import tempfile
from unittest.mock import patch
from core.watcher import follow


class WatcherIdleSignal(BaseException):
    """Custom exception to break out of the infinite idle loop safely during testing."""
    pass


def test_ut_watcher_001_initialization_and_idle() -> None:
    """Verify that follow() starts at the end of the file and enters an idle waiting loop."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp_name = tmp.name
        tmp.write("Pre-existing log line\n")
        tmp.flush()

        # Initialize the follow generator
        watcher_gen = follow(tmp_name)
        
        # Patch time.sleep so that as soon as the generator enters its idle waiting state,
        # it throws our custom signal instead of hanging the entire test suite.
        with patch("core.watcher.time.sleep", side_effect=WatcherIdleSignal):
            try:
                next(watcher_gen)
                pytest.fail("Generator did not enter the expected infinite idle state.")
            except WatcherIdleSignal:
                # SUCCESS: The generator successfully opened the log and reached the idle loop
                pass

    # Safely clean up the file descriptor
    if os.path.exists(tmp_name):
        os.unlink(tmp_name)