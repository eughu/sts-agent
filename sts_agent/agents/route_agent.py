from __future__ import annotations

from ..models import Candidate, GameState, Recommendation
from ..profile import analyze_run


class RouteAgent:
    name = "route-agent"

    def recommend(
        self, state: GameState, options: tuple[Candidate, ...]
    ) -> tuple[Recommendation, ...]:
        profile = analyze_run(state)
        recommendations: list[Recommendation] = []

        for option in options:
            tags = {tag.lower() for tag in option.tags}
            score = 50.0
            reasons: list[str] = []
            cautions: list[str] = []

            if "elite" in tags:
                if state.hp_ratio >= 0.65 and state.floor <= 12:
                    score += 18.0
                    reasons.append("healthy enough to hunt early relics")
                elif state.hp_ratio < 0.45:
                    score -= 22.0
                    cautions.append("low HP makes elite path risky")
                elif profile.risk >= 25:
                    score -= 10.0
                    cautions.append("deck profile has unresolved threats before elite")
                else:
                    score += 4.0
                    reasons.append("elite is viable if potion and damage are ready")

            if "campfire" in tags:
                if state.hp_ratio < 0.55:
                    score += 16.0
                    reasons.append("campfire protects the run when HP is low")
                else:
                    score += 6.0
                    reasons.append("upgrade/rest flexibility is valuable")

            if "shop" in tags:
                if state.gold >= 220:
                    score += 16.0
                    reasons.append("enough gold for premium shop decisions")
                elif profile.risk >= 20 and state.gold >= 120:
                    score += 8.0
                    reasons.append("shop can patch a current deck weakness")
                elif state.gold < 90:
                    score -= 10.0
                    cautions.append("shop is weak with low gold")

            if "question" in tags:
                if state.act.value == "act1" and state.floor <= 6:
                    score -= 8.0
                    cautions.append("early question marks can miss needed card rewards")
                else:
                    score += 4.0
                    reasons.append("events can convert resources efficiently")

            if "hallway" in tags:
                if state.floor <= 5:
                    score += 10.0
                    reasons.append("early hallway fights improve deck quality")
                elif profile.needs and state.hp_ratio >= 0.55:
                    score += 6.0
                    reasons.append("card rewards can patch known deck needs")
                elif state.hp_ratio < 0.35:
                    score -= 8.0
                    cautions.append("avoid avoidable damage at low HP")

            for warning in profile.warnings[:2]:
                cautions.append(warning)

            if "boss" in tags:
                score += 3.0
                reasons.append("forced progression")

            recommendations.append(
                Recommendation(
                    agent=self.name,
                    choice=option.name,
                    score=score,
                    reasons=tuple(reasons) or ("path is acceptable from current resources",),
                    cautions=tuple(cautions),
                )
            )

        return tuple(sorted(recommendations, key=lambda item: item.score, reverse=True))
