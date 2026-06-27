from __future__ import annotations

from ..knowledge import CHARACTER_PRIORITIES, card_tags, deck_tags, normalize_name
from ..models import Candidate, GameState, Recommendation


class CardChoiceAgent:
    name = "card-choice-agent"

    def recommend(
        self, state: GameState, options: tuple[Candidate, ...]
    ) -> tuple[Recommendation, ...]:
        known_deck_tags = deck_tags(state.deck)
        recommendations: list[Recommendation] = []

        for option in options:
            clean = normalize_name(option.name)
            tags = card_tags(clean)
            score = 50.0
            reasons: list[str] = []
            cautions: list[str] = []

            for tag, weight in CHARACTER_PRIORITIES[state.character].items():
                if tag in tags:
                    score += 9.0 * weight
                    reasons.append(f"{tag} fits {state.character.value}")

            if state.act.value == "act1" and "frontload" in tags:
                score += 14.0
                reasons.append("early Act 1 rewards immediate damage")
            if state.act.value == "act1" and "scaling" in tags and "frontload" not in tags:
                score -= 4.0
                cautions.append("scaling can be slow before the deck has damage")

            if "block" in tags and "block" not in known_deck_tags and state.floor > 8:
                score += 8.0
                reasons.append("deck looks light on premium block")
            if "draw" in tags and state.deck_size >= 18:
                score += 7.0
                reasons.append("larger decks value draw and consistency")
            if "scaling" in tags and state.floor >= 15:
                score += 8.0
                reasons.append("boss and late-act fights need scaling")

            duplicate_count = sum(1 for card in state.deck if normalize_name(card) == clean)
            if duplicate_count:
                score -= min(10.0, duplicate_count * 3.0)
                cautions.append("already in deck; avoid redundancy unless it is core")

            if clean in {"clash", "setup", "distraction", "forethought"}:
                score -= 18.0
                cautions.append("historically inconsistent without strong support")

            if not tags:
                score -= 2.0
                cautions.append("unknown card; score is conservative")

            if clean in {"skip", "none"}:
                score = 45.0
                if state.deck_size >= 24:
                    score += 10.0
                    reasons.append("large deck may prefer skipping filler")
                cautions.append("skip only if rewards do not solve a real problem")

            recommendations.append(
                Recommendation(
                    agent=self.name,
                    choice=option.name,
                    score=score,
                    reasons=tuple(reasons) or ("reasonable but not clearly synergistic",),
                    cautions=tuple(cautions),
                )
            )

        return tuple(sorted(recommendations, key=lambda item: item.score, reverse=True))
