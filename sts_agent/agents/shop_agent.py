from __future__ import annotations

from ..knowledge import card_tags, normalize_name
from ..models import Candidate, GameState, Recommendation


class ShopAgent:
    name = "shop-agent"

    def recommend(
        self, state: GameState, options: tuple[Candidate, ...]
    ) -> tuple[Recommendation, ...]:
        recommendations: list[Recommendation] = []

        for option in options:
            clean = normalize_name(option.name)
            tags = set(option.tags) | card_tags(clean)
            cost = float(option.metadata.get("cost", 0) or 0)
            score = 50.0
            reasons: list[str] = []
            cautions: list[str] = []

            if cost > state.gold:
                recommendations.append(
                    Recommendation(
                        agent=self.name,
                        choice=option.name,
                        score=0.0,
                        reasons=("cannot afford this option",),
                    )
                )
                continue

            if "remove" in tags or "card-remove" in tags or "remove" in clean:
                score += 18.0
                reasons.append("removing starter/status clutter improves consistency")
                if state.deck_size <= 12:
                    score -= 5.0
                    cautions.append("small decks may need additions before removals")

            if "relic" in tags:
                score += 10.0
                reasons.append("relics add power without bloating the deck")
            if "premium" in tags:
                score += 16.0
                reasons.append("premium effect can justify the gold")
            if "potion" in tags:
                if state.hp_ratio < 0.6:
                    score += 9.0
                    reasons.append("potion can stabilize next elite or boss")
                else:
                    score -= 2.0
                    cautions.append("healthy runs should avoid overbuying potions")
            if "block" in tags or "attack" in tags or "scaling" in tags:
                score += 7.0
                reasons.append("card solves a recognizable deck role")

            if cost:
                value_pressure = cost / max(state.gold, 1)
                if value_pressure > 0.75:
                    score -= 10.0
                    cautions.append("spends most of your gold; require high confidence")
                elif value_pressure < 0.35:
                    score += 4.0
                    reasons.append("low cost keeps future shop flexibility")

            recommendations.append(
                Recommendation(
                    agent=self.name,
                    choice=option.name,
                    score=score,
                    reasons=tuple(reasons) or ("purchase is acceptable but not urgent",),
                    cautions=tuple(cautions),
                )
            )

        return tuple(sorted(recommendations, key=lambda item: item.score, reverse=True))
