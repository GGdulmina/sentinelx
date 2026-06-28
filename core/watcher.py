import time
import os
import logging

logger = logging.getLogger(__name__)

def follow(log_path: str):
    """
    Generator that yields new lines from a log file in real time.
    Handles log rotation (detecting via os.stat on the log path compared to open fstat)
    and truncation (re-seeking to the start of the file if size drops).
    """
    first_open = True
    while True:
        try:
            if not os.path.exists(log_path):
                logger.warning(f"Log file {log_path} does not exist. Waiting for it to be created...")
                time.sleep(5)
                continue

            with open(log_path, "r", errors="replace") as f:
                # Get initial inode
                try:
                    stat_info = os.fstat(f.fileno())
                    inode = stat_info.st_ino
                    
                    if first_open:
                        # Only seek to end on the initial startup
                        f.seek(0, os.SEEK_END)
                        first_open = False
                        logger.info(f"Opened and started watching {log_path} from the end (Inode: {inode})")
                    else:
                        # On reopen (due to rotation), read from the beginning of the new file
                        f.seek(0)
                        logger.info(f"Reopened and watching {log_path} from the beginning (Inode: {inode})")
                except OSError as e:
                    logger.error(f"Error getting file stat for {log_path}: {e}. Retrying...")
                    time.sleep(5)
                    continue

                while True:
                    line = f.readline()

                    if line:
                        yield line.strip()
                    else:
                        # Check if file was rotated or truncated
                        try:
                            # Check current file path inode
                            try:
                                current_stat = os.stat(log_path)
                                current_inode = current_stat.st_ino
                            except FileNotFoundError:
                                current_inode = None

                            # Check open file descriptor stat
                            fd_stat = os.fstat(f.fileno())
                        except OSError as e:
                            logger.error(f"Error checking stats for {log_path}: {e}. Reopening...")
                            break  # Break inner loop to reopen file

                        # Detect rotation (path has a different inode or does not exist)
                        if current_inode is None or current_inode != inode:
                            logger.info(f"Log rotation detected for {log_path} (Old Inode: {inode}, New Inode: {current_inode}). Reopening...")
                            break  # Break inner loop to reopen

                        # Detect truncation (file size of active descriptor decreased below read pointer)
                        if fd_stat.st_size < f.tell():
                            logger.info(f"Log truncation detected for {log_path}. Seeking to start...")
                            f.seek(0)
                            continue

                        # No new line, wait a bit
                        time.sleep(0.1)

        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Permissions/Missing file error reading {log_path}: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error in watcher for {log_path}: {e}. Retrying in 5 seconds...")
            time.sleep(5)