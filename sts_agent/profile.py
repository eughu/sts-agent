from __future__ import annotations

from dataclasses import dataclass

from .knowledge import BOSS_NEEDS, ELITE_NEEDS, deck_tags, normalize_name, threat_needs
from .models import GameState


@dataclass(frozen=True)
class RunProfile:
    strengths: tuple[str, ...]
    needs: tuple[str, ...]
    warnings: tuple[str, ...]
    risk: float

    def needs_tag(self, tag: str) -> bool:
        return tag in self.needs


def analyze_run(state: GameState) -> RunProfile:
    tags = deck_tags(state.deck)
    needs: set[str] = set()
    warnings: list[str] = []
    risk = 0.0

    boss_needs = threat_needs(state.boss, BOSS_NEEDS)
    elite_needs = threat_needs(state.next_elite, ELITE_NEEDS)
    needs.update(boss_needs)
    needs.update(elite_needs)

    if "attack" not in tags and state.floor <= 10:
        needs.add("frontload")
        warnings.append("early deck lacks reliable damage")
        risk += 12.0
    if "block" not in tags and state.floor >= 10:
        needs.add("block")
        warnings.append("deck lacks premium block for longer fights")
        risk += 10.0
    if "scaling" not in tags and state.floor >= 16:
        needs.add("scaling")
        warnings.append("deck may not scale for boss fights")
        risk += 12.0
    if "draw" not in tags and state.deck_size >= 20:
        needs.add("draw")
        warnings.append("large deck wants more draw or tutoring")
        risk += 7.0
    if "aoe" not in tags and state.act.value in {"act1", "act2"}:
        if normalize_name(state.boss) in {"slime boss", "collector"} or normalize_name(
            state.next_elite
        ) in {"sentries", "slavers", "gremlin leader"}:
            needs.add("aoe")
            warnings.append("upcoming fight rewards area damage")
            risk += 8.0
    if state.hp_ratio < 0.4:
        needs.add("block")
        warnings.append("low HP means route and potion decisions should be conservative")
        risk += 15.0
    if state.is_high_ascension:
        risk += 5.0
        warnings.append("high ascension punishes speculative picks")

    strengths = tuple(sorted(tags))
    return RunProfile(
        strengths=strengths,
        needs=tuple(sorted(needs)),
        warnings=tuple(warnings),
        risk=min(100.0, risk),
    )
