# Finance Agent

An AI-powered financial analysis engine that uses multi-agent collaboration to deliver rigorous, multi-perspective investment analysis and actionable recommendations via CLI.

**Not a trading bot.** Finance Agent analyzes, debates, and recommends. Humans decide and execute.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
  - [1.1 Vision](#11-vision)
  - [1.2 Core Capabilities](#12-core-capabilities)
  - [1.3 Comparison with Existing Projects](#13-comparison-with-existing-projects)
  - [1.4 Use Case Examples](#14-use-case-examples)
- [2. System Architecture](#2-system-architecture)
  - [2.1 Design Principles](#21-design-principles)
  - [2.2 Architecture Overview](#22-architecture-overview)
  - [2.3 The 8 Pillars](#23-the-8-pillars)
  - [2.4 Data Flow](#24-data-flow)
  - [2.5 Key Design Decisions](#25-key-design-decisions)
- [3. Multi-Agent System](#3-multi-agent-system)
  - [3.1 Agent Architecture Overview](#31-agent-architecture-overview)
  - [3.2 Team Leader Agent](#32-team-leader-agent)
  - [3.3 Teammate Agents](#33-teammate-agents)
  - [3.4 Agent Communication](#34-agent-communication)
  - [3.5 Debate Mechanism](#35-debate-mechanism)
  - [3.6 Agent Lifecycle](#36-agent-lifecycle)
  - [3.7 Concurrency Control](#37-concurrency-control)
- [4. Unified Data Layer](#4-unified-data-layer)
  - [4.1 Design Philosophy](#41-design-philosophy)
  - [4.2 TET Pipeline (Transform → Enrich → Tag)](#42-tet-pipeline-transform--enrich--tag)
  - [4.3 Standardized Data Models](#43-standardized-data-models)
  - [4.4 Provider Registry](#44-provider-registry)
  - [4.5 Data Source Catalog](#45-data-source-catalog)
  - [4.6 Data Flow](#46-data-flow)
- [5. Tool System](#5-tool-system)
  - [5.1 Tool Architecture](#51-tool-architecture)
  - [5.2 Tool Loading Strategy](#52-tool-loading-strategy)
  - [5.3 Tool Definition Pattern](#53-tool-definition-pattern)
  - [5.4 MCP Server Design](#54-mcp-server-design)
  - [5.5 Complete Tool Catalog](#55-complete-tool-catalog)
  - [5.6 Tool Execution Flow](#56-tool-execution-flow)
- [6. Memory & Storage System](#6-memory--storage-system)
  - [6.1 Storage Architecture Overview](#61-storage-architecture-overview)
  - [6.2 Knowledge Graph (Neo4j)](#62-knowledge-graph-neo4j)
  - [6.3 Vector Store (ChromaDB)](#63-vector-store-chromadb)
  - [6.4 Time Series Store (DuckDB)](#64-time-series-store-duckdb)
  - [6.5 Shared Board (SQLite WAL)](#65-shared-board-sqlite-wal)
  - [6.6 Per-Agent Scratchpad (In-Memory)](#66-per-agent-scratchpad-in-memory)
  - [6.7 Context Injection Strategy](#67-context-injection-strategy)
  - [6.8 KG Ingestion Pipeline](#68-kg-ingestion-pipeline)
- [7. Technology Stack](#7-technology-stack)
  - [7.1 LLM Strategy](#71-llm-strategy)
  - [7.2 Core Dependencies](#72-core-dependencies)
  - [7.3 Financial Libraries](#73-financial-libraries)
  - [7.4 Project Structure](#74-project-structure)
  - [7.5 Configuration](#75-configuration)
  - [7.6 Deployment](#76-deployment)
  - [7.7 Development Setup](#77-development-setup)
- [8. Implementation Roadmap](#8-implementation-roadmap)
  - [8.1 Phase 1: Foundation (Weeks 1-3)](#81-phase-1-foundation-weeks-1-3)
  - [8.2 Phase 2: Data Layer Expansion (Weeks 4-6)](#82-phase-2-data-layer-expansion-weeks-4-6)
  - [8.3 Phase 3: Multi-Agent Team (Weeks 7-9)](#83-phase-3-multi-agent-team-weeks-7-9)
  - [8.4 Phase 4: Debate & Deep Analysis (Weeks 10-12)](#84-phase-4-debate--deep-analysis-weeks-10-12)
  - [8.5 Phase 5: Knowledge Graph & Intelligence (Weeks 13-16)](#85-phase-5-knowledge-graph--intelligence-weeks-13-16)
  - [8.6 Summary Timeline](#86-summary-timeline)
  - [8.7 Dependencies Between Phases](#87-dependencies-between-phases)
  - [8.8 Risk Factors](#88-risk-factors)
  - [8.9 Definition of Done per Phase](#89-definition-of-done-per-phase)

---

# 1. Project Overview

## 1.1 Vision

Finance Agent is an AI-powered financial analysis engine built on multi-agent collaboration. It brings together specialized analytical perspectives — macroeconomic, technical, fundamental, sentiment, options, and risk — and synthesizes them into actionable investment recommendations.

The system operates through a **Team Leader agent** accessible via CLI. When a user poses a question or scenario, the leader decomposes it into sub-tasks and spawns specialized teammate agents to research, analyze, and debate. Their findings are synthesized into a unified recommendation with explicit reasoning, confidence levels, and risk quantification.

**What it is:** An analysis and recommendation system for professional investors and traders who want rigorous, multi-perspective research delivered in seconds rather than hours.

**What it is not:** A trading bot. Finance Agent never executes trades. It produces analysis, recommendations, and risk assessments that humans act on.

### Design Principles

- **Multi-perspective by default** — every analysis considers bull, bear, and risk viewpoints before reaching a conclusion.
- **Data-driven, not vibes-driven** — recommendations are grounded in quantitative data from 15+ financial sources, not LLM hallucination.
- **Transparent reasoning** — every recommendation includes the chain of logic, data sources consulted, and confidence intervals.
- **Professional-grade** — options Greeks, Monte Carlo risk simulations, backtesting validation. Built for people who know what a Sharpe ratio is.

---

## 1.2 Core Capabilities

| Capability | Description |
|---|---|
| **Multi-Source Data Integration** | 15+ financial data sources unified through a Provider Registry. Market data, economic indicators, news, sentiment, options chains, and alternative data — all accessible through a single interface. |
| **Multi-Perspective Analysis** | Parallel analysis from macro, technical, fundamental, sentiment, options, and risk perspectives. Each perspective operates as a specialized agent with domain-specific tools. |
| **Bull/Bear Debate Mechanism** | Structured adversarial debate between bull and bear perspectives before any recommendation is finalized. Forces the system to stress-test its own conclusions. |
| **Cross-Market Transmission Chains** | Traces how events propagate across markets: geopolitical event → commodity price → sector impact → individual stock exposure. Maps causal chains rather than just correlations. |
| **Options Strategy Analysis** | Full options analysis with QuantLib integration: Greeks calculation (delta, gamma, theta, vega, rho), implied volatility surfaces, and strategy construction (spreads, straddles, condors). |
| **Historical Backtesting** | Validates recommendations against historical data using vectorbt. Tests whether the proposed strategy would have worked in analogous past conditions. |
| **Knowledge Graph** | Entity-relationship graph for multi-hop reasoning. Connects companies, sectors, commodities, countries, and economic indicators to enable questions like "What US small-caps are most exposed to a Euro depreciation?" |
| **Multi-Agent Collaboration** | Team of specialized agents with shared state, coordinated by a Team Leader. Agents can request data, delegate sub-tasks, and build on each other's findings. |

---

## 1.3 Comparison with Existing Projects

| Dimension | TradingAgents | FinRobot | OpenBB | **Finance Agent** |
|---|---|---|---|---|
| **Data Sources** | 1–2 sources | ~5 sources | 90+ sources (terminal) | **15+ sources (unified API)** |
| **Options Analysis** | None | None | None | **QuantLib + full Greeks chain** |
| **Macro Analysis** | None | None | Partial (manual) | **FRED + EIA + cross-market transmission** |
| **Backtesting** | None | Limited | None | **vectorbt integration** |
| **Risk Quantification** | LLM qualitative only | None | None | **Monte Carlo + Greeks + VaR** |
| **Event-Driven Analysis** | None | None | None | **GDELT + news + causal chain mapping** |
| **Cross-Market Reasoning** | None | None | None | **Macro transmission chain analysis** |
| **Agent Framework** | LangGraph | AutoGen | N/A (terminal) | **Custom agent loop with shared state** |
| **Debate Mechanism** | Bull/Bear | None | None | **Bull/Bear + Risk perspective** |

**Key differentiators:**

- **Depth over breadth in data** — OpenBB has more raw sources, but Finance Agent's Provider Registry normalizes and cross-references data specifically for multi-agent analytical workflows.
- **Options as a first-class citizen** — no other agent-based system integrates quantitative options analysis with Greeks and strategy construction.
- **Cross-market causal reasoning** — transmission chain analysis connects macro events to specific tradeable instruments, a capability absent from all compared systems.
- **Three-way debate** — adding a dedicated risk perspective alongside bull/bear prevents the optimism bias common in two-sided debates.

---

## 1.4 Use Case Examples

### Example 1: Geopolitical Event Analysis

**Scenario:** Tensions escalate around the Strait of Hormuz, raising the possibility of a shipping disruption.

**What Finance Agent does:**

1. **Macro Agent** pulls GDELT event data + EIA petroleum supply reports → quantifies disruption probability and oil supply impact.
2. **Cross-Market Transmission** traces the chain: Strait disruption → crude oil spike → European natural gas prices → EU industrial sector margins → specific exposed companies.
3. **Technical Agent** identifies current price levels and key support/resistance for energy ETFs and affected equities.
4. **Options Agent** scans for asymmetric opportunities: cheap out-of-the-money calls on energy names, put protection on exposed European industrials.
5. **Bull/Bear Debate** — Bull: "Energy long is obvious." Bear: "Strait tensions have resolved peacefully 4 of the last 5 times; premium is already priced in." Risk: "Tail risk of $120 oil is under-hedged in most portfolios."
6. **Synthesis** delivers a concrete recommendation: specific instruments, position sizing, entry/exit levels, and a hedge overlay using options.

---

### Example 2: Earnings Season Analysis

**Scenario:** A major cloud provider reports earnings that beat expectations, but guidance is cautious on enterprise spending.

**What Finance Agent does:**

1. **Fundamental Agent** parses the earnings report — revenue breakdown, margin trends, customer metrics, management commentary.
2. **Cross-Market Reasoning** cross-references with peer companies' recent reports and industry-level data (IT spending surveys, enterprise software deal flow).
3. **Sentiment Agent** analyzes post-earnings analyst notes, social media reaction, and options flow to gauge market positioning.
4. **Technical Agent** identifies the stock's reaction relative to historical earnings moves and current implied volatility.
5. **Options Agent** constructs a strategy: if implied vol is elevated post-earnings, sell a put spread to capture premium decay; if the guidance concern is overdone, pair with a call spread for the next quarter's catalyst.
6. **Backtesting** validates: "In the last 8 instances where this company beat on revenue but guided down on enterprise, the stock recovered to pre-earnings levels within 15 trading days 6 out of 8 times."

---

### Example 3: Macro Regime Change Analysis

**Scenario:** The Federal Reserve signals a pivot from rate hikes to a prolonged pause, with markets beginning to price in cuts.

**What Finance Agent does:**

1. **Macro Agent** pulls FRED data (yield curve, inflation expectations, employment trends) and models the regime transition.
2. **Cross-Market Transmission** maps the rotation: falling rates → duration assets benefit → growth over value → small-cap revival → sector-level winners and losers.
3. **Knowledge Graph** queries: "Which sectors have the highest debt-to-equity and would benefit most from lower refinancing costs?" → identifies specific names in real estate, utilities, and high-growth tech.
4. **Risk Agent** runs Monte Carlo simulations on a proposed rotation portfolio under three scenarios: soft landing, recession, and inflation re-acceleration.
5. **Bull/Bear Debate** — Bull: "Rate-sensitive assets are historically undervalued at pivot points." Bear: "Pivots that precede recessions see a different playbook — defensives outperform, not growth." Risk: "Positioning for a pivot that gets delayed by sticky inflation is the biggest risk here."
6. **Synthesis** produces a phased recommendation: immediate portfolio tilts, conditional triggers for adding exposure, and specific options hedges against the "pivot delayed" scenario.

---

# 2. System Architecture

## 2.1 Design Principles

Six principles guide every architectural decision:

1. **Simplicity over complexity** -- Follow the Claude Code philosophy: a single agent loop with rich tools beats multi-framework orchestration. Add complexity only when a simpler approach demonstrably fails.

2. **Composable patterns over monolithic frameworks** -- Align with Anthropic's building effective agents guidance. Use small, well-defined patterns (debate, fan-out, pipeline) that combine freely rather than locking into a rigid graph engine.

3. **MCP for tool integration** -- All external data sources and utilities are exposed through the Model Context Protocol. Tools are registered once and available to every agent uniformly.

4. **Structured data for reports, natural language for debate** -- Inspired by TradingAgents: analysts produce typed Pydantic models for quantitative results; the debate phase uses free-form argumentation so LLMs can reason naturally.

5. **Equal tool access** -- Every agent, regardless of role, can call any registered tool. There are no role-based permission boundaries. This is safe because the system is analysis-only.

6. **Pure analysis, no execution** -- The system recommends; it never places trades, moves funds, or modifies external state. This removes an entire class of guardrail requirements and lets us focus on insight quality.

---

## 2.2 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERFACE LAYER                              │
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
│                      ORCHESTRATION LAYER                            │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                     TEAM LEADER (Opus)                        │  │
│   │         Task Decomposition · Agent Spawning · Synthesis       │  │
│   └──────┬──────────┬──────────┬──────────┬──────────┬───────┘     │
│          │          │          │          │          │              │
│          ▼          ▼          ▼          ▼          ▼              │
│   ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐   │
│   │Fundament.││Technical ││Sentiment ││  Macro   ││  Risk    │   │
│   │ Analyst  ││ Analyst  ││ Analyst  ││ Analyst  ││ Analyst  │   │
│   │ (Sonnet) ││ (Sonnet) ││ (Haiku)  ││ (Sonnet) ││ (Sonnet) │   │
│   └────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘   │
│        │           │           │           │           │           │
│        └─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┘           │
│              ▼           ▼           ▼           ▼                  │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │              SHARED STATE BOARD (SQLite WAL)                  │  │
│   │           findings · positions · debate_log                   │  │
│   └──────────────────────────┬───────────────────────────────────┘  │
│                              │                                      │
│   ┌──────────────────────────┴───────────────────────────────────┐  │
│   │                     DEBATE MODULE                             │  │
│   │       Bull Perspective ◄────────► Bear Perspective            │  │
│   │                └──────── Risk Arbiter ────────┘               │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   UNIFIED DATA LAYER (OpenBB-inspired)              │
│                                                                     │
│   ┌───────────────────────────────┐   ┌──────────────────────────┐  │
│   │      Provider Registry        │   │    MCP Tool Server        │  │
│   │                               │   │                          │  │
│   │  TET Fetchers                 │   │  All data sources as     │  │
│   │  (Transform · Enrich · Tag)   │   │  MCP tools with deferred │  │
│   │                               │   │  loading for cold-start  │  │
│   └───────────────────────────────┘   └──────────────────────────┘  │
│                                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         STORAGE LAYER                               │
│                                                                     │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│   │    Neo4j    │  │   ChromaDB  │  │   DuckDB    │  │  SQLite  │ │
│   │             │  │             │  │             │  │   WAL    │ │
│   │   Entity    │  │  Semantic   │  │    Time     │  │  Board   │ │
│   │  relations  │  │   search    │  │   series    │  │  state   │ │
│   │    (KG)     │  │  (vectors)  │  │  (OHLCV)   │  │ session  │ │
│   └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2.3 The 8 Pillars

Inspired by the Conversational AI (CAI) architecture framework, adapted for financial analysis:

| # | Pillar | Description | Our Implementation |
|---|--------|-------------|--------------------|
| 1 | **Agents** | The reasoning entities that perform work | Team Leader (Opus) owns intent analysis and synthesis. Teammates (Sonnet/Haiku) are spawned dynamically per query as specialized analysts. All agents share full tool access. |
| 2 | **Tools** | External capabilities agents can invoke | MCP servers expose data providers. Python functions use `@function_tool` decorators. Tools support deferred loading -- schema metadata is available immediately; full implementation loads on first call. |
| 3 | **Handoffs** | How work transfers between agents | Not used. Instead of explicit handoffs, all agents read from and write to the shared state board. This eliminates routing logic and prevents information loss during transfers. |
| 4 | **Patterns** | Reusable multi-agent interaction templates | Three composable patterns: **Debate** (Bull vs Bear with Risk arbiter), **Pipeline** (Data -> Analysis -> Synthesis), **Fan-out** (parallel specialist analysis with board-based collection). |
| 5 | **Turns** | Limits on agent execution | Max iteration count per agent. Global timeout per query. Loop detection via board-state hashing (if an agent posts the same finding twice, it is halted). |
| 6 | **Tracing** | Observability and cost tracking | OpenTelemetry spans for every agent turn, tool call, and LLM invocation. Per-agent token usage and estimated cost tracked in session metadata. |
| 7 | **Guardrails** | Safety boundaries on agent behavior | Basic operational guardrails only: loop detection, timeout enforcement, token budget caps. No compliance or trade-execution guardrails needed (pure analysis system). |
| 8 | **HITL** | Human-in-the-loop control | Optional. User can interrupt analysis mid-run, adjust the query, redirect focus ("ignore technicals, focus on macro"), or request deeper investigation on a specific finding. |

---

## 2.4 Data Flow

Step-by-step flow for a user query, e.g. *"Analyze AAPL for a 6-month hold"*:

```
 User                Leader              Teammates           Board            Data Layer
  │                    │                     │                 │                  │
  │  1. "Analyze AAPL" │                     │                 │                  │
  │───────────────────►│                     │                 │                  │
  │                    │                     │                 │                  │
  │                    │ 2. Analyze intent   │                 │                  │
  │                    │    Determine needed  │                 │                  │
  │                    │    specialists       │                 │                  │
  │                    │                     │                 │                  │
  │                    │ 3. Spawn analysts   │                 │                  │
  │                    │────────────────────►│                 │                  │
  │                    │   (fan-out:         │                 │                  │
  │                    │    fundamental,     │                 │                  │
  │                    │    technical,       │                 │                  │
  │                    │    sentiment,       │                 │                  │
  │                    │    macro)           │                 │                  │
  │                    │                     │                 │                  │
  │                    │                     │ 4. Fetch data   │                  │
  │                    │                     │ (parallel MCP)──┼─────────────────►│
  │                    │                     │◄─────────────── ┼──────────────────│
  │                    │                     │                 │                  │
  │                    │                     │ 5. Post         │                  │
  │                    │                     │ findings────────►│                  │
  │                    │                     │ (Pydantic       │                  │
  │                    │                     │  models)        │                  │
  │                    │                     │                 │                  │
  │                    │              6. Debate phase          │                  │
  │                    │              (optional)               │                  │
  │                    │                     │                 │                  │
  │                    │              Bull reads board─────────►│                  │
  │                    │              Bear reads board─────────►│                  │
  │                    │              Risk arbiter─────────────►│                  │
  │                    │              Posts debate_log─────────►│                  │
  │                    │                     │                 │                  │
  │                    │ 7. Read board       │                 │                  │
  │                    │◄────────────────────┼─────────────────│                  │
  │                    │    Synthesize all   │                 │                  │
  │                    │    findings +       │                 │                  │
  │                    │    debate results   │                 │                  │
  │                    │                     │                 │                  │
  │  8. Final report   │                     │                 │                  │
  │◄───────────────────│                     │                 │                  │
  │   (recommendation  │                     │                 │                  │
  │    + confidence +   │                     │                 │                  │
  │    key risks)       │                     │                 │                  │
```

### Step Details

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1 | User | Submits query via CLI | Raw text string |
| 2 | Team Leader | Parses intent: ticker, timeframe, analysis depth | `AnalysisRequest` Pydantic model |
| 3 | Team Leader | Selects and spawns specialist teammates | 2-5 parallel agent instances |
| 4 | Teammates | Call MCP tools to fetch market data, filings, news, technicals | Raw provider responses |
| 5 | Teammates | Analyze data, post structured findings to board | `Finding` models (typed per domain) |
| 6 | Debate Module | Bull and Bear agents argue positions; Risk arbiter scores | `DebateLog` with scored arguments |
| 7 | Team Leader | Reads all board sections, weighs findings and debate | Internal synthesis state |
| 8 | Team Leader | Produces final recommendation | `AnalysisReport` with recommendation, confidence, risks |

---

## 2.5 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Agent framework | **Custom agent loop** | LangGraph, CrewAI, AutoGen | Simpler, no dependency risk, full control over execution. Anthropic's own guidance: "start with a single LLM call + tools; add complexity only when needed." LangGraph adds abstraction without proportional value for our use case. |
| Agent communication | **Shared state board** | Direct message passing, event bus | O(N) complexity: each agent writes once and reads once. Message passing is O(N^2) in a fully connected topology. TradingAgents validated this pattern for financial multi-agent systems. |
| Tool access model | **Equal access for all agents** | Role-based tool restrictions | Simplicity. No execution risk since the system is analysis-only. Role-based restrictions add configuration overhead and debugging complexity with no safety benefit here. |
| Tool protocol | **MCP (Model Context Protocol)** | Custom tool API, function calling only | Industry standard. Tools built once are reusable across projects and compatible with any MCP client. Deferred loading solves cold-start without custom lazy-load infrastructure. |
| Storage | **Hybrid: Neo4j + ChromaDB + DuckDB + SQLite** | Single Postgres, single SQLite | Right tool for each data shape. Neo4j for entity relationship traversal (company -> sector -> peers). ChromaDB for semantic similarity over news/filings. DuckDB for columnar time-series queries (OHLCV, indicators). SQLite WAL for low-latency shared board state. |
| Debate mechanism | **Structured Bull/Bear with Risk arbiter** | Single-pass analysis, voting ensemble | Debate surfaces edge cases and contrarian views that single-pass misses. The Risk arbiter prevents both sides from ignoring tail risks. Adds one extra LLM round but significantly improves recommendation quality. |
| LLM selection | **Opus for leader, Sonnet/Haiku for teammates** | Uniform model for all agents | Cost optimization. The leader needs strong reasoning for synthesis and intent parsing. Teammates perform focused, well-scoped analysis where smaller models excel. Estimated 60-70% cost reduction vs all-Opus. |
| Interface | **CLI-first** | Web UI, API-first | Fastest iteration cycle. CLI integrates naturally with developer workflows. REST API planned as a second interface once the core loop is stable. |

---

# 3. Multi-Agent System

## 3.1 Agent Architecture Overview

The system uses a **Team Leader + Teammates** pattern. The human user interacts only with the Team Leader, who decomposes complex financial queries into parallel sub-tasks executed by autonomous teammate agents.

```
                         +-------------+
                         |    Human    |
                         |   (CLI)     |
                         +------+------+
                                |
                         +------v------+
                         | Team Leader |
                         |  (Opus)     |
                         +------+------+
                                |
              +-----------------+------------------+
              |                 |                   |
        +-----v-----+   +------v------+   +-------v-------+
        | Teammate A |   | Teammate B  |   | Teammate C    |
        | (Sonnet)   |   | (Haiku)     |   | (Sonnet)      |
        +-----+------+   +------+------+   +-------+-------+
              |                 |                   |
              +--------+--------+-------------------+
                       |
                +------v------+
                | Shared      |
                | State Board |
                +-------------+
```

**Key design principles:**

| Principle | Description |
|-----------|-------------|
| Single entry point | Human talks only to Team Leader |
| Dynamic decomposition | Leader decides teammate count and roles per query |
| Equal capabilities | All teammates have full tool access |
| Autonomous execution | Teammates work independently, post results to Shared Board |
| Synthesized output | Leader aggregates findings into a unified recommendation |

---

## 3.2 Team Leader Agent

The Team Leader is the orchestration brain of the system.

| Property | Value |
|----------|-------|
| Model | Claude Opus (complex reasoning, cross-market synthesis) |
| Role | Orchestrator, synthesizer, user-facing communicator |
| Max concurrent teammates | Configurable (default: 6) |

### Responsibilities

1. **Intent Understanding** -- Parse user queries into structured analysis requests. Determine asset class, time horizon, risk profile, and analysis depth.

2. **Task Decomposition** -- Break a complex query into independent sub-tasks that can run in parallel. Example: "Should I buy NVDA?" becomes macro analysis + technical analysis + fundamental analysis + sentiment scan + risk assessment.

3. **Teammate Spawning** -- Decide how many teammates to spawn and what role each plays. Simple queries may need 1-2 teammates; complex portfolio reviews may need 5-6.

4. **Budget Allocation** -- Distribute the total token budget across teammates. High-priority or complex tasks get larger budgets.

5. **Result Synthesis** -- Read all teammate reports from the Shared Board, resolve contradictions, and produce a final recommendation with confidence score.

6. **User Communication** -- Deliver the synthesized result with clear reasoning chain, risk warnings, and actionable next steps.

### Spawning Logic

```python
def decompose_query(self, query: UserQuery) -> list[TeammateTask]:
    """Leader decides dynamically what analysis is needed."""

    tasks = []

    # Always include macro context for equity/options queries
    if query.asset_class in ("equity", "options", "etf"):
        tasks.append(TeammateTask(
            role="macro_analyst",
            model="haiku",  # fast, structured data retrieval
            description="Pull FRED rates, EIA energy, PMI manufacturing data",
            tools=["fred", "eia", "pmi"],
            budget_tokens=4000,
            timeout_seconds=300,
        ))

    # Technical analysis for anything with price history
    if query.has_ticker:
        tasks.append(TeammateTask(
            role="technical_analyst",
            model="sonnet",  # needs reasoning for pattern recognition
            description=f"TA-Lib indicators and chart patterns for {query.ticker}",
            tools=["yfinance", "talib", "charting"],
            budget_tokens=8000,
            timeout_seconds=300,
        ))

    # Fundamental analysis for individual stocks
    if query.asset_class == "equity" and query.ticker:
        tasks.append(TeammateTask(
            role="fundamental_analyst",
            model="sonnet",
            description=f"Financial statements, SEC filings for {query.ticker}",
            tools=["sec_edgar", "financial_statements"],
            budget_tokens=8000,
            timeout_seconds=300,
        ))

    # Sentiment for anything market-facing
    tasks.append(TeammateTask(
        role="sentiment_analyst",
        model="haiku",  # fast scan
        description=f"News sentiment and social signals for {query.context}",
        tools=["gdelt", "finbert", "news_feeds"],
        budget_tokens=4000,
        timeout_seconds=180,
    ))

    # Risk assessment always runs
    tasks.append(TeammateTask(
        role="risk_assessor",
        model="sonnet",
        description="Monte Carlo VaR, stress testing, correlation analysis",
        tools=["quantlib", "monte_carlo", "vectorbt"],
        budget_tokens=8000,
        timeout_seconds=300,
    ))

    return tasks
```

---

## 3.3 Teammate Agents

Teammates are autonomous agents spawned by the Team Leader for specific analysis tasks. Roles are **not hard-coded** -- the Leader assigns them dynamically based on the query.

### Model Selection

| Task Complexity | Model | Rationale |
|----------------|-------|-----------|
| Data retrieval, structured lookups | Haiku | Fast, cheap, reliable for well-defined tasks |
| Pattern recognition, reasoning | Sonnet | Balanced speed/quality for analytical work |
| Cross-domain synthesis (rare) | Opus | Only if teammate needs Leader-level reasoning |

### Typical Specialist Roles

| Role | Data Sources | Key Tools | Typical Model |
|------|-------------|-----------|---------------|
| Macro Analyst | FRED, EIA, PMI, Treasury | `fred_api`, `eia_api` | Haiku |
| Technical Analyst | Price/volume history | `yfinance`, `ta-lib`, `mplfinance` | Sonnet |
| Fundamental Analyst | 10-K, 10-Q, earnings | `sec_edgar`, `financial_ratios` | Sonnet |
| Sentiment/News Analyst | GDELT, news feeds | `gdelt_api`, `finbert`, `rss` | Haiku |
| Options Strategist | Options chains, IV surface | `quantlib`, `options_chain` | Sonnet |
| Risk Assessor | Portfolio history, correlations | `monte_carlo`, `vectorbt` | Sonnet |
| Backtest Validator | Historical scenarios | `vectorbt`, `backtrader` | Sonnet |

### Teammate Capabilities

All teammates share identical tool access. The role distinction is in the **task description and prompt**, not in permissions. This means:

- Any teammate can call any data source if needed
- A Technical Analyst can pull macro data if relevant to their chart analysis
- A Risk Assessor can check sentiment if it affects their stress scenarios

```python
class TeammateAgent:
    """A single autonomous teammate spawned by the Team Leader."""

    def __init__(self, task: TeammateTask, shared_board: SharedStateBoard):
        self.task = task
        self.board = shared_board
        self.model = self._select_model(task.model)
        self.tools = get_all_tools()  # full tool access
        self.budget = TokenBudget(max_tokens=task.budget_tokens)
        self.timeout = task.timeout_seconds

    async def execute(self) -> None:
        """Run the assigned task and post results to the Shared Board."""
        try:
            result = await self._run_analysis()
            self.board.write(
                slot=self.task.role,
                report=result,
                agent_id=self.id,
            )
        except TimeoutError:
            self.board.write(
                slot=self.task.role,
                report=ErrorReport(reason="timeout", partial=self._partial_results()),
                agent_id=self.id,
            )
        finally:
            self._signal_completion()
```

---

## 3.4 Agent Communication

Agents communicate through two channels: a structured Shared State Board (primary) and direct messages (secondary).

```
  +----------------+       writes        +-------------------+
  | Teammate A     | ------------------> |                   |
  | (Macro)        |                     |   Shared State    |
  +----------------+       writes        |      Board        |
  | Teammate B     | ------------------> |                   |
  | (Technical)    |                     | +---------------+ |
  +----------------+       writes        | | macro_report  | |
  | Teammate C     | ------------------> | | tech_report   | |
  | (Sentiment)    |                     | | sent_report   | |
  +----------------+                     | | risk_report   | |
                                         | | debate_log    | |
       reads all                         | +---------------+ |
  +----------------+                     +-------------------+
  | Team Leader    | <-------- reads all slots
  +----------------+
```

### 3.4.1 Shared State Board (Primary Channel)

The Shared Board uses typed Pydantic models for each report slot. This ensures structured, validated data flows between agents.

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


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


# --- Macro Report ---

class MacroIndicator(BaseModel):
    name: str                          # e.g. "Fed Funds Rate"
    value: float
    previous: float
    trend: str                         # "rising", "falling", "stable"
    source: str                        # "FRED", "EIA", "ISM"
    retrieved_at: datetime

class MacroReport(BaseModel):
    indicators: list[MacroIndicator]
    regime: str                        # "expansion", "contraction", "transition"
    regime_confidence: Confidence
    rate_environment: str              # "tightening", "easing", "neutral"
    summary: str
    impact_on_ticker: str              # how macro environment affects the target


# --- Technical Report ---

class TechnicalIndicator(BaseModel):
    name: str                          # e.g. "RSI_14", "MACD"
    value: float
    signal: Signal
    timeframe: str                     # "1D", "1W", "1M"

class SupportResistance(BaseModel):
    level: float
    type: str                          # "support" or "resistance"
    strength: int                      # 1-5, number of touches

class TechnicalReport(BaseModel):
    ticker: str
    indicators: list[TechnicalIndicator]
    support_resistance: list[SupportResistance]
    trend_direction: str               # "bullish", "bearish", "sideways"
    pattern_detected: str | None       # "head_and_shoulders", "double_bottom", etc.
    signal: Signal
    confidence: Confidence
    summary: str


# --- Sentiment Report ---

class NewsItem(BaseModel):
    headline: str
    source: str
    published_at: datetime
    sentiment_score: float             # -1.0 to 1.0
    relevance_score: float             # 0.0 to 1.0

class SentimentReport(BaseModel):
    ticker: str
    overall_sentiment: float           # -1.0 to 1.0
    sentiment_label: str               # "very_negative" to "very_positive"
    news_volume_zscore: float          # unusual activity detection
    top_stories: list[NewsItem]
    finbert_score: float
    social_buzz: str                   # "high", "normal", "low"
    summary: str


# --- Fundamental Report ---

class FinancialMetric(BaseModel):
    name: str                          # e.g. "P/E", "EV/EBITDA"
    value: float
    sector_median: float
    percentile: int                    # 0-100, rank within sector

class FundamentalReport(BaseModel):
    ticker: str
    metrics: list[FinancialMetric]
    revenue_growth_yoy: float
    earnings_surprise_last: float      # % beat/miss
    debt_to_equity: float
    free_cash_flow: float
    moat_assessment: str               # "wide", "narrow", "none"
    signal: Signal
    confidence: Confidence
    summary: str


# --- Risk Report ---

class RiskReport(BaseModel):
    ticker: str
    var_95_1d: float                   # Value at Risk, 95%, 1-day
    var_99_1d: float
    max_drawdown_1y: float
    sharpe_ratio: float
    beta: float
    correlation_to_spy: float
    monte_carlo_median_return_30d: float
    monte_carlo_p5_return_30d: float   # 5th percentile (worst case)
    stress_scenarios: dict[str, float] # scenario_name -> portfolio impact %
    risk_rating: str                   # "low", "moderate", "high", "extreme"
    summary: str


# --- The Board ---

class SharedStateBoard(BaseModel):
    """Central state that all agents read from and write to."""

    macro_report: MacroReport | None = None
    technical_report: TechnicalReport | None = None
    sentiment_report: SentimentReport | None = None
    fundamental_report: FundamentalReport | None = None
    risk_report: RiskReport | None = None
    options_report: dict | None = None       # OptionsReport when needed
    backtest_report: dict | None = None      # BacktestReport when needed
    debate_log: list[str] = Field(default_factory=list)

    # Metadata
    query_id: str
    ticker: str | None = None
    created_at: datetime
    completed_slots: list[str] = Field(default_factory=list)
```

**Board access rules:**

| Operation | Who | Constraint |
|-----------|-----|------------|
| Write to own slot | Teammate | Append-only, one slot per role |
| Read any slot | All agents | Always allowed |
| Write to `debate_log` | All agents | Append-only list |
| Read `completed_slots` | Team Leader | Used to track progress |

### 3.4.2 Direct Messages (Secondary Channel)

Direct messages handle coordination that doesn't fit the board's structured model.

| Direction | Use Case | Example |
|-----------|----------|---------|
| Leader -> Teammate | Task assignment | "Analyze NVDA with focus on AI capex trends" |
| Leader -> Teammate | Feedback/redirect | "Also check options unusual activity" |
| Teammate -> Leader | Clarification | "Ticker SMCI has two listings, which one?" |
| Teammate -> Leader | Status update | "SEC EDGAR rate limited, retrying in 30s" |
| Teammate -> Teammate | Debate only | "Counter-argument to your bullish thesis..." |

Direct messages use plain text (natural language), unlike the board's typed models.

---

## 3.5 Debate Mechanism

Inspired by the TradingAgents framework, the debate mechanism ensures that investment decisions are stress-tested from opposing viewpoints before synthesis.

### 3.5.1 Investment Debate

```
  Round 1                    Round 2                    Synthesis
  +--------+                +--------+                +----------+
  | Bull   |---thesis------>| Bear   |---rebuttal---->| Research |
  | Agent  |                | Agent  |                | Manager  |
  +--------+                +--------+                +----------+
       ^                         |                         |
       |                         |                         v
       +-----counter-argument----+                  Final Report
```

The debate runs for a configurable number of rounds (default: 2-3):

**Round 1 -- Opening Arguments:**
```
Bull Researcher:
  "NVDA is a strong buy. Revenue grew 122% YoY driven by data center demand.
   AI capex from hyperscalers (MSFT, GOOG, AMZN) is accelerating. Blackwell
   architecture launch adds $10B+ revenue opportunity. P/E of 65 is justified
   by 50%+ forward earnings growth."

Bear Researcher:
  "NVDA is overvalued at current levels. P/E of 65 prices in perfection.
   China export restrictions remove 20% of addressable market. Custom silicon
   (Google TPU, Amazon Trainium) is eroding CUDA moat. Inventory build in
   Q3 suggests demand may be peaking."
```

**Round 2 -- Rebuttals:**
```
Bull Researcher:
  "Re: China restrictions -- NVDA already pivoted to H20 chips for China,
   maintaining revenue. Custom silicon covers <5% of training workloads.
   Inventory build is strategic pre-positioning for Blackwell ramp."

Bear Researcher:
  "Re: Blackwell -- initial yield issues delayed shipments. H20 margins are
   significantly lower than A100/H100. Hyperscaler capex growth is decelerating
   per MSFT/GOOG guidance."
```

**Synthesis by Research Manager:**
```
Research Manager synthesizes:
  Signal: BUY (not STRONG_BUY)
  Confidence: MEDIUM
  Reasoning: Strong growth thesis intact but valuation leaves little room
  for error. Position sizing should be conservative.
  Key risk: Hyperscaler capex deceleration in H2 2025.
```

### 3.5.2 Risk Discussion

After the investment debate, a separate risk discussion evaluates position sizing and risk management.

| Perspective | Focus | Typical Arguments |
|-------------|-------|-------------------|
| Aggressive | Maximize return | Larger position, leverage, short-dated options |
| Neutral | Risk-adjusted return | Moderate position, hedged, defined risk |
| Conservative | Capital preservation | Small position, protective puts, wide stops |

```
  +------------+    +----------+    +--------------+
  | Aggressive |    | Neutral  |    | Conservative |
  | Perspective|    |Perspective|   | Perspective  |
  +-----+------+    +----+-----+    +------+-------+
        |                |                 |
        +--------+-------+---------+-------+
                 |                 |
           +-----v-----+    +-----v-----+
           | Risk Judge |    | Final     |
           | (weights   |--->| Risk      |
           |  by user   |    | Assessment|
           |  profile)  |    +-----------+
           +-----------+
```

The Risk Judge weights perspectives based on the user's risk profile:

```python
RISK_WEIGHTS = {
    "aggressive": {"aggressive": 0.5, "neutral": 0.35, "conservative": 0.15},
    "moderate":   {"aggressive": 0.2, "neutral": 0.5,  "conservative": 0.3},
    "conservative": {"aggressive": 0.1, "neutral": 0.3, "conservative": 0.6},
}
```

### 3.5.3 Structured Data vs. Natural Language

The system uses two distinct formats depending on the communication type:

| Communication Type | Format | Rationale |
|-------------------|--------|-----------|
| Analyst reports | Pydantic models | Precise, typed, no information loss, machine-readable |
| Debate arguments | Natural language | Enables nuanced reasoning, rhetorical structure, edge cases |
| Final synthesis | Both | Structured recommendation + narrative explanation |

```python
class DebateRound(BaseModel):
    """Structured wrapper around natural-language debate."""
    round_number: int
    bull_argument: str           # natural language -- free-form reasoning
    bear_argument: str           # natural language -- free-form reasoning
    key_data_cited: list[str]    # structured -- track what evidence was used

class DebateResult(BaseModel):
    rounds: list[DebateRound]
    synthesis: str               # natural language -- Research Manager's conclusion
    signal: Signal               # structured -- final call
    confidence: Confidence       # structured -- how sure
    key_disagreements: list[str] # structured -- unresolved points
```

---

## 3.6 Agent Lifecycle

Each teammate agent follows a strict lifecycle managed by the Team Leader.

```
                          Leader decides
                          task needed
                              |
                              v
  +-------+  spawn   +-------+-------+  execute  +----------+
  | IDLE  | -------> | INITIALIZING  | --------> | RUNNING  |
  +-------+          +---------------+            +----+-----+
                                                       |
                                         +-------------+-------------+
                                         |             |             |
                                         v             v             v
                                    +---------+  +---------+  +---------+
                                    | SUCCESS |  | TIMEOUT |  |  ERROR  |
                                    +----+----+  +----+----+  +----+----+
                                         |             |             |
                                         v             v             v
                                    +---------+  +---------+  +---------+
                                    | REPORT  |  | PARTIAL |  | REPORT  |
                                    | posted  |  | REPORT  |  | error   |
                                    +----+----+  +----+----+  +----+----+
                                         |             |             |
                                         +------+------+-------------+
                                                |
                                                v
                                         +------+------+
                                         |  RECLAIMED  |
                                         | (shutdown)  |
                                         +-------------+
```

### Lifecycle Stages

| Stage | Description | Leader Action |
|-------|-------------|---------------|
| **IDLE** | No agent exists yet | Leader identifies need for analysis |
| **INITIALIZING** | Agent spawned, loading tools | Leader assigned task + budget |
| **RUNNING** | Agent executing analysis autonomously | Leader monitors timeout/budget |
| **SUCCESS** | Agent completed, posted report to board | Leader reads report |
| **TIMEOUT** | Agent hit time limit | Leader reads partial results if any |
| **ERROR** | Agent failed (API error, budget exhausted) | Leader decides: retry or skip |
| **REPORT** | Results written to Shared Board | Leader confirms slot populated |
| **RECLAIMED** | Agent shut down, resources freed | Pool slot available for reuse |

```python
class AgentLifecycle:
    """Manages the lifecycle of a single teammate agent."""

    async def spawn(self, task: TeammateTask) -> str:
        """Create and start a teammate. Returns agent_id."""
        agent = TeammateAgent(task=task, shared_board=self.board)
        self.active_agents[agent.id] = agent
        asyncio.create_task(self._run_with_timeout(agent))
        return agent.id

    async def _run_with_timeout(self, agent: TeammateAgent) -> None:
        try:
            async with asyncio.timeout(agent.timeout):
                await agent.execute()
                agent.status = AgentStatus.SUCCESS
        except TimeoutError:
            agent.status = AgentStatus.TIMEOUT
        except Exception as e:
            agent.status = AgentStatus.ERROR
            agent.error = str(e)
        finally:
            self._signal_leader(agent)

    async def reclaim(self, agent_id: str) -> None:
        """Shut down agent and free pool slot."""
        agent = self.active_agents.pop(agent_id)
        await agent.cleanup()
        self.pool.release()
```

---

## 3.7 Concurrency Control

The system uses an `AgentPool` to manage resource consumption across concurrent teammate agents.

### Agent Pool

```python
class Priority(int, Enum):
    URGENT = 0      # time-sensitive analysis (earnings, breaking news)
    NORMAL = 1      # standard research tasks
    BACKGROUND = 2  # backtesting, historical comparisons


class AgentPool:
    """Controls concurrent agent execution."""

    def __init__(self, max_concurrent: int = 6):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue: asyncio.PriorityQueue[TeammateTask] = asyncio.PriorityQueue()
        self.active: dict[str, TeammateAgent] = {}
        self.metrics = PoolMetrics()

    async def submit(self, task: TeammateTask) -> str:
        """Submit a task to the pool. Blocks if pool is full."""
        await self.semaphore.acquire()
        agent = TeammateAgent(task=task, shared_board=self.board)
        self.active[agent.id] = agent
        asyncio.create_task(self._run_and_release(agent))
        return agent.id

    async def _run_and_release(self, agent: TeammateAgent) -> None:
        try:
            await agent.execute()
        finally:
            del self.active[agent.id]
            self.semaphore.release()
```

### Resource Limits

| Resource | Default | Configurable | Circuit Breaker |
|----------|---------|--------------|-----------------|
| Max concurrent agents | 6 | `MAX_CONCURRENT_AGENTS` env var | Queue overflow at 20 pending |
| Token budget per agent | 4,000 - 8,000 | Set per task by Leader | Hard cutoff at 2x budget |
| Analysis timeout | 5 minutes | Per task | Kill agent, save partial |
| Data fetch timeout | 30 seconds | Per API call | Skip source, note in report |
| Total session budget | 100,000 tokens | User configurable | Warn at 80%, halt at 100% |

### Priority Queue Behavior

```
  Priority Queue                          Active Agents (max 6)
  +-------------------+                   +---+---+---+---+---+---+
  | [P0] Earnings     | --dequeue--->     | A | B | C | D | E | F |
  | [P1] Technical    |                   +---+---+---+---+---+---+
  | [P1] Fundamental  |     waits              |
  | [P2] Backtest     |     until         Agent finishes
  +-------------------+     slot free     --> slot released
                                          --> next in queue starts
```

### Token Budget Circuit Breaker

```python
class TokenBudget:
    """Per-agent token budget with circuit breaker."""

    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.hard_limit = max_tokens * 2  # circuit breaker
        self.used = 0

    def consume(self, tokens: int) -> None:
        self.used += tokens
        if self.used >= self.hard_limit:
            raise CircuitBreakerError(
                f"Hard limit reached: {self.used}/{self.hard_limit} tokens"
            )

    def warn_if_near_limit(self) -> str | None:
        if self.used >= self.max_tokens * 0.8:
            return f"WARNING: {self.used}/{self.max_tokens} tokens used (80%+)"
        return None

    @property
    def remaining(self) -> int:
        return max(0, self.max_tokens - self.used)
```

### Timeout Hierarchy

```
  Session timeout (30 min)
  |
  +-- Analysis task timeout (5 min)
  |   |
  |   +-- Individual API call timeout (30 sec)
  |   |
  |   +-- LLM inference timeout (60 sec)
  |
  +-- Debate round timeout (3 min per round)
  |
  +-- Synthesis timeout (2 min)
```

If an inner timeout fires, the agent captures partial results and reports them. If the session timeout fires, the Leader synthesizes whatever is available and warns the user about incomplete analysis.

---

# 4. Unified Data Layer

## 4.1 Design Philosophy

The data layer follows a single principle borrowed from OpenBB Platform's architecture: **Connect Once, Consume Everywhere**.

Every financial data source — whether a REST API, a local computation library, or a machine learning model — is integrated through a standard **Fetcher** interface. The raw, provider-specific response is transformed into a **standardized Pydantic model** before any agent or tool ever sees it. This means:

- **Agents never talk to APIs directly.** They request data by type ("price", "fundamentals", "options_chain") and the Provider Registry resolves which source to call.
- **Adding a new source never changes agent code.** Implement a Fetcher, register it, and every agent gains access automatically.
- **All data is automatically exposed as MCP tools.** The registry generates tool definitions from registered Fetchers, so agents discover new data sources without manual wiring.

The design separates three concerns:

| Concern | Handled By |
|---|---|
| What data do I need? | Standardized query models |
| Where does the data come from? | Provider Registry + Fetcher implementations |
| What shape does the data have? | Standardized data models (Pydantic) |

---

## 4.2 TET Pipeline (Transform → Enrich → Tag)

Every Fetcher follows a three-stage pipeline — **Transform, Enrich, Tag** — that isolates provider-specific logic from the rest of the system.

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  transform   │     │   enrich     │     │      tag         │
│   _query     │ ──► │   _data      │ ──► │     _data        │
│              │     │              │     │                  │
│ StandardQuery│     │ ProviderQuery│     │ Enriched Data    │
│ ──► Provider │     │ ──► Enriched │     │ ──► Tagged       │
│    Query     │     │    Data      │     │    Std Models    │
└─────────────┘     └──────────────┘     └──────────────────┘
```

### Base Fetcher Interface

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

QueryIn = TypeVar("QueryIn")       # Standardized query
QueryOut = TypeVar("QueryOut")     # Provider-specific query
DataOut = TypeVar("DataOut")       # Standardized data model

class BaseFetcher(ABC, Generic[QueryIn, QueryOut, DataOut]):
    """Base class for all data fetchers. Implements the TET pipeline."""

    @staticmethod
    @abstractmethod
    def transform_query(params: QueryIn) -> QueryOut:
        """Stage 1: Validate and transform standardized input into
        provider-specific query parameters."""

    @staticmethod
    @abstractmethod
    async def extract_data(query: QueryOut, credentials: dict) -> dict:
        """Stage 2 (Enrich): Make the API call and compute derived fields.
        This is the only stage that touches the network."""

    @staticmethod
    @abstractmethod
    def transform_data(query: QueryOut, data: dict) -> list[DataOut]:
        """Stage 3 (Tag): Normalize enriched response into standardized
        data models and add metadata (source, timestamp, reliability)."""

    async def fetch(self, params: QueryIn, credentials: dict) -> list[DataOut]:
        """Execute the full TET pipeline."""
        query = self.transform_query(params)
        raw = await self.extract_data(query, credentials)
        return self.transform_data(query, raw)
```

### Concrete Example: YFinancePriceFetcher

```python
from datetime import datetime
import yfinance as yf
from pydantic import BaseModel


# --- Query Models ---

class PriceQuery(BaseModel):
    """Standardized query for historical price data."""
    ticker: str
    start_date: datetime
    end_date: datetime
    interval: str = "1d"


class YFinancePriceQuery(PriceQuery):
    """YFinance-specific query. Maps interval names to yfinance format."""
    yf_interval: str = "1d"


# --- Data Models ---

class PriceData(BaseModel):
    """Standardized OHLCV price data."""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class YFinancePriceData(PriceData):
    """YFinance extends standard with adjusted close."""
    adj_close: float | None = None


# --- Fetcher ---

class YFinancePriceFetcher(BaseFetcher[PriceQuery, YFinancePriceQuery, YFinancePriceData]):

    @staticmethod
    def transform_query(params: PriceQuery) -> YFinancePriceQuery:
        # Map standardized interval names to yfinance format
        interval_map = {"1d": "1d", "1h": "1h", "5m": "5m", "1w": "1wk", "1mo": "1mo"}
        return YFinancePriceQuery(
            **params.model_dump(),
            yf_interval=interval_map.get(params.interval, "1d"),
        )

    @staticmethod
    async def extract_data(query: YFinancePriceQuery, credentials: dict) -> dict:
        # yfinance is synchronous — run in executor in production
        ticker = yf.Ticker(query.ticker)
        df = ticker.history(
            start=query.start_date,
            end=query.end_date,
            interval=query.yf_interval,
        )
        return {"records": df.reset_index().to_dict(orient="records")}

    @staticmethod
    def transform_data(query: YFinancePriceQuery, data: dict) -> list[YFinancePriceData]:
        results = []
        for row in data["records"]:
            results.append(YFinancePriceData(
                date=row["Date"],
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=int(row["Volume"]),
                adj_close=row.get("Adj Close"),
            ))
        return results
```

**Why TET instead of ETL?** The first **Transform** validates and adapts the query *before* the network call — catching invalid parameters early and mapping standardized field names to provider-specific ones. **Enrich** makes the API call and computes derived fields (ratios, deltas, moving averages) in one pass. **Tag** normalizes the enriched response into a standard shape and annotates it with metadata: source, timestamp, and reliability score. The pipeline never stores raw data — it flows through and comes out clean and tagged.

---

## 4.3 Standardized Data Models

Every data type has a **Standard model** that defines the fields all providers must populate, and providers can extend it with **Extra fields** specific to their source. Agents code against the standard interface and optionally access extras when available.

### The Standard/Extra Pattern

```python
from datetime import datetime
from pydantic import BaseModel


# Standard model — the contract every provider must fulfill
class PriceData(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


# Provider extension — extra fields available when using this source
class YFinancePriceData(PriceData):
    adj_close: float | None = None       # adjusted for splits/dividends


class PolygonPriceData(PriceData):
    vwap: float | None = None            # volume-weighted average price
    num_transactions: int | None = None   # trade count in the bar
```

Agents receive data typed as the standard model. When a specific provider's extras are needed, the agent can check the concrete type:

```python
prices = await registry.fetch("price", ticker="AAPL", provider="polygon")

for p in prices:
    print(f"{p.date} close={p.close}")   # always available
    if isinstance(p, PolygonPriceData):
        print(f"  vwap={p.vwap}")        # provider-specific
```

### Standard Model Catalog

| Model | Key Fields | Use Case |
|---|---|---|
| **PriceData** | date, open, high, low, close, volume | OHLCV bars for any instrument |
| **FundamentalsData** | ticker, period, revenue, net_income, total_assets, total_liabilities, operating_cashflow | Balance sheet, income statement, cashflow |
| **OptionsChainData** | underlying, expiry, strike, option_type, bid, ask, implied_volatility, delta, gamma, theta, vega | Options chain with Greeks |
| **MacroIndicatorData** | indicator_id, name, date, value, unit, frequency | GDP, CPI, interest rates, employment |
| **NewsEventData** | headline, source, published_at, url, sentiment_score, entities | News articles with extracted entities |
| **SentimentScoreData** | source, target, score, confidence, timestamp | Aggregated sentiment from any source |
| **TechnicalIndicatorData** | indicator, date, value, params | RSI, MACD, Bollinger Bands, any computed indicator |
| **SECFilingData** | ticker, filing_type, filed_at, period, url, sections | 10-K, 10-Q, 13-F parsed filings |

Each model lives in `src/data/models/` and is versioned. When a standard model changes, a migration path is provided for existing Fetcher implementations.

---

## 4.4 Provider Registry

The Provider Registry is the single entry point for all data access. It maintains a mapping of data types to providers, handles credential injection, and supports fallback chains when a provider is unavailable.

### Provider Registration

Each provider declares which Fetcher classes it supports:

```python
from dataclasses import dataclass, field


@dataclass
class Provider:
    """A data source that supplies one or more Fetcher implementations."""
    name: str
    fetchers: dict[str, type[BaseFetcher]] = field(default_factory=dict)
    credentials: dict = field(default_factory=dict)


class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, Provider] = {}
        self._defaults: dict[str, list[str]] = {}  # data_type -> [provider priority]

    def register(self, name: str, provider: Provider) -> None:
        """Register a provider and its fetchers."""
        self._providers[name] = provider
        for data_type in provider.fetchers:
            if data_type not in self._defaults:
                self._defaults[data_type] = []
            self._defaults[data_type].append(name)

    async def fetch(
        self,
        data_type: str,
        *,
        provider: str | None = None,
        providers: list[str] | None = None,
        **params,
    ) -> list:
        """Fetch data by type. Tries providers in order until one succeeds."""
        chain = (
            [provider] if provider
            else providers if providers
            else self._defaults.get(data_type, [])
        )

        last_error = None
        for name in chain:
            prov = self._providers.get(name)
            if not prov or data_type not in prov.fetchers:
                continue
            try:
                fetcher = prov.fetchers[data_type]()
                return await fetcher.fetch(params, prov.credentials)
            except Exception as e:
                last_error = e
                continue

        raise LookupError(
            f"No provider could fulfill '{data_type}': {last_error}"
        )
```

### Usage

```python
# --- Setup: register providers at startup ---

registry = ProviderRegistry()

registry.register("yfinance", Provider(
    name="yfinance",
    fetchers={
        "price": YFinancePriceFetcher,
        "fundamentals": YFinanceFundamentalsFetcher,
        "options_chain": YFinanceOptionsFetcher,
    },
))

registry.register("fred", Provider(
    name="fred",
    fetchers={
        "macro_indicator": FREDIndicatorFetcher,
    },
    credentials={"api_key": os.environ["FRED_API_KEY"]},
))

registry.register("polygon", Provider(
    name="polygon",
    fetchers={
        "price": PolygonPriceFetcher,
        "options_chain": PolygonOptionsFetcher,
    },
    credentials={"api_key": os.environ["POLYGON_API_KEY"]},
))


# --- Usage: agents request data by type ---

# Explicit provider
prices = await registry.fetch("price", ticker="AAPL", provider="yfinance")

# Fallback chain: try Polygon first, fall back to YFinance
prices = await registry.fetch(
    "price", ticker="AAPL", providers=["polygon", "yfinance"]
)

# Use default priority (order of registration)
macro = await registry.fetch(
    "macro_indicator", indicator_id="GDP", start_date="2020-01-01"
)
```

### Auto-Discovery

Providers can be discovered automatically from installed packages using entry points:

```python
from importlib.metadata import entry_points

def auto_discover_providers(registry: ProviderRegistry) -> None:
    """Load all providers registered via Python package entry points."""
    for ep in entry_points(group="finance_agent.providers"):
        provider_cls = ep.load()
        provider = provider_cls()
        registry.register(ep.name, provider)
```

A provider package declares itself in `pyproject.toml`:

```toml
[project.entry-points."finance_agent.providers"]
yfinance = "finance_agent_yfinance:YFinanceProvider"
```

---

## 4.5 Data Source Catalog

| Provider | Data Types | Free Tier Limit | API Key Required |
|---|---|---|---|
| **yfinance** | price, fundamentals, options_chain, dividends | Unlimited | No |
| **FinnHub** | quotes, news, insider_transactions, recommendations | 60 req/min | Yes |
| **Alpha Vantage** | price, forex, crypto, technical_indicators | 25 req/day | Yes |
| **FMP** | financials, DCF, SEC filings, earnings | 250 req/day | Yes |
| **FRED** | macro_indicator (GDP, CPI, interest rates, employment) | Unlimited | Yes |
| **EIA** | energy (crude, natural gas, production, inventories) | Unlimited | Yes |
| **SEC EDGAR** | sec_filing (10-K, 10-Q, 13-F, proxy statements) | 10 req/sec | No |
| **Polygon.io** | price (realtime), options_chain, trades, quotes | 5 req/min | Yes |
| **GDELT** | geopolitical_events, news, global media tone | Unlimited | No |
| **TA-Lib** | technical_indicator (200+ indicators) | Local computation | No |
| **QuantLib** | options_pricing, yield_curves, fixed_income | Local computation | No |
| **vectorbt** | backtest, portfolio_simulation | Local computation | No |
| **pandas-ta** | technical_indicator (130+ indicators) | Local computation | No |
| **FinBERT** | sentiment (financial text classification) | Local model | No |
| **OpenInsider** | insider_transactions | Web scraping | No |

**Priority notes:**

- **Phase 1 (MVP):** yfinance, FRED, SEC EDGAR, TA-Lib/pandas-ta, FinBERT — covers price, macro, filings, technicals, and sentiment with zero API key friction.
- **Phase 2:** FinnHub, Alpha Vantage, FMP, GDELT — adds real-time quotes, richer fundamentals, and geopolitical event data.
- **Phase 3:** Polygon.io, QuantLib, vectorbt, EIA — adds real-time streaming, quantitative options pricing, backtesting, and energy data.

---

## 4.6 Data Flow

The complete path from user query to standardized data:

```
User Query
    │
    ▼
┌──────────────────┐
│   Team Leader    │  "What's the risk/reward on AAPL calls?"
│      Agent       │
└────────┬─────────┘
         │  Decomposes into sub-tasks
         ▼
┌──────────────────┐
│  Specialist Agent │  Options Agent needs: price data + options chain + IV
│  (e.g. Options)  │
└────────┬─────────┘
         │  Calls MCP tools (auto-generated from registry)
         ▼
┌──────────────────┐
│    MCP Tool      │  get_price(ticker="AAPL", interval="1d")
│   Interface      │  get_options_chain(ticker="AAPL", expiry="2026-04-17")
└────────┬─────────┘
         │  Routes to registry
         ▼
┌──────────────────┐
│    Provider      │  Resolves: price → yfinance, options → polygon (fallback: yfinance)
│    Registry      │
└────────┬─────────┘
         │  Instantiates Fetcher, passes credentials
         ▼
┌──────────────────────────────────────────────┐
│              Fetcher (TET Pipeline)           │
│                                               │
│  ┌─────────────┐  ┌──────────┐  ┌──────────┐│
│  │ transform   │→ │ enrich   │→ │ tag      ││
│  │  _query     │  │  _data   │  │  _data    ││
│  │             │  │          │  │           ││
│  │ Standard    │  │ API Call │  │ Enriched  ││
│  │ → Provider  │  │ +Enrich  │  │ → Tagged  ││
│  └─────────────┘  └──────────┘  └──────────┘│
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  Standardized    │  list[PriceData], list[OptionsChainData]
│   Data Models    │
└────────┬─────────┘
         │  Returned to agent
         ▼
┌──────────────────┐
│  Specialist Agent │  Combines price + options data → analysis
│  (e.g. Options)  │
└────────┬─────────┘
         │  Returns findings
         ▼
┌──────────────────┐
│   Team Leader    │  Synthesizes across all specialist agents
│      Agent       │
└────────┬─────────┘
         │
         ▼
    Final Analysis
    with recommendation,
    confidence, and
    risk quantification
```

### MCP Tool Auto-Generation

The registry automatically exposes each registered data type as an MCP tool. When a new Fetcher is registered, a corresponding tool definition is generated from the query model's schema:

```python
def generate_mcp_tools(registry: ProviderRegistry) -> list[dict]:
    """Generate MCP tool definitions from all registered fetchers."""
    tools = []
    for data_type, provider_names in registry._defaults.items():
        # Use the first provider's fetcher to get the query schema
        prov = registry._providers[provider_names[0]]
        fetcher_cls = prov.fetchers[data_type]

        # Extract input schema from the query model's type hints
        query_type = fetcher_cls.__orig_bases__[0].__args__[0]
        schema = query_type.model_json_schema()

        tools.append({
            "name": f"get_{data_type}",
            "description": f"Fetch {data_type} data. Available providers: {provider_names}",
            "inputSchema": {
                **schema,
                "properties": {
                    **schema.get("properties", {}),
                    "provider": {
                        "type": "string",
                        "enum": provider_names,
                        "description": "Preferred data provider",
                    },
                },
            },
        })
    return tools
```

This means agents never need hardcoded knowledge of available data sources. They discover tools through MCP, and the registry handles routing, credential injection, and fallback logic behind the scenes.

---

# 5. Tool System

## 5.1 Tool Architecture

Finance Agent organizes its tools into three tiers based on usage frequency and loading cost.

### Tier 1 -- Core Tools (Always Loaded)

Core tools are loaded into every agent context regardless of query type. These are the ~15 tools essential for basic operation: search, retrieval, calculation, formatting, and agent coordination.

| Tool | Purpose |
|---|---|
| `search_knowledge_graph` | Query the entity-relationship graph |
| `update_knowledge_graph` | Add entities/relationships to the graph |
| `get_stock_price` | Current/historical price data |
| `get_market_snapshot` | Broad market overview (indices, sectors, VIX) |
| `web_search` | General web search for news and context |
| `get_news` | Financial news by ticker or topic |
| `calculate` | Evaluate mathematical expressions |
| `convert_currency` | FX conversion at live rates |
| `format_table` | Structure data into markdown tables |
| `create_chart` | Generate visualizations (price charts, scatter plots) |
| `delegate_to_agent` | Spawn or message a teammate agent |
| `read_shared_state` | Read from the shared agent state |
| `write_shared_state` | Write to the shared agent state |
| `get_calendar` | Upcoming earnings, economic events, ex-div dates |
| `lookup_ticker` | Resolve company name/CUSIP/ISIN to ticker symbol |

### Tier 2 -- Domain Tools (Loaded on Demand)

Domain tools are specialized financial tools grouped by analytical domain. They are loaded only when the query requires them, based on intent classification. See [Section 5.2](#52-tool-loading-strategy) for the loading mechanism.

### Tier 3 -- External Tools (via MCP)

External data source tools exposed through MCP servers. These wrap third-party APIs and data providers, giving agents access to live market data, economic indicators, and alternative data without coupling tool definitions to specific provider implementations. See [Section 5.4](#54-mcp-server-design) for details.

---

## 5.2 Tool Loading Strategy

### The Problem

A full financial analysis platform requires 30-60 specialized tools. Loading all of them into every agent context creates two problems:

1. **Token cost.** Each tool's JSON schema averages ~900 tokens (name, description, parameter definitions, enum values). With 60 tools, that is **~54K tokens** consumed before the conversation even starts — 27% of a 200K context window.
2. **Selection degradation.** LLMs degrade in tool selection accuracy beyond 20-30 tools. More tools means more confusion about which to call, more hallucinated parameters, and more wasted turns.

### The Solution: Core + Group-Based Loading

Finance Agent uses a two-phase approach:

**Phase 1 -- Intent Classification (Haiku, ~50ms)**

Before the main agent sees the query, a fast classifier (Claude Haiku) analyzes the user's message and determines which tool groups are relevant. This is a simple classification task, not a full analysis.

```python
INTENT_PROMPT = """Classify which tool groups are needed for this query.
Return a JSON list of group names from:
[market_data, fundamentals, technical, options, macro, sentiment, risk_backtest]

Query: {user_query}
"""

# Example: "What's the RSI and MACD for AAPL?" → ["market_data", "technical"]
# Example: "Run a Monte Carlo on my portfolio" → ["risk_backtest"]
# Example: "Analyze NVDA earnings vs guidance" → ["fundamentals", "sentiment"]
```

**Phase 2 -- Selective Loading**

The agent is initialized with the 15 core tools plus only the tool groups flagged by the classifier. If additional groups are needed mid-conversation, the agent can request them explicitly.

### Tool Groups

| Group | Tools (count) | Trigger |
|---|---|---|
| **Market Data** | `get_stock_price`, `get_ohlcv`, `get_realtime_quote`, `get_historical_data`, `get_market_depth`, `get_sector_performance`, `get_index_constituents`, `get_premarket_data` (8) | Any ticker symbol mentioned or price-related query |
| **Fundamentals** | `get_income_stmt`, `get_balance_sheet`, `get_cashflow`, `get_sec_filing`, `get_earnings_history`, `get_analyst_estimates`, `get_company_profile`, `screen_stocks` (8) | Valuation, earnings, financial statement, or fundamental analysis queries |
| **Technical Analysis** | `calculate_rsi`, `calculate_macd`, `get_bollinger_bands`, `calculate_sma_ema`, `detect_patterns`, `get_support_resistance`, `calculate_atr`, `get_fibonacci_levels` (8) | Chart patterns, indicators, technical setup queries |
| **Options** | `get_options_chain`, `price_option`, `calculate_greeks`, `get_iv_surface`, `build_strategy`, `analyze_spread` (6) | Options pricing, strategy, Greeks, implied volatility queries |
| **Macro** | `get_fred_data`, `get_eia_data`, `get_pmi`, `get_yield_curve`, `get_fx_rates`, `get_global_macro` (6) | Macroeconomic, rates, inflation, GDP, central bank queries |
| **Sentiment/News** | `get_sentiment`, `search_gdelt`, `get_insider_trades`, `get_social_mentions`, `get_analyst_ratings` (5) | Sentiment analysis, news impact, insider activity queries |
| **Risk/Backtest** | `run_backtest`, `monte_carlo_sim`, `calculate_var`, `stress_test`, `calculate_sharpe` (5) | Portfolio risk, backtesting, simulation queries |

### Token Math

| Configuration | Tool Count | Approx. Tokens | % of 200K Context |
|---|---|---|---|
| All 60 tools upfront | 60 | ~54,000 | 27.0% |
| Core 15 + 1 group (avg 7) | 22 | ~20,000 | 10.0% |
| Core 15 + 2 groups (avg 14) | 29 | ~26,000 | 13.0% |
| Core 15 only | 15 | ~13,500 | 6.75% |

**Typical savings: ~63% token reduction per query** compared to loading all tools. Most queries activate 1-2 groups, keeping the tool context well under 30K tokens.

---

## 5.3 Tool Definition Pattern

Tools are defined as async functions decorated with `@function_tool`. The decorator extracts the function signature and docstring to auto-generate the JSON schema that gets passed to the LLM.

```python
from agents import function_tool
from finance_agent.registry import registry


@function_tool
async def get_stock_price(ticker: str, period: str = "1d") -> dict:
    """Get current or historical stock price data.

    Args:
        ticker: Stock symbol (e.g., "AAPL", "GOOGL")
        period: Time period - "1d", "5d", "1mo", "3mo", "1y", "5y"

    Returns:
        Dict with price data including open, high, low, close, volume
    """
    return await registry.fetch("price", ticker=ticker, period=period)


@function_tool
async def calculate_greeks(
    ticker: str,
    strike: float,
    expiry: str,
    option_type: str = "call",
    model: str = "black_scholes",
) -> dict:
    """Calculate options Greeks for a specific contract.

    Args:
        ticker: Underlying stock symbol
        strike: Strike price
        expiry: Expiration date (YYYY-MM-DD)
        option_type: "call" or "put"
        model: Pricing model - "black_scholes" or "binomial"

    Returns:
        Dict with delta, gamma, theta, vega, rho and theoretical price
    """
    return await registry.fetch(
        "greeks",
        ticker=ticker,
        strike=strike,
        expiry=expiry,
        option_type=option_type,
        model=model,
    )
```

### Tool Group Registration

Tools are organized into groups via a simple registry:

```python
from finance_agent.tools.registry import ToolGroup

market_data_tools = ToolGroup(
    name="market_data",
    description="Real-time and historical market data",
    tools=[
        get_stock_price,
        get_ohlcv,
        get_realtime_quote,
        get_historical_data,
        get_market_depth,
        get_sector_performance,
        get_index_constituents,
        get_premarket_data,
    ],
)

# At agent initialization:
active_tools = core_tools + load_groups(classified_groups)
agent = Agent(name="analyst", tools=active_tools, ...)
```

---

## 5.4 MCP Server Design

Data providers are exposed to agents through MCP (Model Context Protocol) servers. This decouples tool definitions from provider implementations and allows external data sources to be added without modifying agent code.

### Architecture

Each major data domain runs as an MCP server. Agents connect to these servers and see their tools alongside locally-defined tools.

```
Agent
  ├── Local Tools (Tier 1 core + Tier 2 domain)
  └── MCP Connections
        ├── market-data-server   (prices, quotes, OHLCV)
        ├── fundamentals-server  (financials, SEC filings)
        ├── macro-server         (FRED, EIA, global macro)
        ├── sentiment-server     (GDELT, news, social)
        └── options-server       (chains, IV surface, pricing)
```

### MCP Tool Definition

MCP tools are auto-generated from the Provider Registry. Each registry capability becomes an MCP tool with the provider selectable as a parameter:

```python
from mcp.server import Server

mcp = Server("market-data-server")


@mcp.tool()
async def market_get_price(
    ticker: str, period: str = "1d", provider: str = "yfinance"
) -> dict:
    """Get stock price data from the market data server.

    Args:
        ticker: Stock symbol (e.g., "AAPL")
        period: Time period - "1d", "5d", "1mo", "3mo", "1y", "5y"
        provider: Data provider - "yfinance", "polygon", "alpha_vantage"
    """
    return await registry.fetch("price", ticker=ticker, period=period, provider=provider)


@mcp.tool()
async def market_get_ohlcv(
    ticker: str,
    interval: str = "1d",
    start: str | None = None,
    end: str | None = None,
    provider: str = "yfinance",
) -> dict:
    """Get OHLCV candlestick data.

    Args:
        ticker: Stock symbol
        interval: Candle interval - "1m", "5m", "15m", "1h", "1d", "1wk"
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        provider: Data provider
    """
    return await registry.fetch(
        "ohlcv", ticker=ticker, interval=interval, start=start, end=end, provider=provider
    )
```

### Unified vs. Multi-Server

The system supports both configurations:

| Approach | Pros | Cons |
|---|---|---|
| **One server per domain** | Isolated failures, independent scaling, clear ownership | More processes to manage, cross-domain queries need multiple connections |
| **Single unified server** | Simpler deployment, single connection, easier local dev | Single point of failure, larger process |

Default: **unified server for local development**, split servers for production deployment.

### Namespacing Convention

MCP tools use a `{domain}_{action}` naming pattern to avoid collisions when multiple servers are connected:

- `market_get_price`, `market_get_ohlcv`, `market_get_depth`
- `fundamentals_get_income_stmt`, `fundamentals_get_balance_sheet`
- `macro_get_fred`, `macro_get_yield_curve`
- `sentiment_get_news`, `sentiment_search_gdelt`
- `options_get_chain`, `options_price`

---

## 5.5 Complete Tool Catalog

### Market Data (8 tools)

| Tool Name | Description | Primary Data Source |
|---|---|---|
| `get_stock_price` | Current/historical price with OHLCV | yfinance, Polygon |
| `get_ohlcv` | Candlestick data at configurable intervals | yfinance, Polygon |
| `get_realtime_quote` | Real-time bid/ask/last with volume | Polygon WebSocket |
| `get_historical_data` | Extended historical price series (20+ years) | yfinance, EODHD |
| `get_market_depth` | Level 2 order book (top-of-book) | Polygon |
| `get_sector_performance` | Sector/industry returns over configurable periods | yfinance, Finviz |
| `get_index_constituents` | List of tickers in an index (S&P 500, Nasdaq 100, etc.) | Wikipedia, Polygon |
| `get_premarket_data` | Pre-market/after-hours price and volume | Polygon |

### Fundamentals (8 tools)

| Tool Name | Description | Primary Data Source |
|---|---|---|
| `get_income_stmt` | Income statement (annual/quarterly) | yfinance, SEC EDGAR |
| `get_balance_sheet` | Balance sheet snapshot | yfinance, SEC EDGAR |
| `get_cashflow` | Cash flow statement | yfinance, SEC EDGAR |
| `get_sec_filing` | Raw SEC filing text (10-K, 10-Q, 8-K) | SEC EDGAR |
| `get_earnings_history` | Historical EPS actuals vs. estimates | yfinance |
| `get_analyst_estimates` | Consensus revenue/EPS estimates and target prices | yfinance, Finviz |
| `get_company_profile` | Company overview, industry, employees, description | yfinance |
| `screen_stocks` | Screen stocks by financial criteria (P/E, market cap, etc.) | Finviz |

### Technical Analysis (8 tools)

| Tool Name | Description | Primary Data Source |
|---|---|---|
| `calculate_rsi` | Relative Strength Index over configurable period | Computed (ta-lib) |
| `calculate_macd` | MACD line, signal line, histogram | Computed (ta-lib) |
| `get_bollinger_bands` | Upper/middle/lower Bollinger Bands | Computed (ta-lib) |
| `calculate_sma_ema` | Simple and exponential moving averages | Computed (ta-lib) |
| `detect_patterns` | Candlestick pattern detection (doji, hammer, engulfing, etc.) | Computed (ta-lib) |
| `get_support_resistance` | Key support/resistance price levels | Computed (custom) |
| `calculate_atr` | Average True Range (volatility measure) | Computed (ta-lib) |
| `get_fibonacci_levels` | Fibonacci retracement/extension levels | Computed (custom) |

### Options (6 tools)

| Tool Name | Description | Primary Data Source |
|---|---|---|
| `get_options_chain` | Full options chain with bid/ask/volume/OI | yfinance, CBOE |
| `price_option` | Theoretical option price (Black-Scholes or binomial) | Computed (QuantLib) |
| `calculate_greeks` | Delta, gamma, theta, vega, rho for a contract | Computed (QuantLib) |
| `get_iv_surface` | Implied volatility surface (strike x expiry) | Computed (QuantLib) |
| `build_strategy` | Construct multi-leg option strategy (spread, straddle, condor) | Computed (custom) |
| `analyze_spread` | P&L profile, max profit/loss, breakevens for a spread | Computed (custom) |

### Macro (6 tools)

| Tool Name | Description | Primary Data Source |
|---|---|---|
| `get_fred_data` | Any FRED series (GDP, CPI, unemployment, fed funds rate, etc.) | FRED API |
| `get_eia_data` | Energy data (crude inventories, production, demand) | EIA API |
| `get_pmi` | Purchasing Managers' Index (manufacturing/services) | ISM via FRED |
| `get_yield_curve` | Treasury yield curve (2Y, 5Y, 10Y, 30Y) with spread calculations | FRED API |
| `get_fx_rates` | Foreign exchange rates and cross rates | ECB, yfinance |
| `get_global_macro` | Cross-country macro comparison (GDP growth, inflation, rates) | World Bank, FRED |

### Sentiment & News (5 tools)

| Tool Name | Description | Primary Data Source |
|---|---|---|
| `get_sentiment` | Aggregated sentiment score for a ticker or topic | News API + LLM |
| `search_gdelt` | Search global events database for geopolitical signals | GDELT API |
| `get_insider_trades` | Recent insider buying/selling (Form 4 filings) | SEC EDGAR |
| `get_social_mentions` | Social media mention volume and sentiment | Reddit, StockTwits |
| `get_analyst_ratings` | Recent analyst upgrades/downgrades/initiations | Finviz, yfinance |

### Risk & Backtesting (5 tools)

| Tool Name | Description | Primary Data Source |
|---|---|---|
| `run_backtest` | Backtest a strategy over historical data | Computed (vectorbt) |
| `monte_carlo_sim` | Monte Carlo simulation for portfolio outcomes | Computed (NumPy) |
| `calculate_var` | Value at Risk (historical, parametric, or Monte Carlo) | Computed (custom) |
| `stress_test` | Apply historical stress scenarios (2008, COVID, etc.) to portfolio | Computed (custom) |
| `calculate_sharpe` | Risk-adjusted return metrics (Sharpe, Sortino, max drawdown) | Computed (custom) |

### Utility (4 tools)

| Tool Name | Description | Primary Data Source |
|---|---|---|
| `calculate` | Evaluate mathematical expressions and financial formulas | Computed (Python) |
| `convert_currency` | Currency conversion at live or historical rates | ECB, yfinance |
| `format_table` | Structure data into a formatted markdown table | Computed |
| `create_chart` | Generate price charts, scatter plots, distribution plots | Computed (matplotlib) |

**Total: 50 tools** across 8 groups.

---

## 5.6 Tool Execution Flow

```
User Query
    │
    ▼
┌─────────────────────────┐
│  Intent Classification  │  Haiku classifies query → selects tool groups
│  (Claude Haiku, ~50ms)  │
└───────────┬─────────────┘
            │ ["market_data", "technical"]
            ▼
┌─────────────────────────┐
│  Agent Initialization   │  Core tools (15) + selected group tools loaded
│  Tool Context Assembly  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Agent Reasoning Loop   │  Agent decides which tool to call
│  (Claude Sonnet/Opus)   │
└───────────┬─────────────┘
            │ tool_call: get_stock_price(ticker="AAPL", period="1mo")
            ▼
┌─────────────────────────┐
│  Schema Validation      │  Validate parameters against tool JSON schema
│                         │  Type checking, enum validation, required fields
└───────────┬─────────────┘
            │ validated params
            ▼
┌─────────────────────────┐
│  Provider Registry      │  Route to best available data provider
│  (Failover + Caching)   │  Check cache → primary provider → fallback
└───────────┬─────────────┘
            │ raw data
            ▼
┌─────────────────────────┐
│  Result Formatting      │  Normalize response to standard schema
│                         │  Add metadata (source, timestamp, latency)
└───────────┬─────────────┘
            │ formatted result
            ▼
┌─────────────────────────┐
│  Back to Agent Loop     │  Agent processes result, decides next action
│                         │  May call another tool or produce final answer
└─────────────────────────┘
```

### Error Handling

When a tool call fails, the system follows a structured recovery path:

1. **Retry with fallback provider** — if the primary provider times out or errors, the registry automatically tries the next provider.
2. **Return structured error** — if all providers fail, the tool returns a structured error message (not an exception) so the agent can reason about the failure.
3. **Agent adapts** — the agent sees the error and can try an alternative tool, use cached data, or inform the user about data unavailability.

```python
# Example: structured error returned to agent
{
    "error": "provider_unavailable",
    "message": "Polygon API rate limit exceeded. Fallback to yfinance also failed (timeout).",
    "suggestion": "Try again in 60 seconds or use get_historical_data for delayed data.",
    "attempted_providers": ["polygon", "yfinance"],
}
```

### Caching Layer

Tool results are cached at two levels:

| Cache Level | TTL | Scope |
|---|---|---|
| **Request cache** | Duration of the analysis session | Prevents duplicate API calls within a single multi-agent analysis |
| **Data cache** | Varies by data type (1min for quotes, 1hr for fundamentals, 24hr for filings) | Shared across sessions, reduces API costs |

Cache keys are derived from the tool name and normalized parameters, so `get_stock_price("AAPL", "1d")` and `get_stock_price("aapl", "1d")` hit the same cache entry.

---

# 6. Memory & Storage System

## 6.1 Storage Architecture Overview

Finance Agent uses a hybrid storage strategy. Each data shape gets the store best suited to its access patterns — no single database handles everything well.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STORAGE LAYER                                    │
│                                                                         │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐   │
│  │    Neo4j (KG)      │  │  ChromaDB (Vector) │  │  DuckDB (Series)  │   │
│  │                    │  │                    │  │                    │   │
│  │  Company ──► Sector │  │  News articles     │  │  OHLCV prices     │   │
│  │  Company ──► Peers  │  │  SEC filings       │  │  Technical indic. │   │
│  │  Event ──► Commodity│  │  Earnings calls    │  │  Macro indicators │   │
│  │  Macro ──► Sector   │  │  Analysis reports  │  │  Backtest results │   │
│  │  Exec ──► Company   │  │  Research notes    │  │  Factor returns   │   │
│  │                    │  │                    │  │                    │   │
│  │  Multi-hop queries  │  │  Semantic search   │  │  Analytical SQL   │   │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────┐  ┌──────────────────────────────┐  │
│  │   SQLite WAL (Shared Board)     │  │   In-Memory (Scratchpads)    │  │
│  │                                 │  │                              │  │
│  │  Findings   — agent discoveries │  │  Per-agent working notes     │  │
│  │  Decisions  — immutable log     │  │  Intermediate calculations   │  │
│  │  Data Cache — TTL-based dedup   │  │  Draft findings before post  │  │
│  │  Alerts     — real-time events  │  │  Prompt context assembly     │  │
│  │                                 │  │                              │  │
│  │  Team coordination layer        │  │  Ephemeral, dies with agent  │  │
│  └─────────────────────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Store Selection Rules

| Question you're asking | Store | Why |
|---|---|---|
| "What companies are in Apple's supply chain?" | Neo4j | Multi-hop entity traversal |
| "What did the Fed chair say about inflation last week?" | ChromaDB | Semantic search over text |
| "What was AAPL's 20-day moving average on March 1?" | DuckDB | Time series analytical query |
| "What has the team found so far about TSLA?" | SQLite Board | Session state, cross-agent coordination |
| "I'm still computing this ratio, not ready to share" | In-Memory | Agent-private working state |

---

## 6.2 Knowledge Graph (Neo4j)

The knowledge graph stores entity relationships that enable multi-hop reasoning — the kind of queries that are impossible with flat data and painful with SQL joins.

### What Goes in the KG

- **Company → Sector → Industry** hierarchies (GICS classification)
- **Company → Company** relationships: supply chain links, competitive overlap, ownership stakes, joint ventures
- **Macro Indicator → Sector** impact chains: Fed funds rate → Banking profitability, Oil price → Airlines cost structure
- **Executive → Company** relationships: CEO/CFO/Board memberships, insider transactions
- **Geopolitical Event → Commodity → Sector → Company** transmission chains
- **Country → Trade Policy → Industry** exposure mappings

### Entity Types

| Entity | Description | Key Properties |
|---|---|---|
| `Company` | Publicly traded companies | ticker, name, market_cap, sector, country |
| `Sector` | GICS sectors | name, code |
| `Industry` | GICS sub-industries | name, code, parent_sector |
| `Executive` | C-suite, board members | name, title, tenure_start |
| `MacroIndicator` | Economic data series | name, source, frequency, latest_value |
| `GeopoliticalEvent` | Wars, sanctions, elections, treaties | name, region, start_date, severity |
| `Commodity` | Oil, gold, copper, wheat, etc. | name, unit, latest_price |
| `Country` | Nation-states | name, iso_code, gdp, region |
| `FinancialInstrument` | ETFs, indices, futures | ticker, type, underlying |

### Relationship Types

| Relationship | From → To | Example | Properties |
|---|---|---|---|
| `BELONGS_TO` | Company → Sector | AAPL → Technology | — |
| `COMPETES_WITH` | Company → Company | AAPL → MSFT | overlap_pct |
| `SUPPLIES_TO` | Company → Company | TSMC → AAPL | revenue_dependency |
| `IMPACTS` | MacroIndicator → Sector | Fed Rate → Banking | direction, lag_months |
| `LEADS` | Executive → Company | Tim Cook → AAPL | title, since |
| `OWNS_STAKE_IN` | Company → Company | BRK.B → AAPL | pct_ownership, shares |
| `PRODUCES` | Country → Commodity | Saudi Arabia → Oil | pct_global_supply |
| `EXPOSED_TO` | Company → Commodity | DAL → Jet Fuel | cost_pct_revenue |
| `TRIGGERS` | GeopoliticalEvent → Commodity | Hormuz Tension → Oil | probability, impact |
| `TRADED_IN` | Company → Country | TSMC → Taiwan | revenue_pct |
| `TRACKS` | FinancialInstrument → Sector | XLF → Financials | — |

### When to Query the KG

The KG answers questions that require traversing relationships across entities. If your question involves "which... because of..." or "what gets affected if...", it's a KG query.

**Use KG for:**

```
Multi-hop reasoning
  "Which S&P 500 companies have supply chain exposure to Taiwan?"
  → Company -[:SUPPLIES_TO]-> Company -[:TRADED_IN]-> Country{name:'Taiwan'}

Entity relationships
  "Who are Apple's competitors and suppliers?"
  → Company{ticker:'AAPL'} -[:COMPETES_WITH|SUPPLIES_TO]- Company

Transmission chains
  "If oil prices spike 30%, what sectors and companies are most affected?"
  → Commodity{name:'Oil'} <-[:EXPOSED_TO]- Company
  → Commodity{name:'Oil'} -[:IMPACTS]-> Sector
```

**Don't use KG for:**
- Price data or technical indicators → DuckDB
- Full-text search over filings/news → ChromaDB
- Current session findings → SQLite Board

### Example Cypher Queries

```cypher
// Find companies with supply chain exposure to Taiwan
MATCH (c:Company)-[:SUPPLIES_TO*1..3]->(supplier:Company)-[:TRADED_IN]->(country:Country {name: 'Taiwan'})
WHERE c.market_cap > 10e9
RETURN c.ticker, c.name, supplier.ticker, supplier.name
ORDER BY c.market_cap DESC

// Trace oil price transmission chain
MATCH (oil:Commodity {name: 'Crude Oil'})<-[e:EXPOSED_TO]-(c:Company)
WHERE e.cost_pct_revenue > 0.1
RETURN c.ticker, c.sector, e.cost_pct_revenue
ORDER BY e.cost_pct_revenue DESC

// Find all companies led by executives who also sit on another board
MATCH (e:Executive)-[:LEADS]->(c1:Company),
      (e)-[:LEADS]->(c2:Company)
WHERE c1 <> c2
RETURN e.name, c1.ticker, c2.ticker
```

---

## 6.3 Vector Store (ChromaDB)

ChromaDB handles semantic search over unstructured and semi-structured text. When an agent needs to find documents by meaning rather than exact keywords, it queries the vector store.

### What Goes in the Vector Store

| Document Type | Chunking Strategy | Metadata Fields |
|---|---|---|
| News articles | 512-token chunks with 64-token overlap | source, date, tickers_mentioned, sentiment |
| SEC filings (10-K, 10-Q) | Section-level chunks (MD&A, Risk Factors, etc.) | ticker, filing_type, section, filing_date |
| Earnings call transcripts | Speaker-turn chunks (Q&A separated from prepared) | ticker, quarter, speaker, section |
| Analyst reports | 512-token chunks | source, ticker, rating, target_price, date |
| System-generated analysis | Full report as single document | analysis_id, tickers, date, agent_id |

### Collections

```
finance_agent_vectorstore/
├── news/              # News articles and press releases
├── sec_filings/       # 10-K, 10-Q, 8-K section chunks
├── earnings_calls/    # Transcript chunks
├── analyst_reports/   # Third-party research
└── system_reports/    # Our own generated analysis reports
```

### When to Query the Vector Store

```
Semantic similarity
  "Find previous analyses similar to this bull thesis on semiconductors"
  → search system_reports collection, embed the thesis, return top-k

Document retrieval by meaning
  "What did Apple say about AI in their last 10-K?"
  → search sec_filings, filter ticker=AAPL, filing_type=10-K, query="artificial intelligence strategy"

Cross-reference
  "Find news articles that discuss the same supply chain risks mentioned in TSMC's risk factors"
  → retrieve TSMC risk factors from sec_filings, use as query against news collection
```

### Embedding Model

Sentence-transformers `all-MiniLM-L6-v2` for initial implementation (384 dimensions, fast, good quality). Can upgrade to OpenAI `text-embedding-3-small` or Cohere `embed-english-v3.0` if retrieval quality requires it.

---

## 6.4 Time Series Store (DuckDB)

DuckDB is the analytical engine for all numerical time series data. It handles the heavy lifting for price data, indicators, and backtesting results.

### What Goes in DuckDB

| Table | Description | Grain |
|---|---|---|
| `ohlcv` | Price data (open, high, low, close, volume) | ticker × date |
| `technical_indicators` | SMA, EMA, RSI, MACD, Bollinger, etc. | ticker × date × indicator |
| `macro_series` | GDP, CPI, unemployment, Fed rate, etc. | series_id × date |
| `backtest_results` | Strategy performance over historical periods | strategy_id × date |
| `factor_returns` | Fama-French, momentum, quality, etc. | factor × date |
| `options_snapshots` | Historical options chain snapshots | ticker × date × strike × expiry |

### Why DuckDB

| Requirement | DuckDB Capability |
|---|---|
| Fast aggregations over millions of rows | Columnar storage with vectorized execution |
| Window functions for rolling calculations | Full SQL window function support |
| Zero deployment complexity | Embedded, single-file database, no server process |
| Load large historical datasets | Native Parquet file reader, memory-mapped I/O |
| No external dependencies | Ships as a single Python package (`pip install duckdb`) |

### Example Queries

```sql
-- 20-day simple moving average for AAPL
SELECT date, close,
       AVG(close) OVER (
         PARTITION BY ticker
         ORDER BY date
         ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
       ) AS sma_20
FROM ohlcv
WHERE ticker = 'AAPL'
  AND date >= '2025-01-01'
ORDER BY date;

-- Compare sector performance over trailing 90 days
SELECT s.name AS sector,
       ROUND((MAX(o.close) / FIRST(o.close ORDER BY o.date) - 1) * 100, 2) AS return_pct
FROM ohlcv o
JOIN companies c ON o.ticker = c.ticker
JOIN sectors s ON c.sector_id = s.id
WHERE o.date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY s.name
ORDER BY return_pct DESC;

-- Detect RSI divergence: price making new highs but RSI declining
WITH ranked AS (
  SELECT ticker, date, close,
         MAX(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS high_20,
         rsi_14
  FROM ohlcv
  JOIN technical_indicators USING (ticker, date)
  WHERE indicator = 'RSI_14'
)
SELECT ticker, date, close, rsi_14
FROM ranked
WHERE close = high_20
  AND rsi_14 < LAG(rsi_14, 20) OVER (PARTITION BY ticker ORDER BY date);
```

### Storage Layout

```
data/
├── duckdb/
│   ├── finance.duckdb          # Main database file
│   └── parquet/
│       ├── ohlcv/              # Partitioned by year: ohlcv_2024.parquet, ohlcv_2025.parquet
│       ├── macro/              # Macro series parquet files
│       └── options/            # Options chain snapshots (large, kept external)
```

DuckDB queries Parquet files directly without importing them. This lets us store large historical datasets on disk without bloating the database file.

---

## 6.5 Shared Board (SQLite WAL)

The Shared Board is the team coordination layer. It's how agents communicate findings, record decisions, share cached data, and broadcast alerts. SQLite with Write-Ahead Logging (WAL) mode provides concurrent read access from multiple agents with serialized writes — good enough for our concurrency model where agents read often and write occasionally.

### 6.5.1 Findings Board (Append-Only)

Every agent posts its discoveries here. Other agents (and the Team Leader during synthesis) read from this board to build a complete picture.

```python
@dataclass
class Finding:
    id: str                    # UUID
    agent_id: str              # "fundamental_analyst", "technical_analyst", etc.
    category: str              # "market", "fundamental", "sentiment", "risk", "options", "macro"
    ticker: Optional[str]      # None for macro/cross-market findings
    summary: str               # One-line human-readable summary
    data: dict                 # Structured payload (varies by category)
    confidence: float          # 0.0 to 1.0
    timestamp: datetime        # When this finding was posted
    tags: list[str]            # Free-form tags for filtering: ["bearish", "earnings", "guidance"]
```

**Rules:**
- Append-only. Agents never edit or delete findings. This preserves the full analytical record.
- Each finding has a unique ID so other findings and decisions can reference it.
- The `data` dict schema varies by category — fundamental findings contain financial ratios, technical findings contain price levels and indicators, etc.

**Example finding:**

```python
Finding(
    id="f-3a7c",
    agent_id="fundamental_analyst",
    category="fundamental",
    ticker="AAPL",
    summary="AAPL FCF yield at 3.8%, below 5-year avg of 4.5%. Valuation stretched relative to history.",
    data={
        "fcf_yield": 0.038,
        "fcf_yield_5y_avg": 0.045,
        "pe_ratio": 31.2,
        "pe_5y_avg": 27.8,
        "revenue_growth_yoy": 0.06,
    },
    confidence=0.82,
    timestamp=datetime(2026, 3, 23, 14, 30, 0),
    tags=["valuation", "bearish_signal"],
)
```

### 6.5.2 Decision Log (Event-Sourced, Immutable)

Every recommendation the system produces is recorded permanently. This creates an auditable trail of what was recommended, why, and what data supported it.

```python
@dataclass
class Decision:
    id: str                           # UUID
    timestamp: datetime               # When the decision was made
    query: str                        # Original user query
    rationale: str                    # Multi-paragraph reasoning
    supporting_findings: list[str]    # Finding IDs that informed this decision
    dissenting_findings: list[str]    # Finding IDs that argued against
    debate_summary: Optional[str]     # Bull/Bear/Risk debate outcome
    recommendation: dict              # Structured recommendation
    confidence: float                 # 0.0 to 1.0
```

**Recommendation structure:**

```python
recommendation = {
    "action": "BUY",                  # BUY, SELL, HOLD, HEDGE, AVOID
    "ticker": "AAPL",
    "timeframe": "6 months",
    "entry_zone": {"low": 185.0, "high": 192.0},
    "target": 220.0,
    "stop_loss": 175.0,
    "position_size": "2-3% of portfolio",
    "strategy": {                     # Optional options overlay
        "type": "bull_call_spread",
        "legs": [...],
        "max_risk": 2500,
        "max_reward": 7500,
    },
    "key_risks": [
        "Multiple compression if growth decelerates",
        "Antitrust regulatory action",
    ],
}
```

**Rules:**
- Immutable. Decisions are never modified after creation — this is event sourcing.
- Every decision must reference at least one supporting finding.
- The rationale must explain the reasoning chain, not just restate the recommendation.

### 6.5.3 Data Cache (TTL-Based)

A shared cache that prevents duplicate API calls when multiple agents need the same data. Agents check the cache before calling any data provider.

```python
@dataclass
class CacheEntry:
    key: str              # Deterministic key: f"{provider}:{sorted(query_params)}"
    value: bytes          # Serialized response (msgpack or JSON)
    created_at: datetime
    ttl_seconds: int
    hit_count: int        # Track usage for cache analytics
```

**TTL by data type:**

| Data Type | TTL | Rationale |
|---|---|---|
| Real-time quotes | 60 seconds | Stale prices are worse than no cache |
| Daily OHLCV | 24 hours | Only changes after market close |
| Company fundamentals | 7 days | Updates quarterly |
| SEC filings | 30 days | Immutable once filed |
| News articles | 4 hours | Sentiment decays, new articles appear |
| Macro indicators | 24 hours | Most update daily or less frequently |
| Options chains | 5 minutes | Greeks change rapidly during trading hours |

### 6.5.4 Alert Board

Real-time events that all agents should be aware of. Agents check the alert board at the start of each iteration.

```python
@dataclass
class Alert:
    id: str
    timestamp: datetime
    severity: str             # "info", "warning", "critical"
    category: str             # "price_move", "news_break", "volatility_spike", "data_stale"
    message: str
    data: dict
    ttl_seconds: int          # Alerts expire — stale alerts are noise
```

**Alert examples:**

```python
Alert(
    id="a-9f2b",
    severity="critical",
    category="price_move",
    message="AAPL down 4.2% in last 30 minutes on heavy volume",
    data={"ticker": "AAPL", "move_pct": -4.2, "volume_ratio": 3.1},
    ttl_seconds=1800,
)

Alert(
    id="a-c3d1",
    severity="warning",
    category="news_break",
    message="Reuters: EU announces new tech regulation framework",
    data={"source": "reuters", "tickers_affected": ["AAPL", "GOOGL", "META"]},
    ttl_seconds=3600,
)
```

---

## 6.6 Per-Agent Scratchpad (In-Memory)

Each agent maintains a private in-memory dictionary for work-in-progress. Nothing in the scratchpad is visible to other agents or persisted across sessions.

```python
class AgentScratchpad:
    """Private working memory for a single agent instance."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._store: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def clear(self) -> None:
        self._store.clear()
```

**What lives in the scratchpad:**

- Intermediate calculations (partial ratio computations, running tallies)
- Draft findings being assembled before posting to the board
- Retrieved data being processed (raw API responses before analysis)
- Agent-specific context (which tools it has called, what it has already examined)

**What does NOT belong in the scratchpad:**

- Anything another agent might need → post it to the Shared Board
- Anything that should survive a session restart → use a persistent store
- Large datasets → query DuckDB or Parquet directly, don't cache in memory

---

## 6.7 Context Injection Strategy

Context is the most constrained resource. Every token of context spent on background information is a token not available for reasoning. The system is aggressive about injecting only what's relevant.

### Automatic Injection (~1,500 tokens)

Every agent receives this baseline context at the start of each turn, assembled by the orchestration layer:

```
┌──────────────────────────────────────────────┐
│           AUTOMATIC CONTEXT BLOCK            │
│                                              │
│  Portfolio Summary (if any)        ~300 tok  │
│  ├─ Current positions and P&L                │
│  └─ Open risk exposures                      │
│                                              │
│  Active Alerts                     ~200 tok  │
│  └─ Only severity >= warning                 │
│                                              │
│  Top-5 Relevant Findings           ~800 tok  │
│  ├─ Filtered by ticker + category match      │
│  └─ Sorted by confidence × recency           │
│                                              │
│  Recent Decisions (last 2)         ~200 tok  │
│  └─ Summary only, not full rationale         │
│                                              │
│  Total: ~1,500 tokens                        │
└──────────────────────────────────────────────┘
```

**Selection logic for Top-5 Findings:**

```python
def select_relevant_findings(
    all_findings: list[Finding],
    current_task: AgentTask,
    k: int = 5,
) -> list[Finding]:
    """Pick the most relevant findings for this agent's current task."""
    scored = []
    for f in all_findings:
        score = 0.0
        # Ticker match: strong relevance signal
        if f.ticker and f.ticker in current_task.tickers:
            score += 3.0
        # Category match: same domain findings are useful
        if f.category == current_task.domain:
            score += 1.0
        # Recency: exponential decay, half-life = 10 minutes
        age_minutes = (datetime.now() - f.timestamp).total_seconds() / 60
        score *= math.exp(-0.069 * age_minutes)  # ln(2)/10 ≈ 0.069
        # Confidence: prefer high-confidence findings
        score *= f.confidence
        scored.append((score, f))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in scored[:k]]
```

### On-Demand Tools

Agents can pull additional context when they need it. These are registered as MCP tools available to all agents.

| Tool | Description | Returns |
|---|---|---|
| `search_findings(query, k=10)` | Semantic search over all findings on the board | Top-k findings ranked by relevance |
| `get_decision_history(ticker)` | Retrieve past decisions involving a ticker | List of Decision summaries |
| `query_knowledge_graph(cypher)` | Run a Cypher query against Neo4j | Query result rows |
| `search_documents(query, collection, k=5)` | Semantic search over ChromaDB | Top-k document chunks with metadata |
| `query_timeseries(sql)` | Run a SQL query against DuckDB | Result rows as dicts |
| `get_alerts(severity_min="info")` | Fetch active (non-expired) alerts | List of Alert objects |

**Why on-demand instead of injecting everything:**

- A macro analyst doesn't need options Greeks in its context.
- A technical analyst doesn't need full SEC filing text.
- Injecting everything wastes ~8,000-12,000 tokens per agent turn — that's reasoning capacity lost.
- On-demand tools let agents pull exactly what they need, when they need it.

---

## 6.8 KG Ingestion Pipeline

Data doesn't start in the knowledge graph. It flows through a pipeline that extracts entities and relationships from raw tool outputs and routes them to the appropriate store.

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  Tool Call   │     │  Raw Response    │     │   Ingestion Router       │
│  (MCP)       │────►│  (JSON/text)     │────►│                         │
│              │     │                  │     │   Inspect data type      │
└─────────────┘     └──────────────────┘     │   and route to stores    │
                                              └─────┬─────┬─────┬───────┘
                                                    │     │     │
                                     ┌──────────────┘     │     └──────────────┐
                                     ▼                    ▼                    ▼
                           ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
                           │  Entity         │  │  Text Chunker   │  │  Series Parser  │
                           │  Extractor      │  │  + Embedder     │  │                 │
                           │                 │  │                 │  │  Validates and   │
                           │  NLP/LLM        │  │  Split text     │  │  normalizes     │
                           │  extracts:      │  │  into chunks,   │  │  time series    │
                           │  - Entities     │  │  compute        │  │  data           │
                           │  - Relations    │  │  embeddings     │  │                 │
                           │  - Properties   │  │                 │  │                 │
                           └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                                    │                    │                    │
                                    ▼                    ▼                    ▼
                           ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
                           │    Neo4j        │  │    ChromaDB     │  │    DuckDB       │
                           │                 │  │                 │  │                 │
                           │  MERGE entities │  │  Upsert chunks  │  │  INSERT rows    │
                           │  CREATE rels    │  │  by doc_id      │  │  (append-only)  │
                           └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Pipeline Steps

**Step 1: Tool returns raw data.**
An agent calls an MCP tool (e.g., `get_company_profile`, `fetch_news`, `get_ohlcv`). The tool returns structured JSON or raw text.

**Step 2: Ingestion router inspects and routes.**
The router examines the data type and source to determine which stores need updating:

```python
def route_ingestion(tool_name: str, response: dict) -> list[str]:
    """Determine which stores should receive this data."""
    routes = []

    # Time series data → DuckDB
    if tool_name in ("get_ohlcv", "get_macro_series", "get_technical_indicators"):
        routes.append("duckdb")

    # Text content → ChromaDB for semantic search
    if tool_name in ("fetch_news", "get_sec_filing", "get_earnings_transcript"):
        routes.append("chromadb")

    # Structured entity data → Neo4j for relationship mapping
    if tool_name in ("get_company_profile", "get_company_peers", "get_insider_trades"):
        routes.append("neo4j")

    # Some tools produce data for multiple stores
    # e.g., SEC filings have text (ChromaDB) AND entity mentions (Neo4j)
    if tool_name == "get_sec_filing":
        routes.append("neo4j")  # Extract entity mentions from filing text

    return routes
```

**Step 3: Entity extraction (for KG).**
Structured data (company profiles, peer lists) maps directly to graph entities. Unstructured text (news, filings) goes through LLM-based extraction:

```python
ENTITY_EXTRACTION_PROMPT = """
Extract entities and relationships from this text.

Return JSON with:
- entities: [{type, name, properties}]
- relationships: [{from_entity, relationship, to_entity, properties}]

Entity types: Company, Sector, Executive, Commodity, Country, GeopoliticalEvent
Relationship types: COMPETES_WITH, SUPPLIES_TO, IMPACTS, LEADS, OWNS_STAKE_IN, EXPOSED_TO, TRIGGERS

Text:
{text}
"""
```

**Step 4: Raw text → Vector Store.**
Text content is chunked according to the strategy for its document type (see Section 6.3), embedded, and upserted into the appropriate ChromaDB collection. Metadata (ticker, date, source) is attached to each chunk.

**Step 5: Time series → DuckDB.**
Numerical series data is validated (correct dtypes, no gaps, ascending dates) and inserted into the appropriate DuckDB table. Large historical loads use Parquet files written to disk, which DuckDB reads directly without import.

### Ingestion Timing

| Trigger | What happens |
|---|---|
| Agent calls a data tool | Response cached in SQLite, routed to stores async |
| Session start | Check for stale KG data, refresh if TTLs expired |
| Background refresh (optional) | Periodic job updates OHLCV and macro series for watched tickers |

### Deduplication

- **Neo4j:** Uses `MERGE` instead of `CREATE`. If an entity already exists, its properties are updated; no duplicate nodes are created.
- **ChromaDB:** Uses document IDs based on `(source, date, section)`. Upserting an existing ID replaces the old embedding.
- **DuckDB:** Uses `INSERT OR REPLACE` with a composite key of `(ticker, date)` for price data. Macro series use `(series_id, date)`.

---

# 7. Technology Stack

## 7.1 LLM Strategy

A tiered model approach balances reasoning quality, speed, and cost across different agent roles.

| Role | Model | Use Case | Reasoning |
|------|-------|----------|-----------|
| Team Leader / Synthesis | Claude Opus 4.6 | Complex reasoning, cross-market analysis, final synthesis | Best reasoning capability for orchestrating multi-agent workflows and producing coherent final output |
| Specialist Workers | Claude Sonnet 4.6 | Data analysis, report generation, tool-intensive tasks | Best balance of cost and capability — handles 80%+ of tool calls and analytical work |
| Intent Classification / Routing | Claude Haiku 4.5 | Quick classification, tool group selection, simple extraction | Fast and cheap — sub-second latency for routing decisions |
| Fallback | via LiteLLM → GPT-4o, Gemini | Disaster recovery, cost optimization | Multi-provider resilience if Anthropic API is unavailable |

**Key design decisions:**

- **LiteLLM** abstracts the fallback layer so switching providers requires zero code changes — just configuration.
- Token budgets are enforced per-agent to prevent runaway costs (see Configuration below).
- The Team Leader uses Opus only for synthesis passes; intermediate reasoning uses Sonnet to keep costs manageable.

## 7.2 Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `anthropic` | latest | Claude API SDK — primary LLM interface with native tool use support |
| `litellm` | latest | Multi-provider LLM abstraction for fallback routing |
| `pydantic` | >=2.7 | Data validation, standardized models, tool input/output schemas |
| `neo4j` | latest | Knowledge Graph driver — entity relationships and cross-query memory |
| `chromadb` | latest | Vector store — semantic search over past analyses and embeddings |
| `duckdb` | latest | Time series and analytical queries — in-process OLAP for market data |
| `mcp` | latest | Model Context Protocol SDK — exposes tools to external MCP clients |
| `rich` | latest | CLI interface — pretty printing, tables, progress bars, live displays |
| `httpx` | latest | Async HTTP client for parallel API calls to data providers |

## 7.3 Financial Libraries

### Market Data Providers

| Package | Purpose |
|---------|---------|
| `yfinance` | Yahoo Finance — price history, fundamentals, options chains |
| `finnhub-python` | FinnHub API — real-time quotes, company news, earnings calendars |
| `fredapi` | FRED — macroeconomic indicators (GDP, CPI, rates, employment) |
| `alpha_vantage` | Alpha Vantage — intraday data, forex, crypto, economic indicators |
| `sec-edgar-downloader` | SEC EDGAR — 10-K, 10-Q, 8-K filings download |

### Analysis & Computation

| Package | Purpose |
|---------|---------|
| `TA-Lib` | Technical indicators — 150+ indicators (SMA, RSI, MACD, Bollinger, etc.) |
| `pandas_ta` | Technical indicators — pure Python fallback when TA-Lib C library is unavailable |
| `QuantLib-Python` | Options pricing, Greeks, yield curve modeling |
| `mibian` | Lightweight options pricing — Black-Scholes, quick Greeks calculation |
| `vectorbt` | Backtesting engine — vectorized strategy simulation |
| `empyrical` | Risk metrics — Sharpe ratio, max drawdown, alpha/beta, Sortino |

## 7.4 Project Structure

```
finance_agent/
├── README.md                  # Project overview
├── pyproject.toml             # Project config & dependencies
├── docs/                      # Architecture documentation
│   ├── 01-overview.md
│   ├── 02-architecture.md
│   ├── ...
│   └── 07-tech-stack.md       # This file
├── src/
│   ├── __init__.py
│   ├── cli.py                 # CLI entry point (rich-based)
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── loop.py            # Core agent loop (while tool_calls)
│   │   ├── team.py            # Team Leader / Teammate management
│   │   ├── pool.py            # AgentPool with concurrency control
│   │   ├── debate.py          # Bull/Bear debate mechanism
│   │   └── prompts/           # System prompts per agent role
│   ├── data/
│   │   ├── __init__.py
│   │   ├── registry.py        # Provider Registry
│   │   ├── fetcher.py         # Base Fetcher (TET pattern)
│   │   ├── models.py          # Standardized Pydantic models
│   │   └── providers/         # One file per data provider
│   │       ├── yfinance.py
│   │       ├── fred.py
│   │       ├── finnhub.py
│   │       └── ...
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py        # Tool registry + group loading
│   │   ├── market.py          # Market data tools
│   │   ├── fundamentals.py    # Fundamental analysis tools
│   │   ├── technical.py       # Technical analysis tools
│   │   ├── options.py         # Options tools
│   │   ├── macro.py           # Macro tools
│   │   ├── sentiment.py       # Sentiment/news tools
│   │   └── risk.py            # Risk/backtest tools
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── kg.py              # Knowledge Graph interface (Neo4j)
│   │   ├── vector.py          # Vector store interface (ChromaDB)
│   │   ├── timeseries.py      # DuckDB interface
│   │   ├── shared_board.py    # SQLite shared board (inter-agent)
│   │   └── scratchpad.py      # Per-agent scratchpad
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── server.py          # MCP server exposing tools
│   └── config.py              # Configuration management
├── tests/
│   ├── test_agent/
│   ├── test_data/
│   ├── test_tools/
│   └── test_memory/
└── docker-compose.yml         # Neo4j + optional services
```

**Directory conventions:**

- `src/agent/` — All agent orchestration logic. No data fetching or tool definitions here.
- `src/data/` — Data access layer. Providers are isolated; the registry provides a uniform interface.
- `src/tools/` — Tool definitions that the LLM can call. Each file groups related tools.
- `src/memory/` — Storage backends. Each file wraps one storage technology behind a clean interface.

## 7.5 Configuration

### API Keys (`.env`)

```bash
# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...

# Financial Data
FINNHUB_API_KEY=...
FRED_API_KEY=...
ALPHA_VANTAGE_API_KEY=...
SEC_EDGAR_USER_AGENT="CompanyName email@example.com"

# Infrastructure
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
```

### System Settings (`config.yaml`)

```yaml
llm:
  default_leader_model: "claude-opus-4-6"
  default_worker_model: "claude-sonnet-4-6"
  default_router_model: "claude-haiku-4-5-20251001"
  fallback_provider: "openai/gpt-4o"

agents:
  max_concurrent: 5
  max_tool_calls_per_turn: 25

tokens:
  leader_budget: 32000
  worker_budget: 16000
  router_budget: 2000

memory:
  neo4j_uri: "bolt://localhost:7687"
  chroma_persist_dir: "./data/chroma"
  duckdb_path: "./data/timeseries.duckdb"
```

### Override Priority

Environment variables override `config.yaml` values using the prefix `FINANCE_AGENT_`:

```
FINANCE_AGENT_LLM__DEFAULT_WORKER_MODEL=claude-sonnet-4-6
```

Priority order: **Environment variables > config.yaml > defaults in code**.

## 7.6 Deployment

### Local Development

The primary deployment target. The agent runs as a CLI application on the developer's machine.

```bash
pip install -e ".[dev]"
docker compose up -d neo4j
python -m finance_agent
```

### Docker Compose (Full Stack)

For a self-contained setup with all infrastructure:

```yaml
# docker-compose.yml
services:
  neo4j:
    image: neo4j:5
    ports:
      - "7474:7474"   # Browser
      - "7687:7687"   # Bolt
    environment:
      NEO4J_AUTH: neo4j/password
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

ChromaDB and DuckDB run in-process (no separate containers needed). Redis can be added optionally for caching API responses if desired.

### No Cloud Deployment

This project is designed to run locally. There is no web server, no REST API, and no cloud infrastructure to manage. The MCP server exposes tools over stdio for local MCP client integration only.

## 7.7 Development Setup

### Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd finance_agent

# Install with dev dependencies
pip install -e ".[dev]"

# Start Neo4j
docker compose up -d neo4j

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Verify setup
python -m finance_agent --health-check

# Run the agent
python -m finance_agent
```

### Prerequisites

- **Python 3.12+**
- **Docker** (for Neo4j)
- **TA-Lib C library** (optional — falls back to `pandas_ta` if unavailable)
  ```bash
  # macOS
  brew install ta-lib
  # Ubuntu
  sudo apt-get install libta-lib-dev
  ```

### Dev Dependencies

```bash
pip install -e ".[dev]"
# Installs: pytest, pytest-asyncio, ruff, mypy, pre-commit
```

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/test_tools/
pytest tests/test_data/

# With coverage
pytest --cov=src --cov-report=term-missing
```

---

# 8. Implementation Roadmap

This document outlines the phased implementation plan for the Finance AI Agent, from a single-agent CLI prototype to a full multi-agent system with persistent knowledge graph intelligence.

---

## 8.1 Phase 1: Foundation (Weeks 1-3)

### Goal
Working single-agent CLI that can answer basic financial questions.

### Deliverables

- **Custom Agent Loop** -- Implement the `while tool_calls` pattern using the Anthropic SDK directly (no framework). The loop handles message construction, tool dispatch, and response streaming.
- **CLI Interface** -- Interactive terminal UI built with the `rich` library. Supports markdown rendering, streaming output, and command history.
- **Provider Registry Skeleton** -- `ProviderRegistry` class with `register()`, `get()`, and `list_providers()`. Define the `BaseProvider` abstract class and `Tool-Executor-Translator (TET)` base classes that all providers will inherit from.
- **First Data Provider: yfinance** -- Implement `YFinanceProvider` with three capabilities:
  - Real-time and historical price data
  - Company fundamentals (income statement, balance sheet, cash flow)
  - Options chain data (calls, puts, expiration dates)
- **5 Core Tools:**
  | Tool | Description | Provider |
  |------|-------------|----------|
  | `get_stock_price` | Current price, daily OHLCV, historical prices | yfinance |
  | `get_financials` | Income statement, balance sheet, cash flow | yfinance |
  | `get_options_chain` | Options data by expiration, strike, type | yfinance |
  | `web_search` | General web search for news and context | Brave/Tavily |
  | `calculate_indicator` | Basic technical indicators (SMA, RSI, MACD) | pandas/numpy |
- **Conversation State Management** -- Simple in-memory conversation history with message list, system prompt management, and token counting.
- **Configuration System** -- `.env` for secrets (API keys), `config.yaml` for runtime settings (model selection, tool groups, cache TTL). Loaded via `pydantic-settings`.

### Milestone
> User asks "What's AAPL trading at?" -> Agent calls `get_stock_price`, receives data, formats a natural language response with current price, daily change, and volume.

---

## 8.2 Phase 2: Data Layer Expansion (Weeks 4-6)

### Goal
Rich multi-source data with standardized models enabling cross-source analysis.

### Deliverables

- **Standardized Pydantic Data Models** -- Define all 8 core model types that normalize data across providers:
  | Model | Fields (key) | Used By |
  |-------|-------------|---------|
  | `PriceBar` | timestamp, open, high, low, close, volume | yfinance, Alpha Vantage |
  | `Fundamental` | metric_name, value, period, filing_date | yfinance, SEC EDGAR |
  | `OptionsContract` | strike, expiry, type, bid, ask, volume, OI, greeks | yfinance, CBOE |
  | `MacroIndicator` | indicator_id, value, date, frequency | FRED |
  | `NewsItem` | headline, source, timestamp, sentiment_score | FinnHub, web_search |
  | `SECFiling` | filing_type, date, url, parsed_sections | SEC EDGAR |
  | `TechnicalSignal` | indicator, value, signal (buy/sell/neutral) | calculate_indicator |
  | `EarningsData` | EPS, revenue, estimates, surprise_pct | yfinance, FinnHub |

- **5+ Data Providers:**
  | Provider | Data Types | Rate Limits |
  |----------|-----------|-------------|
  | yfinance | Price, fundamentals, options | Unofficial, moderate |
  | FRED | Macro indicators (rates, GDP, CPI, employment) | 120 req/min |
  | FinnHub | Real-time quotes, news, earnings calendar | 60 req/min (free) |
  | SEC EDGAR | 10-K, 10-Q, 8-K filings (full text) | 10 req/sec |
  | Alpha Vantage | Price history, forex, crypto, indicators | 5 req/min (free) |

- **20+ Tools** organized into groups:
  - **Market** (6): `get_stock_price`, `get_quote`, `get_market_movers`, `get_sector_performance`, `get_crypto_price`, `get_forex_rate`
  - **Fundamentals** (5): `get_financials`, `get_earnings`, `get_sec_filing`, `get_company_profile`, `compare_companies`
  - **Macro** (4): `get_fed_rate`, `get_economic_indicator`, `get_yield_curve`, `get_economic_calendar`
  - **Technical** (5): `calculate_indicator`, `get_support_resistance`, `detect_pattern`, `get_volume_analysis`, `screen_stocks`
  - **Options** (3): `get_options_chain`, `calculate_greeks`, `find_unusual_activity`

- **Tool Group Loading** -- Intent classifier maps user queries to relevant tool groups. A macro question loads macro + market tools; an options question loads options + technical tools. Reduces context window usage by only injecting relevant tool definitions.

- **Data Cache** -- Redis-backed (or in-memory dict for dev) cache with TTL per data type:
  - Price quotes: 15 seconds
  - Fundamentals: 24 hours
  - Macro indicators: 1 hour
  - SEC filings: 7 days

- **DuckDB Time Series Storage** -- Local DuckDB database for persisting historical price data and indicator calculations. Avoids repeated API calls for backtesting and chart generation.

### Milestone
> User asks "How does the Fed rate decision affect banking stocks?" -> Agent loads macro + market tool groups, fetches FRED funds rate history, pulls banking sector performance via `get_sector_performance`, correlates the data, and delivers a multi-source analysis.

---

## 8.3 Phase 3: Multi-Agent Team (Weeks 7-9)

### Goal
Team Leader agent spawns specialized Teammate agents for parallel analysis workflows.

### Deliverables

- **Team Leader + Teammate Architecture:**
  - `TeamLeader` -- Receives user query, decomposes into sub-tasks, spawns teammates, synthesizes final response. Runs on Claude Opus.
  - `Teammate` -- Receives a focused sub-task with a scoped tool set, writes findings to the shared board. Runs on Claude Sonnet.
  - `Router` (optional) -- Lightweight intent classifier for simple queries that don't need a team. Runs on Claude Haiku.

- **AgentPool with Concurrency Control:**
  ```
  AgentPool
  ├── max_concurrent: 5
  ├── spawn(role, task, tools) -> Teammate
  ├── gather(timeout=30s) -> List[Finding]
  └── cancel_all()
  ```
  Uses `asyncio.Semaphore` for concurrency limits. Each teammate runs in its own async task with isolated conversation state.

- **Shared Board (SQLite WAL mode):**
  | Table | Purpose | Writer | Reader |
  |-------|---------|--------|--------|
  | `findings` | Analysis results from teammates | Teammates | Leader |
  | `decisions` | Leader's reasoning and final conclusions | Leader | All |
  | `cache` | Cross-agent data cache (avoid duplicate fetches) | All | All |
  | `alerts` | Urgent signals (e.g., earnings miss, halt) | Teammates | Leader |

  SQLite WAL mode enables concurrent reads with single-writer safety. Each row is timestamped and tagged with `agent_id`.

- **Per-Agent Scratchpad** -- Each teammate gets an in-memory scratchpad for intermediate calculations and reasoning chains. Not shared; discarded after task completion. Reduces noise on the shared board.

- **Context Injection Strategy:**
  - Leader provides each teammate with a compact summary (under 500 tokens) of the overall query context
  - Teammates receive only the tools relevant to their sub-task
  - On-demand tool loading: if a teammate needs a tool outside its initial set, it can request it from the leader via the board
  - Final synthesis uses structured findings, not raw conversation history

- **LLM Tiering:**
  | Role | Model | Rationale |
  |------|-------|-----------|
  | Team Leader | Claude Opus | Complex reasoning, synthesis, decomposition |
  | Teammates | Claude Sonnet | Focused analysis, tool use, good cost/quality |
  | Router / Classifier | Claude Haiku | Fast, cheap intent classification |

### Milestone
> User asks "Should I invest in NVDA given the current AI spending cycle?" -> Leader decomposes into 3 sub-tasks -> Teammate 1 analyzes NVDA fundamentals, Teammate 2 researches AI capex trends, Teammate 3 checks technical setup -> Leader synthesizes a coherent investment thesis with bull/bear considerations.

---

## 8.4 Phase 4: Debate & Deep Analysis (Weeks 10-12)

### Goal
Bull/Bear debate mechanism and advanced quantitative analysis capabilities.

### Deliverables

- **Bull/Bear Debate Mechanism:**
  - Leader spawns two teammates with opposing mandates: `BullAnalyst` (find reasons to buy) and `BearAnalyst` (find reasons to avoid)
  - Each builds a structured argument with evidence from data tools
  - `Moderator` agent evaluates argument quality, identifies unsupported claims, and synthesizes a balanced verdict
  - Output format: conviction score (-5 to +5), key arguments per side, unresolved risks

- **Risk Perspective Analysis:**
  - Three risk profiles: aggressive, neutral, conservative
  - Each profile adjusts position sizing, stop-loss levels, and time horizon
  - Agent recommends different strategies per profile (e.g., aggressive -> LEAPS calls, conservative -> covered calls)

- **Options Strategy Analysis:**
  - QuantLib integration for precise options pricing (Black-Scholes, binomial tree)
  - Greeks calculation: delta, gamma, theta, vega, rho
  - Implied volatility surface construction
  - Strategy builders: covered call, iron condor, straddle, butterfly, collar
  - P/L visualization data for strategy payoff diagrams

- **Technical Analysis Suite:**
  - TA-Lib integration for 150+ indicators (with `pandas_ta` as pure-Python fallback)
  - Chart pattern detection: head & shoulders, double top/bottom, triangles, flags
  - Multi-timeframe analysis: daily, weekly, monthly alignment
  - Volume profile and VWAP analysis

- **Backtesting Engine:**
  - `vectorbt` integration for fast vectorized backtesting
  - Strategy definition DSL: entry/exit rules based on indicator signals
  - Performance metrics: Sharpe, Sortino, max drawdown, win rate, profit factor
  - Walk-forward optimization to avoid overfitting

- **Monte Carlo Simulation:**
  - Portfolio risk quantification using historical return distributions
  - VaR (Value at Risk) and CVaR at 95% and 99% confidence levels
  - Scenario analysis: custom shocks (e.g., -20% market, +200bps rates)
  - 10,000+ simulation paths with configurable time horizons

- **Sentiment Analysis:**
  - FinBERT model for financial text sentiment (positive/negative/neutral)
  - News feed aggregation from FinnHub, RSS feeds, web search
  - Social sentiment signals (Reddit, StockTwits) when available
  - Sentiment trend tracking over time (shift detection)

### Milestone
> User asks "Analyze the Hormuz blockade scenario" -> Macro analyst evaluates oil price shock and inflation impact -> Sector analyst identifies winners (energy, defense) and losers (airlines, shipping) -> Options analyst recommends hedging strategies with specific strikes and expiries -> Bull/Bear debate on energy sector plays -> Risk assessment with Monte Carlo VaR -> Final report with actionable recommendations across risk profiles.

---

## 8.5 Phase 5: Knowledge Graph & Intelligence (Weeks 13-16)

### Goal
Persistent knowledge layer that learns from every analysis and enables cross-session intelligence.

### Deliverables

- **Neo4j Knowledge Graph Setup:**
  - Entities: `Company`, `Person`, `Sector`, `Indicator`, `Event`, `Product`, `Country`
  - Relationships: `SUPPLIES_TO`, `COMPETES_WITH`, `MEMBER_OF_SECTOR`, `AFFECTS`, `LED_BY`, `HEADQUARTERED_IN`
  - Property graphs with temporal attributes (relationship valid_from/valid_to)

- **Entity Extraction Pipeline:**
  - Every tool output passes through an extraction step
  - LLM-based extraction (Haiku) converts unstructured data into KG triples
  - Example: SEC filing mentions "Apple is our largest customer" -> `(COMPANY:Supplier) -[:SUPPLIES_TO]-> (COMPANY:Apple)`
  - Deduplication and entity resolution using fuzzy matching + canonical IDs

- **Multi-Hop Reasoning Queries:**
  - Cypher query generation from natural language
  - Example: "What companies would be affected if TSMC halts production?" -> Traverse SUPPLIES_TO chain 2-3 hops deep
  - Path ranking by economic significance (revenue dependency weight on edges)

- **ChromaDB Vector Store:**
  - Store embeddings of past analyses, news summaries, and filing excerpts
  - Retrieval-augmented generation for context injection
  - Semantic search: "similar situations to the 2022 chip shortage"
  - Chunking strategy: 512 tokens with 50-token overlap, metadata-tagged

- **Cross-Market Transmission Chain Analysis:**
  - KG-powered impact propagation: Event -> direct affected entities -> second-order effects
  - Weighted edges based on revenue exposure, supply dependency, geographic proximity
  - Visualization-ready output: transmission chain as directed acyclic graph

- **GraphRAG Hybrid Queries:**
  - Combine structured KG traversal with semantic vector search
  - KG provides the entity graph; vector store provides supporting evidence
  - Example: KG finds TSMC -> Apple supply chain; vector store retrieves past analyses of similar disruptions

- **Session Memory and Learning:**
  - Store analysis outcomes and user feedback
  - Track prediction accuracy over time (did the bull case play out?)
  - Improve future analyses by referencing similar past scenarios
  - User preference learning: risk tolerance, preferred sectors, analysis depth

### Milestone
> System knows that "TSMC supply chain disruption" affects Apple (revenue), NVIDIA (GPU supply), AMD (competitor benefit), ASML (equipment demand), and can trace the full impact chain automatically. When a new TSMC-related event occurs, the system proactively surfaces relevant past analyses and affected portfolio positions.

---

## 8.6 Summary Timeline

| Phase | Duration | Key Deliverable | Complexity | Models Used |
|-------|----------|----------------|------------|-------------|
| 1 - Foundation | Weeks 1-3 | Single agent + CLI + 5 tools | Low | Sonnet |
| 2 - Data Layer | Weeks 4-6 | 5+ providers + 20+ tools + cache | Medium | Sonnet |
| 3 - Multi-Agent | Weeks 7-9 | Team Leader + parallel teammates | High | Opus + Sonnet + Haiku |
| 4 - Debate & Analysis | Weeks 10-12 | Bull/Bear debate + quant analysis | High | Opus + Sonnet |
| 5 - Knowledge Graph | Weeks 13-16 | Neo4j KG + GraphRAG + memory | High | Opus + Sonnet + Haiku |

---

## 8.7 Dependencies Between Phases

```
Phase 1 (Foundation)
  │
  │  Agent loop, CLI, provider registry, first tools
  ▼
Phase 2 (Data Layer)
  │
  │  Standardized models, multi-provider, tool groups
  ▼
Phase 3 (Multi-Agent) ◄──── Phase 4 (Debate & Analysis)
  │                          can start partially in parallel:
  │                          - QuantLib/TA-Lib integration (no agent dependency)
  │                          - Backtesting engine (standalone)
  │                          - Sentiment pipeline (standalone)
  │                          Debate mechanism requires Phase 3 agent spawning
  ▼
Phase 5 (Knowledge Graph)
  │
  │  Requires all tool outputs (Phase 2) and multi-agent
  │  findings (Phase 3) to feed the extraction pipeline
  ▼
  Production-ready system
```

**Parallelization opportunities:**
- Phase 4 quantitative tools (QuantLib, vectorbt, FinBERT) can be developed and tested standalone during Phase 3
- ChromaDB vector store (Phase 5) can be prototyped during Phase 3 using single-agent outputs
- Neo4j schema design can begin during Phase 2 once data models are stable

---

## 8.8 Risk Factors

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limits hit during multi-agent parallel execution | Throttled responses, degraded user experience | High | Implement per-provider rate limiters, data cache with TTL, fallback provider chain (e.g., Alpha Vantage -> yfinance) |
| LLM cost escalation from multi-agent workflows | Budget overrun, unsustainable operating costs | High | Token budgets per agent, model tiering (Haiku for simple tasks), response caching, prompt compression |
| TA-Lib C library dependency fails on target platform | Build failures, blocked Phase 4 technical analysis | Medium | Use `pandas_ta` as pure-Python fallback; only require TA-Lib as optional dependency |
| Neo4j operational complexity delays Phase 5 | Delayed knowledge graph delivery | Medium | Start with simpler graph queries in SQLite; migrate to Neo4j incrementally; use NetworkX for prototyping |
| Context window limits degrade multi-agent performance | Agents lose important context, produce shallow analysis | Medium | Aggressive prompt compression, selective context injection, structured findings format, Opus 200k context for leader |
| yfinance unofficial API breaks or gets blocked | Core data source unavailable | Medium | Abstract behind provider interface from day 1; Alpha Vantage and FinnHub as immediate fallbacks |
| QuantLib Python bindings version conflicts | Blocked options analysis | Low | Pin versions in requirements; containerize build; pure-Python Black-Scholes as fallback |

---

## 8.9 Definition of Done per Phase

Each phase is considered complete when:

1. **All listed tools/providers pass integration tests** with real API calls (not just mocks)
2. **The milestone scenario runs end-to-end** and produces a coherent, accurate response
3. **Error handling is in place** for API failures, timeouts, and rate limits
4. **Configuration is externalized** (no hardcoded API keys or model names)
5. **Documentation is updated** reflecting the current architecture and available capabilities
