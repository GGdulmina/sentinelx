# Day 2 — Project Setup & SSH Testing

## What I Did
- Started basic python coding
```bash
log_file = "/var/log/auth.log"
```
- reading log files
```bash
with open(log_file, "r") as file:
        lines = file.readlines()[-10:]
```
- Wxecuting the app.py
```bash
python app.py
```
- Installed ssh & setup
```bash
sudo apt install openssh-server
sudo systemctl start ssh #started SSH service (if not running)
sudo systemctl enable ssh #enabled SSH to start on boot:
sudo systemctl status ssh 
```
- Installed linux based terminal on my android
```bash
https://play.google.com/store/apps/details?id=com.termux&pcampaignid=web_share
```

## Challenges
- when executing the app.py there was a terminal error
```bash
sudo python3 app.py #super user do with python version
python3 app.py #terminal required python version berfore executing
```
- Explored similar monitoring tools like 
	- Fail2Ban
	- wazuh
	- OSSEC

## What I Learned
- Secure Shell(SSH) basics

## Next Step
- How to work with SSH
