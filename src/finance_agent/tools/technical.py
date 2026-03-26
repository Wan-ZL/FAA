"""Technical analysis tools.

8 tools for indicators, patterns, and support/resistance.
Uses pandas-ta as primary library (pure Python, no C dependency).
Falls back gracefully if TA-Lib is unavailable.
"""

from __future__ import annotations

import asyncio
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf

from finance_agent.tools.registry import ToolDefinition, ToolGroup


async def _get_price_df(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """Helper to fetch price data as a DataFrame."""
    loop = asyncio.get_running_loop()
    def _fetch():
        t = yf.Ticker(ticker)
        df = t.history(period=period)
        if df.empty:
            raise ValueError(f"No price data for {ticker}")
        return df
    return await loop.run_in_executor(None, _fetch)


async def calculate_rsi(ticker: str, period: int = 14, lookback: str = "6mo") -> dict[str, Any]:
    """Calculate Relative Strength Index."""
    try:
        df = await _get_price_df(ticker, lookback)
        import pandas_ta as ta
        rsi = ta.rsi(df["Close"], length=period)
        if rsi is None or rsi.empty:
            return {"error": "calculation_failed", "message": "RSI calculation returned empty"}
        current = float(rsi.iloc[-1])
        signal = "oversold" if current < 30 else "overbought" if current > 70 else "neutral"
        return {
            "ticker": ticker,
            "indicator": f"RSI_{period}",
            "value": round(current, 2),
            "signal": signal,
            "history": [round(float(v), 2) for v in rsi.tail(10).tolist() if not np.isnan(v)],
        }
    except ImportError:
        return {"error": "dependency_missing", "message": "pandas-ta not installed"}
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def calculate_macd(
    ticker: str, fast: int = 12, slow: int = 26, signal_period: int = 9, lookback: str = "6mo"
) -> dict[str, Any]:
    """Calculate MACD line, signal line, histogram."""
    try:
        df = await _get_price_df(ticker, lookback)
        import pandas_ta as ta
        macd_df = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal_period)
        if macd_df is None or macd_df.empty:
            return {"error": "calculation_failed"}
        cols = macd_df.columns.tolist()
        macd_val = float(macd_df[cols[0]].iloc[-1])
        signal_val = float(macd_df[cols[1]].iloc[-1]) if len(cols) > 1 else 0
        hist_val = float(macd_df[cols[2]].iloc[-1]) if len(cols) > 2 else 0
        signal_text = "bullish" if macd_val > signal_val else "bearish"
        return {
            "ticker": ticker,
            "macd": round(macd_val, 4),
            "signal_line": round(signal_val, 4),
            "histogram": round(hist_val, 4),
            "signal": signal_text,
        }
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def get_bollinger_bands(
    ticker: str, period: int = 20, std_dev: float = 2.0, lookback: str = "6mo"
) -> dict[str, Any]:
    """Get Bollinger Bands."""
    try:
        df = await _get_price_df(ticker, lookback)
        import pandas_ta as ta
        bb = ta.bbands(df["Close"], length=period, std=std_dev)
        if bb is None or bb.empty:
            return {"error": "calculation_failed"}
        cols = bb.columns.tolist()
        current_price = float(df["Close"].iloc[-1])
        upper = float(bb[cols[0]].iloc[-1]) if len(cols) > 0 else 0
        mid = float(bb[cols[1]].iloc[-1]) if len(cols) > 1 else 0
        lower = float(bb[cols[2]].iloc[-1]) if len(cols) > 2 else 0
        position = "above_upper" if current_price > upper else "below_lower" if current_price < lower else "within_bands"
        return {
            "ticker": ticker,
            "upper": round(upper, 2),
            "middle": round(mid, 2),
            "lower": round(lower, 2),
            "current_price": round(current_price, 2),
            "position": position,
            "bandwidth_pct": round((upper - lower) / mid * 100, 2) if mid else 0,
        }
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def calculate_sma_ema(
    ticker: str, periods: str = "20,50,200", lookback: str = "2y"
) -> dict[str, Any]:
    """Calculate Simple and Exponential Moving Averages."""
    try:
        df = await _get_price_df(ticker, lookback)
        import pandas_ta as ta
        period_list = [int(p.strip()) for p in periods.split(",")]
        current_price = float(df["Close"].iloc[-1])
        results = {"ticker": ticker, "current_price": round(current_price, 2), "moving_averages": {}}
        for p in period_list:
            sma = ta.sma(df["Close"], length=p)
            ema = ta.ema(df["Close"], length=p)
            sma_val = float(sma.iloc[-1]) if sma is not None and not sma.empty else None
            ema_val = float(ema.iloc[-1]) if ema is not None and not ema.empty else None
            results["moving_averages"][f"SMA_{p}"] = round(sma_val, 2) if sma_val else None
            results["moving_averages"][f"EMA_{p}"] = round(ema_val, 2) if ema_val else None
        # Determine trend
        sma_50 = results["moving_averages"].get("SMA_50")
        sma_200 = results["moving_averages"].get("SMA_200")
        if sma_50 and sma_200:
            results["golden_cross"] = sma_50 > sma_200
            results["death_cross"] = sma_50 < sma_200
        return results
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def detect_patterns(ticker: str, lookback: str = "3mo") -> dict[str, Any]:
    """Detect candlestick patterns."""
    try:
        df = await _get_price_df(ticker, lookback)
        import pandas_ta as ta
        patterns_found = []
        # Check common patterns using pandas-ta
        for pattern_name in ["doji", "hammer", "engulfing", "morningstar", "eveningstar"]:
            try:
                result = getattr(ta, f"cdl_{pattern_name}", None)
                if result:
                    pat = result(df["Open"], df["High"], df["Low"], df["Close"])
                    if pat is not None and not pat.empty and pat.iloc[-1] != 0:
                        patterns_found.append({
                            "pattern": pattern_name,
                            "signal": "bullish" if pat.iloc[-1] > 0 else "bearish",
                        })
            except (AttributeError, Exception):
                continue
        return {"ticker": ticker, "patterns": patterns_found, "lookback": lookback}
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def get_support_resistance(ticker: str, lookback: str = "6mo") -> dict[str, Any]:
    """Calculate key support/resistance price levels."""
    try:
        df = await _get_price_df(ticker, lookback)
        closes = df["Close"].values
        highs = df["High"].values
        lows = df["Low"].values
        current = float(closes[-1])

        # Simple pivot points
        high = float(highs.max())
        low = float(lows.min())
        pivot = (high + low + current) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)

        return {
            "ticker": ticker,
            "current_price": round(current, 2),
            "pivot": round(pivot, 2),
            "resistance_1": round(r1, 2),
            "resistance_2": round(r2, 2),
            "support_1": round(s1, 2),
            "support_2": round(s2, 2),
            "period_high": round(high, 2),
            "period_low": round(low, 2),
        }
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def calculate_atr(ticker: str, period: int = 14, lookback: str = "3mo") -> dict[str, Any]:
    """Calculate Average True Range (volatility measure)."""
    try:
        df = await _get_price_df(ticker, lookback)
        import pandas_ta as ta
        atr = ta.atr(df["High"], df["Low"], df["Close"], length=period)
        if atr is None or atr.empty:
            return {"error": "calculation_failed"}
        current_atr = float(atr.iloc[-1])
        current_price = float(df["Close"].iloc[-1])
        return {
            "ticker": ticker,
            "atr": round(current_atr, 2),
            "atr_pct": round(current_atr / current_price * 100, 2),
            "current_price": round(current_price, 2),
            "period": period,
        }
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def get_fibonacci_levels(ticker: str, lookback: str = "6mo") -> dict[str, Any]:
    """Calculate Fibonacci retracement/extension levels."""
    try:
        df = await _get_price_df(ticker, lookback)
        high = float(df["High"].max())
        low = float(df["Low"].min())
        diff = high - low
        current = float(df["Close"].iloc[-1])
        ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        levels = {}
        for r in ratios:
            levels[f"{r:.1%}"] = round(high - diff * r, 2)
        # Extensions
        levels["1.272"] = round(high + diff * 0.272, 2)
        levels["1.618"] = round(high + diff * 0.618, 2)
        return {
            "ticker": ticker,
            "current_price": round(current, 2),
            "swing_high": round(high, 2),
            "swing_low": round(low, 2),
            "retracement_levels": levels,
        }
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


