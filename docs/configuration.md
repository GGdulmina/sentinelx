# SentinelX Configuration Guide

SentinelX is highly customizable through a configuration file (`config.yaml`) and environment variables.

---

## 1. YAML Configuration (`config.yaml`)

A sample configuration file is provided in [config.yaml.example](file:///home/id43/Desktop/GD43/sentinelx/config.yaml.example).

### Configuration Options

| Option Name | Type | Default | Description |
|---|---|---|---|
| `log_paths` | List of strings | `['/var/log/auth.log', '/var/log/secure']` | The list of log files to tail concurrently. |
| `thresholds` | Dictionary | `{info: 1, warning: 3, critical: 5}` | Failed login attempts needed to trigger each severity level. |
| `reset_after` | Integer | `86400` (24 hours) | Inactivity window (in seconds) after which an IP's failure count is reset. |
| `alert_cooldown`| Integer | `300` (5 minutes) | Minimum time (in seconds) between alerts for a specific IP to suppress spam. |
| `state_file` | String | `"sentinelx_state.json"` | Path to the JSON file where state is persisted. Set to `null` to disable persistence. |
| `run_as_user` | String | `"nobody"` | Unprivileged user to drop privileges to if started as root. |
| `run_as_group` | String | `"nogroup"` | Unprivileged group to drop privileges to if started as root. |
| `output_format` | Dictionary | See below | Formatting options for CLI alerts. |

### Output Formatting Settings

The `output_format` object allows customization of the alert display:

```yaml
output_format:
  # The symbol displayed for each alert level
  icons:
    info: "[  INFO  ]"
    warning: "[WARNING ]"
    critical: "[CRITICAL]"
  # Column width for aligned display
  column_widths:
    ip: 16
    username: 12
  # Python strftime format string (e.g., "%Y-%m-%d %H:%M:%S")
  # If left empty, SentinelX uses the original log timestamp.
  date_format: ""
```

---

## 2. Environment Variables

All configuration values can be overridden at startup using environment variables. This is particularly useful in containerized or automated CI environments.

| Environment Variable | Description | Example |
|---|---|---|
| `SENTINELX_LOG_PATHS` | Comma-separated list of log file paths | `/var/log/auth.log,/tmp/custom.log` |
| `SENTINELX_THRESHOLDS_INFO` | Info alert threshold | `2` |
| `SENTINELX_THRESHOLDS_WARNING`| Warning alert threshold | `5` |
| `SENTINELX_THRESHOLDS_CRITICAL`| Critical alert threshold | `10` |
| `SENTINELX_RESET_AFTER` | Reset failure window (seconds) | `3600` |
| `SENTINELX_ALERT_COOLDOWN` | Alert cooldown period (seconds) | `60` |
| `SENTINELX_STATE_FILE` | Path to persistence file | `/var/lib/sentinelx/state.json` |
| `SENTINELX_RUN_AS_USER` | Dropped privileges target user | `sentinelx` |
| `SENTINELX_RUN_AS_GROUP` | Dropped privileges target group | `sentinelx` |

### Environment Variable Priority

SentinelX merges configurations in the following order (highest priority overrides lowest):

1. Command line argument overrides (e.g., `python run.py mock_auth.log` overrides `log_paths`).
2. Environment variables.
3. User `config.yaml` file.
4. Internal default configuration schema.
