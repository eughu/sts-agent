from __future__ import annotations

from .agents import CardChoiceAgent, CombatAgent, RelicAgent, RouteAgent, ShopAgent
from .models import Candidate, Decision, GameState


class SpireCoordinator:
    """Coordinates specialized subagents for a single decision point."""

    def __init__(self) -> None:
        self._agents = {
            "card": CardChoiceAgent(),
            "combat": CombatAgent(),
            "relic": RelicAgent(),
            "route": RouteAgent(),
            "shop": ShopAgent(),
        }

    @property
    def supported_topics(self) -> tuple[str, ...]:
        return tuple(self._agents)

    def decide(
        self, topic: str, state: GameState, options: tuple[Candidate, ...]
    ) -> Decision:
        normalized = topic.lower().strip()
        if normalized not in self._agents:
            allowed = ", ".join(self.supported_topics)
            raise ValueError(f"Unknown topic '{topic}'. Use one of: {allowed}.")
        if not options:
            raise ValueError("At least one option is required.")

        recommendations = self._agents[normalized].recommend(state, options)
        best = recommendations[0]
        summary = self._build_summary(normalized, best.choice, best.score)
        return Decision(
            topic=normalized, recommendations=recommendations, summary=summary
        )

    def _build_summary(self, topic: str, choice: str, score: float) -> str:
        confidence = "high" if score >= 75 else "medium" if score >= 58 else "low"
        return f"For {topic}, prefer '{choice}' with {confidence} confidence."
