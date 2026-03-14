#!/usr/bin/env python3
"""Escape Room Tracker Berlin — Notion Sync.

Synchronisiert alle bekannten Berliner Escape Rooms nach Notion.
Nutzt die kuratierte Raumliste aus rooms_data.py.
"""

import logging
import sys

import config
import notion_sync
from rooms_data import KNOWN_ROOMS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """Hauptfunktion: Rooms nach Notion synchronisieren."""
    db_id = config.DATABASE_ID
    if not db_id:
        logger.error("DATABASE_ID nicht gesetzt in config.py!")
        sys.exit(1)

    logger.info("=== Escape Room Tracker Berlin ===")
    logger.info(f"{len(KNOWN_ROOMS)} Räume in der Datenbasis")

    # Sync nach Notion
    logger.info("Starte Notion-Sync...")
    notion_sync.sync_all(db_id, KNOWN_ROOMS)
    logger.info("=== Fertig! ===")


if __name__ == "__main__":
    main()
