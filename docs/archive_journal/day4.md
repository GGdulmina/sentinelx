# Day 4 — Git & GitHub Integration for SentinelX

## What I Did

- Initialized a Git repository for my project:

```bash
git init
```
- Checked repository status

```bash
git status
```

- Added project files to staging

```bash
git add .
```

- Created first commit
```bash
git commit -m "Initial commit"
```

- Created a repository on GitHub and connected it

```bash
git remote add origin https://github.com/GGdulmina/sentinelx.git
```
- Renamed branch to main

```bash
git branch -M main
```

- Pushed project to GitHub

```bash
git push -u origin main
```
## Challenges
- Git required username and email configuration
- git config --global user.name "Your Name"
- git config --global user.email "your@email.com"

# Faced authentication errors (password not supported)
→ Learned to use Personal Access Tokens instead

# Push rejected due to remote changes
→ Fixed using:
```bash
git pull origin main --allow-unrelated-histories --no-rebase
```

# Mistakenly committed venv/ folder
→ Fixed by using .gitignore and removing it from tracking

## What I Learned
- Git is used to track changes in code locally
- GitHub stores the project online for sharing and backup
- Difference between git add, git commit, and git push
- Importance of .gitignore to avoid unnecessary files

##Importance to Project
- Keeps track of project progress
- Helps manage changes safely
- Allows me to document and share my work professionally
