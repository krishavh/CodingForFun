# Daily Terminal Drop
# Date: 2026-11-09
# Title: Glass Greenhouse: Mist the seedlings before the sun bakes them

#!/usr/bin/env python3
"""GLASS GREENHOUSE - mist the seedlings before the sun bakes them!

Dawn in a steamy glass greenhouse. Rows of SEEDLINGS drink
up the MIST from your watering wand. But the glass roof gets
HOT fast -- each turn the SUN CLIMBS and scorches any seedling
past its heat line. Catch falling RAIN DROPS to refill your
wand, then SPRAY a refreshing cloud of mist!

Legend:
  Y  YOU (wand in hand, bottom row)
  s  seedling (needs mist before heat hits!)
  o  rain drop (falls from the misting pipes -- catch it!)
  ^  heat line (sun bakes anything above it!)
  .  warm greenhouse air

HOW IT WORKS:
  Rain drops FALL one row each turn. Step (a/d) or up/down
  (w/s) to CATCH them -- each drop +1 WATER in your wand.
  Press M to MIST: every seedling within 2 rows of you
  gets a drink (+10 pts) and grows a bit taller!

  Each turn the HEAT LINE rises 1 row from the top.
  A seedling above the line WILTS (-5 pts) -- but a
  MISTED seedling (watered this turn) survives the
  scorch and DROPS back down cooled!

  Wilt 3 seedlings and the glass house is too sad.
  Survive 40 turns to WIN the morning shift!

COMMANDS: a/d/w/s move   m mist   q quit
"""
import random
import sys

W, H = 30, 16
HEAT_START = 5  # rows from top when heat line begins


def main():
    random.seed()
    px, py = W // 2, H - 1
    seedlings = {}  # (x,y) -> height
    for _ in range(6):
        x, y = random.randint(1, W - 2), random.randint(3, H - 4)
        seedlings[(x, y)] = 1
    drops = []
    water = 3
    heat = 0  # rows the heat has risen (line at row heat-1)
    score = 0
    wilted = 0
    turn = 0
    msg = "Catch rain drops, press m to mist seedlings!"
    print(__doc__)
    input("Press ENTER to start your morning shift...")
    while True:
        turn += 1
        heat = min(HEAT_START + turn // 2, H)
        # spawn a drop
        if random.random() < 0.7:
            drops.append([random.randint(0, W - 1), 0])
        # drops fall
        for d in drops:
            d[1] += 1
        caught = [d for d in drops if d[1] == py and d[0] == px]
        for _ in caught:
            water += 1
        drops = [d for d in drops if d[1] < H]
        # draw board
        grid = [["."] * W for _ in range(H)]
        heat_row = heat - 1
        if heat_row >= 0:
            for x in range(W):
                grid[heat_row][x] = "="
        for (x, y), h in seedlings.items():
            grid[y][x] = "s" if h < 3 else "S"
        for d in drops:
            if 0 <= d[1] < H:
                grid[d[1]][d[0]] = "o"
        grid[py][px] = "Y"
        print("\033[2J\033[H", end="")
        print(f"GLASS GREENHOUSE  turn {turn}/40  score {score}  "
              f"wilted {wilted}/3  water {water}")
        print(f"heat line: {'=' * W} (row {heat_row})")
        for row in grid:
            print("".join(row))
        print(f"[you ({px},{py})] {msg}  (a/d/w/s move, m mist, q quit)")
        msg = ""
        cmd = input("> ").strip().lower()
        if cmd == "q":
            print(f"You clock out early. Final score {score}.")
            return
        moved = False
        if cmd in ("a", "d") and not moved:
            nx = px + (-1 if cmd == "a" else 1)
            if 0 <= nx < W:
                px = nx
                moved = True
        elif cmd in ("w", "s"):
            ny = py + (-1 if cmd == "w" else 1)
            if 0 <= ny < H:
                py = ny
                moved = True
        misted = set()
        if cmd == "m" and water > 0:
            water -= 1
            for (x, y) in list(seedlings):
                if abs(y - py) <= 2 and abs(x - px) <= 4:
                    misted.add((x, y))
                    seedlings[(x, y)] += 1
                    score += 10
            if not misted:
                msg = "Mist drifts away... no seedlings close enough!"
            else:
                msg = f"You mist {len(misted)} seedlings! +10 each"
        elif cmd == "m":
            msg = "Wand is dry! Catch rain drops first."
        # heat scorches seedlings above the line
        for (x, y) in list(seedlings):
            if y < heat:
                if (x, y) in misted:
                    # cooled, drops back down
                    nh = seedlings.pop((x, y))
                    ny = min(H - 1, y + 2)
                    seedlings[(x, ny)] = max(1, nh - 1)
                    msg += " Steam saves a seedling! "
                else:
                    del seedlings[(x, y)]
                    score -= 5
                    wilted += 1
                    msg += f" A seedling wilts at ({x},{y})! -5 "
        # respawn a seedling if too few
        while len(seedlings) < 4:
            x, y = random.randint(0, W - 1), random.randint(0, H - 2)
            if (x, y) not in seedlings and y >= heat:
                seedlings[(x, y)] = 1
                break
        # win / lose checks
        if wilted >= 3:
            print(f"\nToo many wilted seedlings! Glass house blues."
                  f"\nFinal score {score} on turn {turn}.")
            return
        if turn >= 40:
            print(f"\nSHIFT COMPLETE! The morning sun rolls off the glass."
                  f"\nFinal score {score}. Seedlings saved: {len(seedlings)}")
            return


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGreenhouse closed.")
        sys.exit(0)
