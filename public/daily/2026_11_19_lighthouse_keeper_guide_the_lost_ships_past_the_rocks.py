# Daily Terminal Drop
# Date: 2026-11-19
# Title: Lighthouse Keeper: Guide the lost ships past the rocks

#!/usr/bin/env python3
"""LIGHTHOUSE KEEPER - sweep the beam, guide every ship home!

Night has fallen on Rocky Point. Ships drift in from the east,
each one lost in the dark. Your lighthouse beam sweeps ONE column
of the bay each turn. Any ship in that column moves safely toward
the harbor; all others drift closer to the rocks. Guide each ship
into the harbor before it crashes on the rocks!

COMMANDS: 1-8 (sweep beam to column)   q quit
"""
import random
import sys

W = 8          # columns of the bay
H = 8          # rows: 0 = harbor (top), H-1 = rocks (bottom)
ROCKS = H - 1
TURNS = 30

def new_ship():
    """A new ship enters at the rocks row, random column."""
    return [random.randrange(W), H - 1]

def draw(ships, beam, score, turns, msg):
    grid = [["." for _ in range(W)] for _ in range(H)]
    for c, r in ships:
        grid[r][c] = "S"
    hr = "+" + "H" * W + "+"   # harbor wall
    print()
    print(hr)
    for r in range(1, H):
        row = " ".join(grid[r])
        mark = ""
        if beam >= 0:
            mark = "   ^ beam" if r == 0 else ""
        print("|" + row + "|" + (mark if r == 1 and beam >= 0 else ""))
    print("\\\\\\\\\\\\\\\\")  # rocky bottom
    print()
    print("Turns left: %d   Ships saved: %d   %s" % (turns, score, msg))
    print("Columns:    1 2 3 4 5 6 7 8")

def main():
    random.seed()
    ships = []
    beam = -1
    score = 0
    msg = ""
    turns = TURNS
    spawn = 3  # turns until next ship
    print(__doc__)
    while turns > 0:
        # spawn
        if spawn <= 0 and len(ships) < 5:
            ships.append(new_ship())
            spawn = random.randrange(2, 5)
        draw(ships, beam, score, turns, msg)
        if not ships:
            print("(No ships in the bay... one approaches!)")
        try:
            raw = input("beam> ").strip().lower()
        except EOFError:
            break
        if raw in ("q", "quit"):
            print("You clocked out. Ships saved: %d" % score)
            return
        if raw not in "12345678" or len(raw) != 1:
            msg = "? pick 1-8"
            continue
        col = int(raw) - 1
        beam = col
        turns -= 1
        spawn -= 1
        msg = ""
        alive = []
        for c, r in ships:
            if c == col:
                r -= 1  # swept: ship sails toward harbor
                if r == 0:
                    score += 1
                    msg += "Ship docked! "
                    continue
            else:
                r += 1  # drifts toward the rocks
                if r > ROCKS:
                    msg += "Ship lost on the rocks! "
                    continue
            alive.append([c, r])
        ships = alive
    print()
    print("Dawn breaks. Final score: %d ships saved." % score)
    if score >= 10:
        print("The town sings your praise, keeper!")
    elif score >= 5:
        print("A fair night's work, keeper.")
    else:
        print("The sea was cruel tonight...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
