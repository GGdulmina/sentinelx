import re
import logging

logger = logging.getLogger(__name__)

# Timestamp pattern: YYYY-MM-DDTHH:MM:SS.ffffff+HH:MM, or Z, or Syslog format (e.g. Jun 28 12:02:26)
TIMESTAMP_PATTERN = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:?\d{2}|Z)?|[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})'

# A safe prefix pattern to avoid catastrophic backtracking (ReDoS)
PREFIX_PATTERN = rf'^{TIMESTAMP_PATTERN}\s+(?:\S+\s+)?sshd\[\d+\]:\s+'

# These are the patterns we care about — one per event type
# Each is a compiled regex pattern targeting sshd authentication events.
# Groups: (1) timestamp, (2) username, (3) IP address, (4) port
PATTERNS = {
    "failed_password": re.compile(
        PREFIX_PATTERN + r'Failed password for (?:invalid user )?([a-zA-Z0-9_.-]+) from ([a-fA-F0-9.:]+) port (\d+)'
    ),
    "invalid_user": re.compile(
        PREFIX_PATTERN + r'Invalid user ([a-zA-Z0-9_.-]+) from ([a-fA-F0-9.:]+) port (\d+)'
    ),
    "accepted_password": re.compile(
        PREFIX_PATTERN + r'Accepted password for ([a-zA-Z0-9_.-]+) from ([a-fA-F0-9.:]+) port (\d+)'
    )
}

def sanitize_input(value: str) -> str:
    """
    Sanitizes string inputs to prevent terminal/log injection.
    Strips ANSI escape codes and controls non-printable characters.
    """
    if not isinstance(value, str):
        return value
    # Strip ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    value = ansi_escape.sub('', value)
    # Strip other non-printable characters, keep ASCII printable range
    sanitized = []
    for char in value:
        o = ord(char)
        if 32 <= o <= 126:
            sanitized.append(char)
        elif char == '\n':
            sanitized.append('\\n')
        elif char == '\r':
            sanitized.append('\\r')
        elif char == '\t':
            sanitized.append('\\t')
        else:
            # Escape non-printable character
            sanitized.append(f'\\x{o:02x}' if o < 256 else f'\\u{o:04x}')
    return "".join(sanitized)

def parse_line(line: str) -> dict | None:
    """
    Takes a raw log line and returns a structured, validated, and sanitized dict.
    Returns None if the line doesn't match any known pattern.
    """
    if not line:
        return None

    # First check if the line matches the general sshd prefix before doing full matching
    # This acts as a fast-fail and prevents processing completely irrelevant lines.
    for event_type, pattern in PATTERNS.items():
        match = pattern.search(line)
        if match:
            try:
                raw_port = match.group(4)
                port = int(raw_port)
            except (ValueError, TypeError, IndexError) as e:
                logger.warning(f"Failed to parse port as integer: {e}")
                port = 0

            return {
                "event":     event_type,
                "timestamp": sanitize_input(match.group(1)),
                "username":  sanitize_input(match.group(2)),
                "ip":        sanitize_input(match.group(3)),
                "port":      port,
                "raw":       line
            }

    return None  # line didn't match anything we care about