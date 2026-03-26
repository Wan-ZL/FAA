"""Sentiment and news tools.

5 tools for news sentiment, GDELT events, insider trades, social mentions, analyst ratings.
"""

from __future__ import annotations

from typing import Any

import yfinance as yf

from finance_agent.tools.registry import ToolDefinition, ToolGroup


async def get_sentiment(ticker: str) -> dict[str, Any]:
    """Get aggregated sentiment score for a ticker."""
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        if not news:
            return {"ticker": ticker, "sentiment": "neutral", "score": 0.0, "news_count": 0}

        # Simple sentiment heuristic based on news titles
        positive_words = {"beat", "surge", "jump", "rally", "upgrade", "growth", "record", "strong", "buy"}
        negative_words = {"miss", "drop", "fall", "decline", "downgrade", "cut", "weak", "sell", "warning"}

        scores = []
        for item in news[:20]:
            title = item.get("title", "").lower()
            pos = sum(1 for w in positive_words if w in title)
            neg = sum(1 for w in negative_words if w in title)
            if pos + neg > 0:
                scores.append((pos - neg) / (pos + neg))
            else:
                scores.append(0.0)

        avg_score = sum(scores) / len(scores) if scores else 0.0
        label = "positive" if avg_score > 0.2 else "negative" if avg_score < -0.2 else "neutral"

        headlines = [
            {"title": item.get("title", ""), "publisher": item.get("publisher", "")}
            for item in news[:5]
        ]

        return {
            "ticker": ticker,
            "sentiment_score": round(avg_score, 3),
            "sentiment_label": label,
            "news_count": len(news),
            "top_headlines": headlines,
            "note": "Basic heuristic sentiment. FinBERT integration available for production.",
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def search_gdelt(query: str, days: int = 7) -> dict[str, Any]:
    """Search GDELT global events database."""
    try:
        import httpx
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": 20,
            "format": "json",
            "timespan": f"{days}d",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return {"error": "gdelt_unavailable", "status": resp.status_code}
            data = resp.json()
        articles = data.get("articles", [])
        return {
            "query": query,
            "results": len(articles),
            "articles": [
                {
                    "title": a.get("title", ""),
                    "source": a.get("domain", ""),
                    "date": a.get("seendate", ""),
                    "tone": a.get("tone", 0),
                    "url": a.get("url", ""),
                }
                for a in articles[:10]
            ],
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_insider_trades(ticker: str) -> dict[str, Any]:
    """Get recent insider buying/selling."""
    try:
        t = yf.Ticker(ticker)
        insiders = t.insider_transactions
        if insiders is None or insiders.empty:
            return {"ticker": ticker, "trades": [], "note": "No recent insider transactions"}
        records = insiders.head(10).to_dict(orient="records")
        return {"ticker": ticker, "trades": records}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_social_mentions(ticker: str) -> dict[str, Any]:
    """Get social media mention volume and sentiment."""
    return {
        "ticker": ticker,
        "note": "Social mention tracking requires Reddit/StockTwits API integration",
        "available_alternatives": ["Use get_sentiment for news-based sentiment", "Use search_gdelt for media coverage"],
    }


async def get_analyst_ratings(ticker: str) -> dict[str, Any]:
    """Get recent analyst upgrades/downgrades."""
    try:
        t = yf.Ticker(ticker)
        recs = t.recommendations
        if recs is None or recs.empty:
            return {"ticker": ticker, "ratings": []}
        recent = recs.tail(10).to_dict(orient="records")
        return {"ticker": ticker, "ratings": recent}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


# --- Tool Group ---

sentiment_group = ToolGroup(
    name="sentiment",
    description="Sentiment analysis, news, insider activity, analyst ratings",
    tools=[
        ToolDefinition(name="get_sentiment", description="Get aggregated sentiment score for a ticker from news",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}, handler=get_sentiment),
        ToolDefinition(name="search_gdelt", description="Search GDELT global events database for geopolitical signals",
            input_schema={"type": "object", "properties": {"query": {"type": "string"}, "days": {"type": "integer", "default": 7}}, "required": ["query"]}, handler=search_gdelt),
        ToolDefinition(name="get_insider_trades", description="Get recent insider buying/selling (Form 4 filings)",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}, handler=get_insider_trades),
        ToolDefinition(name="get_social_mentions", description="Get social media mention volume and sentiment",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}, handler=get_social_mentions),
        ToolDefinition(name="get_analyst_ratings", description="Get recent analyst upgrades/downgrades/initiations",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}, handler=get_analyst_ratings),
    ],
)
