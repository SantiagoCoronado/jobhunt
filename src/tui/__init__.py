"""jobhunt TUI (Textual). Spec: docs/spec-tui.md. Run: python -m src.tui

Only `data.py` opens SQLite; every write goes through db.set_status / touch_contact /
log_event so the events table and the application folders stay consistent with
`python -m src.query`.
"""
