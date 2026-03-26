"""Options analysis tools.

6 tools for options pricing, Greeks, IV surface, and strategy construction.
Uses mibian as primary (lightweight Black-Scholes). QuantLib optional.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import yfinance as yf

from finance_agent.tools.registry import ToolDefinition, ToolGroup


def _black_scholes_price(
    S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> float:
    """Pure Python Black-Scholes pricing."""
    from math import exp, log, sqrt
    from statistics import NormalDist
    nd = NormalDist()
    if T <= 0 or sigma <= 0:
        return max(0, S - K) if option_type == "call" else max(0, K - S)
    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    if option_type == "call":
        return S * nd.cdf(d1) - K * exp(-r * T) * nd.cdf(d2)
    else:
        return K * exp(-r * T) * nd.cdf(-d2) - S * nd.cdf(-d1)


def _calculate_greeks(
    S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> dict[str, float]:
    """Calculate all Greeks using Black-Scholes."""
    from math import exp, log, sqrt, pi
    from statistics import NormalDist
    nd = NormalDist()
    if T <= 0 or sigma <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    nd_pdf_d1 = exp(-0.5 * d1**2) / sqrt(2 * pi)
    if option_type == "call":
        delta = nd.cdf(d1)
        theta = (-S * nd_pdf_d1 * sigma / (2 * sqrt(T)) - r * K * exp(-r * T) * nd.cdf(d2)) / 365
        rho = K * T * exp(-r * T) * nd.cdf(d2) / 100
    else:
        delta = nd.cdf(d1) - 1
        theta = (-S * nd_pdf_d1 * sigma / (2 * sqrt(T)) + r * K * exp(-r * T) * nd.cdf(-d2)) / 365
        rho = -K * T * exp(-r * T) * nd.cdf(-d2) / 100
    gamma = nd_pdf_d1 / (S * sigma * sqrt(T))
    vega = S * nd_pdf_d1 * sqrt(T) / 100
    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 6),
        "theta": round(theta, 4),
        "vega": round(vega, 4),
        "rho": round(rho, 4),
    }


async def get_options_chain(
    ticker: str, expiry: str | None = None, option_type: str | None = None
) -> dict[str, Any]:
    """Get full options chain with bid/ask/volume/OI."""
    try:
        t = yf.Ticker(ticker)
        expirations = t.options
        if not expirations:
            return {"error": "no_data", "message": f"No options for {ticker}"}
        target = expiry if expiry and expiry in expirations else expirations[0]
        chain = t.option_chain(target)
        result: dict[str, Any] = {"ticker": ticker, "expiry": target}
        if option_type != "put":
            result["calls"] = chain.calls.head(20).to_dict(orient="records")
        if option_type != "call":
            result["puts"] = chain.puts.head(20).to_dict(orient="records")
        result["available_expiries"] = list(expirations[:10])
        return result
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def price_option(
    ticker: str, strike: float, expiry: str, option_type: str = "call",
    model: str = "black_scholes",
) -> dict[str, Any]:
    """Calculate theoretical option price."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        S = info.get("regularMarketPrice") or info.get("previousClose", 0)
        if not S:
            return {"error": "no_price", "message": f"Cannot get price for {ticker}"}
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
        T = max((expiry_date - datetime.now()).days / 365, 0.001)
        r = 0.05  # risk-free rate approximation
        sigma = info.get("impliedVolatility", 0.3) or 0.3
        price = _black_scholes_price(S, strike, T, r, sigma, option_type)
        greeks = _calculate_greeks(S, strike, T, r, sigma, option_type)
        return {
            "ticker": ticker,
            "strike": strike,
            "expiry": expiry,
            "option_type": option_type,
            "underlying_price": round(S, 2),
            "theoretical_price": round(price, 2),
            "iv_used": round(sigma, 4),
            "time_to_expiry_years": round(T, 4),
            "greeks": greeks,
            "model": model,
        }
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def calculate_greeks(
    ticker: str, strike: float, expiry: str, option_type: str = "call",
) -> dict[str, Any]:
    """Calculate options Greeks for a specific contract."""
    result = await price_option(ticker, strike, expiry, option_type)
    if "error" in result:
        return result
    return {
        "ticker": ticker,
        "strike": strike,
        "expiry": expiry,
        "option_type": option_type,
        "greeks": result.get("greeks", {}),
    }


async def get_iv_surface(ticker: str) -> dict[str, Any]:
    """Get implied volatility surface (strike x expiry)."""
    try:
        t = yf.Ticker(ticker)
        expirations = t.options[:5]
        surface = []
        for exp in expirations:
            chain = t.option_chain(exp)
            for _, row in chain.calls.iterrows():
                if row.get("impliedVolatility", 0) > 0:
                    surface.append({
                        "expiry": exp,
                        "strike": float(row["strike"]),
                        "iv": round(float(row["impliedVolatility"]), 4),
                        "type": "call",
                    })
        return {"ticker": ticker, "surface_points": len(surface), "surface": surface[:50]}
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


