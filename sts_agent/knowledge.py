from __future__ import annotations

from .models import Character


COMMON_ATTACKS = {
    "anger",
    "battle trance",
    "blade dance",
    "bludgeon",
    "carnage",
    "claw",
    "compile driver",
    "dash",
    "doom and gloom",
    "empty fist",
    "eviscerate",
    "flurry of blows",
    "flying sleeves",
    "glass knife",
    "heavy blade",
    "immolate",
    "meteor strike",
    "perfected strike",
    "predator",
    "ragnarok",
    "rampage",
    "sands of time",
    "streamline",
    "sunder",
    "tantrum",
    "wild strike",
}

PREMIUM_BLOCK = {
    "after image",
    "blur",
    "calipers",
    "charge battery",
    "deceive reality",
    "defragment",
    "flame barrier",
    "footwork",
    "genetic algorithm",
    "glacier",
    "impervious",
    "leap",
    "mental fortress",
    "reinforced body",
    "spirit shield",
    "wallop",
}

SCALING_CARDS = {
    "accuracy",
    "barricade",
    "biased cognition",
    "corruption",
    "dark embrace",
    "defragment",
    "demon form",
    "deva form",
    "echo form",
    "electrodynamics",
    "envenom",
    "feel no pain",
    "footwork",
    "juggernaut",
    "limit break",
    "loop",
    "mental fortress",
    "noxious fumes",
    "rushdown",
    "wraith form",
}

CARD_TAGS: dict[str, set[str]] = {
    "accuracy": {"scaling", "shiv"},
    "after image": {"block", "shiv", "scaling"},
    "anger": {"attack", "frontload"},
    "apotheosis": {"premium", "upgrade"},
    "battle trance": {"draw"},
    "biased cognition": {"scaling", "orb"},
    "blade dance": {"attack", "shiv", "frontload"},
    "blur": {"block"},
    "carnage": {"attack", "frontload"},
    "corruption": {"scaling", "exhaust"},
    "dash": {"attack", "block", "frontload"},
    "defragment": {"scaling", "orb"},
    "demon form": {"scaling"},
    "disarm": {"block", "elite"},
    "doom and gloom": {"attack", "aoe", "orb"},
    "echo form": {"scaling"},
    "electrodynamics": {"scaling", "aoe", "orb"},
    "feel no pain": {"block", "scaling", "exhaust"},
    "flame barrier": {"block"},
    "footwork": {"block", "scaling"},
    "glass knife": {"attack", "frontload"},
    "glacier": {"block", "orb"},
    "immolate": {"attack", "aoe", "frontload"},
    "impervious": {"block"},
    "limit break": {"scaling"},
    "mental fortress": {"block", "scaling", "stance"},
    "noxious fumes": {"scaling", "aoe"},
    "offering": {"energy", "draw"},
    "piercing wail": {"block", "elite"},
    "predator": {"attack", "frontload", "draw"},
    "rushdown": {"draw", "stance", "scaling"},
    "shrug it off": {"block", "draw"},
    "skim": {"draw"},
    "tantrum": {"attack", "stance", "frontload"},
    "vault": {"premium", "draw"},
    "wallop": {"attack", "block"},
    "wraith form": {"block", "scaling", "premium"},
}

CHARACTER_PRIORITIES: dict[Character, dict[str, float]] = {
    Character.IRONCLAD: {
        "attack": 1.1,
        "frontload": 1.2,
        "exhaust": 1.15,
        "block": 0.9,
        "scaling": 1.0,
    },
    Character.SILENT: {
        "attack": 0.9,
        "shiv": 1.2,
        "block": 1.1,
        "draw": 1.1,
        "scaling": 1.1,
    },
    Character.DEFECT: {
        "orb": 1.25,
        "aoe": 1.1,
        "scaling": 1.15,
        "block": 1.0,
        "attack": 0.85,
    },
    Character.WATCHER: {
        "stance": 1.25,
        "attack": 1.1,
        "draw": 1.1,
        "block": 0.9,
        "frontload": 1.1,
    },
}


def normalize_name(name: str) -> str:
    return " ".join(name.lower().replace("+", "").split())


def card_tags(name: str) -> set[str]:
    clean = normalize_name(name)
    tags = set(CARD_TAGS.get(clean, set()))
    if clean in COMMON_ATTACKS:
        tags.add("attack")
    if clean in PREMIUM_BLOCK:
        tags.add("block")
    if clean in SCALING_CARDS:
        tags.add("scaling")
    return tags


def deck_tags(deck: tuple[str, ...]) -> set[str]:
    result: set[str] = set()
    for card in deck:
        result.update(card_tags(card))
    return result
