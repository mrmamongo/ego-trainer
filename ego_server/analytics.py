"""Privacy-preserving daily analytics for public pages and extension traffic."""

from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime, timedelta

from fastapi import Request

_BOT_UA = re.compile(r"bot|crawl|spider|curl", re.IGNORECASE)
_SAFE_KEY = re.compile(r"[^0-9A-Za-z._-]+")


def is_human_request(request: Request) -> bool:
    """Apply the intentionally small bot filter without retaining the user agent."""
    return _BOT_UA.search(request.headers.get("user-agent", "")) is None


def record_event(
    db: sqlite3.Connection,
    request: Request,
    metric: str,
    key: str = "",
    *,
    day: str | None = None,
) -> bool:
    """Increment one daily aggregate; never store IP, UA or client identifiers."""
    if not is_human_request(request):
        return False
    clean_key = _SAFE_KEY.sub("", key.strip())[:100]
    event_day = day or datetime.now(UTC).date().isoformat()
    db.execute(
        """INSERT INTO analytics_daily (day, metric, key, count) VALUES (?, ?, ?, 1)
           ON CONFLICT(day, metric, key) DO UPDATE SET count = count + 1""",
        (event_day, metric, clean_key),
    )
    db.commit()
    return True


def analytics_snapshot(db: sqlite3.Connection, days: int) -> dict:
    """Return daily counters and learning aggregates for the requested UTC window."""
    today = datetime.now(UTC).date()
    start = (today - timedelta(days=days - 1)).isoformat()
    end = today.isoformat()
    rows = db.execute(
        """SELECT day, metric, key, count FROM analytics_daily
           WHERE day BETWEEN ? AND ? ORDER BY day, metric, key""",
        (start, end),
    ).fetchall()
    daily = [dict(row) for row in rows]

    metric_totals = {
        row["metric"]: row["count"]
        for row in db.execute(
            """SELECT metric, SUM(count) AS count FROM analytics_daily
               WHERE day BETWEEN ? AND ? GROUP BY metric""",
            (start, end),
        )
    }
    active_installations_today = db.execute(
        """SELECT COALESCE(SUM(count), 0) AS count FROM analytics_daily
           WHERE day = ? AND metric = 'extension_active'""",
        (end,),
    ).fetchone()["count"]
    active_today = db.execute(
        "SELECT COUNT(DISTINCT student_id) AS count FROM runs WHERE substr(created_at, 1, 10) = ?",
        (end,),
    ).fetchone()["count"]
    week_start = (datetime.now(UTC) - timedelta(days=6)).isoformat()
    active_week = db.execute(
        """SELECT COUNT(DISTINCT student_id) AS count FROM runs
           WHERE julianday(created_at) >= julianday(?)""",
        (week_start,),
    ).fetchone()["count"]
    solved = db.execute(
        """SELECT COUNT(*) AS count FROM progress
           WHERE status = 'passed' AND substr(last_run_at, 1, 10) BETWEEN ? AND ?""",
        (start, end),
    ).fetchone()["count"]
    registrations = db.execute(
        """SELECT COUNT(*) AS count FROM students
           WHERE role = 'student' AND substr(created_at, 1, 10) BETWEEN ? AND ?""",
        (start, end),
    ).fetchone()["count"]

    return {
        "days": days,
        "start_day": start,
        "end_day": end,
        "daily": daily,
        "totals": {
            "landing_views": metric_totals.get("landing_view", 0),
            "student_views": metric_totals.get("student_view", 0),
            "extension_downloads": metric_totals.get("extension_download", 0),
            "active_installations_today": active_installations_today,
        },
        "learning": {
            "active_students_today": active_today,
            "active_students_week": active_week,
            "tasks_passed": solved,
            "new_students": registrations,
        },
    }
