# SentinelX Usage Guide

This guide covers daily operations, running tests, simulating logs, and understanding SentinelX outputs.

---

## 1. Running SentinelX

SentinelX can be run directly from Python or via the helper management script.

### Using Python

```bash
# Run with default config.yaml
python run.py

# Run and override the log path via argument
python run.py /var/log/secure

# Run and load a custom configuration YAML file
python run.py custom_config.yaml
```

### Using the Management Helper Script

```bash
# Run SentinelX
./manage.sh run
```

---

## 2. Simulating SSH Traffic

You can generate mock authentication logs to test SentinelX without needing actual SSH activity or root access.

### Step 1: Start SentinelX Watching the Mock Log
Start SentinelX and direct it to watch `mock_auth.log`:

```bash
python run.py mock_auth.log
# Or
./manage.sh run mock_auth.log
```

### Step 2: Start Mock Log Generator
In another terminal, start the mock log generator:

```bash
python generate_mock_logs.py
# Or
./manage.sh mock-logs
```

The generator will truncate `mock_auth.log` and begin writing random successful and failed login logs. You will see SentinelX instantly capture these lines, track counts, and print color-neutral alerts in the first terminal.

---

## 3. Running the Test Suite

SentinelX has a comprehensive test suite (unit and integration tests) built with `pytest`.

### Using the Helper Script (Recommended)

```bash
./manage.sh test
```

### Using Pytest Directly

```bash
PYTHONPATH=. pytest
```

---

## 4. Understanding Alert Outputs

When SentinelX detects security-related events, it prints structured logs to standard output. Below is an example:

```text
[  INFO  ] 2026-06-28T12:02:26.553975-05:00  IP: 10.0.0.42        User: user1        Failed login attempt
[WARNING ] 2026-06-28T12:02:40.711591-05:00  IP: 185.190.140.5    User: git          Repeated failures — 3 attempts
[CRITICAL] 2026-06-28T12:02:46.225045-05:00  IP: 185.190.140.5    User: guest        Brute force attack detected — 5 failures
[  INFO  ] 2026-06-28T12:02:48.759931-05:00  IP: 192.168.1.105    User: root         Successful login as 'root'
```

### Output Breakdown

- **Level Indicator (`[  INFO  ]`, `[WARNING ]`, `[CRITICAL]`)**: Severity based on failure count thresholds.
- **Timestamp**: Date/time extracted directly from the log file (or formatted using `date_format` config).
- **IP Address**: The origin IP address, padded to align columns.
- **Username**: The target username, padded to align columns.
- **Alert Message**: Actionable description of the event.
