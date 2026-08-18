# Daily Terminal Drop
# Date: 2026-08-18
# Title: Salt Road Gambler: The Midnight Crossing

#!/usr/bin/env python3
"""
SALT ROAD GAMBLER: The Midnight Crossing
========================================
You are a courier hauling a crate of dreams across the Salt Road before
dawn. The border post takes no coin — only gambling chips. Sit at the dice
table, press your luck, and bank 3,000 credits before the horizon cracks.
Bank what you earn. Risk it and bust, and dawn takes everything.
"""
import random
import sys
from collections import Counter

GOAL = 3000       # credits needed to buy the crossing
ROUNDS = 10       # turns (table rounds) before dawn
TOTAL_DICE = 6


def score_dice(dice):
    """Return (points, kept) for a hand of dice following classic Farkle.

    A straight 1-6 is 1500 and uses all six dice. Otherwise score triples
    (1's = 1000, others = value*100, doubled per extra matching die) and any
    leftover single 1 (=100) or 5 (=50). 'kept' is how many dice scored.
    """
    if sorted(dice) == [1, 2, 3, 4, 5, 6]:
        return 1500, TOTAL_DICE
    counts = Counter(dice)
    pts = 0
    kept = 0
    for val in range(1, 7):
        n = counts[val]
        if n >= 3:
            base = 1000 if val == 1 else val * 100
            pts += base * (2 ** (n - 3))
            kept += n
        elif val == 1:
            pts += n * 100
            kept += n
        elif val == 5:
            pts += n * 50
            kept += n
    return pts, kept


def show(dice):
    faces = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6"}
    row = []
    for d in dice:
        top = faces[d]
        row.append("[ {} ]".format(top))
    return "  ".join(row)


def take_turn(rng):
    pot = 0
    dice_count = TOTAL_DICE
    while True:
        dice = [rng.randint(1, 6) for _ in range(dice_count)]
        pts, kept = score_dice(dice)
        print("  " + show(dice))
        print(f"  -> scores {pts} pts across {kept} dice.")
        if kept == 0:
            print("  BUST! No scoring dice rolled. The night takes the pot.")
            return 0
        pot += pts
        remaining = dice_count - kept
        if remaining == 0:
            print(f"  HOT DICE! All {TOTAL_DICE} scored — reroll all and keep going.")
            dice_count = TOTAL_DICE
            continue
        answer = input(
            f"  Pot {pot}. Keep rolling the remaining {remaining} dice? (y/N) "
        ).strip().lower()
        if answer != "y":
            print(f"  You bank {pot} credits.")
            return pot
        dice_count = remaining


def main():
    rng = random.Random()
    total = 0
    print("=" * 56)
    print("SALT ROAD GAMBLER :: THE MIDNIGHT CROSSING")
    print("=" * 56)
    print("Four hours to dawn, ten tables before the border closes.")
    print(f"Bank {GOAL} credits or the deckhands keep your crate.")
    print()
    print("  Rules: roll 6 dice. 1s = 100, 5s = 50. Three-of-a-kind")
    print("  (1s = 1000, others = value x100), doubled per extra die.")
    print("  A straight 1-6 = 1500. Bank anytime, or roll the rest and")
    print("  risk a BUST that empties the pot. All six scoring = hot dice.")
    print("  Commands: y to keep rolling, anything else to bank, quit")
    print()

    for round_num in range(1, ROUNDS + 1):
        print(f"-=[ ROUND {round_num}/{ROUNDS} :: banked {total}/{GOAL} ]=-")
        if total >= GOAL:
            break
        total += take_turn(rng)
        if total >= GOAL:
            break
        if round_num < ROUNDS:
            input("  [enter] slide to the next table...")

    print()
    if total >= GOAL:
        print(f"You bank {total} credits — the border lamp swings open.")
        print("The crate rides east on your shoulder. Dawn is just a rumor.")
    else:
        print(f"You reach {total} credits. The border post turns you away.")
        print("Somewhere past the dunes, your crate burns alone in the dark.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nThe dawn breaks. The table folds.")
        sys.exit(0)
