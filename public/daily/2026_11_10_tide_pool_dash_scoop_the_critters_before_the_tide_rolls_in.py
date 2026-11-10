# Daily Terminal Drop
# Date: 2026-11-10
# Title: Tide Pool Dash: Scoop the critters before the tide rolls in

#!/usr/bin/env python3
"""TIDE POOL DASH - scoop the critters before the tide rolls in!

Low tide reveals a rocky TIDE POOL teeming with SEA CRITTERS!
You are a curious kid with a plastic SCOOP. Hurry -- the tide
creeps in one wave every turn. When the wave reaches a critter,
it WASHES AWAY (gone for good!).

Legend:
  Y  YOU (with your scoop!)
  c  crab (sideways scuttler, 10 pts)
  m  mussel (opens when waves tickle, 5 pts)
  s  sea star (slow but sticky, 15 pts)
  o  octopus (zips away quick, 30 pts!)
  ~  incoming tide (washes critters away!)
  .  wet rocky sand

HOW IT WORKS:
  Move (a/d/w/s) and press B to SCOOP all critters
  touching your bucket (8 directions around you)!
  Each critter caught = points. O = octopus = 30!

  Each turn the TIDE RISES 1 row from the sea.
  Any critter the tide touches is WASHED AWAY!
  Tide washes YOU too? Splash! -3 pts and you
  scramble back to the top of the pool.

  Catch 120 pts of critters before high tide
  fills the pool to WIN! If 10 critters wash
  away, the pool is empty -- game over!

COMMANDS: a/d/w/s move   b scoop   q quit
"""
import random

W, H = 28, 14
TIDE_START = 10  # rows from bottom when tide begins
GOAL = 120
MAX_WASHED = 10

CRITTERS = [("c", 10), ("m", 5), ("s", 15), ("o", 30)]


def board(px, py, critters, tide, msg, score):
    grid = [["." for _ in range(W)] for _ in range(H)]
    for (x, y), (ch, pts) in critters.items():
        grid[y][x] = ch
    # tide rises from the bottom (sea)
    for y in range(H - tide, H):
        for x in range(W):
            grid[y][x] = "~"
    grid[py][px] = "Y"
    out = []
    if msg:
        out.append(msg)
    out += ["+" + "-" * W + "+"]
    for row in grid:
        out.append("|" + "".join(row) + "|")
    out.append("+" + "-" * W + "+")
    out.append("Score: %d  Tide: %d/12  (b=scoop, q=quit)" % (score, tide))
    return "\n".join(out)


def main():
    random.seed()
    px, py = W // 2, 1
    score = 0
    tide = 0
    washed = 0
    turns = 0
    msg = "Scoop critters before the tide rolls in!"
    critters = {}
    while len(critters) < 8:
        x, y = random.randint(0, W - 1), random.randint(0, H - 3)
        if (x, y) != (px, py) and (x, y) not in critters:
            ch, pts = random.choice(CRITTERS)
            critters[(x, y)] = [ch, pts]
    # guarantee a snack near spawn so first scoop pays
    for oy in (1, 2):
        if (px, py + oy) not in critters:
            critters[(px, py + oy)] = ["c", 10]
    print(__doc__)
    input("Press ENTER to hit the tide pools...")
    while True:
        turns += 1
        print(board(px, py, critters, tide, msg, score))
        cmd = input("> ").strip().lower()
        if cmd == "q":
            print("Bye! Final score: %d" % score)
            return
        dx, dy = {"a": (-1, 0), "d": (1, 0), "w": (0, -1), "s": (0, 1)}.get(cmd, (0, 0))
        if dx or dy:
            nx, ny = px + dx, py + dy
            if 0 <= nx < W and 0 <= ny < H:
                px, py = nx, ny
        if cmd == "b":
            got = []
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    key = (px + ox, py + oy)
                    if key in critters:
                        ch, pts = critters.pop(key)
                        score += pts
                        got.append("%s(+%d)" % (ch, pts))
            msg = "Scooped: %s!" % " ".join(got) if got else "Empty scoop!"
        else:
            msg = ""
        if cmd != "b" and cmd != "":
            msg = ""
        # tide rises every 2 turns
        if turns % 2 == 0 and tide < 12:
            tide += 1
        # tide washes critters
        for key in list(critters):
            x, y = key
            if y >= H - tide:
                ch = critters.pop(key)[0]
                washed += 1
                extra = " Wave took the %s!" % {"c": "crab", "m": "mussel", "s": "sea star", "o": "octopus"}.get(ch, "critter")
                if cmd == "b":
                    msg += extra
                else:
                    msg = msg or ""  # keep simple
                    msg = (msg + extra) if msg else extra.lstrip()
        # spawn new critters to keep pool lively
        while len(critters) < 8 and washed < MAX_WASHED:
            x, y = random.randint(0, W - 1), random.randint(0, H - 3)
            if (x, y) != (px, py) and (x, y) not in critters and y < H - tide:
                ch, pts = random.choice(CRITTERS)
                critters[(x, y)] = [ch, pts]
        # tide catches YOU
        if py >= H - tide:
            score = max(0, score - 3)
            py = 0
            msg += " Splash! The tide got you! Back to top."
        if score >= GOAL:
            print(board(px, py, critters, tide, "", score))
            print("YOU WIN! Bucket full with %d pts in %d turns!" % (score, turns))
            return
        if washed >= MAX_WASHED:
            print(board(px, py, critters, tide, "", score))
            print("Pool washed clean... only %d pts. Tide wins!" % score)
            return


if __name__ == "__main__":
    main()
