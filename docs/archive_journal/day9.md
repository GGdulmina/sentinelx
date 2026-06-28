# Day 9 — Core Engineering Overhaul & State Architecture Hardening

## What I Did

* Refactored core/alerts.py to Production Standards:
 -  Rebuilt the AlertEngine from scratch to resolve four critical architectural flaws discovered during the code audit. [QA Review Document](../QA/qa_review.md)
* Engineered Severity-Aware Escalation: Implemented integer-mapped severity matrices to allow high-severity alerts to instantly bypass the global cooldown gate during rapid brute-force attacks.
* Resolved Disk Write-Amplification: Built an in-memory debouncing and buffering system that groups state flushes to disk every 5 seconds, rather than executing synchronous I/O blocks on every raw log line.
* Eliminated the State Memory Leak: Programmed a deterministic, time-to-live (TTL) memory pruning routine that automatically purges inactive IP historical vectors from system RAM.
* Implemented Atomic File Persistence: Replaced risky standard file writes with an atomic execution swap (os.replace) using isolated temporary files to completely eliminate state-file corruption risks during power drops or OS-level process panics.

## Findings

1. The Cooldown Masking Vulnerability (Fixed)

- Previously, if an attacker initiated a rapid automated dictionary attack, the first attempt generated an INFO alert. This action erroneously locked a global 5-minute cooldown timer for that IP. Any subsequent escalations to WARNING (3 failures) or CRITICAL (5 failures) that occurred within that 5-minute window were completely silenced by the software.

	The Fix: The engine now tracks max_severity dynamically via integer hierarchies (INFO=1, WARNING=2, CRITICAL=3). If a new incoming event evaluates mathematically higher than the historical baseline ($current > max$), the system classifies it as an escalation bypass, punches through the time gate, and alerts the security center instantly.

2. File I/O Bottlenecks (Fixed)

- Writing states to disk on every single log entry creates massive disk I/O latency, stalling the single-threaded daemon loop during high-volume distributed brute-force events.

    The Fix: Introduced a save_interval threshold (default 5.0s). State schemas are updated in RAM instantaneously but only flushed to disk periodically, unless an emergency CRITICAL alert explicitly forces an immediate synchronous cache dump.

3. State Schema Volatility & Inode Mechanics (Identified)

- Analyzing the state persistence design highlighted an operational loop hazard: if the daemon restarts while the log watcher is mid-stream, it forgets its offset position inside /var/log/secure. Upon boot, it would either re-read the entire log file from byte 0 (generating thousands of duplicate alerts) or skip directly to EOF (causing blind spots).

## Technical Implementation Blueprint

* Here is the finalized structural layout of the hardened state tracking and mitigation layer:
```bash
# Core State Schema Layout
payload = {
    "fail_info": {
        "192.168.1.100": {"fail_count": 5, "last_seen": 1719614158.0}
    },
    "ip_state": {
        "192.168.1.100": {"last_time": 1719614158.0, "max_severity": 3}
    }
}
```

## What I Learned

* Asynchronous Alignment Errors: Bypassing software design flaws by artificially modifying test assertions (e.g., overriding tracking parameters back to 0.0 inside tests) creates a false sense of security. Code logic must be structurally fixed, not masked by tests.

* The Ordering Rule of Linux Privileges: Dropping privileges to an unprivileged user like nobody must happen after setting up initial system assets. Furthermore, dropping permissions completely breaks the log rotation cycle if the software attempts to call a raw open() on root-restricted logs like /var/log/secure as a low-privilege user.

* Atomic Transactions are Mandatory: Overwriting a single state configuration file directly (open("state.json", "w")) truncates the file size to 0 bytes before writing data. If the underlying server loses power precisely during that microsecond block, your historical data is corrupted and lost. Using os.replace() provides kernel-level atomic safety.


