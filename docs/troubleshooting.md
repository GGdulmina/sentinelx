# SentinelX Troubleshooting Guide

This guide helps you identify and resolve common issues encountered while deploying or operating SentinelX.

---

## 1. File Permissions / Access Issues

### Symptom: `[ERROR] Cannot read log file /var/log/auth.log: [Errno 13] Permission denied`

#### Why this happens:
System logs are highly sensitive and are restricted to `root` or members of privileged administrative groups (like `adm` or `log`).

#### Solutions:
- **Run as root with automatic privilege dropping**: 
  Start SentinelX as root. It will open the log files, then drop privileges to `nobody` or the configured unprivileged user.
  ```bash
  sudo ./manage.sh run
  ```
- **Ensure the unprivileged user has access**:
  If you configure privilege dropping to user `sentinelx`, make sure this user is added to the `adm` group so that it has permission to reopen the log file after rotation:
  ```bash
  sudo usermod -aG adm sentinelx
  ```
- **Run as an authorized user directly**:
  Run SentinelX as a user who already has read permissions to the files (without using sudo).

---

## 2. Log Rotation Issues

### Symptom: SentinelX stops showing new login alerts after midnight or log rotation.

#### Why this happens:
In older versions, SentinelX tracked log files via their open file descriptor (`f.fileno()`). When the file was rotated by `logrotate`, the inode of the path changed, but the file descriptor kept pointing to the old rotated log file (e.g., `auth.log.1`), failing to monitor new entries.

#### Solutions:
- **Upgrade**: Ensure you are running the latest version of `core/watcher.py` which stats the *file path* (`os.stat(log_path).st_ino`) and compares it with the descriptor's inode to detect rotations and reopen the files automatically.
- **Permission Check**: Make sure the unprivileged user that SentinelX dropped privileges to has read access to the directory containing the logs, so it can read the newly created log file.

---

## 3. State Persistence Issues

### Symptom: Failure counts reset to 0 after SentinelX restarts, or errors like `[ERROR] Error loading state...` are logged.

#### Why this happens:
- State file path (`sentinelx_state.json`) is not configured or disabled (`state_file: null`).
- The unprivileged user running SentinelX does not have write access to the directory to save/update the state file.
- The state file was corrupted.

#### Solutions:
- **Enable State Persistence**: Verify that `state_file` is defined in `config.yaml` and is set to a valid writable path.
- **Fix Directory Ownership**: Ensure the SentinelX process user has write permissions to the working directory:
  ```bash
  sudo chown -R sentinelx:sentinelx /opt/sentinelx
  ```
- **Corrupted State Recovery**: If the state file contains invalid JSON, delete it. SentinelX will automatically initialize a new state file on the next failure event:
  ```bash
  rm sentinelx_state.json
  ```
  *(Note: SentinelX uses atomic file replacements via temporary files (`os.replace`) to prevent file corruption during sudden system shutdowns).*

---

## 4. Watcher/Tailing Stalled

### Symptom: Log generator writes log entries but SentinelX prints nothing.

#### Solutions:
- Check if you started SentinelX and the log generator on different file paths. Ensure both point to the exact same file (e.g., `./manage.sh run mock_auth.log` and `./manage.sh mock-logs`).
- Remember that SentinelX seeks to the end of the file on its *very first* run to skip old logs. It will only print alerts for logs appended *after* SentinelX starts.
