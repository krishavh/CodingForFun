# Daily Terminal Drop
# Date: 2026-10-14
# Title: Mushroom Spores: Ride the gusts before the vigor wilts

#!/usr/bin/env python3
"""MUSHROOM SPORES - an original terminal game of drift and domes.

You are a spore riding the wind across the mushroom meadow. The wind
blows WEST (left) every turn. Giant mushrooms grow from the floor and
BLOCK the wind: behind each cap the air is still.

Legend:
  .  open air (wind pushes you 1 left)
  M  mushroom cap (blocks wind, safe perch behind it)
  @  your spore
  =  forest floor (start, land soft to score)
  $  dew drop (collect for points, +10)

Watch your VIGOR: each turn afloat costs 1. Resting on a cap or floor
costs 0. Land on the floor between mushrooms to SCORE BIG (+50) and
spring back up!

Each TURN you pick ONE:
  a      drift AGAINST the wind (cost 2 vigor, move 1 right)
  d      dive WITH the wind (cost 1 vigor, move 2 left)
  w      waft UP (cost 2 vigor, rise 1 row)
  s      settle DOWN (cost 1 vigor, sink 1 row)
  q      quit

If vigor hits 0, you wilt -- GAME OVER. 50 turns of gusts start.
"""
import random
import shutil
import subprocess

WIDTH = 32
HEIGHT = 10
START_VIGOR = 45
TURN_LIMIT = 50
ROWS_ABOVE = 6  # playable air rows above the floor


def clear():
    subprocess.run(["clear"] if True else [], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def build_row():
    """Build one row of air. Wind blows west (left)."""
    row = ["."] * WIDTH
    for _ in range(random.randint(1, 2)):
        x = random.randrange(WIDTH)
        row[x] = "M"  # cap
    for _ in range(random.randint(0, 2)):
        x = random.randrange(WIDTH)
        if row[x] == ".":
            row[x] = "$"  # dew
    return row


def draw(rows, y, x, vigor, turns, score, msg):
    clear()
    cols = min(max(term_cols(), 40), 120)
    print("MUSHROOM SPORES".center(cols))
    print(("vigor:%d  turns:%d/%d  score:%d" % (vigor, turns, TURN_LIMIT, score)).center(cols))
    print()
    screen = []
    for ry in range(HEIGHT):
        if ry == HEIGHT - 1:
            screen.append(["="] * WIDTH)
        else:
            src = rows[ry] if ry < len(rows) else ["."] * WIDTH
            row = list(src)
            if ry == y:
                row[x] = "@"
            screen.append(row)
    for ry in range(HEIGHT):
        print("  " + "".join(screen[ry]) + "  ")
    print()
    print("  " + ("wind >>> . <<< WEST  every turn (unless you hide!)"))
    print("  a=anti-wind(right)  d=dive(left)  w=up  s=down  q=quit")
    if msg:
        print("  ** %s" % msg)
    print()


def main():
    random.seed()
    rows = [build_row() for _ in range(ROWS_ABOVE)]
    y = 0
    x = WIDTH - 6
    vigor = START_VIGOR
    turns = 0
    score = 0
    msg = "Ride the gusts! Land on floor between mushrooms for +50!"
    while turns < TURN_LIMIT and vigor > 0:
        draw(rows, y, x, vigor, turns, score, msg)
        try:
            choice = input("  move [a/d/w/s/q] > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if choice == "q":
            break
        msg = ""
        moved = False
        cost = 0
        if choice == "a":
            cost = 2
            nx = min(x + 1, WIDTH - 2)
            moved = nx != x
            x = nx
        elif choice == "d":
            cost = 1
            nx = max(x - 2, 0)
            moved = nx != x
            x = nx
        elif choice == "w":
            cost = 2
            if y > 0:
                y -= 1
                moved = True
            else:
                msg = "Sky ceiling! Can't go higher."
        elif choice == "s":
            cost = 1
            if y < ROWS_ABOVE - 1:
                y += 1
                moved = True
            else:
                # land on floor
                if rows[y][x] == "M":
                    msg = "Cap blocks the floor here!"
                else:
                    score += 50
                    msg = "SOFT LANDING! +50 and spring back up!"
                    y = 0  # spring to top
                    vigor += 5
        else:
            msg = "Use a/d/w/s or q to quit."
            cost = 0
        vigor -= cost
        # wind drift (west) if not resting on cap
        on_cap = rows[y][x] == "M" if y < ROWS_ABOVE else False
        if choice in ("a", "d", "w", "s") and not on_cap:
            nx = max(x - 1, 0)
            if nx != x:
                x = nx
                if msg == "":
                    msg = "Wind pushes you west!"
        # collect dew
        if y < ROWS_ABOVE and rows[y][x] == "$":
            rows[y][x] = "."
            score += 10
            msg = (msg + " " if msg else "") + "Dew drop! +10"
        # refill row at top when spore lands low (recycle air)
        if choice == "s" and y == ROWS_ABOVE - 1:
            rows.pop(0)
            rows.append(build_row())
        # cap bonk: drifting into cap costs extra bump? No, caps are safe
        turns += 1
        if vigor <= 0:
            msg = "Wilted! Out of vigor."
    # final draw
    draw(rows, y, x, max(vigor, 0), turns, score, msg or "Run over!")
    print("  FINAL SCORE: %d  (%d turns)" % (score, turns))
    print()


if __name__ == "__main__":
    main()
