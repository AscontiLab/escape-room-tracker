"""Notion API integration for Escape Room Tracker."""

import httpx
import logging
import config

logger = logging.getLogger(__name__)

HEADERS = {
    "Authorization": f"Bearer {config.NOTION_TOKEN}",
    "Notion-Version": config.NOTION_VERSION,
    "Content-Type": "application/json",
}

NOTION_API = "https://api.notion.com/v1"

# Select options for properties
ANBIETER_OPTIONS = [
    "EXITROOM", "EXIT Game", "Escape Berlin", "TeamEscape",
    "House of Tales", "THE ROOM", "Final Escape", "Smart Room",
    "Labyrintoom", "MIRACULUM", "Illuminati Escape", "Black Room",
    "Make a Break", "Cat in the Bag", "your time2escape", "Sonstige",
]

BEZIRK_OPTIONS = [
    "Mitte", "Friedrichshain", "Kreuzberg", "Prenzlauer Berg",
    "Charlottenburg", "Lichtenberg", "Neukölln", "Tempelhof",
    "Wedding", "Schöneberg", "Steglitz", "Treptow", "Köpenick",
    "Reinickendorf", "Spandau", "Pankow",
]

THEMA_OPTIONS = [
    "Horror", "Krimi", "Abenteuer", "Sci-Fi", "Historie",
    "Fantasy", "Thriller", "Comedy", "Mystery", "Action",
    "Sonstige",
]

SCHWIERIGKEIT_OPTIONS = ["Leicht", "Mittel", "Schwer"]

BEWERTUNG_OPTIONS = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]


def create_database(parent_page_id: str) -> str:
    """Create the Escape Rooms Berlin database in Notion."""
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Escape Rooms Berlin"}}],
        "icon": {"type": "emoji", "emoji": "🔐"},
        "properties": {
            "Name": {"title": {}},
            "Anbieter": {
                "select": {
                    "options": [{"name": n} for n in ANBIETER_OPTIONS]
                }
            },
            "Bezirk": {
                "select": {
                    "options": [{"name": n} for n in BEZIRK_OPTIONS]
                }
            },
            "Thema": {
                "select": {
                    "options": [{"name": n} for n in THEMA_OPTIONS]
                }
            },
            "Spieler": {"rich_text": {}},
            "Dauer (Min)": {"number": {"format": "number"}},
            "Schwierigkeit": {
                "select": {
                    "options": [{"name": n} for n in SCHWIERIGKEIT_OPTIONS]
                }
            },
            "Preis ab (€)": {"number": {"format": "euro"}},
            "Gespielt ✓": {"checkbox": {}},
            "Gespielt am": {"date": {}},
            "Meine Bewertung": {
                "select": {
                    "options": [{"name": n} for n in BEWERTUNG_OPTIONS]
                }
            },
            "Notizen": {"rich_text": {}},
            "Booking-Link": {"url": {}},
            "Website": {"url": {}},
            "Adresse": {"rich_text": {}},
            "Aktiv": {"checkbox": {}},
        },
    }

    with httpx.Client(headers=HEADERS, timeout=30) as client:
        resp = client.post(f"{NOTION_API}/databases", json=payload)
        resp.raise_for_status()
        db_id = resp.json()["id"]
        logger.info(f"Database created: {db_id}")
        return db_id


def query_existing_rooms(db_id: str) -> dict[str, dict]:
    """Query all existing rooms. Returns dict keyed by 'provider|name' (normalized)."""
    rooms = {}
    start_cursor = None

    with httpx.Client(headers=HEADERS, timeout=30) as client:
        while True:
            payload = {"page_size": 100}
            if start_cursor:
                payload["start_cursor"] = start_cursor

            resp = client.post(f"{NOTION_API}/databases/{db_id}/query", json=payload)
            resp.raise_for_status()
            data = resp.json()

            for page in data["results"]:
                props = page["properties"]
                name = _get_title(props.get("Name", {}))
                provider = _get_select(props.get("Anbieter", {}))
                gespielt = _get_checkbox(props.get("Gespielt ✓", {}))
                key = _normalize_key(provider, name)
                rooms[key] = {
                    "page_id": page["id"],
                    "gespielt": gespielt,
                    "name": name,
                    "provider": provider,
                }

            if not data.get("has_more"):
                break
            start_cursor = data.get("next_cursor")

    logger.info(f"Found {len(rooms)} existing rooms in Notion")
    return rooms


