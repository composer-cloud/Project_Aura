"""
Event Store — the memory substrate for Sofia's perception.

Two layers:
1. Immutable append-only JSONL audit log (the sacred record)
2. SQLite hot store for fast queries during perception cycles

This module never deletes the audit. It only ages out the SQLite view.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from ..models import Event, PerceptionSummary


class EventStore:
    """
    Thread/Async-safe enough for single-writer daemon usage.
    """

    def __init__(self, data_dir: Path, max_hot_days: int = 30):
        self.data_dir = data_dir
        self.audit_dir = data_dir / "audit"
        self.db_path = data_dir / "events.db"
        self.max_hot_days = max_hot_days

        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._init_sqlite()

    def _init_sqlite(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                ts TEXT NOT NULL,
                sensor TEXT NOT NULL,
                kind TEXT NOT NULL,
                subject TEXT NOT NULL,
                metadata TEXT,
                raw_ref TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS perception_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                phase TEXT NOT NULL,
                narrative TEXT,
                tags TEXT,
                rhythm_shift TEXT,
                attunement_delta REAL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);")
        conn.commit()
        conn.close()

    def _audit_path_for(self, dt: datetime) -> Path:
        return self.audit_dir / f"{dt.strftime('%Y-%m-%d')}.jsonl"

    def append_event(self, event: Event) -> None:
        """Write to both audit (immutable) and hot SQLite."""
        # 1. Immutable audit
        audit_line = event.to_audit_line() + "\n"
        audit_path = self._audit_path_for(event.ts)
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(audit_line)

        # 2. Hot store
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO events (id, ts, sensor, kind, subject, metadata, raw_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.ts.isoformat(),
                event.sensor,
                event.kind.value,
                event.subject,
                json.dumps(event.metadata, ensure_ascii=False),
                event.raw_ref,
            ),
        )
        conn.commit()
        conn.close()

    def append_summary(self, summary: PerceptionSummary) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO perception_summaries (ts, phase, narrative, tags, rhythm_shift, attunement_delta)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                summary.ts.isoformat(),
                summary.phase,
                summary.narrative_fragment,
                json.dumps(summary.attention_tags),
                summary.rhythm_shift,
                summary.attunement_delta,
            ),
        )
        conn.commit()
        conn.close()

    def get_recent_events(self, hours: int = 4, limit: int = 200) -> list[dict]:
        """Fast query for perception cycles."""
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT * FROM events
            WHERE ts >= ?
            ORDER BY ts DESC
            LIMIT ?
            """,
            (since, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_events_since(self, since: datetime) -> list[Event]:
        """Rehydrate Events (used for deeper analysis)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM events WHERE ts >= ? ORDER BY ts ASC",
            (since.isoformat(),),
        ).fetchall()
        conn.close()

        events: list[Event] = []
        for r in rows:
            events.append(
                Event(
                    id=r["id"],
                    ts=datetime.fromisoformat(r["ts"]),
                    sensor=r["sensor"],
                    kind=r["kind"],
                    subject=r["subject"],
                    metadata=json.loads(r["metadata"] or "{}"),
                    raw_ref=r["raw_ref"],
                )
            )
        return events

    def prune_hot_store(self) -> int:
        """Remove old events from SQLite (audit is never touched)."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=self.max_hot_days)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("DELETE FROM events WHERE ts < ?", (cutoff,))
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        return deleted

    def write_journal_entry(self, content: str, path: Path) -> None:
        """Append a beautiful entry to the living journal."""
        path = path.expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
        entry = f"\n{ts}\n\n{content.strip()}\n\n"

        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)
