"""Risk and backtesting tools.

5 tools for VaR, Monte Carlo, stress testing, backtesting, and risk metrics.
"""

from __future__ import annotations

import asyncio
from typing import Any

import numpy as np
import yfinance as yf

from finance_agent.tools.registry import ToolDefinition, ToolGroup


async def _get_ticker_history(ticker: str, period: str = "1y") -> Any:
    """Async helper to fetch ticker history without blocking the event loop."""
    loop = asyncio.get_running_loop()
    def _fetch():
        t = yf.Ticker(ticker)
        return t.history(period=period)
    return await loop.run_in_executor(None, _fetch)


async def run_backtest(
    ticker: str, strategy: str = "buy_and_hold", period: str = "1y"
) -> dict[str, Any]:
    """Backtest a strategy over historical data."""
    try:
        hist = await _get_ticker_history(ticker, period)
        if hist.empty:
            return {"error": "no_data"}
        returns = hist["Close"].pct_change().dropna()
        cum_return = float((1 + returns).prod() - 1)
        ann_return = float((1 + cum_return) ** (252 / len(returns)) - 1) if len(returns) > 0 else 0
        ann_vol = float(returns.std() * np.sqrt(252))
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0
        max_dd = float((hist["Close"] / hist["Close"].cummax() - 1).min())
        win_rate = float((returns > 0).sum() / len(returns)) if len(returns) > 0 else 0
        return {
            "ticker": ticker,
            "strategy": strategy,
            "period": period,
            "total_return_pct": round(cum_return * 100, 2),
            "annualized_return_pct": round(ann_return * 100, 2),
            "annualized_volatility_pct": round(ann_vol * 100, 2),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown_pct": round(max_dd * 100, 2),
            "win_rate_pct": round(win_rate * 100, 1),
            "trading_days": len(returns),
        }
    except Exception as e:
        return {"error": "backtest_failed", "message": str(e)}


async def monte_carlo_sim(
    ticker: str, days: int = 30, simulations: int = 10000
) -> dict[str, Any]:
    """Run Monte Carlo simulation for portfolio outcomes."""
    try:
        hist = await _get_ticker_history(ticker, "1y")
        if hist.empty:
            return {"error": "no_data"}
        returns = hist["Close"].pct_change().dropna()
        mu = float(returns.mean())
        sigma = float(returns.std())
        current_price = float(hist["Close"].iloc[-1])

        # Run simulations
        rng = np.random.default_rng(42)
        sims = rng.normal(mu, sigma, (simulations, days))
        price_paths = current_price * np.exp(np.cumsum(sims, axis=1))
        final_prices = price_paths[:, -1]
        final_returns = (final_prices / current_price - 1) * 100

        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "simulation_days": days,
            "num_simulations": simulations,
            "median_price": round(float(np.median(final_prices)), 2),
            "median_return_pct": round(float(np.median(final_returns)), 2),
            "p5_price": round(float(np.percentile(final_prices, 5)), 2),
            "p5_return_pct": round(float(np.percentile(final_returns, 5)), 2),
            "p25_price": round(float(np.percentile(final_prices, 25)), 2),
            "p75_price": round(float(np.percentile(final_prices, 75)), 2),
            "p95_price": round(float(np.percentile(final_prices, 95)), 2),
            "p95_return_pct": round(float(np.percentile(final_returns, 95)), 2),
            "prob_positive_return_pct": round(float((final_returns > 0).mean() * 100), 1),
        }
    except Exception as e:
        return {"error": "simulation_failed", "message": str(e)}


async def calculate_var(
    ticker: str, confidence: float = 0.95, horizon_days: int = 1, method: str = "historical"
) -> dict[str, Any]:
    """Calculate Value at Risk."""
    try:
        hist = await _get_ticker_history(ticker, "1y")
        if hist.empty:
            return {"error": "no_data"}
        returns = hist["Close"].pct_change().dropna()
        current_price = float(hist["Close"].iloc[-1])

        if method == "historical":
            var_pct = float(np.percentile(returns, (1 - confidence) * 100))
        else:  # parametric
            mu = float(returns.mean())
            sigma = float(returns.std())
            from scipy import stats
            z = stats.norm.ppf(1 - confidence)
            var_pct = mu + z * sigma

        var_pct_scaled = var_pct * np.sqrt(horizon_days)
        var_dollar = current_price * abs(var_pct_scaled)

        return {
            "ticker": ticker,
            "confidence": confidence,
            "horizon_days": horizon_days,
            "method": method,
            "var_pct": round(float(var_pct_scaled) * 100, 3),
            "var_dollar_per_share": round(float(var_dollar), 2),
            "current_price": round(current_price, 2),
            "interpretation": f"With {confidence:.0%} confidence, {ticker} should not lose more than {abs(var_pct_scaled)*100:.2f}% (${var_dollar:.2f}/share) over {horizon_days} day(s)",
        }
    except ImportError:
        return {"error": "dependency_missing", "message": "scipy required for parametric VaR"}
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


