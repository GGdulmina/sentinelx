# SentinelX Installation Guide

This document outlines the step-by-step procedure to install and set up SentinelX on Linux-based environments.

## Prerequisites

- **OS**: Linux (tested on RHEL, CentOS, Debian, Ubuntu)
- **Python**: Version 3.7 or higher
- **Privileges**: SentinelX needs read permission to target log files (e.g., `/var/log/auth.log` or `/var/log/secure`). This requires root privileges or membership in an unprivileged group like `adm`.

---

## 1. System Setup

### Clone Repository

Clone the project repository to your desired installation directory:

```bash
git clone https://github.com/GGdulmina/sentinelx.git /opt/sentinelx
cd /opt/sentinelx
```

### Virtual Environment Setup

We recommend running SentinelX in a dedicated Python virtual environment to avoid package dependency conflicts.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

## 2. Permissions Management

To read system authentication logs, the user running SentinelX must have read access.

### Option A: Dedicated Unprivileged User (Recommended)

1. Create a dedicated system user (e.g., `sentinelx`) and add them to the `adm` group (or whichever group owns `/var/log/auth.log`):

   ```bash
   sudo useradd -r -s /usr/sbin/nologin sentinelx
   sudo usermod -aG adm sentinelx
   ```

2. Configure SentinelX to run under this user. Ensure that the state file path (`sentinelx_state.json`) is writable by the `sentinelx` user:

   ```bash
   sudo chown -R sentinelx:sentinelx /opt/sentinelx
   ```

### Option B: Drop Privileges from Root

You can start SentinelX as `root` (via `sudo`) to allow opening the log files. SentinelX is designed to automatically drop privileges to an unprivileged user (defaults to `nobody` user and `nogroup` group) once files are opened.

Ensure the unprivileged user has read access to the log path. If not, the application will fail to reopen the logs when they rotate.

---

## 3. Running as a Service (systemd)

For continuous, reliable monitoring in production environments, run SentinelX as a systemd service.

1. Create a service file at `/etc/systemd/system/sentinelx.service`:

```ini
[Unit]
Description=SentinelX Authentication Log Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/sentinelx
ExecStart=/opt/sentinelx/venv/bin/python /opt/sentinelx/run.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

2. Reload systemd, enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sentinelx.service
sudo systemctl start sentinelx.service
```

3. Check the service status:

```bash
sudo systemctl status sentinelx.service
```
