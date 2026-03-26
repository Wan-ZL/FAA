"""Macro economic tools.

6 tools for FRED data, EIA energy, yield curves, and FX rates.
"""

from __future__ import annotations

from typing import Any

from finance_agent.data.registry import registry
from finance_agent.tools.registry import ToolDefinition, ToolGroup


async def get_fred_data(
    series_id: str, start_date: str | None = None, end_date: str | None = None
) -> dict[str, Any]:
    """Get any FRED series data."""
    try:
        data = await registry.fetch(
            "macro_indicator",
            indicator_id=series_id,
            start_date=start_date,
            end_date=end_date,
        )
        if not data:
            return {"error": "no_data", "message": f"No data for FRED series {series_id}"}
        records = [{"date": str(d.date), "value": d.value} for d in data[-50:]]
        return {
            "series_id": series_id,
            "name": data[0].name if data else series_id,
            "source": "FRED",
            "data_points": len(data),
            "latest_value": data[-1].value,
            "latest_date": str(data[-1].date),
            "records": records,
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_eia_data(
    series_id: str, start_date: str | None = None, end_date: str | None = None
) -> dict[str, Any]:
    """Get EIA energy data."""
    try:
        data = await registry.fetch(
            "energy",
            indicator_id=series_id,
            start_date=start_date,
            end_date=end_date,
        )
        if not data:
            return {"error": "no_data", "message": f"No data for EIA series {series_id}"}
        records = [{"date": str(d.date), "value": d.value} for d in data[-50:]]
        return {
            "series_id": series_id,
            "name": data[0].name if data else series_id,
            "source": "EIA",
            "data_points": len(data),
            "latest_value": data[-1].value,
            "records": records,
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_pmi(indicator: str = "manufacturing") -> dict[str, Any]:
    """Get Purchasing Managers' Index."""
    series_map = {
        "manufacturing": "MANEMP",
        "services": "NMFCI",
    }
    series_id = series_map.get(indicator, "MANEMP")
    return await get_fred_data(series_id)


async def get_yield_curve() -> dict[str, Any]:
    """Get Treasury yield curve with spread calculations."""
    tenors = {"3M": "DGS3MO", "2Y": "DGS2", "5Y": "DGS5", "10Y": "DGS10", "30Y": "DGS30"}
    results: dict[str, Any] = {"tenors": {}, "spreads": {}}
    for tenor, series in tenors.items():
        try:
            data = await registry.fetch("macro_indicator", indicator_id=series)
            if data:
                results["tenors"][tenor] = data[-1].value
        except Exception:
            results["tenors"][tenor] = None

    # Calculate spreads
    t2y = results["tenors"].get("2Y")
    t10y = results["tenors"].get("10Y")
    t3m = results["tenors"].get("3M")
    if t10y is not None and t2y is not None:
        results["spreads"]["10Y-2Y"] = round(t10y - t2y, 3)
        results["spreads"]["curve_inverted"] = t10y < t2y
    if t10y is not None and t3m is not None:
        results["spreads"]["10Y-3M"] = round(t10y - t3m, 3)
    return results


async def get_fx_rates(base: str = "USD", targets: str = "EUR,GBP,JPY,CNY") -> dict[str, Any]:
    """Get foreign exchange rates."""
    try:
        import yfinance as yf
        target_list = [t.strip() for t in targets.split(",")]
        rates = {}
        for target in target_list:
            pair = f"{base}{target}=X"
            t = yf.Ticker(pair)
            hist = t.history(period="1d")
            if not hist.empty:
                rates[f"{base}/{target}"] = round(float(hist["Close"].iloc[-1]), 4)
        return {"base": base, "rates": rates}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def get_global_macro(countries: str = "US,EU,CN,JP") -> dict[str, Any]:
    """Get cross-country macro comparison."""
    country_list = [c.strip() for c in countries.split(",")]
    return {
        "countries": country_list,
        "note": "Cross-country macro comparison requires World Bank API integration",
        "available_via_fred": {
            "US": {"gdp": "GDP", "cpi": "CPIAUCSL", "unemployment": "UNRATE"},
            "EU": {"gdp": "EUNGDP", "cpi": "EUCPI"},
        },
    }


# --- Tool Group ---

macro_group = ToolGroup(
    name="macro",
    description="Macroeconomic data: FRED, EIA, yield curves, FX",
    tools=[
        ToolDefinition(name="get_fred_data", description="Get any FRED series (GDP, CPI, unemployment, fed funds rate, etc.)",
            input_schema={"type": "object", "properties": {"series_id": {"type": "string", "description": "FRED series ID or alias (e.g., GDP, FEDFUNDS, CPIAUCSL)"}, "start_date": {"type": "string"}, "end_date": {"type": "string"}}, "required": ["series_id"]}, handler=get_fred_data),
        ToolDefinition(name="get_eia_data", description="Get EIA energy data (crude oil, natural gas, production)",
            input_schema={"type": "object", "properties": {"series_id": {"type": "string"}, "start_date": {"type": "string"}, "end_date": {"type": "string"}}, "required": ["series_id"]}, handler=get_eia_data),
        ToolDefinition(name="get_pmi", description="Get Purchasing Managers' Index (manufacturing/services)",
            input_schema={"type": "object", "properties": {"indicator": {"type": "string", "enum": ["manufacturing", "services"], "default": "manufacturing"}}, "required": []}, handler=get_pmi),
        ToolDefinition(name="get_yield_curve", description="Get Treasury yield curve (3M, 2Y, 5Y, 10Y, 30Y) with spread calculations",
            input_schema={"type": "object", "properties": {}, "required": []}, handler=get_yield_curve),
        ToolDefinition(name="get_fx_rates", description="Get foreign exchange rates and cross rates",
            input_schema={"type": "object", "properties": {"base": {"type": "string", "default": "USD"}, "targets": {"type": "string", "default": "EUR,GBP,JPY,CNY"}}, "required": []}, handler=get_fx_rates),
        ToolDefinition(name="get_global_macro", description="Cross-country macro comparison (GDP growth, inflation, rates)",
            input_schema={"type": "object", "properties": {"countries": {"type": "string", "default": "US,EU,CN,JP"}}, "required": []}, handler=get_global_macro),
    ],
)