async def build_strategy(
    ticker: str, strategy_type: str = "bull_call_spread",
    strike_low: float | None = None, strike_high: float | None = None,
    expiry: str | None = None,
) -> dict[str, Any]:
    """Construct multi-leg option strategy."""
    strategies = {
        "bull_call_spread": "Buy lower strike call, sell higher strike call",
        "bear_put_spread": "Buy higher strike put, sell lower strike put",
        "straddle": "Buy call and put at same strike (ATM)",
        "strangle": "Buy OTM call and OTM put",
        "iron_condor": "Sell OTM put spread + sell OTM call spread",
        "covered_call": "Long stock + sell OTM call",
        "protective_put": "Long stock + buy OTM put",
    }
    if strategy_type not in strategies:
        return {"error": "unknown_strategy", "available": list(strategies.keys())}
    return {
        "ticker": ticker,
        "strategy": strategy_type,
        "description": strategies[strategy_type],
        "legs": {
            "strike_low": strike_low,
            "strike_high": strike_high,
            "expiry": expiry,
        },
        "note": "Use price_option to price individual legs and calculate total P&L",
    }


async def analyze_spread(
    ticker: str, buy_strike: float, sell_strike: float,
    expiry: str, spread_type: str = "call",
) -> dict[str, Any]:
    """Analyze P&L profile, max profit/loss, breakevens for a spread."""
    try:
        buy_result = await price_option(ticker, buy_strike, expiry, spread_type)
        sell_result = await price_option(ticker, sell_strike, expiry, spread_type)
        if "error" in buy_result or "error" in sell_result:
            return {"error": "pricing_failed", "buy": buy_result, "sell": sell_result}
        buy_premium = buy_result["theoretical_price"]
        sell_premium = sell_result["theoretical_price"]
        net_debit = buy_premium - sell_premium
        if spread_type == "call":
            max_profit = abs(sell_strike - buy_strike) - abs(net_debit)
            max_loss = abs(net_debit)
            breakeven = min(buy_strike, sell_strike) + abs(net_debit)
        else:
            max_profit = abs(sell_strike - buy_strike) - abs(net_debit)
            max_loss = abs(net_debit)
            breakeven = max(buy_strike, sell_strike) - abs(net_debit)
        return {
            "ticker": ticker,
            "spread_type": f"{spread_type}_spread",
            "buy_strike": buy_strike,
            "sell_strike": sell_strike,
            "expiry": expiry,
            "net_debit": round(net_debit, 2),
            "max_profit": round(max_profit, 2),
            "max_loss": round(max_loss, 2),
            "breakeven": round(breakeven, 2),
            "risk_reward_ratio": round(max_profit / max_loss, 2) if max_loss > 0 else float("inf"),
        }
    except Exception as e:
        return {"error": "analysis_failed", "message": str(e)}


# --- Tool Group ---

options_group = ToolGroup(
    name="options",
    description="Options pricing, Greeks, IV surface, and strategy construction",
    tools=[
        ToolDefinition(name="get_options_chain", description="Get full options chain with bid/ask/volume/OI",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "expiry": {"type": "string", "description": "YYYY-MM-DD"}, "option_type": {"type": "string", "enum": ["call", "put"]}}, "required": ["ticker"]}, handler=get_options_chain),
        ToolDefinition(name="price_option", description="Calculate theoretical option price using Black-Scholes",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "strike": {"type": "number"}, "expiry": {"type": "string"}, "option_type": {"type": "string", "default": "call"}, "model": {"type": "string", "default": "black_scholes"}}, "required": ["ticker", "strike", "expiry"]}, handler=price_option),
        ToolDefinition(name="calculate_greeks", description="Calculate delta, gamma, theta, vega, rho for a contract",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "strike": {"type": "number"}, "expiry": {"type": "string"}, "option_type": {"type": "string", "default": "call"}}, "required": ["ticker", "strike", "expiry"]}, handler=calculate_greeks),
        ToolDefinition(name="get_iv_surface", description="Get implied volatility surface (strike x expiry matrix)",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}, handler=get_iv_surface),
        ToolDefinition(name="build_strategy", description="Construct multi-leg option strategy (spread, straddle, condor)",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "strategy_type": {"type": "string", "enum": ["bull_call_spread", "bear_put_spread", "straddle", "strangle", "iron_condor", "covered_call", "protective_put"]}, "strike_low": {"type": "number"}, "strike_high": {"type": "number"}, "expiry": {"type": "string"}}, "required": ["ticker", "strategy_type"]}, handler=build_strategy),
        ToolDefinition(name="analyze_spread", description="Analyze P&L profile, max profit/loss, breakevens for a spread",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "buy_strike": {"type": "number"}, "sell_strike": {"type": "number"}, "expiry": {"type": "string"}, "spread_type": {"type": "string", "default": "call"}}, "required": ["ticker", "buy_strike", "sell_strike", "expiry"]}, handler=analyze_spread),
    ],
)
