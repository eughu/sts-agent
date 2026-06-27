from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .coordinator import SpireCoordinator
from .models import Act, Candidate, Character, Decision, GameState
from .profile import analyze_run


class StateFileError(ValueError):
    """Raised when the Slay the Spire state JSON cannot be read."""


def load_state_file(path: str | Path) -> dict[str, Any]:
    state_path = Path(path)
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateFileError(f"State file not found: {state_path}") from exc
    except json.JSONDecodeError as exc:
        raise StateFileError(f"Invalid JSON in {state_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise StateFileError("State file root must be a JSON object.")
    return payload


def build_state(raw: dict[str, Any]) -> GameState:
    try:
        return GameState(
            character=Character(str(raw["character"]).lower()),
            act=Act(str(raw["act"]).lower()),
            floor=int(raw["floor"]),
            hp=int(raw["hp"]),
            max_hp=int(raw["max_hp"]),
            gold=int(raw.get("gold", 0)),
            deck=tuple(str(item) for item in raw.get("deck", [])),
            relics=tuple(str(item) for item in raw.get("relics", [])),
            potions=tuple(str(item) for item in raw.get("potions", [])),
            boss=str(raw.get("boss", "")),
            next_elite=str(raw.get("next_elite", "")),
            ascension=int(raw.get("ascension", 0)),
            notes=str(raw.get("notes", "")),
        )
    except KeyError as exc:
        raise StateFileError(f"Missing required state field: {exc.args[0]}") from exc
    except ValueError as exc:
        raise StateFileError(f"Invalid state value: {exc}") from exc


def build_candidate(raw: dict[str, Any] | str) -> Candidate:
    if isinstance(raw, str):
        return Candidate(name=raw)
    if not isinstance(raw, dict):
        raise StateFileError("Decision options must be strings or objects.")
    name = str(raw.get("name", "")).strip()
    if not name:
        raise StateFileError("Decision option is missing a name.")
    return Candidate(
        name=name,
        tags=tuple(str(tag) for tag in raw.get("tags", [])),
        metadata=dict(raw.get("metadata", {})),
    )


def evaluate_state_file(path: str | Path) -> dict[str, Any]:
    payload = load_state_file(path)
    raw_state = payload.get("state", payload)
    if not isinstance(raw_state, dict):
        raise StateFileError("'state' must be an object.")
    state = build_state(raw_state)
    decisions = evaluate_decisions(state, payload.get("decisions", []))
    profile = analyze_run(state)
    return {
        "ok": True,
        "source": str(Path(path)),
        "state": serialize_state(state),
        "profile": {
            "strengths": profile.strengths,
            "needs": profile.needs,
            "warnings": profile.warnings,
            "risk": profile.risk,
        },
        "decisions": decisions,
    }


def evaluate_decisions(
    state: GameState, raw_decisions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    if not raw_decisions:
        return []
    coordinator = SpireCoordinator()
    evaluated: list[dict[str, Any]] = []
    for item in raw_decisions:
        if not isinstance(item, dict):
            raise StateFileError("Each decision must be an object.")
        topic = str(item.get("topic", "")).strip().lower()
        options = tuple(build_candidate(raw) for raw in item.get("options", []))
        decision = coordinator.decide(topic, state, options)
        evaluated.append(serialize_decision(decision))
    return evaluated


def serialize_state(state: GameState) -> dict[str, Any]:
    data = asdict(state)
    data["character"] = state.character.value
    data["act"] = state.act.value
    data["hp_ratio"] = state.hp_ratio
    data["deck_size"] = state.deck_size
    return data


def serialize_decision(decision: Decision) -> dict[str, Any]:
    return {
        "topic": decision.topic,
        "summary": decision.summary,
        "best": decision.best.choice if decision.best else None,
        "recommendations": [
            {
                "agent": item.agent,
                "choice": item.choice,
                "score": round(item.score, 1),
                "reasons": item.reasons,
                "cautions": item.cautions,
            }
            for item in decision.recommendations
        ],
    }
