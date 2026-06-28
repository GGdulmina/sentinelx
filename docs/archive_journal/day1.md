# Day 1 — Project Setup & SSH Testing

## What I Did
- Set up Linux Mint
- Explored /var/log/auth.log
- Creating the virtual enviromentt
```bash
python3 -m venv venv
```
- Activated the enviroment
```bash
source venv/bin/activate
```
- Installed the first packeages
```bash
pip install flask && pip install bcrypt
```
```bash
pip list #check installed packeges
```
- Created Python script to read logs
```bash
touch app.py
```
```bash
code app.py #opens the file in Vs code
```

## Challenges
- The virtual enviroment wasn't created succesgully.
```bash
sudo apt install python3.12 -venv
```
- Internet connection timeout a common package installing problem
```bash
pip install flask bcrypt -default-timeout=100
```
```bash
upgrade pip python -m pip install --upgrade pip
```

## What I Learned
- How Linux logs work

## Next Step
- Improve detection logic
- Add real-time monitoring
