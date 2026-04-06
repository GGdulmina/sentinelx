# SentinelX 🔐

![Project Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![Language](https://img.shields.io/badge/Language-Python-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-orange)

SentinelX is a Linux-based authentication log monitoring tool designed to help users understand failed login attempts and potential unauthorized access. It is part of a hands-on learning journey in cybersecurity and Python programming.

---

## Overview

SentinelX reads Linux authentication logs (e.g., `/var/log/auth.log`) and identifies failed login attempts, providing alerts for potential suspicious activity. The project is focused on **learning and documenting the process of building a small security monitoring tool** while practicing:

- Linux system fundamentals
- Python scripting and log parsing
- SSH setup and remote access
- Version control with Git and GitHub

---

## Learning Objectives

This project helps you learn:

- How Linux authentication and system logs work
- Basics of SSH and secure remote access
- Parsing logs with Python (`re` module, collections)
- Detecting patterns of failed logins (for awareness or simulation of brute-force attacks)
- Proper use of Git and GitHub for version control and documentation

---

## How to Run

> SentinelX is still in development. The current version reads logs locally.

```bash
sudo python3 app.py```

- You will see a report showing the last failed login attempts and a simple alert if suspicious activity is detected.

## Project Status

🚧 In Progress — continuously improving with modular architecture and real-time monitoring in future updates

## Documentation & Learning

- The project includes a journal documenting the step-by-step learning process: ``` /journal```
