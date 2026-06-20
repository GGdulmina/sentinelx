# SentinelX

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Stage](https://img.shields.io/badge/status-concept__prototype-orange.svg)

SentinelX is a lightweight, real-time security information and event management (SIEM) concept designed to monitor Linux authentication logs, detect suspicious login patterns, and alert on potential security threats like brute-force attacks in real time.

By streaming log data through a decoupled pipeline (Watcher → Parser → Alert Engine), SentinelX provides immediate visibility into host-level authentication activity.

---

## Features

* **Real-Time Log Tailing:** Non-blocking, stream-based monitoring of authentication logs (`/var/log/auth.log`, `/var/log/secure`, or custom mock logs).
* **Stateful Alert Engine:** Tracks failure thresholds per IP address over time and dynamically escalates risk severities (`INFO` -> `WARNING` -> `CRITICAL`).
* **Immediate Visibility:** Structured console logging for actionable insight into authentication successes and failures.
* **Extensible Architecture:** Modular separation of log ingestion, pattern parsing, and event handling.

---

## Architecture Overview

SentinelX processes events through a unidirectional processing pipeline:

[ Log Source ] -> [ Watcher ] -> [ Parser ] -> [ Alert Engine ] -> [ Console Output ]

1. **Watcher (`core/watcher.py`):** Acts as a `tail -f` generator yielding new log lines as they hit the disk.
2. **Parser (`core/parser.py`):** Extracts timestamps, target usernames, source IP addresses, and event status.
3. **Alert Engine (`core/alerts.py`):** Maintains an in-memory cache of connection attempts to evaluate risk thresholds and trigger security alerts.

---

## Installation & Setup

### Prerequisites
* Python 3.9 or higher
* Root/Sudo privileges (if monitoring live production logs like `/var/log/auth.log`)

### Installation

```bash
cd sentinelx
pip install -r requirements.txt
```
## Manual Verification & Testing

You can safely test SentinelX in an isolated environment using the included mock log generator, or deploy it against live system logs.
Option 1: Verification via Mock Log Simulation

Run these commands in two separate terminal windows to verify the data pipeline end-to-end:
### Terminal 1: Start the mock log generator to stream simulated events into a local file
```bash
python3 generate_mock_logs.py
```

### Terminal 2: Point SentinelX at the newly generated mock file to monitor the output
```bash
python3 run.py mock_auth.log
```

## Option 2: Live System Monitoring

To monitor live host authentication logs in real time, run the application targeting your system's authentication log:

- Debian / Ubuntu systems
```bash
sudo python3 run.py /var/log/auth.log
```

- RHEL / CentOS / Rocky Linux systems
```bash
sudo python3 run.py /var/log/secure
```

## Alerting Thresholds

The stateful AlertEngine escalates incidents based on repeated failures from a unique source IP:
```bash
|_  Failure Count  _|_  Severity Level  _|_  Threat Status Description                             _|
|   1 Failure       |        INFO        |   Single failed login attempt.                           |
|   3 Failures      |       WARNING      |   Repeated login failures detected from the same source. |
|   5+ Failures     |       CRITICAL     |   Potential Brute Force attack signature identified.     |
|_  Success        _|_       INFO       _|_  Immediate notification on successful authentication.  _|
```

## Project Scope & Development Roadmap

- Current Implementation Note: While designed conceptually as a holistic Linux Authentication Monitor (SIEM), the baseline release focuses primarily on core SSH Daemon (sshd) log strings.

- To transition SentinelX into a comprehensive authentication monitoring ecosystem, the following expansion modules are planned:

* [ ] **Extended Event Parsing:** Add regex definitions within `core/parser.py` for local privilege escalations (`sudo` failures), PAM-level subsystem anomalies (`pam_unix`), and account modifications.
* [ ] **Systemd Integration:** Support reading directly from the systemd journal via `journalctl` bindings.
* [ ] **Persistent State Cache:** Migrate the in-memory alert counter to a lightweight local database (SQLite/Redis) to retain alert states across application restarts.
* [ ] **External Webhook Integrations:** Support alerts via Slack, Discord, or generic HTTP POST webhooks.
