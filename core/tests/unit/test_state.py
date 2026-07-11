"""Unit tests targeting edge case serialization actions for the state engine."""

from core.alerts import load_state


def test_ut_state_001_invalid_file_fallback() -> None:
    """Ensure load_state cleanly defaults to empty structures when file is missing."""
    fail_info, last_alert, last_severity = load_state("non_existent_file_path.json")
    assert fail_info == {}
    assert last_alert == {}
    assert last_severity == {}