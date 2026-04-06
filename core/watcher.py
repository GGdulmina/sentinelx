import time
import os


def follow(log_path: str): # the generator
    """
    Generator that yields new lines from a log file in real time.
    Works like 'tail -f' — waits for new content and yields
    each line as it appears.
    """
    try:
        with open(log_path, "r") as f:
            f.seek(0, os.SEEK_END)  # jump to end — skip old history

            print(f"[SentinelX] Watching {log_path} ...")

            while True:
                line = f.readline()

                if line:
                    yield line.strip()
                else:
                    time.sleep(0.1)  # no new line yet — wait briefly

    except FileNotFoundError:
        print(f"[ERROR] Log file not found: {log_path}")
    except PermissionError:
        print(f"[ERROR] Permission denied reading: {log_path}")
        print("        Try running with: sudo python run.py")