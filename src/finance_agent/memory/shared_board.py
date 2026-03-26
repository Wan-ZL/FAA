"""Shared State Board using SQLite WAL mode.

The team coordination layer. Agents communicate findings, record decisions,
share cached data, and broadcast alerts through this board.

SQLite WAL mode provides concurrent reads with serialized writes.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from finance_agent.agent.models import Alert, Decision, Finding

logger = logging.getLogger(__name__)


class SharedBoardManager:
    """Manages the SQLite-based shared state board.

    Thread-safe with WAL mode for concurrent read access.
    """

    def __init__(self, db_path: str = "./data/shared_board.db") -> None:
        self.db_path = db_path
        self._local = threading.local()
        self._ensure_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return self._local.conn

    def _ensure_db(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                category TEXT NOT NULL,
                ticker TEXT,
                summary TEXT NOT NULL,
                data TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                tags TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                rationale TEXT NOT NULL,
                supporting_findings TEXT NOT NULL,
                dissenting_findings TEXT NOT NULL,
                debate_summary TEXT,
                recommendation TEXT NOT NULL,
                confidence REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS data_cache (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL,
                created_at TEXT NOT NULL,
                ttl_seconds INTEGER NOT NULL,
                hit_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                data TEXT NOT NULL,
                ttl_seconds INTEGER NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_findings_ticker ON findings(ticker);
            CREATE INDEX IF NOT EXISTS idx_findings_category ON findings(category);
            CREATE INDEX IF NOT EXISTS idx_findings_timestamp ON findings(timestamp);
            CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
        """)
        conn.commit()

    # --- Findings ---

    def write_finding(self, finding: Finding) -> None:
        """Append a finding to the board (append-only)."""
        conn = self._get_conn()
        conn.execute(
            """INSERT OR IGNORE INTO findings
            (id, agent_id, category, ticker, summary, data, confidence, timestamp, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                finding.id,
                finding.agent_id,
                finding.category,
                finding.ticker,
                finding.summary,
                json.dumps(finding.data, default=str),
                finding.confidence,
                finding.timestamp.isoformat(),
                json.dumps(finding.tags),
            ),
        )
        conn.commit()

    def read_findings(
        self,
        ticker: str | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> list[Finding]:
        """Read findings with optional filters."""
        conn = self._get_conn()
        query = "SELECT * FROM findings WHERE 1=1"
        params: list[Any] = []
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        return [
            Finding(
                id=row["id"],
                agent_id=row["agent_id"],
                category=row["category"],
                ticker=row["ticker"],
                summary=row["summary"],
                data=json.loads(row["data"]),
                confidence=row["confidence"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                tags=json.loads(row["tags"]),
            )
            for row in rows
        ]

    # --- Decisions ---

    def write_decision(self, decision: Decision) -> None:
        """Record a decision (immutable, event-sourced)."""
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO decisions
            (id, timestamp, query, rationale, supporting_findings, dissenting_findings,
             debate_summary, recommendation, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                decision.id,
                decision.timestamp.isoformat(),
                decision.query,
                decision.rationale,
                json.dumps(decision.supporting_findings),
                json.dumps(decision.dissenting_findings),
                decision.debate_summary,
                json.dumps(decision.recommendation, default=str),
                decision.confidence,
            ),
        )
        conn.commit()

    def read_decisions(self, limit: int = 10) -> list[Decision]:
        """Read recent decisions."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            Decision(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                query=row["query"],
                rationale=row["rationale"],
                supporting_findings=json.loads(row["supporting_findings"]),
                dissenting_findings=json.loads(row["dissenting_findings"]),
                debate_summary=row["debate_summary"],
                recommendation=json.loads(row["recommendation"]),
                confidence=row["confidence"],
            )
            for row in rows
        ]

    # --- Cache ---

    def cache_get(self, key: str) -> bytes | None:
        """Get a cached value if it exists and hasn't expired."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT value, created_at, ttl_seconds FROM data_cache WHERE key = ?",
            (key,),
        ).fetchone()
        if not row:
            return None
        created = datetime.fromisoformat(row["created_at"])
        if datetime.now() - created > timedelta(seconds=row["ttl_seconds"]):
            conn.execute("DELETE FROM data_cache WHERE key = ?", (key,))
            conn.commit()
            return None
        conn.execute(
            "UPDATE data_cache SET hit_count = hit_count + 1 WHERE key = ?", (key,)
        )
        conn.commit()
        return row["value"]

    def cache_set(self, key: str, value: bytes, ttl_seconds: int) -> None:
        """Set a cache entry with TTL."""
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO data_cache (key, value, created_at, ttl_seconds, hit_count)
            VALUES (?, ?, ?, ?, 0)""",
            (key, value, datetime.now().isoformat(), ttl_seconds),
        )
        conn.commit()

    def cache_cleanup(self) -> int:
        """Remove expired cache entries. Returns count of removed entries."""
        conn = self._get_conn()
        cursor = conn.execute(
            """DELETE FROM data_cache
            WHERE (julianday('now') - julianday(created_at)) * 86400 > ttl_seconds"""
        )
        conn.commit()
        return cursor.rowcount

    # --- Alerts ---

    def write_alert(self, alert: Alert) -> None:
        """Post an alert."""
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO alerts
            (id, timestamp, severity, category, message, data, ttl_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                alert.id,
                alert.timestamp.isoformat(),
                alert.severity,
                alert.category,
                alert.message,
                json.dumps(alert.data, default=str),
                alert.ttl_seconds,
            ),
        )
        conn.commit()

    def read_alerts(self, severity_min: str = "info") -> list[Alert]:
        """Read active (non-expired) alerts."""
        conn = self._get_conn()
        severity_order = {"info": 0, "warning": 1, "critical": 2}
        min_level = severity_order.get(severity_min, 0)

        # Filter expired alerts in SQL
        rows = conn.execute(
            """SELECT * FROM alerts
            WHERE (julianday('now') - julianday(timestamp)) * 86400 <= ttl_seconds
            ORDER BY timestamp DESC"""
        ).fetchall()

        return [
            alert for alert in (
                Alert(
                    id=row["id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    severity=row["severity"],
                    category=row["category"],
                    message=row["message"],
                    data=json.loads(row["data"]),
                    ttl_seconds=row["ttl_seconds"],
                )
                for row in rows
            )
            if severity_order.get(alert.severity, 0) >= min_level
        ]

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
