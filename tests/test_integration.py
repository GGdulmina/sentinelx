import os
import time
import pytest
import threading
import queue
from core.watcher import follow
from core.parser import parse_line
from core.alerts import AlertEngine

def test_integration_pipeline(tmp_path):
    log_file = tmp_path / "integration_auth.log"
    log_file.write_text("")
    
    # Configure alerts
    state_file = tmp_path / "integration_state.json"
    config = {
        'thresholds': {
            'info': 1,
            'warning': 2,      # lower thresholds for integration test speed
            'critical': 3
        },
        'reset_after': 3600,
        'alert_cooldown': 0,   # no cooldown for test assertions
        'state_file': str(state_file)
    }
    
    engine = AlertEngine(config)
    line_queue = queue.Queue()
    stop_event = threading.Event()
    
    def watch():
        for line in follow(str(log_file)):
            line_queue.put(line)
            if stop_event.is_set():
                break
                
    t = threading.Thread(target=watch, daemon=True)
    t.start()
    time.sleep(0.2)  # Wait for watcher to seek to end
    
    # Helper to write to log
    def write_log(line):
        with open(log_file, "a") as f:
            f.write(line + "\n")
            f.flush()
        time.sleep(0.1)

    # 1. Simulate a failed login
    write_log("2026-06-28T12:00:01.123456-05:00 localhost sshd[123]: Failed password for root from 192.168.1.50 port 55555 ssh2")
    raw_line = line_queue.get(timeout=2.0)
    parsed = parse_line(raw_line)
    assert parsed is not None
    assert parsed["event"] == "failed_password"
    
    alert = engine.process(parsed)
    assert alert is not None
    assert alert["severity"] == "info"
    assert alert["ip"] == "192.168.1.50"
    assert alert["username"] == "root"
    
    # 2. Simulate an invalid user login (should be count 2)
    write_log("2026-06-28T12:00:02.123456-05:00 localhost sshd[123]: Invalid user guest from 192.168.1.50 port 55556")
    raw_line = line_queue.get(timeout=2.0)
    parsed = parse_line(raw_line)
    assert parsed is not None
    assert parsed["event"] == "invalid_user"
    
    alert = engine.process(parsed)
    assert alert is not None
    assert alert["severity"] == "warning"  # threshold 2
    assert "Repeated failures — 2 attempts" in alert["message"]
    
    # 3. Simulate another failed login (should be count 3)
    write_log("2026-06-28T12:00:03.123456-05:00 localhost sshd[123]: Failed password for root from 192.168.1.50 port 55557 ssh2")
    raw_line = line_queue.get(timeout=2.0)
    parsed = parse_line(raw_line)
    
    alert = engine.process(parsed)
    assert alert is not None
    assert alert["severity"] == "critical"  # threshold 3
    assert "Brute force attack detected — 3 failures" in alert["message"]
    
    # 4. Simulate a successful login
    write_log("2026-06-28T12:00:04.123456-05:00 localhost sshd[123]: Accepted password for root from 192.168.1.50 port 55558 ssh2")
    raw_line = line_queue.get(timeout=2.0)
    parsed = parse_line(raw_line)
    
    alert = engine.process(parsed)
    assert alert is not None
    assert alert["severity"] == "info"
    assert "Successful login as 'root'" in alert["message"]
    
    stop_event.set()
