"""Configuration for Escape Room Tracker."""

import os

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_VERSION = "2022-06-28"

# Will be set after DB creation
DATABASE_ID = "323bea2a-e889-8112-9229-cb5c15953989"

# Scraping
REQUEST_DELAY = 2.0  # Seconds between requests to same provider
USER_AGENT = "EscapeRoomTracker/1.0"
