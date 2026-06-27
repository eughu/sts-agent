from __future__ import annotations

import argparse
from typing import Any

from .coordinator import SpireCoordinator
from .models import Act, Candidate, Character, GameState, split_csv


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    state = GameState(
        character=Character(args.character),
        act=Act(args.act),
        floor=args.floor,
        hp=args.hp,
        max_hp=args.max_hp,
        gold=args.gold,
        deck=split_csv(args.deck),
        relics=split_csv(args.relics),
        potions=split_csv(args.potions),
        boss=args.boss or "",
        next_elite=args.next_elite or "",
        ascension=args.ascension,
        notes=args.notes or "",
    )
    options = parse_options(args.option)
    decision = SpireCoordinator().decide(args.topic, state, options)
    print_decision(decision)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sts-agent",
        description="Local multi-agent companion for Slay the Spire 1 decisions.",
    )
    parser.add_argument("topic", choices=("card", "combat", "relic", "route", "shop"))
    parser.add_argument("--character", choices=[item.value for item in Character], required=True)
    parser.add_argument("--act", choices=[item.value for item in Act], required=True)
    parser.add_argument("--floor", type=int, required=True)
    parser.add_argument("--hp", type=int, required=True)
    parser.add_argument("--max-hp", type=int, required=True)
    parser.add_argument("--gold", type=int, default=0)
    parser.add_argument("--deck", default="", help="Comma separated deck cards.")
    parser.add_argument("--relics", default="", help="Comma separated relics.")
    parser.add_argument("--potions", default="", help="Comma separated potions.")
    parser.add_argument("--boss", default="", help="Known boss, for example 'Slime Boss'.")
    parser.add_argument("--next-elite", default="", help="Known or suspected next elite.")
    parser.add_argument("--ascension", type=int, default=0)
    parser.add_argument("--notes", default="")
    parser.add_argument(
        "--option",
        action="append",
        required=True,
        help=(
            "Decision option. Format: name|tag1,tag2|key=value,key=value. "
            "Example: 'Elite path|elite,campfire' or 'Buy remove|remove|cost=125'."
        ),
    )
    return parser


def parse_options(raw_options: list[str]) -> tuple[Candidate, ...]:
    return tuple(parse_option(raw) for raw in raw_options)


def parse_option(raw: str) -> Candidate:
    parts = raw.split("|")
    name = parts[0].strip()
    tags = split_csv(parts[1]) if len(parts) >= 2 else ()
    metadata = parse_metadata(parts[2]) if len(parts) >= 3 else {}
    if not name:
        raise ValueError("Option name cannot be empty.")
    return Candidate(name=name, tags=tags, metadata=metadata)


def parse_metadata(raw: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for part in split_csv(raw):
        if "=" not in part:
            result[part] = True
            continue
        key, value = part.split("=", 1)
        result[key.strip()] = coerce_value(value.strip())
    return result


def coerce_value(value: str) -> str | int | float | bool:
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def print_decision(decision) -> None:
    print(decision.summary)
    print()
    for index, recommendation in enumerate(decision.recommendations, start=1):
        print(f"{index}. {recommendation.choice} [{recommendation.score:.1f}]")
        for reason in recommendation.reasons:
            print(f"   + {reason}")
        for caution in recommendation.cautions:
            print(f"   ! {caution}")


if __name__ == "__main__":
    raise SystemExit(main())
