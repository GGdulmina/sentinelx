# SentinelX

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Stage](https://img.shields.io/badge/status-production__ready-brightgreen.svg)
![Tests](https://img.shields.io/badge/tests-16%20passed-brightgreen.svg)

SentinelX is a lightweight, real-time **Security Information & Event Management
(SIEM)** daemon for Linux authentication logs. It tails `sshd` log streams,
parses authentication events with anchored (ReDoS-safe) regular expressions,
tracks per-IP failure counts, escalates alerts as failure thresholds are
crossed, persists state atomically, and ships every alert to a live web
dashboard over WebSocket.

The runtime is built on Flask + Flask-SocketIO (eventlet) and is safe to run
without root: the watcher reads whatever file path is given to it, including
the bundled test fixture used in development.

---

## Quick Start

The fastest way to see SentinelX working is to point it at the bundled
fixture file with the `SENTINELX_LOG_PATH` environment variable, then open the
dashboard in a browser.

### 1. Clone, install, and verify

```bash
git clone https://github.com/GGdulmina/sentinelx.git
cd sentinelx

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

./manage.sh test      # 16/16 unit + integration + stress tests
./manage.sh lint      # syntax check
```

### 2. Run SentinelX against a log file

The runtime looks for a log path in this order:

1. `SENTINELX_LOG_PATH` environment variable (highest priority — **use this for the demo flow**)
2. The first existing path listed in `log_paths` from `config.yaml`
3. Built-in fallback: `core/tests/fixtures/auth_small.log`

```bash
export SENTINELX_LOG_PATH="core/tests/fixtures/auth_small.log"
./manage.sh run
```

You should see:

```text
Initializing SentinelX Operational System Fabric...
Background daemon tracking target log vector: core/tests/fixtures/auth_small.log
Opened and started watching core/tests/fixtures/auth_small.log from the end
 * Running on http://127.0.0.1:5000
```

Open <http://127.0.0.1:5000> for the real-time dashboard, or query the API:

```bash
curl http://127.0.0.1:5000/api/v1/health
curl http://127.0.0.1:5000/api/v1/stats
```

### 3. Feed it mock traffic

In a second terminal, point the mock generator at the **same** file and watch
alerts flow into the dashboard:

```bash
export SENTINELX_LOG_PATH="core/tests/fixtures/auth_small.log"
./manage.sh mock-logs
```

The generator truncates the fixture, then writes randomised
`Failed password`, `Invalid user`, and `Accepted password` lines. The watcher
detects the truncation, the parser extracts the events, the alert engine
escalates them, and the dashboard updates in real time via SocketIO.

---

## Features

- **Real-time tailing** of any `sshd`-style auth log via a generator-based
  watcher that detects log rotation (inode comparison) and truncation.
- **Threaded background daemon** (Flask-SocketIO background task) parses and
  alerts off the main thread, so the web server stays responsive.
- **ReDoS-safe regex** — patterns are anchored and free of greedy `.*` so
  hostile input cannot trigger catastrophic backtracking.
- **Input sanitisation** — `core.parser.sanitize_input` strips ANSI escapes
  and escapes non-printable bytes to prevent log/terminal injection.
- **Atomic state persistence** — per-IP failure counts, last-alert timestamps,
  and last-severity maps are written through a `*.tmp` + `os.replace` pair so
  abrupt shutdowns do not corrupt `sentinelx_state.json`.
- **Severity escalation** — `INFO → WARNING → CRITICAL` thresholds are
  configurable, with severity-escalation bypass on the alert cooldown so
  critical events are never throttled away.
- **Privilege dropping** — when started as `root`, the runtime drops to the
  configured unprivileged user/group (defaults: `nobody` / `nogroup`) before
  serving HTTP traffic.
- **Live web dashboard** — `templates/index.html` plus a SocketIO channel
  (`security_alert` events) renders alerts and runtime stats.
- **Layered configuration** — defaults, `config.yaml`, and `SENTINELX_*`
  environment variables merge in priority order.

---

## Documentation

The full documentation set lives under `docs/`:

| Guide | Purpose |
|---|---|
| [docs/installation.md](docs/installation.md) | Prerequisites, venv setup, permissions, systemd unit |
| [docs/configuration.md](docs/configuration.md) | `config.yaml` schema, environment variables, merge order |
| [docs/usage.md](docs/usage.md) | Running the daemon, the mock-logs flow, reading the dashboard |
| [docs/architecture.md](docs/architecture.md) | Component layout, data flow, threading model |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Common runtime errors and their fixes |
| [docs/QA/](docs/QA) | Test reports and QA findings |
| [docs/archive_journal/](docs/archive_journal) | Development journal entries |

---

## Project Layout

```text
sentinelx/
├── manage.sh                  # Helper script (run / test / mock-logs / lint / clean)
├── run.py                     # Daemon + Flask-SocketIO web entrypoint
├── config.py                  # YAML + env-var configuration loader
├── config.yaml                # Active configuration
├── config.yaml.example        # Documented configuration template
├── generate_mock_logs.py      # Mock sshd traffic generator
├── requirements.txt
├── templates/
│   └── index.html             # Live web dashboard
├── core/
│   ├── watcher.py             # Log tailing / rotation / truncation
│   ├── parser.py              # ReDoS-safe regex parser + sanitiser
│   ├── alerts.py              # AlertEngine + state persistence
│   ├── privileges.py          # Root → unprivileged drop
│   └── tests/                 # unit/, integration/, stress/
└── docs/
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, test layout, and
the pull-request checklist.

## License

MIT — see [LICENSE](LICENSE).
