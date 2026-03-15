#!/bin/bash
# Escape Room Tracker — Cron-Wrapper
# Wöchentlich Sonntags 06:03 UTC
cd /home/claude-agent/escape-room-tracker || exit 1
# Load env vars from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi
python3 scraper.py >> /home/claude-agent/escape-room-tracker/scraper.log 2>&1