def upsert_room(db_id: str, room: dict, existing: dict | None = None):
    """Create or update a room in Notion."""
    key = _normalize_key(room["provider"], room["name"])

    properties = _build_properties(room)

    with httpx.Client(headers=HEADERS, timeout=30) as client:
        if existing and key in existing:
            # Update existing page — NEVER overwrite Gespielt
            page_id = existing[key]["page_id"]
            # Remove Gespielt from update
            properties.pop("Gespielt ✓", None)
            properties.pop("Gespielt am", None)
            properties.pop("Meine Bewertung", None)
            properties.pop("Notizen", None)

            resp = client.patch(
                f"{NOTION_API}/pages/{page_id}",
                json={"properties": properties},
            )
            resp.raise_for_status()
            logger.info(f"Updated: {room['provider']} - {room['name']}")
        else:
            # Create new page
            resp = client.post(
                f"{NOTION_API}/pages",
                json={
                    "parent": {"database_id": db_id},
                    "properties": properties,
                },
            )
            resp.raise_for_status()
            logger.info(f"Created: {room['provider']} - {room['name']}")


def sync_all(db_id: str, scraped_rooms: list[dict]):
    """Sync all scraped rooms to Notion."""
    existing = query_existing_rooms(db_id)
    scraped_keys = set()

    for room in scraped_rooms:
        key = _normalize_key(room["provider"], room["name"])
        scraped_keys.add(key)
        upsert_room(db_id, room, existing)

    # Mark rooms that disappeared as inactive
    for key, entry in existing.items():
        if key not in scraped_keys:
            with httpx.Client(headers=HEADERS, timeout=30) as client:
                client.patch(
                    f"{NOTION_API}/pages/{entry['page_id']}",
                    json={"properties": {"Aktiv": {"checkbox": False}}},
                )
                logger.info(f"Deactivated: {entry['provider']} - {entry['name']}")

    logger.info(f"Sync complete: {len(scraped_rooms)} rooms processed")


def _build_properties(room: dict) -> dict:
    """Build Notion properties from room dict."""
    props = {
        "Name": {"title": [{"text": {"content": room["name"]}}]},
        "Aktiv": {"checkbox": room.get("active", True)},
        "Gespielt ✓": {"checkbox": False},
    }

    if room.get("provider"):
        props["Anbieter"] = {"select": {"name": room["provider"]}}
    if room.get("district"):
        props["Bezirk"] = {"select": {"name": room["district"]}}
    if room.get("theme"):
        props["Thema"] = {"select": {"name": room["theme"]}}
    if room.get("players"):
        props["Spieler"] = {"rich_text": [{"text": {"content": room["players"]}}]}
    if room.get("duration"):
        props["Dauer (Min)"] = {"number": room["duration"]}
    if room.get("difficulty"):
        props["Schwierigkeit"] = {"select": {"name": room["difficulty"]}}
    if room.get("price_from") is not None:
        props["Preis ab (€)"] = {"number": room["price_from"]}
    if room.get("booking_url"):
        props["Booking-Link"] = {"url": room["booking_url"]}
    if room.get("room_url"):
        props["Website"] = {"url": room["room_url"]}
    if room.get("address"):
        props["Adresse"] = {"rich_text": [{"text": {"content": room["address"]}}]}

    return props


def _normalize_key(provider: str, name: str) -> str:
    """Normalize provider+name for deduplication."""
    return f"{provider.lower().strip()}|{name.lower().strip()}"


def _get_title(prop: dict) -> str:
    title = prop.get("title", [])
    return title[0]["plain_text"] if title else ""


def _get_select(prop: dict) -> str:
    sel = prop.get("select")
    return sel["name"] if sel else ""


def _get_checkbox(prop: dict) -> bool:
    return prop.get("checkbox", False)