# --- Tool Group ---

technical_group = ToolGroup(
    name="technical",
    description="Technical analysis indicators, patterns, and levels",
    tools=[
        ToolDefinition(name="calculate_rsi", description="Calculate Relative Strength Index over configurable period",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "period": {"type": "integer", "default": 14}, "lookback": {"type": "string", "default": "6mo"}}, "required": ["ticker"]}, handler=calculate_rsi),
        ToolDefinition(name="calculate_macd", description="Calculate MACD line, signal line, histogram",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "fast": {"type": "integer", "default": 12}, "slow": {"type": "integer", "default": 26}, "signal_period": {"type": "integer", "default": 9}}, "required": ["ticker"]}, handler=calculate_macd),
        ToolDefinition(name="get_bollinger_bands", description="Get upper/middle/lower Bollinger Bands",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "period": {"type": "integer", "default": 20}, "std_dev": {"type": "number", "default": 2.0}}, "required": ["ticker"]}, handler=get_bollinger_bands),
        ToolDefinition(name="calculate_sma_ema", description="Calculate SMA and EMA for multiple periods",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "periods": {"type": "string", "default": "20,50,200"}}, "required": ["ticker"]}, handler=calculate_sma_ema),
        ToolDefinition(name="detect_patterns", description="Detect candlestick patterns (doji, hammer, engulfing, etc.)",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "lookback": {"type": "string", "default": "3mo"}}, "required": ["ticker"]}, handler=detect_patterns),
        ToolDefinition(name="get_support_resistance", description="Calculate key support/resistance levels using pivot points",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "lookback": {"type": "string", "default": "6mo"}}, "required": ["ticker"]}, handler=get_support_resistance),
        ToolDefinition(name="calculate_atr", description="Calculate Average True Range (volatility measure)",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "period": {"type": "integer", "default": 14}}, "required": ["ticker"]}, handler=calculate_atr),
        ToolDefinition(name="get_fibonacci_levels", description="Calculate Fibonacci retracement and extension levels",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "lookback": {"type": "string", "default": "6mo"}}, "required": ["ticker"]}, handler=get_fibonacci_levels),
    ],
)
