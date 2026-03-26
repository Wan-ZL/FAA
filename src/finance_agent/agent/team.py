"""Team Leader and Teammate agent management.

The Team Leader orchestrates the analysis by decomposing queries,
spawning specialized teammates, and synthesizing results.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from finance_agent.agent.loop import AgentLoop
from finance_agent.agent.models import (
    AgentStatus,
    AnalysisRequest,
    Finding,
    SharedStateBoard,
    TeammateTask,
)
from finance_agent.config import settings

logger = logging.getLogger(__name__)


class TeammateAgent:
    """A single autonomous teammate spawned by the Team Leader."""

    def __init__(
        self,
        task: TeammateTask,
        board: SharedStateBoard,
        tools: list[dict[str, Any]] | None = None,
        tool_handlers: dict[str, Any] | None = None,
    ) -> None:
        self.id = f"{task.role}-{uuid4().hex[:6]}"
        self.task = task
        self.board = board
        self.status = AgentStatus.INITIALIZING
        self.error: str | None = None

        model_map = {
            "opus": settings.llm.leader_model,
            "sonnet": settings.llm.worker_model,
            "haiku": settings.llm.router_model,
        }
        model = model_map.get(task.model, settings.llm.worker_model)

        self.loop = AgentLoop(
            model=model,
            system_prompt=self._build_prompt(),
            tools=tools or [],
            tool_handlers=tool_handlers or {},
            max_iterations=15,
            max_tokens=task.budget_tokens,
        )

    def _build_prompt(self) -> str:
        """Build system prompt for this teammate."""
        return (
            f"You are a {self.task.role} agent in a financial analysis team.\n"
            f"Your task: {self.task.description}\n\n"
            f"Analyze thoroughly and provide structured findings.\n"
            f"Focus on data-driven insights, not speculation.\n"
            f"Be concise but comprehensive in your analysis."
        )

    async def execute(self) -> Finding | None:
        """Run the assigned task and return findings."""
        self.status = AgentStatus.RUNNING
        try:
            result = await self.loop.run(self.task.description)

            finding = Finding(
                agent_id=self.id,
                category=self._role_to_category(),
                ticker=self.board.ticker,
                summary=result[:500],
                data={"full_analysis": result},
                confidence=0.7,
            )
            self.status = AgentStatus.SUCCESS
            return finding

        except asyncio.TimeoutError:
            self.status = AgentStatus.TIMEOUT
            logger.warning(f"Teammate {self.id} timed out")
            return Finding(
                agent_id=self.id,
                category=self._role_to_category(),
                ticker=self.board.ticker,
                summary=f"Analysis timed out for {self.task.role}",
                data={"error": "timeout"},
                confidence=0.1,
            )

        except Exception as e:
            self.status = AgentStatus.ERROR
            self.error = str(e)
            logger.error(f"Teammate {self.id} failed: {e}")
            return Finding(
                agent_id=self.id,
                category=self._role_to_category(),
                ticker=self.board.ticker,
                summary=f"Error in {self.task.role}: {e}",
                data={"error": str(e)},
                confidence=0.0,
            )

    def _role_to_category(self) -> str:
        """Map role name to finding category."""
        role_map = {
            "macro_analyst": "macro",
            "technical_analyst": "market",
            "fundamental_analyst": "fundamental",
            "sentiment_analyst": "sentiment",
            "options_strategist": "options",
            "risk_assessor": "risk",
            "backtest_validator": "risk",
        }
        return role_map.get(self.task.role, "market")


class TeamLeader:
    """Orchestrates multi-agent financial analysis.

    Receives user queries, decomposes them into sub-tasks,
    spawns teammate agents, and synthesizes their findings.
    """

    def __init__(
        self,
        tools: list[dict[str, Any]] | None = None,
        tool_handlers: dict[str, Any] | None = None,
    ) -> None:
        self.tools = tools or []
        self.tool_handlers = tool_handlers or {}
        self.board: SharedStateBoard | None = None

    async def analyze(self, query: str) -> str:
        """Run a full analysis for the given query.

        1. Parse intent
        2. Decompose into sub-tasks
        3. Spawn teammates
        4. Collect findings
        5. Synthesize final report
        """
        # Create fresh board for this analysis
        self.board = SharedStateBoard(created_at=datetime.now())

        # Parse intent
        request = await self._parse_intent(query)
        self.board.ticker = request.ticker

        # Decompose into teammate tasks
        tasks = self._decompose_query(request)

        if not tasks:
            # Simple query - handle directly
            loop = AgentLoop(
                model=settings.llm.leader_model,
                system_prompt="You are a financial analysis assistant. Provide clear, data-driven answers.",
                tools=self.tools,
                tool_handlers=self.tool_handlers,
            )
            return await loop.run(query)

        # Spawn teammates and gather findings
        findings = await self._spawn_and_gather(tasks)

        # Synthesize
        report = await self._synthesize(query, request, findings)
        return report

    async def _parse_intent(self, query: str) -> AnalysisRequest:
        """Parse user query into structured analysis request."""
        loop = AgentLoop(
            model=settings.llm.router_model,
            system_prompt=(
                "You are an intent parser. Extract structured information from financial queries.\n"
                "Return a JSON object with these fields:\n"
                "- ticker: stock symbol if mentioned (null otherwise)\n"
                "- asset_class: equity, options, etf, crypto, forex, or macro\n"
                "- timeframe: day_trade, swing, 6_months, 1_year, or long_term\n"
                "- analysis_depth: quick, standard, or deep\n"
                "- specific_focus: the user's specific question or concern\n"
                "Return ONLY the JSON object, no other text."
            ),
            max_iterations=1,
        )
        result = await loop.run(query)

        # Try to parse JSON from result
        try:
            data = json.loads(result)
            return AnalysisRequest(
                raw_query=query,
                ticker=data.get("ticker"),
                tickers=[data["ticker"]] if data.get("ticker") else [],
                asset_class=data.get("asset_class", "equity"),
                timeframe=data.get("timeframe", ""),
                analysis_depth=data.get("analysis_depth", "standard"),
                specific_focus=data.get("specific_focus", ""),
            )
        except (json.JSONDecodeError, KeyError):
            return AnalysisRequest(raw_query=query)

    def _decompose_query(self, request: AnalysisRequest) -> list[TeammateTask]:
        """Decompose analysis request into teammate sub-tasks."""
        tasks = []

        if request.asset_class in ("equity", "options", "etf"):
            tasks.append(TeammateTask(
                role="macro_analyst",
                model="haiku",
                description=f"Pull macro context: FRED rates, economic regime, impact on {request.ticker or 'market'}",
                tools=["fred", "eia"],
                budget_tokens=4000,
                timeout_seconds=300,
            ))

        if request.ticker:
            tasks.append(TeammateTask(
                role="technical_analyst",
                model="sonnet",
                description=f"Technical analysis for {request.ticker}: indicators, patterns, support/resistance",
                tools=["yfinance", "talib"],
                budget_tokens=8000,
                timeout_seconds=300,
            ))

        if request.asset_class == "equity" and request.ticker:
            tasks.append(TeammateTask(
                role="fundamental_analyst",
                model="sonnet",
                description=f"Fundamental analysis for {request.ticker}: financials, valuation, moat assessment",
                tools=["sec_edgar", "yfinance"],
                budget_tokens=8000,
                timeout_seconds=300,
            ))

        tasks.append(TeammateTask(
            role="sentiment_analyst",
            model="haiku",
            description=f"Sentiment scan for {request.ticker or request.raw_query}: news, social signals",
            tools=["news", "finbert"],
            budget_tokens=4000,
            timeout_seconds=180,
        ))

        tasks.append(TeammateTask(
            role="risk_assessor",
            model="sonnet",
            description=f"Risk assessment: VaR, stress testing, correlation analysis for {request.ticker or 'portfolio'}",
            tools=["monte_carlo", "vectorbt"],
            budget_tokens=8000,
            timeout_seconds=300,
        ))

        return tasks

    async def _spawn_and_gather(self, tasks: list[TeammateTask]) -> list[Finding]:
        """Spawn teammate agents and gather their findings."""
        from finance_agent.agent.pool import AgentPool

        pool = AgentPool(max_concurrent=settings.agents.max_concurrent)

        findings = []
        async def _run_teammate(task: TeammateTask) -> Finding | None:
            teammate = TeammateAgent(
                task=task,
                board=self.board,
                tools=self.tools,
                tool_handlers=self.tool_handlers,
            )
            return await teammate.execute()

        # Run all teammates with concurrency control
        coros = [pool.submit(_run_teammate, task) for task in tasks]
        results = await asyncio.gather(*coros, return_exceptions=True)

        for result in results:
            if isinstance(result, Finding):
                findings.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Teammate failed: {result}")

        return findings

    async def _synthesize(
        self,
        query: str,
        request: AnalysisRequest,
        findings: list[Finding],
    ) -> str:
        """Synthesize all findings into a final report."""
        findings_text = "\n\n".join(
            f"### {f.agent_id} ({f.category})\n"
            f"**Confidence:** {f.confidence:.0%}\n"
            f"**Summary:** {f.summary}\n"
            for f in findings
        )

        synthesis_prompt = (
            "You are the Team Leader synthesizing a financial analysis.\n"
            "Review all teammate findings below and produce a comprehensive report.\n\n"
            "Include:\n"
            "1. Executive Summary\n"
            "2. Key Findings (organized by perspective)\n"
            "3. Bull/Bear Arguments\n"
            "4. Risk Assessment\n"
            "5. Recommendation (with confidence level)\n"
            "6. Key Risks and Caveats\n\n"
            "Be specific, data-driven, and actionable."
        )

        loop = AgentLoop(
            model=settings.llm.leader_model,
            system_prompt=synthesis_prompt,
            max_iterations=1,
            max_tokens=8192,
        )

        synthesis_query = (
            f"Original query: {query}\n\n"
            f"Ticker: {request.ticker or 'N/A'}\n"
            f"Timeframe: {request.timeframe or 'Not specified'}\n\n"
            f"## Teammate Findings\n\n{findings_text}"
        )

        return await loop.run(synthesis_query)
