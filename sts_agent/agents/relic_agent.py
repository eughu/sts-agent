from __future__ import annotations

from ..knowledge import deck_tags, normalize_name
from ..models import Candidate, GameState, Recommendation


class RelicAgent:
    name = "relic-agent"

    def recommend(
        self, state: GameState, options: tuple[Candidate, ...]
    ) -> tuple[Recommendation, ...]:
        tags_in_deck = deck_tags(state.deck)
        recommendations: list[Recommendation] = []

        for option in options:
            clean = normalize_name(option.name)
            tags = {tag.lower() for tag in option.tags}
            score = 50.0
            reasons: list[str] = []
            cautions: list[str] = []

            if "energy" in tags or clean in {
                "coffee dripper",
                "cursed key",
                "fusion hammer",
                "slaver's collar",
                "sozu",
            }:
                score += 18.0
                reasons.append("extra energy is usually run-defining")
            if "draw" in tags:
                score += 10.0
                reasons.append("more draw improves consistency")
            if "defense" in tags or "block" in tags:
                score += 7.0
                reasons.append("defensive relics reduce HP pressure")
            if "shiv" in tags and "shiv" in tags_in_deck:
                score += 14.0
                reasons.append("relic aligns with shiv package")
            if "orb" in tags and "orb" in tags_in_deck:
                score += 14.0
                reasons.append("relic aligns with orb package")

            if clean == "coffee dripper" and state.hp_ratio < 0.5:
                score -= 14.0
                cautions.append("no resting is dangerous while low HP")
            if clean == "sozu" and len(state.potions) == 0:
                score -= 7.0
                cautions.append("losing future potions hurts elite safety")
            if clean == "busted crown" and state.act.value != "act3":
                score -= 18.0
                cautions.append("reduced card rewards are punishing before the deck is solved")

            recommendations.append(
                Recommendation(
                    agent=self.name,
                    choice=option.name,
                    score=score,
                    reasons=tuple(reasons) or ("relic has neutral value from the current context",),
                    cautions=tuple(cautions),
                )
            )

        return tuple(sorted(recommendations, key=lambda item: item.score, reverse=True))
