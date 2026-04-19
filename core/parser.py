import re
from datetime import datetime


# These are the patterns we care about — one per event type
# Each is a tuple of (event_name, compiled_regex_pattern)

PATTERNS = [
    (
        "failed_password",
        re.compile(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*"
            r"Failed password for (?:invalid user )?(\w+) "
            r"from (\d+\.\d+\.\d+\.\d+) port (\d+)"
        )
    ),
    (
        "invalid_user",
        re.compile(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*"
            r"Invalid user (\w+) "
            r"from (\d+\.\d+\.\d+\.\d+) port (\d+)"
        )
    ),
    (
        "accepted_password",
        re.compile(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*"
            r"Accepted password for (\w+) "
            r"from (\d+\.\d+\.\d+\.\d+) port (\d+)"
        )
    ),
]


def parse_line(line: str) -> dict | None:
    """
    Takes a raw log line and returns a structured dict.
    Returns None if the line doesn't match any known pattern.
    """
    for event_type, pattern in PATTERNS:
        match = pattern.search(line)

        if match:
            return {
                "event":     event_type,
                "timestamp": match.group(1),
                "username":  match.group(2),
                "ip":        match.group(3),
                "port":      match.group(4),
                "raw":       line
            }

    return None  # line didn't match anything we care about