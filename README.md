# SentinelX

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](file:///home/id43/Desktop/GD43/sentinelx/LICENSE)
![Stage](https://img.shields.io/badge/status-production__ready-brightgreen.svg)

SentinelX is a lightweight, real-time security information and event management (SIEM) daemon designed to monitor Linux authentication logs, detect suspicious login patterns, and alert on potential security threats like brute-force attacks in real time.

By streaming log data through a concurrent, multi-threaded pipeline, SentinelX provides immediate, structured visibility into host-level authentication activity.

---

## Technical Documentation

Detailed guides are available in the `docs/` directory:

1. **[Installation Guide](file:///home/id43/Desktop/GD43/sentinelx/docs/installation.md)**: System prerequisites, environment setup, privileges dropping, and configuring systemd.
2. **[Configuration Guide](file:///home/id43/Desktop/GD43/sentinelx/docs/configuration.md)**: Configuration schema explanation (`config.yaml`), defaults, and environment variables.
3. **[Usage Guide](file:///home/id43/Desktop/GD43/sentinelx/docs/usage.md)**: Executing the application, simulating traffic using the mock generator, and reading outputs.
4. **[Troubleshooting Guide](file:///home/id43/Desktop/GD43/sentinelx/docs/troubleshooting.md)**: Permissions, log rotation recovery, state corruption, and watcher details.
5. **[Architecture Guide](file:///home/id43/Desktop/GD43/sentinelx/docs/architecture.md)**: Decoupled design overview, Mermaid sequence flow diagram, and components detail.

---

## Quick Start

### 1. Setup & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/GGdulmina/sentinelx.git
cd sentinelx

# Create virtual environment and install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Test Suite
Ensure that all unit and integration tests pass:
```bash
./manage.sh test
```

### 3. Simulate Traffic
To test the pipeline end-to-end without needing root privileges:

- **Terminal 1**: Start SentinelX on the mock log file:
  ```bash
  ./manage.sh run mock_auth.log
  ```

- **Terminal 2**: Generate mock authentication events:
  ```bash
  ./manage.sh mock-logs
  ```

---

## Features

- **Concurrent Multi-Tailing**: Tail multiple authentication log paths in parallel using thread-safe queues.
- **Robust Watcher**: Detects log rotation (inode changes) and truncation automatically, ensuring no gaps in logging.
- **ReDoS Prevention**: Anchored, strict regex patterns that prevent catastrophic backtracking vulnerabilities.
- **Input Sanitization**: Automatically strips ANSI escape codes and controls non-printable bytes to prevent terminal injection.
- **State Persistence**: Saves brute-force event counts atomically in a JSON file to withstand application crashes or restarts.
- **Privilege Dropping**: If started as root, automatically drops privileges to an unprivileged user (`nobody`) after startup.
- **Flexible Configuration**: Full YAML file and environment variable overrides.

---

## Contributing

Please read the **[Contributing Guidelines](file:///home/id43/Desktop/GD43/sentinelx/CONTRIBUTING.md)** before submitting pull requests.

## License

This project is licensed under the MIT License - see the **[LICENSE](file:///home/id43/Desktop/GD43/sentinelx/LICENSE)** file for details.
