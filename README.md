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

### 4. Pointing SentinelX at real log files

The Quick Start above uses a fixture plus a mock generator so you can see the
full pipeline without any setup. To run SentinelX against a **real** SSH auth
log, just point it at the file that already exists on your system — the mock
generator is not needed.

The runtime picks the log file in this order (see `run.py`):

1. `SENTINELX_LOG_PATH` env var — highest priority
2. The first existing path listed in `log_paths` from `config.yaml`
   (defaults: `/var/log/auth.log` on Debian/Ubuntu, `/var/log/secure` on
   RHEL/Fedora)
3. Built-in fallback fixture

**Auto-detect (recommended)** — SentinelX already knows about the two common
auth-log locations, so the simplest invocation is:

```bash
sudo ./manage.sh run
```

`sudo` is required because system auth logs are only readable by root (or the
`adm` / `wheel` group). SentinelX drops privileges to `nobody:nogroup`
(configurable in `config.yaml`) *after* opening the file, so the one-shot
`sudo` is enough.

**Explicit path** — if the auto-detect picks the wrong file, or you want to
read an archived / off-host log, set `SENTINELX_LOG_PATH` directly:

```bash
# Fedora / RHEL
sudo SENTINELX_LOG_PATH=/var/log/secure ./manage.sh run

# Debian / Ubuntu
sudo SENTINELX_LOG_PATH=/var/log/auth.log ./manage.sh run

# Archived or copied log
SENTINELX_LOG_PATH=/var/log/auth.log.1 ./manage.sh run
SENTINELX_LOG_PATH=/home/id43/logs/from-prod-server.log ./manage.sh run
```

**What lines are recognised** — the parser only matches OpenSSH syslog
patterns, so the file must contain lines like:

```text
Jul 11 21:30:15 host sshd[2201]: Failed password for root from 1.2.3.4 port 22 ssh2
Jul 11 21:30:15 host sshd[2201]: Invalid user admin from 1.2.3.4 port 22
Jul 11 21:30:15 host sshd[2201]: Accepted password for user1 from 1.2.3.4 port 22 ssh2
```

Lines in other formats (e.g. journald JSON export, `journalctl` output) are
read but silently skipped. If your environment logs SSH in a non-syslog
format, you'll need to extend `core/parser.py` with a matching regex.

**Important caveats**

- **Real-time only.** `core/watcher.py` opens the file and starts tailing
  from the end. Historical lines that existed before launch are *not*
  replayed — only new events written after SentinelX starts are processed.
- **Never run `mock-logs` against a real auth log.** `generate_mock_logs.py`
  truncates its target file on startup (line 23–24), so pointing it at
  `/var/log/auth.log` would wipe it. Only use `mock-logs` against a fixture
  or throwaway file.
- **Rotation is handled.** When logrotate moves the file out from under the
  watcher, the inode check in `core/watcher.py` re-opens the new file
  automatically.
- **Non-root reads work too.** If the file is world-readable (or owned by a
  group your user belongs to), you can run `./manage.sh run` without
  `sudo` — the privilege drop in `run.py` is only triggered when started as
  root.

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
| [Installation Guide](docs/installation.md) | Prerequisites, venv setup, permissions, systemd unit |
| [Configuration Guide](docs/configuration.md) | `config.yaml` schema, environment variables, merge order |
| [Usage Guide](docs/usage.md) | Running the daemon, the mock-logs flow, reading the dashboard |
| [Architecture Guide](docs/architecture.md) | Component layout, data flow, threading model |
| [Troubleshooting Guide](docs/troubleshooting.md) | Common runtime errors and their fixes |
| [QA-Tests](docs/QA) | Test reports and QA findings |
| [Archive_Journal](docs/archive_journal) | Development journal entries |

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
