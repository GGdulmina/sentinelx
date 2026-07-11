"""Integration tests verifying clean process signal handling."""

import sys
import signal
import subprocess
import time


def test_it_shutdown_001_graceful_sigint() -> None:
    """Verify that run.py handles execution termination cleanly with no traceback."""
    # Ensure run.py exists in root or create a baseline mockup for runtime processing
    # Spawning the actual script entrypoint under an independent runtime process
    proc = subprocess.Popen(
        [sys.executable, "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Allow startup allocation flights to resolve
    time.sleep(1.0)

    # Issue clean SIGINT to mimic manual operator cancellation
    proc.send_signal(signal.SIGINT)
    
    try:
        stdout, stderr = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()

    # The presence of Traceback indicates failure to catch signals properly
    assert "Traceback" not in stderr, f"Raw execution traceback leaked during exit:\n{stderr}"