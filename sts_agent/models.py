from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Character(str, Enum):
    IRONCLAD = "ironclad"
    SILENT = "silent"
    DEFECT = "defect"
    WATCHER = "watcher"


class Act(str, Enum):
    ACT_1 = "act1"
    ACT_2 = "act2"
    ACT_3 = "act3"
    ACT_4 = "act4"


@dataclass(frozen=True)
class GameState:
    character: Character
    act: Act
    floor: int
    hp: int
    max_hp: int
    gold: int = 0
    deck: tuple[str, ...] = ()
    relics: tuple[str, ...] = ()
    potions: tuple[str, ...] = ()
    boss: str = ""
    next_elite: str = ""
    ascension: int = 0
    notes: str = ""

    @property
    def hp_ratio(self) -> float:
        if self.max_hp <= 0:
            return 0.0
        return max(0.0, min(1.0, self.hp / self.max_hp))

    @property
    def deck_size(self) -> int:
        return len(self.deck)

    @property
    def is_high_ascension(self) -> bool:
        return self.ascension >= 15


@dataclass(frozen=True)
class Candidate:
    name: str
    tags: tuple[str, ...] = ()
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class Recommendation:
    agent: str
    choice: str
    score: float
    reasons: tuple[str, ...]
    cautions: tuple[str, ...] = ()

    def short(self) -> str:
        return f"{self.agent}: {self.choice} ({self.score:.1f})"


@dataclass(frozen=True)
class Decision:
    topic: str
    recommendations: tuple[Recommendation, ...]
    summary: str

    @property
    def best(self) -> Recommendation | None:
        if not self.recommendations:
            return None
        return max(self.recommendations, key=lambda item: item.score)


def split_csv(text: str | None) -> tuple[str, ...]:
    if not text:
        return ()
    return tuple(part.strip() for part in text.split(",") if part.strip())


def candidates_from_names(names: Iterable[str]) -> tuple[Candidate, ...]:
    return tuple(Candidate(name=name.strip()) for name in names if name.strip())
