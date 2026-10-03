# Daily Terminal Drop
# Date: 2026-10-03
# Title: Pickle Pit Boss: Tip the oldest barrel before the brine blows

#!/usr/bin/env python3
"""PICKLE PIT BOSS - an original terminal game of fermenting barrels.

You are the new pickle pit boss. Five barrels of brine sit in the cellar,
and every day the oldest barrel must be TIPPED and SOLD before it turns.

Barrels ferment at different speeds. Each day you pick ONE barrel:
  1-5   tip barrel n (sell its pickles, gain its FERMEN score)
  m     mix the barrels (shuffle their speeds - costs 1 splash)
  q     quit the cellar (end of week)

After your pick, NIGHT FALLS: every barrel gains +1 ferment... but the
barrel you just sold REFILLS at ferment 0. Any barrel that reaches
ferment 10 EXPLODES (game over, brine everywhere!).

A pickle-taster visits every 3 days and buys your OLDEST barrel
(highest ferment) AUTOMATICALLY -- plan your tipping around it!

Survive 14 days. Sell sweet pickles (low ferment = CRUNCH),
score points for every barrel sold. How rich can you get?
"""
import random
import sys

DAYS = 14
BOOM = 10
NUM = 5


def new_barrels():
    """Barrel = [ferment, price]. Fresh barrels cost 3."""
    return [[random.randint(0, 4), 3] for _ in range(NUM)]


def draw(barrels, day, splashes, points, msg):
    print()
    print(f"DAY {day} of {DAYS}   points:{points}   splashes:{splashes}")
    print("  barrel   1     2     3     4     5")
    for row, label in ((0, "ferment"), (1, "price  ")):
        cells = []
        for b in barrels:
            f = b[0]
            bar = "#" * f + "." * (BOOM - f) if row == 0 else ""
            cells.append(bar if row == 0 else str(b[1]))
        print(f"  {label}  " + "  ".join(cells))
    print("  legend   # ferment   . room left   explodes at 10")
    if msg:
        print(msg)
    print("tip 1-5 / m mix / q quit >")


def main():
    random.seed()
    barrels = new_barrels()
    day, splashes, points = 1, 3, 0
    msg = "Welcome to the cellar. Tip low ferment for CRUNCH points!"
    while day <= DAYS:
        draw(barrels, day, splashes, points, msg)
        try:
            raw = input().strip().lower()
        except EOFError:
            print("\nCellar closed early (EOF). Bye!")
            return
        msg = ""
        if raw == "q":
            print(f"\nYou quit after {day - 1} days. Final points: {points}")
            return
        if raw == "m":
            if splashes <= 0:
                msg = "No splashes left to mix!"
                continue
            splashes -= 1
            random.shuffle(barrels)
            msg = "You splash the barrels around. Speeds shuffled!"
            night(barrels)
            day += 1
            continue
        if not raw.isdigit() or not (1 <= int(raw) <= NUM):
            msg = "Pick 1-5, m to mix, or q."
            continue
        n = int(raw) - 1
        f = barrels[n][0]
        if f >= BOOM:
            msg = "That barrel is already brine!"
            continue
        crunch = max(0, 4 - f)  # low ferment = sweet crunch
        points += crunch + barrels[n][1]
        msg = f"Sold barrel {n + 1}: +{crunch + barrels[n][1]} pts (crunch {crunch})"
        barrels[n] = [0, 3]  # refill fresh
        night(barrels)
        day += 1
        # pickle-taster buys oldest barrel every 3 days
        if day % 3 == 0 and day <= DAYS:
            oldest = max(range(NUM), key=lambda i: barrels[i][0])
            if barrels[oldest][0] > 0:
                f2 = barrels[oldest][0]
                pts = max(0, 4 - f2) + barrels[oldest][1]
                points += pts
                msg += f" | Taster bought barrel {oldest + 1}: +{pts} pts"
                barrels[oldest] = [0, 3]
                night(barrels)
        if any(b[0] >= BOOM for b in barrels):
            boom_i = next(i for i, b in enumerate(barrels) if b[0] >= BOOM)
            draw(barrels, day, splashes, points, msg)
            print(f"\nBARREL {boom_i + 1} EXPLODED! Brine everywhere. Final: {points}")
            return
    draw(barrels, day, splashes, points, msg)
    print(f"\nWEEK DONE! You survived {DAYS} days with {points} points!")


def night(barrels):
    for b in barrels:
        b[0] += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCellar door slams shut. Bye!")
        sys.exit(0)
