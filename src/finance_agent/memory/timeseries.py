"""DuckDB time series store.

Handles all numerical time series data: OHLCV prices, technical indicators,
macro series, backtest results. DuckDB provides fast columnar analytics
with zero deployment complexity.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

logger = logging.getLogger(__name__)


class TimeSeriesStore:
    """DuckDB-based time series storage and analytics.

    Tables: ohlcv, technical_indicators, macro_series, backtest_results
    """

    def __init__(self, db_path: str = "./data/timeseries.duckdb") -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        """Create tables if they don't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ohlcv (
                ticker VARCHAR NOT NULL,
                date TIMESTAMP NOT NULL,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume BIGINT,
                adj_close DOUBLE,
                PRIMARY KEY (ticker, date)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS technical_indicators (
                ticker VARCHAR NOT NULL,
                date TIMESTAMP NOT NULL,
                indicator VARCHAR NOT NULL,
                value DOUBLE,
                params VARCHAR,
                PRIMARY KEY (ticker, date, indicator)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS macro_series (
                series_id VARCHAR NOT NULL,
                date TIMESTAMP NOT NULL,
                value DOUBLE,
                source VARCHAR,
                PRIMARY KEY (series_id, date)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                strategy_id VARCHAR NOT NULL,
                date TIMESTAMP NOT NULL,
                portfolio_value DOUBLE,
                returns DOUBLE,
                drawdown DOUBLE,
                PRIMARY KEY (strategy_id, date)
            )
        """)

    def insert_ohlcv(self, ticker: str, records: list[dict[str, Any]]) -> int:
        """Insert OHLCV price records. Uses INSERT OR REPLACE for dedup."""
        if not records:
            return 0
        rows = [
            (ticker, r["date"], r.get("open"), r.get("high"), r.get("low"),
             r.get("close"), r.get("volume"), r.get("adj_close"))
            for r in records
        ]
        self.conn.executemany(
            """INSERT OR REPLACE INTO ohlcv (ticker, date, open, high, low, close, volume, adj_close)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        return len(rows)

    def insert_macro(self, series_id: str, records: list[dict[str, Any]], source: str = "") -> int:
        """Insert macro series data."""
        if not records:
            return 0
        rows = [
            (series_id, r["date"], r["value"], source)
            for r in records
        ]
        self.conn.executemany(
            """INSERT OR REPLACE INTO macro_series (series_id, date, value, source)
            VALUES (?, ?, ?, ?)""",
            rows,
        )
        return len(rows)

    def query(self, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return results as dicts."""
        result = self.conn.execute(sql, params or [])
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def get_ohlcv(
        self, ticker: str, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict[str, Any]]:
        """Get OHLCV data for a ticker."""
        sql = "SELECT * FROM ohlcv WHERE ticker = ?"
        params: list[Any] = [ticker]
        if start_date:
            sql += " AND date >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND date <= ?"
            params.append(end_date)
        sql += " ORDER BY date"
        return self.query(sql, params)

    def get_sma(self, ticker: str, period: int = 20, start_date: str | None = None) -> list[dict[str, Any]]:
        """Calculate SMA using DuckDB window functions."""
        sql = f"""
            SELECT date, close,
                   AVG(close) OVER (
                     PARTITION BY ticker
                     ORDER BY date
                     ROWS BETWEEN {period - 1} PRECEDING AND CURRENT ROW
                   ) AS sma_{period}
            FROM ohlcv
            WHERE ticker = ?
        """
        params: list[Any] = [ticker]
        if start_date:
            sql += " AND date >= ?"
            params.append(start_date)
        sql += " ORDER BY date"
        return self.query(sql, params)

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
