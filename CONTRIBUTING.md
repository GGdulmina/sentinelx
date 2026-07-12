# Contributing to SentinelX

Thanks for your interest in contributing. This guide covers the
contribution workflow, coding standards, and the test layout used in
this repository.

---

## 1. Development environment

```bash
git clone https://github.com/GGdulmina/sentinelx.git
cd sentinelx
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`manage.sh` already wraps `venv/bin/python` and `venv/bin/pytest`, so
you do not need to keep the venv activated for the commands below.

---

## 2. Contribution workflow

1. **Fork** the repository.
2. **Create a feature branch** with a descriptive name:

   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Write code + tests** — see [§3 Coding standards](#3-coding-standards)
   and [§4 Test layout](#4-test-layout) below.
4. **Verify locally** before pushing:

   ```bash
   ./manage.sh lint    # syntax check across run.py, config.py, core/*.py
   ./manage.sh test    # full pytest suite — must be 16/16 green
   ```

5. **Open a pull request** against `main`. Describe the problem, the
   solution, and how you validated it. Reference any related issue.

---

## 3. Coding standards

- **PEP 8.** Standard Python style. Four-space indent, snake_case,
  type hints on public function signatures.
- **Type hints.** Function signatures in `core/` and `run.py` should
  include parameter and return type annotations. Tests should too.
- **ReDoS safety.** Never use unbounded `.*` in a regex. All patterns
  in `core/parser.py` are anchored at line start and avoid greedy
  repetition. New patterns must be ReDoS-safe by construction.
- **Input sanitisation.** Every string field extracted from a log line
  must be passed through `core.parser.sanitize_input` before reaching
  the alert engine, the WebSocket payload, or the API response.
- **Use the `logging` module.** No `print()` statements in `core/`. The
  exception is `generate_mock_logs.py`, which is a developer tool, not
  production code.
- **Atomic state writes.** Any code that mutates `sentinelx_state.json`
  must use the `temp_file` + `os.replace` pattern in
  `core/alerts.py:save_state` so abrupt termination cannot corrupt
  the file.
- **Configuration through `config.py`.** New tunables belong in
  `DEFAULT_CONFIG` and `config.yaml.example`, and should be overridable
  by an environment variable. Add validation in `validate_config` if
  the value has structural constraints.

---

## 4. Test layout

Tests live under `core/tests/` and are organised by scope:

```text
core/tests/
├── unit/                 # Pure logic, no I/O
│   ├── test_parser.py    # regex extraction, sanitisation, ReDoS guard
│   ├── test_alerts.py    # severity escalation, per-IP counting
│   ├── test_queue.py     # queue bound enforcement
│   ├── test_state.py     # load_state fallback behaviour
│   └── test_watcher.py   # follow() idle-loop entry
├── integration/          # Multi-module behaviour + child processes
│   ├── test_pipeline.py
│   ├── test_restart.py   # state survives engine restart
│   ├── test_rotation.py  # log rotation / truncation
│   └── test_shutdown.py  # SIGINT clean exit
└── stress/               # High-volume / memory stability
    ├── memory_test.py
    ├── test_stress_parser.py
    └── test_stress_pipeline.py
```

Conventions:

- Test file names start with `test_` so pytest auto-discovers them.
- Test function names start with `test_` and use snake_case.
- Group tests by module: `test_ut_<module>_NNN_description` for unit
  tests, `test_it_<scenario>_NNN_description` for integration tests,
  `test_str_<scenario>_NNN_description` for stress tests.
- The `stress/` directory previously had a misnamed file
  (`stress_pipeline.py`) that pytest ignored; the convention going
  forward is to **always** prefix with `test_`.
- The shutdown integration test uses `sys.executable` to spawn the
  child process so the active virtualenv is honoured; keep that
  pattern in any new subprocess-based tests.

### Running the suite

```bash
./manage.sh test                   # full suite
./manage.sh test -k watcher -v     # filter by substring
./manage.sh test core/tests/unit/  # one directory
```

The expected output is `16 passed`. Do not submit a PR with a failing
or skipped test.

---

## 5. Adding a new regex event type

If you want SentinelX to recognise a new kind of `sshd` line:

1. Add the compiled pattern to `core/parser.PATTERNS` (keep it anchored
   and ReDoS-safe).
2. Update `core/parser.parse_line` to populate the returned dict.
3. If the event should be counted toward brute-force detection, add a
   branch in `core/alerts.AlertEngine.process_event`.
4. Cover the new pattern with a unit test in
   `core/tests/unit/test_parser.py` and, if you added alert logic, a
   unit test in `test_alerts.py`.
5. Add a ReDoS guard test that feeds a 5 000+ byte crafted string and
   asserts completion under 100 ms (the existing
   `test_sec_redos_001_backtracking_protection` is the template).

---

## 6. Pull request checklist

- [ ] `./manage.sh lint` passes
- [ ] `./manage.sh test` shows 16+ passed
- [ ] New behaviour has tests
- [ ] `config.py` defaults and `config.yaml.example` are updated for
      any new tunable
- [ ] Documentation under `docs/` and `README.md` is updated for any
      user-visible change
- [ ] Commit messages are clear and reference any related issue

---

## 7. Reporting issues

Open a GitHub issue with:

- SentinelX version (commit hash)
- OS and Python version
- The exact `manage.sh` command and the full output
- A minimal log snippet if the issue is in parsing or alerting

Bug reports without repro steps are hard to act on; spend a few minutes
narrowing it down to the smallest failing case.
