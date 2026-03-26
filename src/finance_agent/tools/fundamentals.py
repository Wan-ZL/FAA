"""Fundamental analysis tools.

8 tools for financial statements, valuations, and SEC filings.
"""

from __future__ import annotations

from typing import Any

from finance_agent.data.registry import registry
from finance_agent.tools.registry import ToolDefinition, ToolGroup


async def get_income_stmt(ticker: str, period: str = "annual") -> dict[str, Any]:
    """Get income statement data."""
    try:
        data = await registry.fetch("fundamentals", ticker=ticker, period=period)
        if not data:
            return {"error": "no_data", "message": f"No income data for {ticker}"}
        records = [
            {
                "period_date": str(d.period_date),
                "revenue": d.revenue,
                "net_income": d.net_income,
                "eps": d.eps,
                "ebitda": d.ebitda,
                "gross_profit": d.gross_profit,
                "operating_income": d.operating_income,
            }
            for d in data
        ]
        return {"ticker": ticker, "period": period, "statements": records}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_balance_sheet(ticker: str, period: str = "annual") -> dict[str, Any]:
    """Get balance sheet snapshot."""
    try:
        data = await registry.fetch("fundamentals", ticker=ticker, period=period)
        if not data:
            return {"error": "no_data", "message": f"No balance sheet data for {ticker}"}
        records = [
            {
                "period_date": str(d.period_date),
                "total_assets": d.total_assets,
                "total_liabilities": d.total_liabilities,
                "total_equity": d.total_equity,
            }
            for d in data
        ]
        return {"ticker": ticker, "period": period, "statements": records}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_cashflow(ticker: str, period: str = "annual") -> dict[str, Any]:
    """Get cash flow statement."""
    try:
        data = await registry.fetch("fundamentals", ticker=ticker, period=period)
        if not data:
            return {"error": "no_data", "message": f"No cashflow data for {ticker}"}
        records = [
            {
                "period_date": str(d.period_date),
                "operating_cashflow": d.operating_cashflow,
                "free_cashflow": d.free_cashflow,
            }
            for d in data
        ]
        return {"ticker": ticker, "period": period, "statements": records}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_sec_filing(ticker: str, filing_type: str = "10-K", limit: int = 5) -> dict[str, Any]:
    """Get SEC filing data."""
    try:
        data = await registry.fetch(
            "sec_filing", ticker=ticker, filing_type=filing_type, limit=limit
        )
        if not data:
            return {"error": "no_data", "message": f"No {filing_type} filings for {ticker}"}
        records = [
            {
                "filing_type": d.filing_type,
                "filed_at": str(d.filed_at),
                "period": d.period,
                "url": d.url,
                "accession_number": d.accession_number,
            }
            for d in data
        ]
        return {"ticker": ticker, "filing_type": filing_type, "filings": records}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_earnings_history(ticker: str, limit: int = 8) -> dict[str, Any]:
    """Get historical EPS actuals vs. estimates."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        earnings = t.earnings_history
        if earnings is None or earnings.empty:
            return {"error": "no_data", "message": f"No earnings history for {ticker}"}
        records = earnings.head(limit).to_dict(orient="records")
        return {"ticker": ticker, "earnings": records}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_analyst_estimates(ticker: str) -> dict[str, Any]:
    """Get consensus revenue/EPS estimates and target prices."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "ticker": ticker,
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "target_mean": info.get("targetMeanPrice"),
            "target_median": info.get("targetMedianPrice"),
            "recommendation": info.get("recommendationKey"),
            "number_of_analysts": info.get("numberOfAnalystOpinions"),
            "forward_eps": info.get("forwardEps"),
            "forward_pe": info.get("forwardPE"),
            "trailing_eps": info.get("trailingEps"),
            "trailing_pe": info.get("trailingPE"),
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_company_profile(ticker: str) -> dict[str, Any]:
    """Get company overview, industry, employees, description."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "ticker": ticker,
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "country": info.get("country", ""),
            "employees": info.get("fullTimeEmployees"),
            "market_cap": info.get("marketCap"),
            "description": info.get("longBusinessSummary", "")[:500],
            "website": info.get("website", ""),
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def screen_stocks(
    min_market_cap: float | None = None,
    max_pe: float | None = None,
    min_dividend_yield: float | None = None,
    sector: str | None = None,
) -> dict[str, Any]:
    """Screen stocks by financial criteria."""
    return {
        "note": "Stock screening requires Finviz or dedicated screener API",
        "criteria": {
            "min_market_cap": min_market_cap,
            "max_pe": max_pe,
            "min_dividend_yield": min_dividend_yield,
            "sector": sector,
        },
        "error": "not_fully_implemented",
    }


# --- Tool Group Registration ---

fundamentals_group = ToolGroup(
    name="fundamentals",
    description="Financial statements, valuations, and SEC filings",
    tools=[
        ToolDefinition(
            name="get_income_stmt",
            description="Get income statement (annual/quarterly) with revenue, net income, EPS",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                    "period": {"type": "string", "description": "annual or quarterly", "default": "annual"},
                },
                "required": ["ticker"],
            },
            handler=get_income_stmt,
        ),
        ToolDefinition(
            name="get_balance_sheet",
            description="Get balance sheet with total assets, liabilities, equity",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                    "period": {"type": "string", "description": "annual or quarterly", "default": "annual"},
                },
                "required": ["ticker"],
            },
            handler=get_balance_sheet,
        ),
        ToolDefinition(
            name="get_cashflow",
            description="Get cash flow statement with operating and free cash flow",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                    "period": {"type": "string", "description": "annual or quarterly", "default": "annual"},
                },
                "required": ["ticker"],
            },
            handler=get_cashflow,
        ),
        ToolDefinition(
            name="get_sec_filing",
            description="Get SEC filing data (10-K, 10-Q, 8-K) with URLs and metadata",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                    "filing_type": {"type": "string", "description": "Filing type: 10-K, 10-Q, 8-K", "default": "10-K"},
                    "limit": {"type": "integer", "description": "Max filings to return", "default": 5},
                },
                "required": ["ticker"],
            },
            handler=get_sec_filing,
        ),
        ToolDefinition(
            name="get_earnings_history",
            description="Get historical EPS actuals vs. estimates with surprise percentage",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                    "limit": {"type": "integer", "description": "Number of quarters", "default": 8},
                },
                "required": ["ticker"],
            },
            handler=get_earnings_history,
        ),
        ToolDefinition(
            name="get_analyst_estimates",
            description="Get consensus target prices, EPS estimates, and analyst recommendations",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                },
                "required": ["ticker"],
            },
            handler=get_analyst_estimates,
        ),
        ToolDefinition(
            name="get_company_profile",
            description="Get company overview: name, sector, industry, market cap, description",
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock symbol"},
                },
                "required": ["ticker"],
            },
            handler=get_company_profile,
        ),
        ToolDefinition(
            name="screen_stocks",
            description="Screen stocks by financial criteria (P/E, market cap, dividend yield, sector)",
            input_schema={
                "type": "object",
                "properties": {
                    "min_market_cap": {"type": "number", "description": "Minimum market cap"},
                    "max_pe": {"type": "number", "description": "Maximum P/E ratio"},
                    "min_dividend_yield": {"type": "number", "description": "Minimum dividend yield (%)"},
                    "sector": {"type": "string", "description": "Sector filter"},
                },
                "required": [],
            },
            handler=screen_stocks,
        ),
    ],
)
