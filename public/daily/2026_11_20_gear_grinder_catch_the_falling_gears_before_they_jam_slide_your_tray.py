# Daily Terminal Drop
# Date: 2026-11-20
# Title: Gear Grinder: Catch the falling gears before they jam: Slide your tray, grab gold, dodge the rust

# Daily Terminal Drop
# Date: 2026-11-20
# Title: Gear Grinder: Catch the falling gears before they jam

#!/usr/bin/env python3
"""GEAR GRINDER - catch the falling gears before they jam the works!

The old clock tower is raining gears! Slide your TRAY left and
right to CATCH them. A golden gear is worth 5 points, a plain
gear 1 -- but a RUSTY gear (x) jams your tray for 2 turns!
Miss 5 gears and the works seize up.

COMMANDS: a (left)  d (right)  s (stay)  q (quit)
"""
import random
import sys

W = 12          # columns of the tower
H = 10          # rows of falling space (tray sits below row H-1)
MISSES = 5      # gears you may drop before jam

def new_gear():
    """Random gear: [col, row, kind] kind in 'gold','plain','rusty'"""
    roll = random.random()
    kind = "plain"
    if roll < 0.15:
        kind = "gold"
    elif roll < 0.35:
        kind = "rusty"
    return [random.randrange(W), 0, kind]

def draw(gears, tray, score, misses, tray_wait, msg):
    print()
    print("+" + "-" * W + "+")
    grid = [[" "] * W for _ in range(H)]
    for c, r, kind in gears:
        if 0 <= r < H:
            grid[r][c] = {"gold": "O", "plain": "o", "rusty": "x"}[kind]
    tray_row = [" "] * W
    for c in tray:
        if 0 <= c < W:
            tray_row[c] = "="
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "=" * W + "+")
    print("tray  " + "".join(tray_row))
    wait = "   TRAY JAMMED (%d)" % tray_wait if tray_wait else ""
    print("score %d   dropped %d/%d%s" % (score, misses, MISSES, wait))
    if msg:
        print(msg)
    print("[a] left [d] right [s] stay [q] quit", end=" ", flush=True)

def main():
    gears = []
    tray = [5, 6, 7]
    score = 0
    misses = 0
    tray_wait = 0
    msg = "Catch gears! o=1 O=5 x=rusty (jams tray 2 turns)"
    spawn_in = 0
    while True:
        spawn_in -= 1
        if spawn_in <= 0:
            gears.append(new_gear())
            spawn_in = random.randrange(2, 4)
        draw(gears, tray, score, misses, tray_wait, msg)
        cmd = input().strip().lower()
        if cmd == "q":
            print("\nBye! Final score: %d" % score)
            return
        msg = ""
        if cmd not in ("a", "d", "s", ""):
            msg = "? use a / d / s"
        elif not tray_wait:
            if cmd == "a" and tray[0] > 0:
                tray = [c - 1 for c in tray]
            elif cmd == "d" and tray[-1] < W - 1:
                tray = [c + 1 for c in tray]
        elif tray_wait:
            tray_wait -= 1
            msg = "tray jammed! (%d more turns)" % tray_wait if tray_wait else "tray works again!"
        # gears fall one row
        remaining = []
        for c, r, kind in gears:
            r += 1
            if r == H - 1 and c in tray:
                if kind == "rusty":
                    msg = (msg + " " if msg else "") + "RUSTY GEAR! tray jams!"
                    tray_wait = 2
                else:
                    pts = 5 if kind == "gold" else 1
                    score += pts
                    msg = (msg + " " if msg else "") + ("GOLDEN! +%d" % pts if pts > 1 else "+1")
                continue
            if r >= H:
                misses += 1
                msg = (msg + " " if msg else "") + "missed %d!" % misses
                continue
            remaining.append([c, r, kind])
        gears = remaining
        if misses >= MISSES:
            print("\nJAMMED! Too many gears dropped. Final score: %d" % score)
            return

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
        sys.exit(0)
