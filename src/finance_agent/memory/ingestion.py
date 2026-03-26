"""KG Ingestion Pipeline.

Routes tool outputs to the appropriate storage backends:
- Structured entities -> Neo4j
- Text content -> ChromaDB (chunked + embedded)
- Time series -> DuckDB
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


def route_ingestion(tool_name: str, response: dict[str, Any]) -> list[str]:
    """Determine which stores should receive this data.

    Returns list of store names: "duckdb", "chromadb", "neo4j"
    """
    routes = []

    # Time series data -> DuckDB
    if tool_name in ("get_ohlcv", "get_historical_data", "get_fred_data", "get_eia_data"):
        routes.append("duckdb")

    # Text content -> ChromaDB for semantic search
    if tool_name in ("get_sec_filing", "get_sentiment", "search_gdelt"):
        routes.append("chromadb")

    # Structured entity data -> Neo4j
    if tool_name in ("get_company_profile", "get_analyst_ratings", "get_insider_trades"):
        routes.append("neo4j")

    # SEC filings also have entity mentions
    if tool_name == "get_sec_filing":
        routes.append("neo4j")

    return routes


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """Split text into overlapping chunks for embedding.

    Args:
        text: Input text
        chunk_size: Target tokens per chunk (approximate using words)
        overlap: Overlap between chunks in words

    Returns:
        List of text chunks
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    return chunks


async def ingest_to_duckdb(
    store: Any, tool_name: str, data: dict[str, Any]
) -> int:
    """Ingest time series data into DuckDB."""
    count = 0
    if tool_name in ("get_ohlcv", "get_historical_data"):
        ticker = data.get("ticker", "")
        candles = data.get("candles", [])
        if candles:
            count = store.insert_ohlcv(ticker, candles)
    elif tool_name in ("get_fred_data", "get_eia_data"):
        series_id = data.get("series_id", "")
        records = data.get("records", [])
        source = data.get("source", "")
        if records:
            count = store.insert_macro(series_id, records, source)
    return count


async def ingest_to_chromadb(
    store: Any, tool_name: str, data: dict[str, Any]
) -> int:
    """Ingest text documents into ChromaDB."""
    if tool_name == "get_sec_filing":
        collection = "sec_filings"
        filings = data.get("filings", [])
        docs, ids, metas = [], [], []
        for f in filings:
            doc_id = f"{data.get('ticker', '')}_{f.get('filing_type', '')}_{f.get('filed_at', '')}"
            # For now, store the filing metadata as the document
            # Full text parsing would happen here in production
            doc_text = f"{f.get('filing_type', '')} filing for {data.get('ticker', '')} on {f.get('filed_at', '')}"
            docs.append(doc_text)
            ids.append(doc_id)
            metas.append({
                "ticker": data.get("ticker", ""),
                "filing_type": f.get("filing_type", ""),
                "filed_at": f.get("filed_at", ""),
            })
        if docs:
            store.add_documents(collection, docs, ids, metas)
        return len(docs)

    elif tool_name == "search_gdelt":
        collection = "news"
        articles = data.get("articles", [])
        docs, ids, metas = [], [], []
        for a in articles:
            doc_id = f"gdelt_{uuid4().hex[:8]}"
            docs.append(a.get("title", ""))
            ids.append(doc_id)
            metas.append({
                "source": a.get("source", ""),
                "date": a.get("date", ""),
                "tone": str(a.get("tone", 0)),
            })
        if docs:
            store.add_documents(collection, docs, ids, metas)
        return len(docs)

    return 0


async def ingest_to_neo4j(
    kg: Any, tool_name: str, data: dict[str, Any]
) -> int:
    """Ingest entity data into Neo4j Knowledge Graph."""
    count = 0
    if tool_name == "get_company_profile":
        ticker = data.get("ticker", "")
        if ticker:
            kg.merge_entity("Company", {
                "ticker": ticker,
                "name": data.get("name", ""),
                "sector": data.get("sector", ""),
                "industry": data.get("industry", ""),
                "country": data.get("country", ""),
                "market_cap": data.get("market_cap"),
            })
            count += 1
            # Create sector relationship
            sector = data.get("sector")
            if sector:
                kg.merge_entity("Sector", {"name": sector})
                kg.create_relationship("Company", ticker, "BELONGS_TO", "Sector", sector)
                count += 1

    elif tool_name == "get_insider_trades":
        ticker = data.get("ticker", "")
        for trade in data.get("trades", []):
            insider_name = trade.get("insiderName") or trade.get("name", "Unknown")
            kg.merge_entity("Executive", {
                "name": insider_name,
                "title": trade.get("title", ""),
            })
            kg.create_relationship("Executive", insider_name, "LEADS", "Company", ticker)
            count += 1

    return count
