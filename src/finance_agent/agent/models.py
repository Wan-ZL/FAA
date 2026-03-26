"""Models for the multi-agent system.

Includes shared state board, findings, decisions, debate structures,
and agent lifecycle models.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# --- Enums ---

class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Signal(str, Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class AgentStatus(str, Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    RECLAIMED = "reclaimed"


class Priority(int, Enum):
    URGENT = 0
    NORMAL = 1
    BACKGROUND = 2


# --- Macro Report ---

class MacroIndicator(BaseModel):
    name: str
    value: float
    previous: float
    trend: str  # "rising", "falling", "stable"
    source: str
    retrieved_at: datetime


class MacroReport(BaseModel):
    indicators: list[MacroIndicator] = Field(default_factory=list)
    regime: str = ""  # "expansion", "contraction", "transition"
    regime_confidence: Confidence = Confidence.MEDIUM
    rate_environment: str = ""  # "tightening", "easing", "neutral"
    summary: str = ""
    impact_on_ticker: str = ""


# --- Technical Report ---

class TechnicalIndicatorResult(BaseModel):
    name: str
    value: float
    signal: Signal = Signal.HOLD
    timeframe: str = "1D"


class SupportResistance(BaseModel):
    level: float
    type: str  # "support" or "resistance"
    strength: int = 1  # 1-5


class TechnicalReport(BaseModel):
    ticker: str
    indicators: list[TechnicalIndicatorResult] = Field(default_factory=list)
    support_resistance: list[SupportResistance] = Field(default_factory=list)
    trend_direction: str = ""  # "bullish", "bearish", "sideways"
    pattern_detected: str | None = None
    signal: Signal = Signal.HOLD
    confidence: Confidence = Confidence.MEDIUM
    summary: str = ""


# --- Sentiment Report ---

class SentimentNewsItem(BaseModel):
    headline: str
    source: str
    published_at: datetime
    sentiment_score: float  # -1.0 to 1.0
    relevance_score: float = 0.0


class SentimentReport(BaseModel):
    ticker: str
    overall_sentiment: float = 0.0  # -1.0 to 1.0
    sentiment_label: str = ""  # "very_negative" to "very_positive"
    news_volume_zscore: float = 0.0
    top_stories: list[SentimentNewsItem] = Field(default_factory=list)
    finbert_score: float = 0.0
    social_buzz: str = "normal"  # "high", "normal", "low"
    summary: str = ""


# --- Fundamental Report ---

class FinancialMetric(BaseModel):
    name: str
    value: float
    sector_median: float = 0.0
    percentile: int = 50  # 0-100


class FundamentalReport(BaseModel):
    ticker: str
    metrics: list[FinancialMetric] = Field(default_factory=list)
    revenue_growth_yoy: float = 0.0
    earnings_surprise_last: float = 0.0
    debt_to_equity: float = 0.0
    free_cash_flow: float = 0.0
    moat_assessment: str = ""  # "wide", "narrow", "none"
    signal: Signal = Signal.HOLD
    confidence: Confidence = Confidence.MEDIUM
    summary: str = ""


# --- Risk Report ---

class RiskReport(BaseModel):
    ticker: str
    var_95_1d: float = 0.0
    var_99_1d: float = 0.0
    max_drawdown_1y: float = 0.0
    sharpe_ratio: float = 0.0
    beta: float = 0.0
    correlation_to_spy: float = 0.0
    monte_carlo_median_return_30d: float = 0.0
    monte_carlo_p5_return_30d: float = 0.0
    stress_scenarios: dict[str, float] = Field(default_factory=dict)
    risk_rating: str = ""  # "low", "moderate", "high", "extreme"
    summary: str = ""


# --- Shared State Board ---

class SharedStateBoard(BaseModel):
    """Central state that all agents read from and write to."""
    query_id: str = Field(default_factory=lambda: str(uuid4())[:8])
    ticker: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    macro_report: MacroReport | None = None
    technical_report: TechnicalReport | None = None
    sentiment_report: SentimentReport | None = None
    fundamental_report: FundamentalReport | None = None
    risk_report: RiskReport | None = None
    options_report: dict | None = None
    backtest_report: dict | None = None
    debate_log: list[str] = Field(default_factory=list)

    completed_slots: list[str] = Field(default_factory=list)


# --- Findings ---

class Finding(BaseModel):
    """A single discovery posted by an agent to the shared board."""
    id: str = Field(default_factory=lambda: f"f-{uuid4().hex[:4]}")
    agent_id: str
    category: str  # "market", "fundamental", "sentiment", "risk", "options", "macro"
    ticker: str | None = None
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.5  # 0.0 to 1.0
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)


# --- Decisions ---

class Decision(BaseModel):
    """An immutable record of a recommendation."""
    id: str = Field(default_factory=lambda: f"d-{uuid4().hex[:4]}")
    timestamp: datetime = Field(default_factory=datetime.now)
    query: str
    rationale: str
    supporting_findings: list[str] = Field(default_factory=list)
    dissenting_findings: list[str] = Field(default_factory=list)
    debate_summary: str | None = None
    recommendation: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.5


# --- Cache ---

class CacheEntry(BaseModel):
    """TTL-based cache entry for data deduplication."""
    key: str
    value: bytes
    created_at: datetime = Field(default_factory=datetime.now)
    ttl_seconds: int
    hit_count: int = 0


# --- Alerts ---

class Alert(BaseModel):
    """Real-time event for agent awareness."""
    id: str = Field(default_factory=lambda: f"a-{uuid4().hex[:4]}")
    timestamp: datetime = Field(default_factory=datetime.now)
    severity: str  # "info", "warning", "critical"
    category: str  # "price_move", "news_break", "volatility_spike", "data_stale"
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    ttl_seconds: int = 3600


# --- Debate ---

class DebateRound(BaseModel):
    """Structured wrapper around natural-language debate."""
    round_number: int
    bull_argument: str
    bear_argument: str
    key_data_cited: list[str] = Field(default_factory=list)


class DebateResult(BaseModel):
    """Outcome of a Bull/Bear debate."""
    rounds: list[DebateRound] = Field(default_factory=list)
    synthesis: str = ""
    signal: Signal = Signal.HOLD
    confidence: Confidence = Confidence.MEDIUM
    key_disagreements: list[str] = Field(default_factory=list)


# --- Task / Agent Config ---

class TeammateTask(BaseModel):
    """Task assignment for a teammate agent."""
    role: str
    model: str = "sonnet"  # "opus", "sonnet", "haiku"
    description: str
    tools: list[str] = Field(default_factory=list)
    budget_tokens: int = 8000
    timeout_seconds: int = 300
    priority: Priority = Priority.NORMAL


class AnalysisRequest(BaseModel):
    """Parsed user query."""
    raw_query: str
    ticker: str | None = None
    tickers: list[str] = Field(default_factory=list)
    asset_class: str = "equity"  # "equity", "options", "etf", "crypto", "forex", "macro"
    timeframe: str = ""  # "day_trade", "swing", "6_months", "1_year", "long_term"
    analysis_depth: str = "standard"  # "quick", "standard", "deep"
    risk_profile: str = "moderate"  # "aggressive", "moderate", "conservative"
    specific_focus: str = ""  # user's specific question/concern


# --- Token Budget ---

class TokenBudget(BaseModel):
    """Per-agent token budget with circuit breaker."""
    max_tokens: int
    hard_limit: int = 0  # set to 2x max_tokens
    used: int = 0

    def model_post_init(self, __context: Any) -> None:
        if self.hard_limit == 0:
            self.hard_limit = self.max_tokens * 2

    def consume(self, tokens: int) -> None:
        self.used += tokens
        if self.used >= self.hard_limit:
            raise RuntimeError(f"Hard limit reached: {self.used}/{self.hard_limit} tokens")

    def warn_if_near_limit(self) -> str | None:
        if self.used >= self.max_tokens * 0.8:
            return f"WARNING: {self.used}/{self.max_tokens} tokens used (80%+)"
        return None

    @property
    def remaining(self) -> int:
        return max(0, self.max_tokens - self.used)


# --- Risk Weights ---

RISK_WEIGHTS: dict[str, dict[str, float]] = {
    "aggressive": {"aggressive": 0.5, "neutral": 0.35, "conservative": 0.15},
    "moderate": {"aggressive": 0.2, "neutral": 0.5, "conservative": 0.3},
    "conservative": {"aggressive": 0.1, "neutral": 0.3, "conservative": 0.6},
}
