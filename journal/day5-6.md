# Day 5/6 — Real time log monitoring / Architecture Design & Project restructure

## What I Did

- Restructured the SentinelX project into a modular format:

```bash
sentinelx/
├── core/
│   ├── __init__.py
│   ├── watcher.py
│   ├── parser.py
│   └── alerts.py
├── .gitignore
├── requirements.txt
└── run.py
```

- Created core modules for better separation of logic:
	- watcher.py → will handle real-time log monitoring
	- parser.py → will extract useful data (e.g., IP addresses)
	- alerts.py → will handle detection and warnings
- Planned project flow using a flowchart
![Flowchart](journal/docs/day5-6_flowchat.png)

# Architecture Understanding
- Separated responsibilities into different modules
- Prepared system for real-time monitoring
- Designed scalable structure for future improvements

## Challenges
- Understanding how to split one script (app.py) into multiple modules
- Deciding responsibilities for each file
- Leaned to implement the real-time logmintoring into coding

## What I Learned
- pyton functions
- file handling:
	- f.readline()
	- f.read()
	- f.seek()
```bash
[Line1\n][Line2\n][Line3\n]
            ^
          cursor # how f.seek() works
```

- Real-time behavior comes from:
	- while True: → keeps checking forever
	- f.readline() → reads new data as it appears
	- yield → outputs each new line immediately
	- time.sleep(0.1) → prevents CPU overload while waiting

- Importance of modular programming
- How real-world Python projects are structured
- Difference between script-based and structured applications

## Importance to Project
- Makes SentinelX easier to maintain and expand
- Improves readability and organization
- Prepares project for advanced features like real-time detection
