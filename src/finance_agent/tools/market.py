"""Market data tools.

8 tools for real-time and historical market data access.
"""

from __future__ import annotations

from typing import Any

from finance_agent.data.registry import registry
from finance_agent.tools.registry import ToolDefinition, ToolGroup


async def get_stock_price(ticker: str, period: str = "1d") -> dict[str, Any]:
    """Get current or historical stock price data."""
    try:
        data = await registry.fetch("price", ticker=ticker, period=period)
        if not data:
            return {"error": "no_data", "message": f"No price data for {ticker}"}
        latest = data[-1]
        return {
            "ticker": ticker,
            "date": str(latest.date),
            "open": latest.open,
            "high": latest.high,
            "low": latest.low,
            "close": latest.close,
            "volume": latest.volume,
            "data_points": len(data),
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_ohlcv(
    ticker: str,
    interval: str = "1d",
    start: str | None = None,
    end: str | None = None,
    period: str | None = None,
) -> dict[str, Any]:
    """Get OHLCV candlestick data."""
    try:
        params: dict[str, Any] = {"ticker": ticker, "interval": interval}
        if period:
            params["period"] = period
        if start:
            params["start_date"] = start
        if end:
            params["end_date"] = end

        data = await registry.fetch("price", **params)
        records = [
            {
                "date": str(d.date),
                "open": d.open,
                "high": d.high,
                "low": d.low,
                "close": d.close,
                "volume": d.volume,
            }
            for d in data
        ]
        return {"ticker": ticker, "interval": interval, "candles": records}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_realtime_quote(ticker: str) -> dict[str, Any]:
    """Get real-time bid/ask/last with volume."""
    try:
        data = await registry.fetch("price", ticker=ticker, period="1d", interval="1m")
        if not data:
            return {"error": "no_data", "message": f"No real-time data for {ticker}"}
        latest = data[-1]
        return {
            "ticker": ticker,
            "last": latest.close,
            "high": latest.high,
            "low": latest.low,
            "volume": latest.volume,
            "timestamp": str(latest.date),
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_historical_data(
    ticker: str, years: int = 5
) -> dict[str, Any]:
    """Get extended historical price series."""
    try:
        data = await registry.fetch("price", ticker=ticker, period=f"{years}y")
        if not data:
            return {"error": "no_data", "message": f"No historical data for {ticker}"}
        return {
            "ticker": ticker,
            "period": f"{years} years",
            "data_points": len(data),
            "first_date": str(data[0].date),
            "last_date": str(data[-1].date),
            "first_close": data[0].close,
            "last_close": data[-1].close,
            "total_return_pct": round((data[-1].close / data[0].close - 1) * 100, 2),
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_market_depth(ticker: str) -> dict[str, Any]:
    """Get Level 2 order book (top-of-book)."""
    return {
        "ticker": ticker,
        "note": "Market depth requires Polygon WebSocket subscription",
        "error": "not_implemented",
    }


async def get_sector_performance(period: str = "1mo") -> dict[str, Any]:
    """Get sector/industry returns over configurable periods."""
    import asyncio
    import yfinance as yf

    sectors = {
        "Technology": "XLK", "Healthcare": "XLV", "Financials": "XLF",
        "Consumer Discretionary": "XLY", "Industrials": "XLI",
        "Energy": "XLE", "Utilities": "XLU", "Materials": "XLB",
        "Real Estate": "XLRE", "Communication Services": "XLC",
        "Consumer Staples": "XLP",
    }
    loop = asyncio.get_running_loop()

    def _fetch():
        tickers = list(sectors.values())
        data = yf.download(tickers, period=period, group_by="ticker", progress=False)
        results = {}
        for name, etf in sectors.items():
            try:
                if etf in data.columns.get_level_values(0):
                    closes = data[etf]["Close"].dropna()
                    if len(closes) >= 2:
                        ret = (closes.iloc[-1] / closes.iloc[0] - 1) * 100
                        results[name] = round(ret, 2)
            except (KeyError, IndexError):
                results[name] = None
        return results

    results = await loop.run_in_executor(None, _fetch)
    return {"period": period, "sectors": results}


async def get_index_constituents(index: str = "SP500") -> dict[str, Any]:
    """Get list of tickers in an index."""
    # SP500 from Wikipedia
    if index.upper() in ("SP500", "S&P500"):
        try:
            import pandas as pd
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            if tables:
                df = tables[0]
                tickers = df["Symbol"].tolist()
                return {"index": "S&P 500", "count": len(tickers), "tickers": tickers[:50]}
        except Exception as e:
            return {"error": "fetch_failed", "message": str(e)}
    return {"error": "unsupported_index", "message": f"Index {index} not supported"}


async def get_premarket_data(ticker: str) -> dict[str, Any]:
    """Get pre-market/after-hours price and volume."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "ticker": ticker,
            "pre_market_price": info.get("preMarketPrice"),
            "pre_market_change_pct": info.get("preMarketChangePercent"),
            "post_market_price": info.get("postMarketPrice"),
            "post_market_change_pct": info.get("postMarketChangePercent"),
            "regular_market_price": info.get("regularMarketPrice"),
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


# --- Tool Group Registration ---

market_data_group = ToolGroup(
    name="market_data",
    description="Real-time and historical market data",
    tools=[
        ToolDefinition(
            name="get_stock_price",
            description="Get current or historical stock price data with OHLCV",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol (e.g., AAPL)"},
                    "period": {"type": "string", "description": "Time period: 1d, 5d, 1mo, 3mo, 1y, 5y", "default": "1d"},
                },
                "required": ["ticker"],
            },
            handler=get_stock_price,
        ),
        ToolDefinition(
            name="get_ohlcv",
            description="Get OHLCV candlestick data at configurable intervals",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                    "interval": {"type": "string", "description": "Candle interval: 1m, 5m, 15m, 1h, 1d, 1wk", "default": "1d"},
                    "start": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "period": {"type": "string", "description": "Period shorthand: 1d, 5d, 1mo, 3mo, 1y"},
                },
                "required": ["ticker"],
            },
            handler=get_ohlcv,
        ),
        ToolDefinition(
            name="get_realtime_quote",
            description="Get real-time quote with last price, high, low, volume",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                },
                "required": ["ticker"],
            },
            handler=get_realtime_quote,
        ),
        ToolDefinition(
            name="get_historical_data",
            description="Get extended historical price series (up to 20+ years)",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                    "years": {"type": "integer", "description": "Number of years of history", "default": 5},
                },
                "required": ["ticker"],
            },
            handler=get_historical_data,
        ),
        ToolDefinition(
            name="get_market_depth",
            description="Get Level 2 order book data (top-of-book)",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                },
                "required": ["ticker"],
            },
            handler=get_market_depth,
        ),
        ToolDefinition(
            name="get_sector_performance",
            description="Get sector/industry returns over configurable periods",
            input_schema={
                "type": "object",
                "properties": {
                    "period": {"type": "string", "description": "Time period: 1d, 5d, 1mo, 3mo, 1y", "default": "1mo"},
                },
                "required": [],
            },
            handler=get_sector_performance,
        ),
        ToolDefinition(
            name="get_index_constituents",
            description="Get list of tickers in an index (S&P 500, Nasdaq 100, etc.)",
            input_schema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name: SP500, NASDAQ100", "default": "SP500"},
                },
                "required": [],
            },
            handler=get_index_constituents,
        ),
        ToolDefinition(
            name="get_premarket_data",
            description="Get pre-market and after-hours price and volume",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                },
                "required": ["ticker"],
            },
            handler=get_premarket_data,
        ),
    ],
)
