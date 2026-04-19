# SentinelX 🔐 (Light-weight Security Information and Event Management tool)

![Project Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![Language](https://img.shields.io/badge/Language-Python-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-orange)

SentinelX is a lightweight security monitoring tool designed to analyze Linux authentication logs and detect suspicious login activity in real time.

The goal of this project is to explore how system-level data can be used to identify potential threats such as brute-force attacks and unauthorized access attempts.

---

## Concept

Modern systems generate large amounts of log data, but interpreting that data in real time is difficult without proper tools.

SentinelX aims to solve this by:

- Monitoring authentication logs (`/var/log/auth.log`)
- Detecting failed login attempts
- Identifying repeated access patterns from the same IP
- Providing simple alerts for suspicious behavior

---

## Current Capabilities

- Reads Linux authentication logs
- Detects failed SSH login attempts
- Tracks repeated failures per IP
- Generates basic alerts for potential brute-force activity

---

## How to Run

```bash
sudo python3 app.py
