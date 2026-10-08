# Daily Terminal Drop
# Date: 2026-10-08
# Title: Kelp Forest Drift: Ride the current before the tide strands you

# Daily Terminal Drop
# Date: 2026-10-08
# Title: Kelp Forest Drift: Ride the current before the tide strands you

#!/usr/bin/env python3
"""KELP FOREST DRIFT - an original terminal game of currents and kelp.

You are a tiny fish in a giant kelp forest. The current pulls you
EAST (right) every turn. Kelp stalks grow UP from the floor and
BLOCK the current: behind each stalk the water is still.

Legend:
  ~  open water (current pushes you 1 east)
  |  kelp stalk (blocks current, safe spot behind it)
  F  your fish
  .  sea floor
  >  exit reef (east edge) - reach it to win!

Watch your BREATH: each turn underwater costs 1 breath. Surface
pockets (o) refill you, but the current drags you past them fast!

Each TURN you pick ONE:
  a      swim AGAINST the current (cost 2 breath, move 1 west)
  d      swim WITH the current (cost 1 breath, move 2 east)
  u      UP to surface pocket (if on one: +20 breath, else cost 3)
  s      hide STILL behind kelp (cost 1 breath, no move)
  q      quit

If breath hits 0, you float up -- GAME OVER. If current pushes you
past the reef edge, you crash -- GAME OVER. 40 turns of air start.
"""
import random
import shutil
import subprocess

WIDTH = 24
DEPTH = 7
START_BREATH = 45
TURN_LIMIT = 60


def clear():
    subprocess.run(["clear"] if True else [], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def make_row():
    """Random row: some water, some kelp, rare surface pocket."""
    row = []
    for _ in range(WIDTH):
        r = random.random()
        if r < 0.30:
            row.append("|")
        elif r < 0.36:
            row.append("o")
        else:
            row.append("~")
    return row


def new_forest():
    """Rows top(surface) to bottom(floor). Floor row is extra."""
    rows = [make_row() for _ in range(DEPTH)]
    for r in rows:
        r[0] = "~"  # spawn clear
        if random.random() < 0.5:
            r[WIDTH - 1] = "~"  # not always blocked at exit
    return rows


def show(fish, rows, breath, turn, msg):
    clear()
    cols = min(term_cols(), 100)
    print("KELP FOREST DRIFT" .center(cols))
    print(f"breath {breath}  turn {turn}/{TURN_LIMIT}".center(cols))
    print()
    for y, row in enumerate(rows):
        line = ""
        for x, cell in enumerate(row):
            if (fish[0], fish[1]) == (x, y):
                line += "F"
            elif cell == "o":
                line += "o"
            elif cell == "|":
                line += "|"
            else:
                # current arrow: shows drag direction
                line += "~" if x == 0 else ("~" if row[x - 1] == "|" else ">")
        print(" " + line)
    print(" " + "." * WIDTH)
    print()
    print(msg)
    print("[a]gainst [d]with [u]p [s]till [q]uit > ", end="", flush=True)


def blocked(x, y, rows):
    """Kelp blocks east moves INTO it; you may still land on o."""
    return rows[y][x] == "|"


def drift_push(x, y, rows):
    """Current pushes 1 east unless kelp west of us blocks it."""
    if x == 0:
        return x
    if rows[y][x - 1] == "|":
        return x
    return min(x + 1, WIDTH)  # past edge = crash


def main():
    random.seed()
    rows = new_forest()
    fish = [0, random.randrange(DEPTH)]
    breath = START_BREATH
    turn = 0
    msg = "Reach the reef east! Kelp blocks the current."
    while True:
        show(fish, rows, breath, turn, msg)
        cmd = input().strip().lower()[:1]
        if cmd == "q":
            print("\nYou swim home. Bye!")
            return
        turn += 1
        if turn > TURN_LIMIT:
            print("\nSun sets. Too slow! GAME OVER")
            return
        x, y = fish
        if cmd == "a":
            breath -= 2
            x = max(0, x - 1)
        elif cmd == "d":
            breath -= 1
            if not blocked(min(x + 2, WIDTH - 1), y, rows):
                x = min(x + 2, WIDTH - 1)
            elif not blocked(x + 1, y, rows):
                x = min(x + 1, WIDTH - 1)
        elif cmd == "u":
            if rows[y][x] == "o":
                breath += 20
                msg = "GLUB GLUB! Fresh air!"
            else:
                breath -= 3
                msg = "No pocket here! Panic bubbles..."
        elif cmd == "s":
            breath -= 1
            msg = "You hide still behind the kelp."
        else:
            breath -= 1
            msg = "You wiggle in place."
        # apply drift after move (unless still kelp-sheltered)
        if not (cmd == "s" and x > 0 and rows[y][x - 1] == "|"):
            x = drift_push(x, y, rows)
        if x >= WIDTH:
            print("\nYou crash into the reef! GAME OVER")
            return
        if rows[y][x] == "o" and cmd != "u":
            breath += 2  # small sip passing through
        fish = [x, y]
        breath -= 1  # living underwater costs air
        if breath <= 0:
            print("\nOut of air! You float up, dizzy. GAME OVER")
            return
        if x == WIDTH - 1:
            print(f"\nYou reach the reef! Turn {turn}, breath {breath}. YOU WIN!")
            return


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
