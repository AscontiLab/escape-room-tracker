# Escape Room Tracker Berlin

Alle Berliner Escape Rooms in einer Notion-Datenbank — mit "Gespielt"-Checkbox, Booking-Links und wöchentlichem Sync.

## Übersicht

- **95 Räume** von **15 Anbietern**
- Notion-DB als UI: filtern, sortieren, Häkchen setzen
- Wöchentlicher Re-Sync (Sonntags 06:03 UTC) — `Gespielt`-Status wird nie überschrieben

## Anbieter

| Anbieter | Räume | Bezirk |
|----------|-------|--------|
| EXITROOM | 10 | Mitte |
| EXIT Game | 8 | Mitte |
| Escape Berlin | 12 | Lichtenberg |
| Black Room | 10 | Lichtenberg |
| Smart Room | 10 | Lichtenberg |
| TeamEscape | 6 | Mitte |
| Illuminati Escape | 7 | Charlottenburg |
| House of Tales | 6 | Mitte |
| Final Escape | 6 | Prenzlauer Berg |
| MIRACULUM | 4 | Kreuzberg |
| THE ROOM | 4 | Lichtenberg |
| Labyrintoom | 4 | Lichtenberg |
| Cat in the Bag | 3 | Mitte |
| Make a Break | 3 | Friedrichshain |
| your time2escape | 2 | Wedding |

## Notion-Properties

Name, Anbieter, Bezirk, Thema, Spieler, Dauer (Min), Schwierigkeit, Preis ab (€), Gespielt ✓, Gespielt am, Meine Bewertung, Notizen, Booking-Link, Website, Adresse, Aktiv

## Nutzung

```bash
# Manueller Sync
export NOTION_TOKEN="ntn_..."
python3 scraper.py

# Neuen Raum hinzufügen: in rooms_data.py ergänzen, dann sync
```

## Dateien

| Datei | Beschreibung |
|-------|-------------|
| `scraper.py` | Hauptskript — synchronisiert rooms_data.py nach Notion |
| `rooms_data.py` | Kuratierte Liste aller 95 Räume |
| `notion_sync.py` | Notion API: DB erstellen, Räume upserten, Dedup |
| `config.py` | Notion Token (via `NOTION_TOKEN` env var) + DB-ID |
| `run_scrape.sh` | Cron-Wrapper (lädt `.env`, Log-Rotation fuer `scraper.log`: max 1000 Zeilen, behält 500) |

## Cron

```
# Sonntags 06:03 UTC
3 6 * * 0 /home/claude-agent/escape-room-tracker/run_scrape.sh
```
