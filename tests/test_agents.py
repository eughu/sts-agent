from sts_agent.coordinator import SpireCoordinator
from sts_agent.models import Act, Candidate, Character, GameState


def make_state(**overrides):
    data = {
        "character": Character.IRONCLAD,
        "act": Act.ACT_1,
        "floor": 5,
        "hp": 60,
        "max_hp": 80,
        "gold": 120,
        "deck": ("Strike", "Strike", "Defend", "Shrug It Off"),
        "relics": (),
        "potions": (),
    }
    data.update(overrides)
    return GameState(**data)


def test_card_agent_prioritizes_frontload_in_act_one():
    decision = SpireCoordinator().decide(
        "card",
        make_state(),
        (
            Candidate("Demon Form"),
            Candidate("Carnage"),
            Candidate("Skip"),
        ),
    )

    assert decision.best is not None
    assert decision.best.choice == "Carnage"


def test_route_agent_avoids_elite_when_low_hp():
    decision = SpireCoordinator().decide(
        "route",
        make_state(hp=18, max_hp=80, floor=10),
        (
            Candidate("Greedy elite", tags=("elite",)),
            Candidate("Campfire path", tags=("campfire", "hallway")),
        ),
    )

    assert decision.best is not None
    assert decision.best.choice == "Campfire path"


def test_shop_agent_rejects_unaffordable_option():
    decision = SpireCoordinator().decide(
        "shop",
        make_state(gold=90),
        (
            Candidate("Card remove", tags=("remove",), metadata={"cost": 125}),
            Candidate("Attack potion", tags=("potion",), metadata={"cost": 50}),
        ),
    )

    remove = next(item for item in decision.recommendations if item.choice == "Card remove")
    assert remove.score == 0.0


def test_combat_agent_prefers_lethal_line():
    decision = SpireCoordinator().decide(
        "combat",
        make_state(),
        (
            Candidate("Block for 12", tags=("block",), metadata={"incoming": 12}),
            Candidate("Bash + Strike lethal", tags=("attack",), metadata={"lethal": True}),
        ),
    )

    assert decision.best is not None
    assert decision.best.choice == "Bash + Strike lethal"


def test_boss_profile_pushes_slime_boss_aoe_pick():
    decision = SpireCoordinator().decide(
        "card",
        make_state(boss="Slime Boss", deck=("Strike", "Strike", "Defend")),
        (
            Candidate("Cleave"),
            Candidate("Demon Form"),
            Candidate("Skip"),
        ),
    )

    assert decision.best is not None
    assert decision.best.choice == "Cleave"
    assert "aoe" in decision.summary
