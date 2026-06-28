# Day 8 — Parser Verification & Foundation Hardening

## What I Did

* Performed a technical review of the current SentinelX architecture

  * watcher.py
  * parser.py
  * alerts.py
  * run.py

* Validated the current project structure and separation of concerns

  * Log collection layer
  * Parsing layer
  * Alerting layer

* Reviewed actual authentication logs from Fedora

```bash
sudo tail -n 20 /var/log/secure
```

* Compared real Fedora log entries against existing parser regex patterns

## Findings

### Parser Not Yet Verified

Discovered that the parser was built around an ISO timestamp format:

```bash
2025-06-20T14:30:15
```

However, real Fedora authentication logs use:

```bash
Jun 20 16:43:43 fedora sudo[11178]:
```

This means the current parser patterns do not accurately represent the actual log format being monitored.

### Hardcoded Log Path

Identified that SentinelX currently uses:

```python
LOG_FILE = "/var/log/auth.log"
```

This path is valid on:

* Ubuntu
* Debian

But Fedora uses:

```bash
/var/log/secure
```

This highlighted the need for:

* Operating system detection
* Configurable log paths
* Startup validation

### Watcher Limitations

Reviewed the current tail-style log watcher implementation.

Identified a future issue:

* Log rotation is not handled

Example:

```bash
/var/log/secure
```

may become:

```bash
/var/log/secure.1
```

after rotation.

The current file descriptor would continue monitoring the old file and miss new events.

### Alert Engine Review

Verified that:

* Failed attempts are tracked per IP
* Severity escalation works as designed

Current thresholds:

```text
INFO      -> 1 failure
WARNING   -> 3 failures
CRITICAL  -> 5 failures
```

Identified a future improvement:

* Failure counters never expire
* Old attack history remains indefinitely

A future version should implement time-based windows.

## What I Learned

* Writing code is not the same as verifying code
* Real-world log formats often differ from assumptions
* Security tools must fail loudly rather than silently
* Hardcoded system paths reduce portability
* Log rotation is an important operational concern
* Validation is required before adding new features

## Engineering Lessons

A major lesson from today:

> A feature is not complete because it compiles.
> A feature is complete when it has been tested against real-world data.

The parser appeared correct when viewed in isolation, but comparison with actual Fedora logs revealed incompatibilities that would prevent reliable event detection.

This reinforced the importance of:

* Verification
* Testing
* Assumption checking

during security software development.

## Next Steps

### Foundation Hardening

Planned tasks:

1. Create config.yaml
2. Implement operating system detection
3. Support Fedora and Debian-based log locations
4. Validate log file accessibility during startup
5. Create parser test cases using real log samples
6. Generate requirements.txt from a clean virtual environment
7. Improve project documentation

### Future Roadmap

After parser verification:

* Step 3 — Flask backend
* Step 4 — WebSocket live updates
* Step 5 — Dashboard UI
* Step 6 — Remote access

## Project Direction Update

SentinelX is evolving from:

```text
SSH Log Reader
```

into:

```text
Real-Time Linux Authentication Monitoring Platform
```

with emphasis on:

* Visibility
* Detection
* Reliability
* Extensibility

The current priority is strengthening the foundation before introducing web-based components.
