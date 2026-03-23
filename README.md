# FinSight

> Multi-agent AI engine that turns 15+ financial data sources into unified, actionable investment intelligence.

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. System Architecture](#2-system-architecture)
- [3. Agent System Design](#3-agent-system-design)
- [4. Data Layer Design](#4-data-layer-design)
- [5. Memory and Storage](#5-memory-and-storage)
- [6. Tool System Design](#6-tool-system-design)
- [7. Implementation Roadmap](#7-implementation-roadmap)

---

## 1. Project Overview

### 1.1 Project Name and Tagline

# **FinSight**

> *Multi-agent AI engine that turns 15+ financial data sources into unified, actionable investment intelligence.*

### 1.2 What is This?

FinSight is a multi-agent AI system purpose-built for financial analysis and investment recommendations. It orchestrates a team of specialist AI agents — each with deep expertise in a specific domain such as macroeconomics, technical analysis, fundamentals, options pricing, or sentiment — to produce comprehensive research that no single model or analyst could deliver alone. FinSight is a pure analysis and recommendation engine; it never executes trades.

A human analyst interacts with FinSight through a CLI interface by posing questions or requesting analysis. The **Team Leader** agent receives the request, decomposes it into sub-tasks, and spawns the appropriate specialist teammates. Each specialist independently gathers data, runs its analysis, and returns structured findings. The Team Leader then synthesizes these into a coherent, multi-perspective recommendation — surfacing agreements, conflicts, and confidence levels across disciplines.

FinSight covers the full spectrum of investment analysis: macro regime detection, cross-market correlation, equity and ETF technicals, fundamental valuation, options flow and Greeks, news and social sentiment, quantitative risk metrics, and historical backtesting. By fusing these perspectives in a single collaborative loop, it delivers the kind of cross-disciplinary reasoning that typically requires an entire research desk.

### 1.3 Key Capabilities

| # | Capability | Description |
|---|-----------|-------------|
| 1 | **Macro Regime Analysis** | Identifies current economic regime (expansion, contraction, stagflation) using Fed data, yield curves, and leading indicators to frame all downstream analysis |
| 2 | **Cross-Market Correlation** | Detects relationships across equities, bonds, commodities, and currencies — flags divergences that signal regime shifts or dislocations |
| 3 | **Technical Analysis** | Multi-timeframe chart pattern recognition, support/resistance levels, momentum indicators, and volume profile analysis |
| 4 | **Fundamental Valuation** | DCF modeling, comparable analysis, earnings quality scoring, and balance sheet health assessment using SEC filings and financial APIs |
| 5 | **Options Flow & Strategy** | Analyzes unusual options activity, computes Greeks, evaluates implied volatility surfaces, and recommends hedging or directional strategies |
| 6 | **Sentiment Analysis** | Aggregates and scores sentiment from news, earnings calls, social media, and analyst reports with source credibility weighting |
| 7 | **Risk Quantification** | Calculates VaR, CVaR, maximum drawdown, correlation risk, and tail-event probabilities for positions and portfolios |
| 8 | **Historical Backtesting** | Tests proposed strategies against historical data with realistic assumptions for slippage, fees, and market impact |
| 9 | **Multi-Agent Debate** | Specialist agents challenge each other's conclusions through structured debate, surfacing blind spots and strengthening final recommendations |
| 10 | **Unified Data Fusion** | Ingests 15+ data sources (market data, SEC filings, Fed economic data, news, social, options chains, etc.) into a single analytical pipeline |

### 1.4 Differentiation from Existing Projects

| Feature | **FinSight** | TradingAgents | FinRobot | OpenBB | FinRL |
|---------|:---:|:---:|:---:|:---:|:---:|
| Multi-agent collaborative analysis | Yes | Yes | Partial | No | No |
| 15+ unified data sources | Yes | No | Partial | Yes | Partial |
| Options flow & Greeks analysis | Yes | No | No | Partial | No |
| Macro cross-market reasoning | Yes | No | No | Partial | No |
| Integrated backtesting engine | Yes | No | No | Partial | Yes |
| Risk quantification (VaR/CVaR) | Yes | No | No | Partial | Yes |
| Structured inter-agent debate | Yes | Yes | No | No | No |
| MCP-standardized tool integration | Yes | No | No | No | No |
| Cost-aware multi-tier LLM routing | Yes | No | No | N/A | N/A |
| Pure analysis (no trade execution) | Yes | No | Yes | Yes | No |
| CLI-first professional interface | Yes | No | Partial | Yes | No |

### 1.5 Design Philosophy

- **Simple agent loop over complex frameworks.** Inspired by the architecture behind Claude Code, each agent runs a straightforward prompt-tool-response loop rather than relying on heavyweight orchestration frameworks. This keeps the system debuggable, auditable, and easy to extend — complexity lives in the prompts and tools, not in the plumbing.

- **Hybrid communication: structured data for reports, natural language for debate.** Agents return analysis results as structured objects (JSON with typed fields) so downstream consumers can parse them reliably. But when agents challenge each other's conclusions during the debate phase, they communicate in natural language — because nuanced disagreement resists rigid schemas.

- **All agents are equals.** Every specialist agent has access to the full tool suite. There are no artificial permission boundaries — the Team Leader coordinates through task assignment, not access control. This avoids the brittleness of capability hierarchies and lets any agent pull the data it needs to do its job.

- **Start with vector RAG, add knowledge graphs when needed.** The retrieval layer begins with vector-based semantic search over documents and filings. Knowledge graphs (for entity relationships, ownership chains, sector mappings) are introduced incrementally where they demonstrably improve answer quality — not as an upfront architectural commitment.

- **MCP for tool integration standardization.** All external data sources and APIs are wrapped as Model Context Protocol (MCP) servers. This provides a uniform interface for tool discovery, invocation, and schema validation — making it straightforward to add new data sources without touching agent code.

- **Cost-aware multi-tier LLM strategy.** Not every sub-task requires the most capable model. FinSight routes work across model tiers (Opus for synthesis and complex reasoning, Sonnet for analysis and data interpretation, Haiku for extraction and formatting) to keep per-query costs manageable without sacrificing quality where it matters.

---

## 2. System Architecture

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INTERFACE LAYER                              │
│                                                                     │
│   ┌───────────┐   ┌──────────────┐   ┌──────────────────────────┐  │
│   │  Rich CLI  │   │ Session Mgr  │   │  Output Formatter        │  │
│   │  (Textual) │   │              │   │  (Markdown / Tables)     │  │
│   └─────┬─────┘   └──────┬───────┘   └────────────┬─────────────┘  │
│         │                │                         │                │
└─────────┼────────────────┼─────────────────────────┼────────────────┘
          │                │                         │
          ▼                ▼                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION LAYER                             │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                      TEAM LEADER (Opus)                      │  │
│   │          Task Decomposition · Agent Spawning · Synthesis     │  │
│   └──────┬──────────┬──────────┬──────────┬──────────┬───────┘     │
│          │          │          │          │          │              │
│          ▼          ▼          ▼          ▼          ▼              │
│   ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐   │
│   │  Macro   ││Technical ││Fundament.││ Options  ││Sentiment │   │
│   │ Analyst  ││ Analyst  ││ Analyst  ││Strategist││ Analyst  │   │
│   │ (Sonnet) ││ (Sonnet) ││ (Sonnet) ││ (Sonnet) ││ (Haiku)  │   │
│   └────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘   │
│        │           │           │           │           │           │
│        └─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┘           │
│              ▼           ▼           ▼           ▼                  │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                 SHARED STATE BOARD (SQLite)                   │  │
│   │     Findings · Decisions · Data Cache · Alerts               │  │
│   └──────────────────────────┬───────────────────────────────────┘  │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                   │
│                                                                     │
│   ┌───────────────────┐   ┌──────────────────────────────────────┐  │
│   │ Provider Registry │   │        TET Pipeline                  │  │
│   │                   │   │  Transform → Enrich → Tag            │  │
│   │  Yahoo Finance    │   │                                      │  │
│   │  Alpha Vantage    │   │  ┌─────────┐ ┌───────┐ ┌─────────┐  │  │
│   │  FRED API         │   │  │ Raw JSON│→│Pydantic│→│Enriched │  │  │
│   │  SEC EDGAR        │   │  │  / CSV  │ │ Model │ │+ Tagged │  │  │
│   │  News APIs        │   │  └─────────┘ └───────┘ └─────────┘  │  │
│   │  Options Data     │   │                                      │  │
│   │  Social APIs      │   └──────────────────────────────────────┘  │
│   │  ... (15+ total)  │                                             │
│   └───────────────────┘   ┌──────────────────────────────────────┐  │
│                           │       Hybrid Storage                 │  │
│                           │  SQLite · ChromaDB · NetworkX        │  │
│                           └──────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 The 8 Pillars

Every design decision in FinSight maps back to one of these eight architectural pillars:

| # | Pillar | Role in FinSight |
|---|--------|-----------------|
| 1 | **Agents** | Specialist AI agents (Team Leader + 7 teammates), each running a simple prompt-tool-response loop via the Anthropic SDK |
| 2 | **Tools** | 43+ tools exposed via MCP servers — market data fetchers, calculators, search, file I/O, charting |
| 3 | **Handoffs** | Team Leader decomposes tasks and delegates to specialists; results flow back for synthesis |
| 4 | **Patterns** | Hub-and-spoke for task distribution; shared state board for coordination; direct messaging for debate rounds |
| 5 | **Turns** | Each agent turn = one LLM call + zero or more tool calls; Team Leader manages the overall conversation turn budget |
| 6 | **Tracing** | Structured logging of every agent action, tool call, and decision for auditability and debugging |
| 7 | **Memory** | Per-agent scratchpad (ephemeral) + team shared board (SQLite) + knowledge graph (persistent cross-session) |
| 8 | **HITL** | Human-in-the-loop checkpoints — the analyst can approve, redirect, or refine at key decision points |

### 2.3 Layer Details

#### Interface Layer

The interface layer is a terminal-based CLI built with **Rich** (for tables, panels, progress bars, and Markdown rendering) and **Textual** (for interactive TUI elements when needed). It handles:

- **Session management**: Maintains conversation history, supports save/restore of analysis sessions
- **Input parsing**: Recognizes asset tickers, analysis commands, and natural language queries
- **Output formatting**: Renders agent findings as structured tables, Markdown reports, and inline charts (via `plotext` for terminal-native plotting)
- **HITL prompts**: Surfaces decision points where the analyst can approve, modify, or reject agent recommendations before they influence downstream analysis

#### Orchestration Layer

The orchestration layer is where the multi-agent system lives. It consists of:

- **Team Leader (Opus)**: The persistent, long-running agent that receives user requests, decomposes them into sub-tasks, assigns work to specialists, manages the debate process, and synthesizes final recommendations. Runs on Claude Opus for maximum reasoning capability.
- **Specialist teammates (Sonnet/Haiku)**: Spawned on demand by the Team Leader. Each runs an independent agent loop, calls tools to gather and analyze data, and writes structured findings to the shared state board. Most run on Claude Sonnet; extraction-heavy tasks use Haiku for cost efficiency.
- **Shared State Board (SQLite)**: The coordination backbone. Agents read each other's findings, post alerts, and log decisions here. SQLite with WAL mode provides concurrent read access with serialized writes — sufficient for the concurrency level of a single-user analytical system.

#### Data Layer

The data layer provides all external data through a uniform interface:

- **Provider Registry**: A registry of `BaseFetcher` implementations, one per data source. Each fetcher handles authentication, rate limiting, pagination, and error recovery for its API. The registry provides `get(source, params)` as the single entry point.
- **TET Pipeline** (Transform → Enrich → Tag): Raw API responses are transformed into standardized Pydantic models, enriched with derived fields (e.g., moving averages computed from raw prices), and tagged with metadata (source, timestamp, reliability score). This ensures every piece of data in the system has a known shape and provenance.
- **Hybrid Storage**: SQLite for structured data and session state, ChromaDB for vector embeddings (document search, semantic retrieval), NetworkX for in-memory knowledge graph operations (entity relationships, sector mappings).

### 2.4 Request Lifecycle

A typical analysis request flows through 10 steps:

```
 User Query                                            Final Report
    │                                                       ▲
    ▼                                                       │
 ┌──────┐  ┌──────┐  ┌───────┐  ┌──────┐  ┌───────┐  ┌────────┐
 │  1   │→ │  2   │→ │  3    │→ │  4   │→ │  5    │→ │   6    │
 │Parse │  │Route │  │Decomp.│  │Spawn │  │Execute│  │Collect │
 │Input │  │to TL │  │Tasks  │  │Agents│  │Parallel│ │Findings│
 └──────┘  └──────┘  └───────┘  └──────┘  └───────┘  └────────┘
                                                          │
                                                          ▼
                                            ┌──────┐  ┌───────┐
                                            │  8   │← │  7    │
                                            │Synth.│  │Debate │
                                            │Report│  │Rounds │
                                            └──┬───┘  └───────┘
                                               │
                                          ┌────▼───┐  ┌───────┐
                                          │   9    │→ │  10   │
                                          │  HITL  │  │Deliver│
                                          │Review  │  │Output │
                                          └────────┘  └───────┘
```

| Step | Name | Description |
|------|------|-------------|
| 1 | **Parse Input** | CLI parses the user query, extracts tickers, timeframes, and intent |
| 2 | **Route to Team Leader** | The parsed request is sent to the Team Leader agent |
| 3 | **Decompose Tasks** | Team Leader breaks the request into sub-tasks for specialist agents |
| 4 | **Spawn Agents** | Specialist agents are spawned from the AgentPool with appropriate model tier and tools |
| 5 | **Execute in Parallel** | Each specialist independently fetches data and runs analysis (up to 6 concurrent agents) |
| 6 | **Collect Findings** | Structured findings are written to the Shared State Board as they complete |
| 7 | **Debate Rounds** | Bull/Bear agents debate the investment thesis (3 rounds); Risk agents discuss position sizing |
| 8 | **Synthesize Report** | Team Leader reads all findings and debate transcripts, produces a unified recommendation |
| 9 | **HITL Review** | The analyst reviews the recommendation; can approve, request deeper analysis, or override |
| 10 | **Deliver Output** | Final report is rendered as Markdown tables, charts, and narrative in the CLI |

### 2.5 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.12+ | Primary implementation language |
| LLM SDK | `anthropic` SDK | Direct API access to Claude models (Opus, Sonnet, Haiku) |
| CLI Framework | Rich + Textual | Terminal UI rendering, tables, progress, interactive elements |
| Data Validation | Pydantic v2 | Typed data models for all API responses and inter-agent messages |
| Database | SQLite (WAL mode) | Shared state board, session persistence, data cache |
| Vector Store | ChromaDB | Semantic search over documents, filings, and research notes |
| Knowledge Graph | NetworkX | In-memory entity relationship graph with persistence via JSON serialization |
| HTTP Client | `httpx` | Async HTTP for all API calls with connection pooling |
| Tool Protocol | MCP (Model Context Protocol) | Standardized tool exposure and discovery |
| Configuration | TOML | Human-readable config files for API keys, model routing, and agent parameters |
| Testing | pytest + pytest-asyncio | Unit and integration testing with async support |
| Terminal Charts | plotext | Terminal-native plotting for price charts and indicators |
| Task Runner | `asyncio` | Concurrent agent execution and parallel data fetching |

---

## 3. Agent System Design

### 3.1 Agent Loop

Every agent in FinSight — from the Team Leader to the most lightweight specialist — runs the same core loop. This uniformity is intentional: it keeps the system simple, debuggable, and easy to extend.

```python
async def agent_loop(agent: Agent) -> AgentResult:
    """Core agent loop — shared by all agents."""
    messages = [{"role": "user", "content": agent.task_prompt}]

    while True:
        # 1. Call the LLM
        response = await anthropic_client.messages.create(
            model=agent.model,           # opus / sonnet / haiku
            max_tokens=agent.max_tokens,
            system=agent.system_prompt,
            tools=agent.tools,
            messages=messages,
        )

        # 2. Check stop conditions
        if response.stop_reason == "end_turn":
            return AgentResult(
                agent_id=agent.id,
                content=response.content,
                tool_calls=agent.tool_history,
            )

        # 3. Handle tool calls
        tool_results = []
        for tool_use in response.tool_use_blocks:
            result = await agent.execute_tool(
                name=tool_use.name,
                input=tool_use.input,
            )
            tool_results.append(result)
            agent.tool_history.append((tool_use, result))

        # 4. Append assistant response and tool results
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        # 5. Check budget limits
        if agent.over_budget():
            return AgentResult(
                agent_id=agent.id,
                content=agent.summarize_progress(),
                truncated=True,
            )
```

### 3.2 Team Leader

The Team Leader is the only persistent agent in the system. It runs on **Claude Opus** for maximum reasoning capability and manages the entire lifecycle of an analysis request.

**Responsibilities:**
- Parse the user's intent and determine which specialist agents are needed
- Decompose complex queries into discrete, parallelizable sub-tasks
- Assign sub-tasks to specialist agents with clear instructions and constraints
- Monitor progress via the Shared State Board
- Orchestrate the debate phase (Bull vs Bear, Risk Discussion)
- Synthesize all findings into a coherent, multi-perspective recommendation
- Manage the conversation turn budget across all agents

**System prompt includes:**
- Full knowledge of all available specialist agents and their capabilities
- Decision framework for task decomposition (when to parallelize vs. sequence)
- Synthesis guidelines (how to weight conflicting signals, confidence scoring)
- Cost-awareness rules (when to use Opus vs. Sonnet vs. Haiku for sub-tasks)

### 3.3 Specialist Teammates

| Agent | Model | Primary Role | Key Tools |
|-------|-------|-------------|-----------|
| **Macro Analyst** | Sonnet | Economic regime detection, yield curve analysis, cross-market correlation | `fred_fetch`, `treasury_yields`, `economic_calendar`, `correlation_matrix` |
| **Technical Analyst** | Sonnet | Chart patterns, support/resistance, momentum indicators, volume analysis | `price_history`, `compute_indicators`, `detect_patterns`, `plot_chart` |
| **Fundamental Analyst** | Sonnet | DCF valuation, comparable analysis, earnings quality, balance sheet health | `sec_filings`, `financial_statements`, `dcf_model`, `peer_comparison` |
| **Options Strategist** | Sonnet | Options flow analysis, Greeks computation, IV surface modeling, strategy recs | `options_chain`, `compute_greeks`, `iv_surface`, `strategy_payoff` |
| **Risk Assessor** | Sonnet | VaR/CVaR calculation, drawdown analysis, correlation risk, tail events | `var_calculation`, `monte_carlo`, `stress_test`, `correlation_risk` |
| **Sentiment Analyst** | Haiku | News aggregation, social sentiment scoring, earnings call analysis | `news_search`, `social_sentiment`, `earnings_transcripts`, `credibility_score` |
| **Backtest Runner** | Sonnet | Historical strategy testing, performance metrics, regime-conditional analysis | `backtest_strategy`, `performance_metrics`, `regime_filter`, `plot_equity_curve` |

### 3.4 Communication Patterns

FinSight uses three distinct communication patterns, each suited to a different coordination need:

#### Hub-and-Spoke (Task Distribution)

```
                    ┌──────────┐
           ┌───────→│  Macro   │
           │        └──────────┘
           │        ┌──────────┐
           ├───────→│Technical │
           │        └──────────┘
┌──────────┤        ┌──────────┐
│  Team    ├───────→│Fundament.│
│  Leader  │        └──────────┘
└──────────┤        ┌──────────┐
           ├───────→│ Options  │
           │        └──────────┘
           │        ┌──────────┐
           └───────→│Sentiment │
                    └──────────┘
```

The Team Leader assigns tasks and collects results. Specialists do not communicate with each other during this phase — they work independently and write findings to the Shared State Board.

#### Shared State Board (Coordination)

All agents read from and write to a shared SQLite database. This provides loose coupling: agents do not need to know about each other, they just read the board for relevant findings.

```
Agent A writes → [Findings Board] ← Agent B reads
Agent C writes → [Alert Board]    ← Team Leader reads
Team Leader  → [Decision Log]    ← All agents read
```

#### Direct Messages (Debate)

During debate rounds, agents communicate directly through structured message passing. This is the only time agents interact with each other outside the Shared State Board.

### 3.5 Debate Mechanism

The debate mechanism is FinSight's most distinctive coordination pattern. It ensures that investment recommendations are stress-tested from multiple perspectives before being delivered to the analyst.

#### Phase 1: Bull vs Bear Debate (3 rounds)

```
Round 1:  Bull Agent presents thesis  →  Bear Agent presents counter-thesis
Round 2:  Bull responds to Bear       →  Bear responds to Bull
Round 3:  Bull final argument         →  Bear final argument
          ↓
    Research Manager reads both transcripts
          ↓
    Synthesis: Agreed points, unresolved conflicts, confidence assessment
```

- **Bull Agent**: Constructed from agents whose findings support the position (e.g., bullish technicals + positive sentiment)
- **Bear Agent**: Constructed from agents whose findings oppose the position (e.g., deteriorating fundamentals + macro headwinds)
- **Research Manager** (Team Leader role): Reads the full debate transcript and produces a synthesis that identifies areas of agreement, unresolved conflicts, and an overall confidence score

#### Phase 2: Risk Discussion (3 perspectives)

```
Aggressive Perspective → "Here's why the reward justifies the risk"
Neutral Perspective    → "Here's the balanced position sizing"
Conservative Perspective → "Here's what could go wrong and how to hedge"
          ↓
    Risk Judge synthesizes into final position recommendation
```

- Each perspective agent has access to the Bull/Bear debate transcript and all specialist findings
- The Risk Judge (Team Leader role) produces the final position sizing and risk management recommendation

### 3.6 Agent Lifecycle Management

#### AgentPool

```python
class AgentPool:
    """Manages agent lifecycle, concurrency, and resource budgets."""

    MAX_CONCURRENT = 6          # Max parallel agents
    TOKEN_BUDGET_PER_AGENT = {
        "opus":   200_000,      # Team Leader
        "sonnet": 100_000,      # Analyst agents
        "haiku":   30_000,      # Extraction agents
    }

    def __init__(self):
        self.active: dict[str, Agent] = {}
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

    async def spawn(self, agent_config: AgentConfig) -> Agent:
        """Spawn a new agent, respecting concurrency limits."""
        async with self.semaphore:
            agent = Agent(**agent_config)
            self.active[agent.id] = agent
            try:
                result = await agent_loop(agent)
                return result
            finally:
                del self.active[agent.id]

    async def shutdown(self, timeout: float = 30.0):
        """Graceful shutdown — let running agents finish, then cancel."""
        for agent in self.active.values():
            agent.request_stop()
        # Wait up to timeout for agents to finish gracefully
        await asyncio.wait_for(
            asyncio.gather(*[a.wait() for a in self.active.values()]),
            timeout=timeout,
        )
```

**Key design decisions:**
- **Max 6 concurrent agents**: Balances parallelism against API rate limits and cost. Most analysis requests need 3-5 specialists.
- **Priority queue**: Urgent agents (e.g., risk assessment when a position alert fires) can jump the queue ahead of background research.
- **Token budgets**: Each agent has a per-model token budget. If an agent exceeds its budget, it is asked to summarize its progress and terminate — preventing runaway costs.
- **Graceful shutdown**: On user interrupt (Ctrl+C), running agents are asked to stop. They have 30 seconds to produce a partial summary before being cancelled.

---

## 4. Data Layer Design

### 4.1 TET Pipeline (Transform → Enrich → Tag)

Every piece of external data that enters FinSight passes through the TET pipeline. This guarantees that all data — regardless of source — arrives at agents in a consistent, typed, and annotated form.

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Raw API     │     │  Transform   │     │   Enrich     │     │    Tag       │
│  Response    │────→│              │────→│              │────→│              │
│  (JSON/CSV)  │     │  Parse into  │     │  Compute     │     │  Add source, │
│              │     │  Pydantic    │     │  derived     │     │  timestamp,  │
│              │     │  model       │     │  fields      │     │  reliability │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

| Stage | What Happens | Example |
|-------|-------------|---------|
| **Transform** | Raw API response is parsed into a typed Pydantic model. Missing fields get defaults, unexpected fields are dropped. | Yahoo Finance JSON → `PriceData` model with OHLCV fields |
| **Enrich** | Derived fields are computed from the base data. These are fields that agents frequently need but APIs do not provide directly. | Raw prices → add `sma_20`, `sma_50`, `rsi_14`, `atr_14` fields |
| **Tag** | Metadata is attached: data source, fetch timestamp, staleness threshold, reliability score (based on source track record). | Tag with `source="yahoo"`, `fetched_at=2026-03-23T10:00Z`, `reliability=0.95` |

### 4.2 Provider Registry

The Provider Registry is a centralized catalog of all data sources. It provides a single entry point (`get`) that agents use to request data without knowing the specifics of any API.

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class BaseFetcher(ABC):
    """Base class for all data source fetchers."""

    source_name: str
    rate_limit: float          # requests per second
    requires_api_key: bool

    @abstractmethod
    async def fetch(self, params: dict) -> BaseModel:
        """Fetch data and return a typed Pydantic model."""
        ...

    async def fetch_with_retry(self, params: dict, max_retries: int = 3) -> BaseModel:
        """Fetch with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                return await self.fetch(params)
            except RateLimitError:
                await asyncio.sleep(2 ** attempt)
            except APIError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)


class ProviderRegistry:
    """Registry of all data providers with unified access."""

    def __init__(self):
        self._providers: dict[str, BaseFetcher] = {}

    def register(self, fetcher: BaseFetcher):
        self._providers[fetcher.source_name] = fetcher

    async def get(self, source: str, params: dict) -> BaseModel:
        """Unified data access — the only method agents call."""
        fetcher = self._providers[source]
        raw = await fetcher.fetch_with_retry(params)
        transformed = self._transform(raw, fetcher.source_name)
        enriched = self._enrich(transformed)
        tagged = self._tag(enriched, fetcher.source_name)
        return tagged

    def available_sources(self) -> list[str]:
        return list(self._providers.keys())
```

### 4.3 Standard Data Models

All data flowing through FinSight conforms to one of these eight Pydantic models:

| Model | Key Fields | Used By |
|-------|-----------|---------|
| **PriceData** | `ticker`, `timeframe`, `ohlcv[]`, `adjusted_close`, `volume_profile` | Technical Analyst, Backtest Runner |
| **FundamentalsData** | `ticker`, `income_statement`, `balance_sheet`, `cash_flow`, `ratios`, `earnings_history` | Fundamental Analyst |
| **OptionsChain** | `ticker`, `expiration`, `strikes[]`, `calls[]`, `puts[]`, `iv_surface`, `open_interest` | Options Strategist |
| **MacroIndicator** | `indicator_id`, `name`, `series[]`, `frequency`, `seasonal_adjustment`, `latest_value` | Macro Analyst |
| **NewsEvent** | `headline`, `source`, `published_at`, `tickers[]`, `sentiment_score`, `credibility` | Sentiment Analyst |
| **TechnicalIndicators** | `ticker`, `timeframe`, `sma`, `ema`, `rsi`, `macd`, `bollinger`, `atr`, `volume_sma` | Technical Analyst |
| **SentimentScore** | `ticker`, `source_type`, `score`, `magnitude`, `sample_size`, `time_decay_weight` | Sentiment Analyst |
| **BacktestResult** | `strategy_name`, `period`, `total_return`, `sharpe`, `max_drawdown`, `win_rate`, `trades[]` | Backtest Runner |

### 4.4 Data Sources

| # | Source | API | Data Type | API Key Required |
|---|--------|-----|-----------|:---:|
| 1 | Yahoo Finance | `yfinance` | Prices, fundamentals, options chains | No |
| 2 | Alpha Vantage | REST | Prices, technicals, fundamentals, forex, crypto | Yes |
| 3 | FRED | REST | Macroeconomic indicators (GDP, CPI, rates, employment) | Yes (free) |
| 4 | SEC EDGAR | REST | 10-K, 10-Q, 8-K filings, insider transactions | No |
| 5 | Polygon.io | REST/WebSocket | Real-time and historical prices, options, trades | Yes |
| 6 | CBOE | REST | VIX, options volume, put/call ratios | No |
| 7 | Treasury.gov | REST | Yield curve data, auction results | No |
| 8 | News API | REST | Financial news aggregation | Yes |
| 9 | Finnhub | REST/WebSocket | News, sentiment, earnings calendar, filings | Yes (free tier) |
| 10 | Reddit (PRAW) | REST | r/wallstreetbets, r/investing sentiment | Yes (free) |
| 11 | Unusual Whales | REST | Options flow, dark pool data, congressional trades | Yes |
| 12 | Quandl/Nasdaq | REST | Alternative data, economic indicators | Yes |
| 13 | OpenBB Platform | Python SDK | Aggregated financial data from multiple providers | Depends on provider |
| 14 | Tavily | REST | AI-powered web search for financial research | Yes |
| 15 | Financial Modeling Prep | REST | Fundamentals, DCF, analyst estimates, earnings transcripts | Yes |

### 4.5 MCP Tool Exposure

Every data source is wrapped as an MCP tool with a consistent naming convention:

```
{source}_{action}

Examples:
  yahoo_price_history     → Fetch OHLCV price data from Yahoo Finance
  fred_fetch              → Fetch economic indicator series from FRED
  sec_filing              → Retrieve SEC filing by accession number
  polygon_options_chain   → Fetch options chain from Polygon.io
  news_search             → Search financial news across providers
```

Each MCP tool has:
- **Typed input schema**: Pydantic model defining required and optional parameters
- **Typed output schema**: One of the 8 standard data models
- **Description**: Human-readable description that the LLM uses to decide when to call it
- **Rate limit metadata**: So the agent loop can throttle calls appropriately

### 4.6 Data Flow

```
User asks: "Analyze NVDA for a 6-month hold"
                    │
                    ▼
           Team Leader decomposes:
           ├── Macro Analyst  → fred_fetch, treasury_yields, correlation_matrix
           ├── Technical      → yahoo_price_history, compute_indicators, detect_patterns
           ├── Fundamental    → sec_filings, financial_statements, dcf_model
           ├── Options        → polygon_options_chain, compute_greeks, iv_surface
           ├── Sentiment      → news_search, social_sentiment, earnings_transcripts
           └── Risk           → var_calculation, monte_carlo, stress_test
                    │
                    ▼  (all pass through TET pipeline)
                    │
           ┌───────────────────┐
           │ Shared State Board│
           │                   │
           │ Findings:         │
           │  macro_regime: "late_expansion"
           │  technical_bias: "bullish"
           │  valuation: "fair_to_overvalued"
           │  options_flow: "institutional_accumulation"
           │  sentiment: "positive_0.72"
           │  var_95: "-12.3%"
           └───────────────────┘
                    │
                    ▼
           Debate → Synthesis → Report
```

---

## 5. Memory and Storage

### 5.1 Storage Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     MEMORY ARCHITECTURE                        │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Per-Agent Scratchpad (Ephemeral)             │  │
│  │  In-memory dict, lives only for the duration of agent    │  │
│  │  execution. Used for intermediate calculations.          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          Team Shared Board (SQLite WAL — Session)        │  │
│  │                                                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│  │  │  Findings   │  │  Decision   │  │  Data Cache  │     │  │
│  │  │  Board      │  │  Log        │  │              │     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│  │  ┌─────────────┐                                        │  │
│  │  │  Alert      │                                        │  │
│  │  │  Board      │                                        │  │
│  │  └─────────────┘                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Persistent Storage (Cross-Session)               │  │
│  │                                                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│  │  │  ChromaDB   │  │  Knowledge  │  │  Session     │     │  │
│  │  │  (Vectors)  │  │  Graph (NX) │  │  Archive     │     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 5.2 What Goes Where

| Data Type | Storage | Lifetime | Access Pattern |
|-----------|---------|----------|---------------|
| Intermediate calculations | Per-agent scratchpad (dict) | Agent execution | Single agent, read/write |
| Agent findings | Shared Board — Findings table | Session | All agents, write-once read-many |
| Debate transcripts | Shared Board — Decision Log | Session | Team Leader reads, debate agents write |
| API response cache | Shared Board — Data Cache | TTL-based (minutes to hours) | All agents, read-heavy |
| Threshold breach alerts | Shared Board — Alert Board | Session | All agents write, Team Leader reads |
| Document embeddings | ChromaDB | Persistent | Semantic search queries |
| Entity relationships | Knowledge Graph (NetworkX) | Persistent | Graph traversal queries |
| Past analysis sessions | Session Archive (SQLite) | Persistent | Historical lookup |

### 5.3 Per-Agent Scratchpad

Each agent maintains a simple in-memory dictionary during its execution. This is for intermediate calculations that have no value to other agents or to persistence.

```python
class AgentScratchpad:
    """Ephemeral per-agent working memory."""

    def __init__(self):
        self._data: dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def clear(self):
        self._data.clear()
```

Examples of scratchpad use:
- Technical Analyst stores computed indicator values while deciding which pattern to report
- Fundamental Analyst accumulates peer comparison data before computing relative valuation
- Risk Assessor stores Monte Carlo simulation intermediate results

### 5.4 Team Shared Board

The Shared State Board is the primary coordination mechanism between agents. It is implemented as a SQLite database in WAL (Write-Ahead Logging) mode, which allows concurrent reads with serialized writes.

#### Findings Board

```python
class Finding(BaseModel):
    """A structured finding from a specialist agent."""

    id: str                        # UUID
    agent_id: str                  # Which agent produced this
    agent_type: str                # e.g., "macro_analyst", "technical_analyst"
    ticker: str | None             # Relevant ticker, if applicable
    category: str                  # e.g., "regime", "support_level", "valuation"
    signal: str                    # "bullish" | "bearish" | "neutral"
    confidence: float              # 0.0 to 1.0
    summary: str                   # Human-readable summary
    data: dict                     # Structured data payload
    created_at: datetime
```

#### Decision Log

```python
class Decision(BaseModel):
    """A decision point logged during analysis."""

    id: str
    phase: str                     # "decomposition" | "debate" | "synthesis"
    decision: str                  # What was decided
    rationale: str                 # Why
    inputs: list[str]              # Finding IDs that informed this decision
    created_at: datetime
```

#### Data Cache

```python
class CachedData(BaseModel):
    """Cached API response with TTL."""

    cache_key: str                 # source:params hash
    data: dict                     # Serialized response
    fetched_at: datetime
    ttl_seconds: int               # Time-to-live
    source: str                    # Data provider name
```

#### Alert Board

```python
class Alert(BaseModel):
    """An alert raised by an agent for Team Leader attention."""

    id: str
    agent_id: str
    severity: str                  # "info" | "warning" | "critical"
    message: str
    related_findings: list[str]    # Finding IDs
    created_at: datetime
```

### 5.5 Knowledge Graph

The knowledge graph captures entity relationships that enrich analysis across sessions. It is implemented with NetworkX for in-memory graph operations and persisted as JSON for durability.

#### Entity Types

| Entity Type | Examples | Key Properties |
|------------|---------|----------------|
| **Company** | NVDA, AAPL, MSFT | ticker, sector, market_cap, country |
| **Sector** | Semiconductors, Cloud Computing | name, parent_sector |
| **Person** | CEO, CFO, Board Members | name, role, company |
| **Index** | S&P 500, NASDAQ-100 | name, components |
| **MacroIndicator** | Fed Funds Rate, CPI | name, frequency, latest_value |
| **Event** | Earnings, FDA Approval, FOMC Meeting | type, date, affected_entities |

#### Relationship Types

| Relationship | Example | Properties |
|-------------|---------|------------|
| `BELONGS_TO_SECTOR` | NVDA → Semiconductors | weight, since |
| `COMPETES_WITH` | NVDA → AMD | overlap_score |
| `SUPPLIES_TO` | TSMC → NVDA | relationship_type, revenue_pct |
| `MEMBER_OF_INDEX` | NVDA → NASDAQ-100 | weight, since |
| `LED_BY` | NVDA → Jensen Huang | role, since |
| `CORRELATED_WITH` | NVDA → SMH ETF | correlation, period |
| `AFFECTED_BY` | NVDA → FOMC Meeting | impact_type, magnitude |

#### Example Graph

```
                    ┌──────────────┐
                    │  S&P 500     │
                    └──────┬───────┘
                           │ MEMBER_OF_INDEX
                    ┌──────▼───────┐
        ┌──────────→│    NVDA      │←──────────┐
        │           └──┬───┬───┬───┘           │
        │ COMPETES     │   │   │    SUPPLIES   │ CORRELATED
        │ _WITH        │   │   │    _TO        │ _WITH
   ┌────▼────┐        │   │   │         ┌─────▼─────┐
   │   AMD   │        │   │   │         │  SMH ETF  │
   └─────────┘        │   │   │         └───────────┘
              LED_BY──→│   │   │←──BELONGS_TO_SECTOR
         ┌─────────────▼┐ │ ┌─▼─────────────┐
         │ Jensen Huang  │ │ │Semiconductors │
         └───────────────┘ │ └───────────────┘
                           │
                     AFFECTED_BY
                           │
                    ┌──────▼───────┐
                    │ FOMC Meeting │
                    └──────────────┘
```

#### Temporal Modeling

Relationships carry temporal metadata so the graph reflects the current state of the world:

```python
class Relationship(BaseModel):
    source: str
    target: str
    type: str
    properties: dict
    valid_from: datetime
    valid_to: datetime | None    # None = currently valid
    confidence: float
    source_document: str | None  # SEC filing, news article, etc.
```

### 5.6 Context Window Management

LLM context windows are finite and expensive. FinSight manages context through two complementary strategies:

#### Strategy 1: Compact Summary Injection

When the Team Leader spawns a specialist agent, it does not dump the entire conversation history. Instead, it constructs a focused task prompt that includes:
- The specific sub-task assignment
- A compact summary of relevant prior findings (from the Shared State Board)
- Only the data schema the specialist needs

#### Strategy 2: On-Demand Query Tools

Agents have tools to query the Shared State Board and Knowledge Graph directly. Rather than pre-loading all available context, agents pull what they need during execution:

- `query_findings(filter)` — search the Findings Board by agent type, ticker, category, or signal
- `query_knowledge_graph(entity, depth)` — traverse the knowledge graph from an entity
- `search_documents(query)` — semantic search over ChromaDB for relevant documents

### 5.7 Implementation Phases

| Phase | Memory Component | Scope |
|-------|-----------------|-------|
| Phase 1 | Per-agent scratchpad + simple dict-based shared state | MVP |
| Phase 2 | SQLite shared board with WAL + API response caching | Core |
| Phase 3 | ChromaDB for document/filing embeddings | Enhancement |
| Phase 4 | NetworkX knowledge graph with JSON persistence | Enhancement |
| Phase 5 | Cross-session memory (past analysis retrieval, learning) | Advanced |

---

## 6. Tool System Design

### 6.1 Design Principles

1. **Every tool has a typed schema.** Input and output are defined as Pydantic models. The LLM sees the JSON schema; the runtime validates against it.
2. **Tools are stateless.** A tool call is a pure function of its inputs (plus the external world). No tool maintains internal state across invocations.
3. **Tools are exposed via MCP.** All tools — whether they wrap external APIs, perform local computation, or access storage — are exposed through Model Context Protocol servers. This provides uniform discovery, invocation, and error handling.
4. **Fail loudly, recover gracefully.** Tools return structured errors that the agent can reason about (e.g., "rate limited, retry after 60s" vs. "ticker not found"). Silent failures are forbidden.
5. **Cost-aware.** Expensive tool calls (e.g., large data fetches, multi-page PDF parsing) are tagged with estimated cost/latency so the agent loop can make informed decisions.

### 6.2 Two-Tier Loading Strategy

Not all 43+ tools need to be in every agent's context window. FinSight uses a two-tier loading strategy to minimize token overhead:

| Tier | Loading Strategy | Token Cost | Examples |
|------|-----------------|-----------|----------|
| **Tier 1: Always Loaded** | Included in every agent's system prompt | ~2,000 tokens | `query_findings`, `post_finding`, `query_knowledge_graph`, `search_documents` |
| **Tier 2: On-Demand** | Loaded only for agents that need them, based on agent type | ~500-1,500 tokens per tool set | `yahoo_price_history` (Technical), `fred_fetch` (Macro), `compute_greeks` (Options) |

**Token budget math:**

| Component | Tokens |
|-----------|--------|
| System prompt (base) | ~3,000 |
| Tier 1 tools (4 tools) | ~2,000 |
| Tier 2 tools (5-8 per specialist) | ~4,000 |
| Task prompt + context | ~2,000 |
| **Total prompt overhead** | **~11,000** |
| Remaining for conversation | ~89,000 (Sonnet 100k budget) |

### 6.3 Tool Inventory

#### Market Data Tools

| Tool | Source | Description |
|------|--------|-------------|
| `yahoo_price_history` | Yahoo Finance | OHLCV price data with adjustable timeframe and interval |
| `yahoo_fundamentals` | Yahoo Finance | Key financial metrics, ratios, and company info |
| `yahoo_options_chain` | Yahoo Finance | Options chain by expiration with Greeks |
| `alpha_vantage_prices` | Alpha Vantage | Intraday, daily, weekly, monthly price data |
| `alpha_vantage_forex` | Alpha Vantage | Currency pair exchange rates |
| `alpha_vantage_crypto` | Alpha Vantage | Cryptocurrency price data |
| `polygon_trades` | Polygon.io | Tick-level trade data |
| `polygon_options` | Polygon.io | Options chain and historical options data |

#### Macroeconomic Tools

| Tool | Source | Description |
|------|--------|-------------|
| `fred_fetch` | FRED API | Fetch any FRED series by ID (GDP, CPI, unemployment, etc.) |
| `treasury_yields` | Treasury.gov | Current and historical yield curve data |
| `economic_calendar` | Finnhub | Upcoming economic events and releases |
| `correlation_matrix` | Computed | Cross-asset correlation matrix over specified period |

#### Fundamental Analysis Tools

| Tool | Source | Description |
|------|--------|-------------|
| `sec_filings` | SEC EDGAR | Retrieve 10-K, 10-Q, 8-K, and other filings |
| `financial_statements` | FMP / Yahoo | Income statement, balance sheet, cash flow (quarterly/annual) |
| `dcf_model` | Computed | Discounted cash flow valuation with configurable assumptions |
| `peer_comparison` | Computed | Side-by-side comparison of financial metrics across peers |
| `earnings_transcripts` | FMP / Finnhub | Earnings call transcripts with searchable text |
| `insider_transactions` | SEC EDGAR | Recent insider buys and sells |

#### Technical Analysis Tools

| Tool | Source | Description |
|------|--------|-------------|
| `compute_indicators` | Computed | Calculate SMA, EMA, RSI, MACD, Bollinger Bands, ATR, etc. |
| `detect_patterns` | Computed | Identify chart patterns (head-and-shoulders, triangles, flags, etc.) |
| `support_resistance` | Computed | Calculate key support and resistance levels |
| `volume_profile` | Computed | Volume-by-price analysis for identifying value areas |
| `plot_chart` | plotext | Render terminal-native price charts with overlays |

#### Options Analysis Tools

| Tool | Source | Description |
|------|--------|-------------|
| `compute_greeks` | Computed | Calculate Delta, Gamma, Theta, Vega, Rho for options positions |
| `iv_surface` | Computed | Build implied volatility surface from options chain data |
| `strategy_payoff` | Computed | Model payoff diagrams for multi-leg options strategies |
| `unusual_activity` | Unusual Whales | Detect unusual options volume and open interest changes |
| `put_call_ratio` | CBOE | Put/call ratio for indices and individual names |

#### Sentiment Analysis Tools

| Tool | Source | Description |
|------|--------|-------------|
| `news_search` | News API / Finnhub | Search financial news by ticker, topic, or keyword |
| `social_sentiment` | Reddit (PRAW) | Aggregate sentiment from financial subreddits |
| `credibility_score` | Computed | Score source reliability based on historical accuracy |
| `earnings_sentiment` | Computed | NLP-based sentiment extraction from earnings transcripts |

#### Risk Analysis Tools

| Tool | Source | Description |
|------|--------|-------------|
| `var_calculation` | Computed | Value at Risk (parametric, historical, Monte Carlo) |
| `monte_carlo` | Computed | Monte Carlo simulation for portfolio outcomes |
| `stress_test` | Computed | Stress test positions against historical scenarios (2008, COVID, etc.) |
| `correlation_risk` | Computed | Identify concentration risk from correlated positions |
| `max_drawdown` | Computed | Calculate maximum drawdown and recovery time for strategies |

#### Backtesting Tools

| Tool | Source | Description |
|------|--------|-------------|
| `backtest_strategy` | Computed | Run strategy against historical data with configurable parameters |
| `performance_metrics` | Computed | Calculate Sharpe, Sortino, Calmar, win rate, profit factor |
| `regime_filter` | Computed | Filter backtest results by macro regime |
| `plot_equity_curve` | plotext | Render equity curve with drawdown overlay in terminal |

#### Storage and Retrieval Tools (Tier 1 — Always Loaded)

| Tool | Source | Description |
|------|--------|-------------|
| `query_findings` | Shared Board | Search the Findings Board by agent, ticker, category, or signal |
| `post_finding` | Shared Board | Write a structured finding to the Findings Board |
| `query_knowledge_graph` | NetworkX | Traverse entity relationships by type and depth |
| `search_documents` | ChromaDB | Semantic search over embedded documents and filings |

### 6.4 MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Process                           │
│                                                             │
│  agent_loop() ──→ tool_call("yahoo_price_history", {...})  │
│       ▲                        │                            │
│       │                        ▼                            │
│       │              ┌──────────────────┐                   │
│       │              │   MCP Router     │                   │
│       │              │                  │                   │
│       │              │  Routes to the   │                   │
│       │              │  correct server  │                   │
│       │              └────┬───┬───┬─────┘                   │
│       │                   │   │   │                         │
└───────┼───────────────────┼───┼───┼─────────────────────────┘
        │                   │   │   │
        │         ┌─────────▼┐ ┌▼──────────┐ ┌▼──────────┐
        │         │  Market  │ │   Macro   │ │ Analysis  │
        │         │  Data    │ │   Data    │ │  Compute  │
        │         │  Server  │ │  Server   │ │  Server   │
        │         │          │ │           │ │           │
        │         │ yahoo_*  │ │ fred_*    │ │ compute_* │
        │         │ alpha_*  │ │ treasury_*│ │ detect_*  │
        │         │ polygon_*│ │ econ_*    │ │ dcf_*     │
        │         └──────────┘ └───────────┘ └───────────┘
        │
        └── Result returned as typed Pydantic model
```

Each MCP server is a lightweight process that:
- Registers its tools with name, description, and JSON schema
- Handles invocations by routing to the appropriate fetcher or computation function
- Returns results as JSON conforming to the output schema
- Reports errors as structured error objects the agent can reason about

### 6.5 Custom Tool Creation

Adding a new tool to FinSight is straightforward. Define the input/output schemas and register the function:

```python
from pydantic import BaseModel, Field
from finsight.tools import function_tool

class PriceHistoryInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol (e.g., 'NVDA')")
    period: str = Field(default="1y", description="Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y")
    interval: str = Field(default="1d", description="Data interval: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo")

class PriceHistoryOutput(BaseModel):
    ticker: str
    period: str
    interval: str
    data: list[dict]                # List of OHLCV records
    metadata: dict                  # Source, fetch time, record count

@function_tool(
    name="yahoo_price_history",
    description="Fetch OHLCV price data from Yahoo Finance for a given ticker and timeframe.",
)
async def yahoo_price_history(input: PriceHistoryInput) -> PriceHistoryOutput:
    import yfinance as yf

    ticker = yf.Ticker(input.ticker)
    df = ticker.history(period=input.period, interval=input.interval)

    return PriceHistoryOutput(
        ticker=input.ticker,
        period=input.period,
        interval=input.interval,
        data=df.reset_index().to_dict(orient="records"),
        metadata={
            "source": "yahoo_finance",
            "fetched_at": datetime.utcnow().isoformat(),
            "record_count": len(df),
        },
    )
```

---

## 7. Implementation Roadmap

### 7.1 Phased Delivery

#### Phase 1: Skeleton (Weeks 1-2)

**Goal:** End-to-end request flow with a single agent and minimal tooling.

| Deliverable | Description |
|------------|-------------|
| Project scaffolding | Directory structure, config loader, logging setup |
| CLI shell | Basic Rich-based CLI that accepts queries and displays responses |
| Single agent loop | Team Leader agent running the core loop with the Anthropic SDK |
| 2-3 data tools | `yahoo_price_history`, `fred_fetch`, `news_search` |
| Simple output | Markdown-formatted response displayed in terminal |

**Exit criteria:** User can type "Analyze NVDA" and receive a single-agent response that includes price data, a macro indicator, and recent news.

#### Phase 2: Data Layer (Weeks 3-4)

**Goal:** Full Provider Registry with TET pipeline and data caching.

| Deliverable | Description |
|------------|-------------|
| Provider Registry | BaseFetcher implementations for all 15+ data sources |
| TET pipeline | Transform → Enrich → Tag for all data models |
| Pydantic models | All 8 standard data models validated and tested |
| SQLite cache | API response caching with TTL-based expiration |
| MCP server setup | Market Data and Macro Data MCP servers operational |

**Exit criteria:** All data sources return typed, enriched, tagged Pydantic models through the Provider Registry.

#### Phase 3: Multi-Agent (Weeks 5-7)

**Goal:** Full multi-agent system with all 7 specialists and the debate mechanism.

| Deliverable | Description |
|------------|-------------|
| AgentPool | Concurrent agent execution with priority queue and budget limits |
| All 7 specialists | Macro, Technical, Fundamental, Options, Risk, Sentiment, Backtest agents |
| Shared State Board | SQLite WAL with Findings, Decision Log, Data Cache, Alert Board tables |
| Hub-and-spoke coordination | Team Leader assigns tasks, collects findings |
| Debate mechanism | Bull vs Bear (3 rounds) + Risk Discussion + synthesis |

**Exit criteria:** Multi-agent analysis produces findings from all relevant specialists, runs a debate, and synthesizes a unified recommendation.

#### Phase 4: Advanced Analysis (Weeks 8-10)

**Goal:** Knowledge graph, vector search, and advanced analytical tools.

| Deliverable | Description |
|------------|-------------|
| ChromaDB integration | Document embeddings for SEC filings and research notes |
| Knowledge graph | NetworkX-based entity relationship graph with temporal modeling |
| Advanced tools | DCF model, Monte Carlo simulation, stress testing, IV surface |
| Backtesting engine | Full strategy backtesting with performance metrics |
| Context management | Compact summary injection + on-demand query tools |

**Exit criteria:** Agents can query the knowledge graph for entity relationships and search embedded documents for semantic matches.

#### Phase 5: Polish (Weeks 11-12)

**Goal:** Production-quality CLI, session persistence, and cost optimization.

| Deliverable | Description |
|------------|-------------|
| Interactive CLI | Textual-based TUI with panels, tabs, and live-updating displays |
| Session persistence | Save/restore analysis sessions with full state |
| Cost optimization | Fine-tuned model routing, token budget enforcement, caching hit rates |
| Tracing and observability | Structured logging of all agent actions and tool calls |
| Documentation | User guide, configuration reference, tool catalog |

**Exit criteria:** A financial analyst can run FinSight as their daily research tool with reliable, cost-efficient performance.

### 7.2 Project Directory Structure

```
finsight/
├── pyproject.toml              # Project metadata, dependencies
├── config/
│   ├── default.toml            # Default configuration
│   └── agents.toml             # Agent system prompts and parameters
├── src/
│   └── finsight/
│       ├── __init__.py
│       ├── main.py             # CLI entry point
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py          # Rich/Textual CLI application
│       │   ├── display.py      # Output formatting (tables, charts, markdown)
│       │   └── session.py      # Session management (save/restore)
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── loop.py         # Core agent loop implementation
│       │   ├── pool.py         # AgentPool with concurrency management
│       │   ├── team_leader.py  # Team Leader agent configuration
│       │   ├── specialists/
│       │   │   ├── __init__.py
│       │   │   ├── macro.py
│       │   │   ├── technical.py
│       │   │   ├── fundamental.py
│       │   │   ├── options.py
│       │   │   ├── risk.py
│       │   │   ├── sentiment.py
│       │   │   └── backtest.py
│       │   └── debate/
│       │       ├── __init__.py
│       │       ├── bull_bear.py
│       │       └── risk_discussion.py
│       ├── data/
│       │   ├── __init__.py
│       │   ├── registry.py     # ProviderRegistry
│       │   ├── pipeline.py     # TET pipeline (Transform, Enrich, Tag)
│       │   ├── models.py       # 8 standard Pydantic data models
│       │   └── providers/
│       │       ├── __init__.py
│       │       ├── yahoo.py
│       │       ├── alpha_vantage.py
│       │       ├── fred.py
│       │       ├── sec_edgar.py
│       │       ├── polygon.py
│       │       ├── finnhub.py
│       │       ├── news.py
│       │       ├── reddit.py
│       │       ├── unusual_whales.py
│       │       └── fmp.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── registry.py     # Tool registration and MCP exposure
│       │   ├── market.py       # Market data tools
│       │   ├── macro.py        # Macroeconomic tools
│       │   ├── fundamental.py  # Fundamental analysis tools
│       │   ├── technical.py    # Technical analysis tools
│       │   ├── options.py      # Options analysis tools
│       │   ├── sentiment.py    # Sentiment analysis tools
│       │   ├── risk.py         # Risk analysis tools
│       │   └── backtest.py     # Backtesting tools
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── scratchpad.py   # Per-agent ephemeral memory
│       │   ├── shared_board.py # SQLite shared state board
│       │   ├── knowledge.py    # NetworkX knowledge graph
│       │   └── vectors.py      # ChromaDB vector storage
│       └── tracing/
│           ├── __init__.py
│           └── logger.py       # Structured tracing and logging
├── tests/
│   ├── test_agents/
│   ├── test_data/
│   ├── test_tools/
│   └── test_memory/
└── data/
    ├── chromadb/               # Vector database storage
    ├── knowledge_graph.json    # Persisted knowledge graph
    └── sessions/               # Saved analysis sessions
```

### 7.3 Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `anthropic` | >=0.40.0 | Claude API SDK for agent LLM calls |
| `pydantic` | >=2.0 | Data validation and typed models |
| `rich` | >=13.0 | Terminal formatting (tables, panels, Markdown, progress) |
| `textual` | >=0.50 | Interactive TUI framework |
| `httpx` | >=0.27 | Async HTTP client with connection pooling |
| `yfinance` | >=0.2 | Yahoo Finance data access |
| `chromadb` | >=0.4 | Vector database for document embeddings |
| `networkx` | >=3.0 | Knowledge graph operations |
| `plotext` | >=5.0 | Terminal-native charting |
| `mcp` | >=1.0 | Model Context Protocol SDK |
| `numpy` | >=1.26 | Numerical computation (indicators, risk metrics) |
| `pandas` | >=2.0 | Data manipulation and time series |
| `scipy` | >=1.12 | Statistical functions (VaR, distributions) |

### 7.4 Configuration

FinSight uses TOML configuration files for all settings:

```toml
# config/default.toml

[project]
name = "FinSight"
version = "0.1.0"
log_level = "INFO"

[llm]
default_model = "claude-sonnet-4-6"
team_leader_model = "claude-opus-4-6"
extraction_model = "claude-haiku-4-5-20251001"
max_tokens_per_request = 8192
temperature = 0.0

[llm.token_budgets]
opus = 200_000
sonnet = 100_000
haiku = 30_000

[agents]
max_concurrent = 6
debate_rounds = 3
shutdown_timeout = 30

[data]
cache_ttl_seconds = 3600
max_retries = 3
request_timeout = 30

[data.api_keys]
alpha_vantage = "${ALPHA_VANTAGE_API_KEY}"
fred = "${FRED_API_KEY}"
polygon = "${POLYGON_API_KEY}"
news_api = "${NEWS_API_KEY}"
finnhub = "${FINNHUB_API_KEY}"
fmp = "${FMP_API_KEY}"
tavily = "${TAVILY_API_KEY}"

[storage]
sqlite_path = "data/finsight.db"
chromadb_path = "data/chromadb"
knowledge_graph_path = "data/knowledge_graph.json"
sessions_path = "data/sessions"

[cli]
theme = "dark"
chart_width = 80
table_max_rows = 50
```

### 7.5 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/finsight.git
cd finsight

# Install dependencies
pip install -e ".[dev]"

# Set up API keys
cp .env.example .env
# Edit .env with your API keys

# Run FinSight
python -m finsight

# Example queries
> Analyze NVDA for a 6-month hold
> Compare AAPL vs MSFT fundamentals
> What's the macro regime telling us?
> Show me unusual options activity on SPY
> Backtest a momentum strategy on QQQ over 5 years
```

---

## License

This project is proprietary and confidential.

## Disclaimer

FinSight is a research and analysis tool. It does not provide financial advice and does not execute trades. All investment decisions are the sole responsibility of the user. Past performance of backtested strategies does not guarantee future results.