async def stress_test(
    ticker: str,
    scenarios: str = "2008_crisis,covid_2020,rate_shock_2022"
) -> dict[str, Any]:
    """Apply historical stress scenarios to a position."""
    # Historical drawdowns for reference
    scenario_data = {
        "2008_crisis": {"sp500_drawdown": -56.8, "duration_months": 17, "description": "Global Financial Crisis"},
        "covid_2020": {"sp500_drawdown": -33.9, "duration_months": 1, "description": "COVID-19 pandemic crash"},
        "rate_shock_2022": {"sp500_drawdown": -25.4, "duration_months": 10, "description": "Fed rate hiking cycle"},
        "dot_com_2000": {"sp500_drawdown": -49.1, "duration_months": 30, "description": "Dot-com bubble burst"},
        "flash_crash_2010": {"sp500_drawdown": -9.2, "duration_months": 0.1, "description": "Flash crash"},
    }
    try:
        t = yf.Ticker(ticker)
        info = t.info
        beta = info.get("beta", 1.0) or 1.0
        current_price = info.get("regularMarketPrice") or info.get("previousClose", 0)

        scenario_list = [s.strip() for s in scenarios.split(",")]
        results = {}
        for name in scenario_list:
            s = scenario_data.get(name, {"sp500_drawdown": -20, "duration_months": 6, "description": name})
            estimated_impact = s["sp500_drawdown"] * beta
            estimated_price = current_price * (1 + estimated_impact / 100)
            results[name] = {
                "description": s["description"],
                "sp500_drawdown_pct": s["sp500_drawdown"],
                "estimated_impact_pct": round(estimated_impact, 1),
                "estimated_price": round(estimated_price, 2),
                "beta_used": round(beta, 2),
            }

        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "beta": round(beta, 2),
            "scenarios": results,
        }
    except Exception as e:
        return {"error": "stress_test_failed", "message": str(e)}


async def calculate_sharpe(ticker: str, period: str = "1y", risk_free_rate: float = 0.05) -> dict[str, Any]:
    """Calculate risk-adjusted return metrics."""
    try:
        hist = await _get_ticker_history(ticker, period)
        if hist.empty:
            return {"error": "no_data"}
        returns = hist["Close"].pct_change().dropna()
        ann_return = float((1 + returns.mean()) ** 252 - 1)
        ann_vol = float(returns.std() * np.sqrt(252))
        sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0
        neg_returns = returns[returns < 0]
        downside_vol = float(neg_returns.std() * np.sqrt(252)) if len(neg_returns) > 0 else 0
        sortino = (ann_return - risk_free_rate) / downside_vol if downside_vol > 0 else 0
        max_dd = float((hist["Close"] / hist["Close"].cummax() - 1).min())
        calmar = ann_return / abs(max_dd) if max_dd != 0 else 0
        return {
            "ticker": ticker,
            "period": period,
            "annualized_return_pct": round(ann_return * 100, 2),
            "annualized_volatility_pct": round(ann_vol * 100, 2),
            "sharpe_ratio": round(sharpe, 3),
            "sortino_ratio": round(sortino, 3),
            "max_drawdown_pct": round(max_dd * 100, 2),
            "calmar_ratio": round(calmar, 3),
            "risk_free_rate": risk_free_rate,
        }
    except Exception as e:
        return {"error": "calculation_failed", "message": str(e)}


# --- Tool Group ---

risk_backtest_group = ToolGroup(
    name="risk_backtest",
    description="Risk metrics, VaR, Monte Carlo, stress testing, backtesting",
    tools=[
        ToolDefinition(name="run_backtest", description="Backtest a strategy over historical data with performance metrics",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "strategy": {"type": "string", "default": "buy_and_hold"}, "period": {"type": "string", "default": "1y"}}, "required": ["ticker"]}, handler=run_backtest),
        ToolDefinition(name="monte_carlo_sim", description="Run Monte Carlo simulation (10K paths) for return distribution",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "days": {"type": "integer", "default": 30}, "simulations": {"type": "integer", "default": 10000}}, "required": ["ticker"]}, handler=monte_carlo_sim),
        ToolDefinition(name="calculate_var", description="Calculate Value at Risk (historical or parametric) at given confidence",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "confidence": {"type": "number", "default": 0.95}, "horizon_days": {"type": "integer", "default": 1}, "method": {"type": "string", "enum": ["historical", "parametric"], "default": "historical"}}, "required": ["ticker"]}, handler=calculate_var),
        ToolDefinition(name="stress_test", description="Apply historical stress scenarios (2008, COVID, rate shock) to a position",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "scenarios": {"type": "string", "default": "2008_crisis,covid_2020,rate_shock_2022"}}, "required": ["ticker"]}, handler=stress_test),
        ToolDefinition(name="calculate_sharpe", description="Calculate Sharpe, Sortino, Calmar ratios and max drawdown",
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}, "period": {"type": "string", "default": "1y"}, "risk_free_rate": {"type": "number", "default": 0.05}}, "required": ["ticker"]}, handler=calculate_sharpe),
    ],
)
