#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m tests.test_theee_title
python -m tests.test_mlb_yankees
python -m yankees_theee_bot --dry-run
