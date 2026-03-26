"""Bull/Bear debate mechanism with Risk arbiter.

Implements structured adversarial debate between bull and bear perspectives
before any recommendation is finalized. Adds a Risk arbiter to prevent
both sides from ignoring tail risks.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from finance_agent.agent.loop import AgentLoop
from finance_agent.agent.models import (
    Confidence,
    DebateResult,
    DebateRound,
    Finding,
    RISK_WEIGHTS,
    Signal,
)
from finance_agent.config import settings

logger = logging.getLogger(__name__)


class DebateModule:
    """Manages the Bull/Bear debate and Risk discussion.

    The debate runs for a configurable number of rounds (default: 2).
    Each round has opening arguments followed by rebuttals.
    A Risk arbiter evaluates both sides and produces a balanced verdict.
    """

    def __init__(self, num_rounds: int = 2) -> None:
        self.num_rounds = num_rounds

    async def run_investment_debate(
        self,
        ticker: str,
        findings: list[Finding],
        context: str = "",
    ) -> DebateResult:
        """Run a structured Bull/Bear debate.

        Args:
            ticker: The ticker being analyzed
            findings: All findings from specialist agents
            context: Additional context for the debate

        Returns:
            DebateResult with rounds, synthesis, signal, and confidence
        """
        findings_text = "\n".join(
            f"- [{f.category}] {f.summary} (confidence: {f.confidence:.0%})"
            for f in findings
        )

        rounds: list[DebateRound] = []

        bull_history = ""
        bear_history = ""

        for round_num in range(1, self.num_rounds + 1):
            # Bull argument
            bull_prompt = self._build_bull_prompt(
                ticker, findings_text, bear_history, round_num, context
            )
            bull_loop = AgentLoop(
                model=settings.llm.worker_model,
                system_prompt=bull_prompt,
                max_iterations=1,
                max_tokens=2000,
            )

            # Bear argument
            bear_prompt = self._build_bear_prompt(
                ticker, findings_text, bull_history, round_num, context
            )
            bear_loop = AgentLoop(
                model=settings.llm.worker_model,
                system_prompt=bear_prompt,
                max_iterations=1,
                max_tokens=2000,
            )

            if round_num == 1:
                # Round 1: bull and bear are independent, run concurrently
                bull_arg, bear_arg = await asyncio.gather(
                    bull_loop.run(
                        f"Round {round_num}: Make your opening argument for {ticker}"
                    ),
                    bear_loop.run(
                        f"Round {round_num}: Make your opening argument against {ticker}"
                    ),
                )
            else:
                # Subsequent rounds: bear needs bull's argument for rebuttal
                bull_arg = await bull_loop.run(
                    f"Round {round_num}: Make your rebuttal argument for {ticker}"
                )
                bear_prompt = self._build_bear_prompt(
                    ticker, findings_text, bull_arg, round_num, context
                )
                bear_loop = AgentLoop(
                    model=settings.llm.worker_model,
                    system_prompt=bear_prompt,
                    max_iterations=1,
                    max_tokens=2000,
                )
                bear_arg = await bear_loop.run(
                    f"Round {round_num}: Make your rebuttal argument against {ticker}"
                )

            rounds.append(DebateRound(
                round_number=round_num,
                bull_argument=bull_arg,
                bear_argument=bear_arg,
                key_data_cited=[],
            ))

            bull_history += f"\nRound {round_num} Bull: {bull_arg}"
            bear_history += f"\nRound {round_num} Bear: {bear_arg}"

        # Risk arbiter synthesis
        synthesis = await self._risk_synthesis(
            ticker, rounds, findings_text, context
        )

        return synthesis

    async def run_risk_discussion(
        self,
        ticker: str,
        debate_result: DebateResult,
        risk_profile: str = "moderate",
    ) -> dict[str, Any]:
        """Run a risk perspective discussion across three profiles.

        Args:
            ticker: The ticker being analyzed
            debate_result: Result from the investment debate
            risk_profile: User's risk profile (aggressive, moderate, conservative)

        Returns:
            Dict with position sizing, strategy recommendations per profile
        """
        profiles = ["aggressive", "neutral", "conservative"]

        async def _run_profile(profile: str) -> tuple[str, str]:
            prompt = (
                f"You are a {profile} risk advisor.\n"
                f"Given the debate conclusion for {ticker}:\n"
                f"Signal: {debate_result.signal.value}\n"
                f"Confidence: {debate_result.confidence.value}\n"
                f"Key disagreements: {', '.join(debate_result.key_disagreements)}\n\n"
                f"Recommend position sizing, entry/exit strategy, and risk management "
                f"from a {profile} perspective. Be specific with numbers."
            )
            loop = AgentLoop(
                model=settings.llm.worker_model,
                system_prompt=prompt,
                max_iterations=1,
                max_tokens=1500,
            )
            result = await loop.run(
                f"What is the {profile} strategy for {ticker}?"
            )
            return profile, result

        results = await asyncio.gather(*[_run_profile(p) for p in profiles])
        perspectives = dict(results)

        # Weight perspectives based on user's risk profile
        weights = RISK_WEIGHTS.get(risk_profile, RISK_WEIGHTS["moderate"])

        return {
            "perspectives": perspectives,
            "weights": weights,
            "risk_profile": risk_profile,
            "weighted_recommendation": perspectives.get(risk_profile, ""),
        }

    def _build_bull_prompt(
        self,
        ticker: str,
        findings: str,
        bear_history: str,
        round_num: int,
        context: str,
    ) -> str:
        """Build the bull researcher's system prompt."""
        base = (
            f"You are a Bull Researcher. Your job is to find compelling reasons to BUY {ticker}.\n"
            f"Base your arguments on data and evidence, not hope.\n"
            f"Cite specific metrics, trends, and catalysts.\n\n"
            f"Available findings:\n{findings}\n"
        )
        if context:
            base += f"\nAdditional context: {context}\n"
        if bear_history and round_num > 1:
            base += f"\nBear's previous arguments to rebut:\n{bear_history}\n"
        return base

    def _build_bear_prompt(
        self,
        ticker: str,
        findings: str,
        bull_argument: str,
        round_num: int,
        context: str,
    ) -> str:
        """Build the bear researcher's system prompt."""
        base = (
            f"You are a Bear Researcher. Your job is to find compelling reasons to AVOID {ticker}.\n"
            f"Look for risks, overvaluation, headwinds, and red flags.\n"
            f"Cite specific metrics, historical precedents, and risk factors.\n\n"
            f"Available findings:\n{findings}\n"
        )
        if context:
            base += f"\nAdditional context: {context}\n"
        if bull_argument:
            base += f"\nBull's argument to counter:\n{bull_argument}\n"
        return base

    async def _risk_synthesis(
        self,
        ticker: str,
        rounds: list[DebateRound],
        findings: str,
        context: str,
    ) -> DebateResult:
        """Risk arbiter synthesizes the debate into a verdict."""
        debate_text = ""
        for r in rounds:
            debate_text += f"\n--- Round {r.round_number} ---\n"
            debate_text += f"BULL: {r.bull_argument}\n"
            debate_text += f"BEAR: {r.bear_argument}\n"

        prompt = (
            f"You are the Risk Arbiter for a debate on {ticker}.\n"
            f"Review the bull/bear debate and original findings.\n"
            f"Produce a balanced synthesis that:\n"
            f"1. Identifies the strongest arguments on each side\n"
            f"2. Highlights unresolved disagreements\n"
            f"3. Assesses tail risks both sides may have ignored\n"
            f"4. Provides a final signal and confidence level\n\n"
            f"End your response with a JSON block:\n"
            f'{{"signal": "strong_buy|buy|hold|sell|strong_sell", '
            f'"confidence": "high|medium|low", '
            f'"key_disagreements": ["point1", "point2"]}}\n\n'
            f"Original findings:\n{findings}\n\n"
            f"Debate:\n{debate_text}"
        )

        loop = AgentLoop(
            model=settings.llm.leader_model,
            system_prompt=prompt,
            max_iterations=1,
            max_tokens=3000,
        )
        synthesis = await loop.run(f"Synthesize the {ticker} debate")

        # Try to parse JSON from the synthesis
        signal = Signal.HOLD
        confidence = Confidence.MEDIUM
        disagreements: list[str] = []

        try:
            # Find JSON block in the text
            json_start = synthesis.rfind("{")
            json_end = synthesis.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                parsed = json.loads(synthesis[json_start:json_end])
                signal = Signal(parsed.get("signal", "hold"))
                confidence = Confidence(parsed.get("confidence", "medium"))
                disagreements = parsed.get("key_disagreements", [])
        except (json.JSONDecodeError, ValueError):
            pass

        return DebateResult(
            rounds=rounds,
            synthesis=synthesis,
            signal=signal,
            confidence=confidence,
            key_disagreements=disagreements,
        )
