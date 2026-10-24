"""Privacy-first support issue intake and deterministic daily aggregates.

Disabled by default. No raw chat transcript, IP, user agent, email or names stored.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sqlite3
import threading

KINDS = {"faq", "ux", "bug", "feature", "ai_quality"}
MAX_TEXT = 600
_lock = threading.Lock()
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+?84|0)\d[\d .-]{8,13}(?!\d)")
SECRETS = re.compile(r"(?i)\b(password|passwd|token|secret|api[_-]?key|authorization)\s*[:=]\s*\S+")
BEARER = re.compile(r"(?i)bearer\s+\S+")


def sanitize(value: str, limit: int = MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise ValueError("Expected text")
    value = EMAIL.sub("[email]", value[:limit])
    value = PHONE.sub("[phone]", value)
    value = SECRETS.sub("[credential]", value)
    value = BEARER.sub("[credential]", value)
    return value.strip()[:limit]


def _connect(db_path: str):
    # Path must be provisioned by operator; never derive from request fields.
    db = sqlite3.connect(db_path, timeout=2)
    db.execute("PRAGMA busy_timeout=2000")
    db.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,
        app TEXT NOT NULL,
        kind TEXT NOT NULL,
        summary TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'new'
    )""")
    return db


def validate_report(app: str, kind: str, summary: str) -> str:
    """Full payload validation, no storage. Returns the sanitized summary."""
    if not isinstance(app, str) or not isinstance(kind, str) or kind not in KINDS \
            or not re.fullmatch(r"[a-z][a-z0-9_-]{1,31}", app):
        raise ValueError("Invalid category or application")
    safe = sanitize(summary)
    if len(safe) < 8:
        raise ValueError("Insufficient description")
    return safe


def record(db_path: str, app: str, kind: str, summary: str) -> int:
    safe = validate_report(app, kind, summary)
    day = datetime.now(timezone.utc).date().isoformat()
    with _lock, _connect(db_path) as db:
        # Same app + kind + sanitized text on the same day counts once (no per-caller identifiers kept).
        same = db.execute("SELECT id FROM feedback WHERE day=? AND app=? AND kind=? AND summary=?",
                          (day, app, kind, safe)).fetchone()
        if same:
            return same[0]
        cursor = db.execute(
            "INSERT INTO feedback(day,app,kind,summary) VALUES (?,?,?,?)", (day, app, kind, safe))
        return cursor.lastrowid


def summary(db_path: str, app: str | None = None, days: int = 7) -> list[dict]:
    if not 1 <= days <= 90:
        raise ValueError("Invalid range")
    from datetime import timedelta
    since = (datetime.now(timezone.utc).date() - timedelta(days=days - 1)).isoformat()
    with _connect(db_path) as db:
        if app:
            rows = db.execute("SELECT app,kind,COUNT(*) FROM feedback WHERE day>=? AND app=? GROUP BY app,kind", (since, app))
        else:
            rows = db.execute("SELECT app,kind,COUNT(*) FROM feedback WHERE day>=? GROUP BY app,kind", (since,))
        return [{"app": a, "kind": k, "count": n} for a, k, n in rows]


def retention(db_path: str, keep_days: int = 30) -> int:
    if not 1 <= keep_days <= 365:
        raise ValueError("Invalid retention")
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc).date() - timedelta(days=keep_days)).isoformat()
    with _lock, _connect(db_path) as db:
        return db.execute("DELETE FROM feedback WHERE day < ?", (cutoff,)).rowcount


def recent(db_path: str, app: str | None = None, kind: str | None = None, limit: int = 100) -> list[dict]:
    """Admin-only list of minimized reports for manual triage."""
    if kind is not None and kind not in KINDS:
        raise ValueError("Invalid kind")
    if app is not None and not re.fullmatch(r"[a-z][a-z0-9_-]{1,31}", app):
        raise ValueError("Invalid application")
    if not 1 <= limit <= 200:
        raise ValueError("Invalid limit")
    where, args = [], []
    if app:
        where.append("app=?")
        args.append(app)
    if kind:
        where.append("kind=?")
        args.append(kind)
    clause = " WHERE " + " AND ".join(where) if where else ""
    with _connect(db_path) as db:
        rows = db.execute("SELECT id,day,app,kind,summary,status FROM feedback" + clause +
                          " ORDER BY id DESC LIMIT ?", (*args, limit)).fetchall()
        return [dict(zip(("id", "day", "app", "kind", "summary", "status"), row)) for row in rows]


def set_status(db_path: str, report_id: int, status: str) -> bool:
    if status not in {"new", "reviewed", "resolved"} or type(report_id) is not int or report_id < 1:
        raise ValueError("Invalid status update")
    with _lock, _connect(db_path) as db:
        result = db.execute("UPDATE feedback SET status=? WHERE id=?", (status, report_id))
        return result.rowcount == 1
