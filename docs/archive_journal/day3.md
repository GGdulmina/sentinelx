# Day 3 — Termux, SSH Exploration & OverTheWire Bandit

## What I Did

- Installed and explored Termux on Android
- Learned basic Linux commands inside Termux
- Practiced SSH using OverTheWire Bandit wargame
```bash
https://overthewire.org/wargames/
```
- Established SSH connection from mobile to my PC

---

## SSH Practice (OverTheWire Bandit)

- Connected to Bandit server:

```bash
ssh bandit0@bandit.labs.overthewire.org -p 2220
```
- Learned how to navigate Linux systems remotely
- Solved basic levels using commands like

```bash
whoami
ls
cd
cat
pwd
file
du
find
```
## Connecting to My Own PC

- Used Termux to connect to my Linux machine
```bash
ssh id43@192.168.x.x
 # id43 is my pc
 # ip address 
```
- Successfully accessed my system remotely from mobile

## Challenges

- Understanding how SSH works across devices
- Initial confusion about IP addresses and ports
- Needed both devices on the same network

## What I Learned

- SSH can be used from any device (including mobile)
- Remote login attempts are logged in /var/log/auth.log
- Practicing with Bandit improves real Linux skills
- Termux can act like a full Linux terminal

## Importance to Project

- Helps simulate real-world login attempts
- Generates useful log data for SentinelX
- Strengthens understanding of attack patterns

## Next Step

- Generate failed login attempts
- Analyze logs for suspicious activity
- Improve detection logic in Python script
