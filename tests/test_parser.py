import pytest
from core.parser import parse_line, sanitize_input

def test_sanitize_input():
    # Regular inputs remain unchanged
    assert sanitize_input("root") == "root"
    assert sanitize_input("192.168.1.1") == "192.168.1.1"
    
    # ANSI escape sequences stripped
    dirty_username = "\x1b[31mroot\x1b[0m"
    assert sanitize_input(dirty_username) == "root"
    
    # Control/non-printable characters escaped
    dirty_with_newline = "user\nname"
    assert sanitize_input(dirty_with_newline) == "user\\nname"
    
    dirty_control = "user\x00name"
    assert sanitize_input(dirty_control) == "user\\x00name"

def test_parse_failed_password_iso():
    line = "2026-06-28T12:02:29.884783-05:00 localhost sshd[2201]: Failed password for admin from 198.51.100.12 port 61620 ssh2"
    result = parse_line(line)
    assert result is not None
    assert result["event"] == "failed_password"
    assert result["timestamp"] == "2026-06-28T12:02:29.884783-05:00"
    assert result["username"] == "admin"
    assert result["ip"] == "198.51.100.12"
    assert result["port"] == 61620
    assert result["raw"] == line

def test_parse_failed_password_syslog():
    line = "Jun 28 12:02:29 localhost sshd[2201]: Failed password for admin from 198.51.100.12 port 61620 ssh2"
    result = parse_line(line)
    assert result is not None
    assert result["event"] == "failed_password"
    assert result["timestamp"] == "Jun 28 12:02:29"
    assert result["username"] == "admin"
    assert result["ip"] == "198.51.100.12"
    assert result["port"] == 61620

def test_parse_invalid_user():
    line = "2026-06-28T12:02:26.553975-05:00 localhost sshd[2201]: Invalid user user1 from 10.0.0.42 port 39503"
    result = parse_line(line)
    assert result is not None
    assert result["event"] == "invalid_user"
    assert result["timestamp"] == "2026-06-28T12:02:26.553975-05:00"
    assert result["username"] == "user1"
    assert result["ip"] == "10.0.0.42"
    assert result["port"] == 39503

def test_parse_accepted_password():
    line = "2026-06-28T12:02:28.338452-05:00 localhost sshd[2201]: Accepted password for root from 185.190.140.5 port 60858 ssh2"
    result = parse_line(line)
    assert result is not None
    assert result["event"] == "accepted_password"
    assert result["timestamp"] == "2026-06-28T12:02:28.338452-05:00"
    assert result["username"] == "root"
    assert result["ip"] == "185.190.140.5"
    assert result["port"] == 60858

def test_parse_non_sshd_log():
    line = "2026-06-28T12:02:28.338452-05:00 localhost systemd[1]: Started User Manager for UID 1000."
    assert parse_line(line) is None

def test_parse_malformed_sshd():
    # SSHD log but unexpected format
    line = "2026-06-28T12:02:28.338452-05:00 localhost sshd[2201]: Connection closed by authenticating user root 185.190.140.5 port 60858 [preauth]"
    assert parse_line(line) is None

def test_parse_empty_and_none():
    assert parse_line("") is None
    assert parse_line(None) is None

def test_username_with_special_characters():
    # Usernames can have dots, dashes, numbers, etc.
    line = "2026-06-28T12:02:29-05:00 localhost sshd[2201]: Failed password for user.name-123 from 10.0.0.1 port 22 ssh2"
    result = parse_line(line)
    assert result is not None
    assert result["username"] == "user.name-123"
    assert result["ip"] == "10.0.0.1"
    assert result["port"] == 22
