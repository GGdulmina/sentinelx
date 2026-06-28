import os
import time
import pytest
import threading
from core.watcher import follow

def test_watcher_follow_and_append(tmp_path):
    log_file = tmp_path / "auth.log"
    # Create empty file
    log_file.write_text("")
    
    lines = []
    stop_event = threading.Event()
    
    def watch():
        for line in follow(str(log_file)):
            lines.append(line)
            if stop_event.is_set():
                break

    t = threading.Thread(target=watch, daemon=True)
    t.start()
    time.sleep(0.2)  # Wait for watcher to seek to end
    
    # Write line
    with open(log_file, "a") as f:
        f.write("Line 1\n")
        f.flush()
        
    time.sleep(0.2)
    assert len(lines) == 1
    assert lines[0] == "Line 1"
    
    # Write another line
    with open(log_file, "a") as f:
        f.write("Line 2\n")
        f.flush()
        
    time.sleep(0.2)
    assert len(lines) == 2
    assert lines[1] == "Line 2"
    
    stop_event.set()

def test_watcher_truncation(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text("")
    
    lines = []
    stop_event = threading.Event()
    
    def watch():
        for line in follow(str(log_file)):
            lines.append(line)
            if stop_event.is_set():
                break

    t = threading.Thread(target=watch, daemon=True)
    t.start()
    time.sleep(0.2)
    
    # Append line 1
    with open(log_file, "a") as f:
        f.write("Line 1\n")
        f.flush()
        
    time.sleep(0.2)
    assert len(lines) == 1
    assert lines[-1] == "Line 1"
    
    # Truncate file (size drops to 0)
    with open(log_file, "w") as f:
        pass
        
    time.sleep(0.2)  # Wait for watcher to register size drop and seek to 0
    
    # Write line 2 at start of file
    with open(log_file, "a") as f:
        f.write("Line 2 after truncate\n")
        f.flush()
        
    time.sleep(0.2)
    # The watcher should seek to 0 and find "Line 2 after truncate"
    assert len(lines) == 2
    assert lines[-1] == "Line 2 after truncate"
    
    stop_event.set()

def test_watcher_rotation(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text("")
    
    lines = []
    stop_event = threading.Event()
    
    def watch():
        for line in follow(str(log_file)):
            lines.append(line)
            if stop_event.is_set():
                break

    t = threading.Thread(target=watch, daemon=True)
    t.start()
    time.sleep(0.2)
    
    # Write line 1
    with open(log_file, "a") as f:
        f.write("Line 1 before rotate\n")
        f.flush()
        
    time.sleep(0.2)
    assert len(lines) == 1
    assert lines[-1] == "Line 1 before rotate"
    
    # Rotate: rename original file and create a new empty file at the original path
    rotated_file = tmp_path / "auth.log.1"
    os.rename(log_file, rotated_file)
    
    # Create new file with original name
    log_file.write_text("")
    
    # Write line 2 to new file
    with open(log_file, "a") as f:
        f.write("Line 2 after rotate\n")
        f.flush()
        
    time.sleep(0.3)
    # The watcher should detect the inode change, reopen the file, and yield Line 2
    assert len(lines) == 2
    assert lines[-1] == "Line 2 after rotate"
    
    stop_event.set()
