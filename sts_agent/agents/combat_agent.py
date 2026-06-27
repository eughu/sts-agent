from __future__ import annotations

from ..knowledge import card_tags, normalize_name
from ..models import Candidate, GameState, Recommendation
from ..profile import analyze_run


class CombatAgent:
    name = "combat-agent"

    def recommend(
        self, state: GameState, options: tuple[Candidate, ...]
    ) -> tuple[Recommendation, ...]:
        profile = analyze_run(state)
        recommendations: list[Recommendation] = []

        for option in options:
            clean = normalize_name(option.name)
            tags = set(option.tags) | card_tags(clean)
            score = 50.0
            reasons: list[str] = []
            cautions: list[str] = []

            incoming = float(option.metadata.get("incoming", 0) or 0)
            lethal = bool(option.metadata.get("lethal", False))
            energy = float(option.metadata.get("energy", 0) or 0)

            if lethal:
                score += 40.0
                reasons.append("line claims lethal damage")
            if incoming >= max(10, state.hp * 0.25):
                if "block" in tags or "defend" in clean:
                    score += 20.0
                    reasons.append("large incoming damage makes block valuable")
                elif not lethal:
                    score -= 18.0
                    cautions.append("does not address dangerous incoming damage")
            if "scaling" in tags and incoming <= 8 and not lethal:
                score += 12.0
                reasons.append("safe turn to deploy scaling")
            if "scaling" in tags and profile.needs_tag("scaling") and not lethal:
                score += 7.0
                reasons.append("fight plan needs scaling to close safely")
            if "attack" in tags and state.act.value == "act1":
                score += 8.0
                reasons.append("Act 1 fights reward ending fights quickly")
            if "aoe" in tags and profile.needs_tag("aoe"):
                score += 8.0
                reasons.append("upcoming or current threat rewards area damage")
            if "draw" in tags:
                score += 4.0
                reasons.append("draw improves line flexibility")
            if energy > 0:
                score += min(8.0, energy * 2.0)
                reasons.append("uses available energy productively")
            if "potion" in tags:
                if lethal or incoming >= state.hp * 0.35:
                    score += 15.0
                    reasons.append("potion use is justified by danger or lethal")
                else:
                    score -= 7.0
                    cautions.append("save potion unless this prevents major damage")

            recommendations.append(
                Recommendation(
                    agent=self.name,
                    choice=option.name,
                    score=score,
                    reasons=tuple(reasons) or ("line is playable but lacks standout upside",),
                    cautions=tuple(cautions),
                )
            )

        return tuple(sorted(recommendations, key=lambda item: item.score, reverse=True))
