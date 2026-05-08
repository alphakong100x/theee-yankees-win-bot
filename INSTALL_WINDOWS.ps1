$ErrorActionPreference = "Stop"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m tests.test_theee_title
.\.venv\Scripts\python.exe -m tests.test_mlb_yankees
.\.venv\Scripts\python.exe -m yankees_theee_bot --dry-run
