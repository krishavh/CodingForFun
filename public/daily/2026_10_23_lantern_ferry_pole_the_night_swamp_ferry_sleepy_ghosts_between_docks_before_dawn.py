# Daily Terminal Drop
# Date: 2026-10-23
# Title: Lantern Ferry: Pole the Night Swamp: Ferry sleepy ghosts between docks before dawn

#!/usr/bin/env python3
"""LANTERN FERRY - pole the night ferry, land sleepy ghosts before dawn!

You ferry ghostly passengers across a dark swamp. Your POLE pushes
the boat; currents DRIFT you each turn. Dock at glowing LANES
to drop passengers -- but grab every ghost you pass!

Legend:
  @  your ferry (starts with 3 ghosts aboard)
  #  reeds (blocks you)
  ~  slow current (push 1)
  =  fast current (push 2!)
  D  dock (land ghosts here, glow fades)

HOW IT WORKS:
  Each turn: pick a direction to POLE (move 1) or '.' to drift.
  Then CURRENTS push you: every ~ under you shoves 1, = shoves 2.
  Passengers board when you touch G (sleepy ghost, wanders!).
  Dock on D to drop ALL ghosts -- 25 points each!

WATCH THE DAWN: 40 turns and the sun rises. Swamp winds WRAP
  around (east edge meets west!) -- use the wrap to slingshot!

GOAL: 12 ghosts landed before dawn -- or swamp keeps them forever!
COMMANDS: a/d/w/s pole   . drift   q quit
"""
import random
import shutil
import subprocess

W, H = 36, 14
GOAL = 12
TURNS = 40


def clear():
    subprocess.run(["clear"], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def new_swamp():
    """Reeds, docks, currents, ghosts, ferry."""
    g = [["."] * W for _ in range(H)]
    spots = random.sample(range(W * H), 40)
    k = iter(spots)
    for _ in range(8):
        g[next(k) // W][next(k) % W] = "#" if False else "#"
    for i in range(8):
        g[spots[i] // W][spots[i] % W] = "#"
    for j in range(8, 14):
        g[spots[j] // W][spots[j] % W] = "~"
    for j in range(14, 18):
        g[spots[j] // W][spots[j] % W] = "="
    for j in range(18, 21):
        g[spots[j] // W][spots[j] % W] = "D"
    ghosts = []
    for j in range(21, 24):
        x, y = spots[j] % W, spots[j] // W
        g[y][x] = "G"
        ghosts.append([x, y])
    fx, fy = W // 2, H // 2
    g[fy][fx] = "@"
    return g, [fx, fy], ghosts


def wrap_x(x):
    return x % W


def wrap_y(y):
    return y % H


def tile(g, x, y):
    return g[y % H][x % W]


def draw(g, boat, ghosts, ghosts_landed, turn, msg):
    print("\n".join("".join(row) for row in g))
    print("ghosts aboard: %d   landed: %d/%d   turn: %d/%d" %
          (3, ghosts_landed, GOAL, turn, TURNS))
    print(msg)
    print("COMMANDS: a/d/w/s pole   . drift   q quit")


def main():
    random.seed()
    g, boat, ghosts = new_swamp()
    # clear spawn tiles under things
    landed = 0
    msg = "Night falls. Ferry 12 ghosts home!"
    for t in range(1, TURNS + 1):
        clear()
        # redraw grid fresh each turn (ghosts wander)
        gg = [[r for r in row] for row in g]
        # rebuild base grid without ghosts/boat markers
        base = [["." if c in "G@" else c for c in row] for row in g]
        for gx, gy in ghosts:
            base[gy][gx] = "G"
        base[boat[1] % H][boat[0] % W] = "@"
        draw(base, boat, ghosts, landed, t, msg)
        cmd = input("? ").strip().lower()[:1] or "."
        if cmd == "q":
            print("Ferry docked for the night. %d ghosts landed." % landed)
            return
        dx, dy = {"a": (-1, 0), "d": (1, 0), "w": (0, -1), "s": (0, 1),
                  ".": (0, 0)}.get(cmd, (0, 0))
        if cmd not in "adws.":
            msg = "? use a/d/w/s or ."
            continue
        # pole move
        nx, ny = wrap_x(boat[0] + dx), wrap_y(boat[1] + dy)
        if tile(g, nx, ny) != "#":
            boat[0], boat[1] = nx, ny
        else:
            msg = "Reeds! Ferry bumps."
        # board ghosts
        for ghp in ghosts:
            if ghp[0] == boat[0] and ghp[1] == boat[1]:
                pass  # riding now (count via landed logic below)
        # land ghosts on dock
        if tile(g, boat[0], boat[1]) == "D" and ghosts:
            # drop up to 3 per visit (boat capacity feeling)
            drop = min(3, len(ghosts))
            landed += drop
            del ghosts[:drop]
            msg = "%d ghosts drift home sleepy +happy!" % drop
        else:
            msg = ""
        # currents push
        pushes = 0
        tt = tile(g, boat[0], boat[1])
        if tt == "~":
            pushes = 1
        elif tt == "=":
            pushes = 2
        for _ in range(pushes):
            nx = wrap_x(boat[0] + 1)
            if tile(g, nx, boat[1]) != "#":
                boat[0] = nx
        # ghosts wander (slow, spooky)
        for ghp in ghosts:
            if random.random() < 0.4:
                gdx, gdy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                gx, gy = wrap_x(ghp[0] + gdx), wrap_y(ghp[1] + gdy)
                if tile(g, gx, gy) not in "#D" and [gx, gy] != boat:
                    ghp[0], ghp[1] = gx, gy
        # WIN / LOSE
        if landed >= GOAL:
            clear()
            base = [["." if c in "G@" else c for c in row] for row in g]
            for gx, gy in ghosts:
                base[gy][gx] = "G"
            base[boat[1] % H][boat[0] % W] = "@"
            print("\n".join("".join(row) for row in base))
            print("DAWN: %d ghosts home before sunrise! FERRY WINS!" % landed)
            return
    # dawn - lose
    print("SUNRISE! %d ghosts still swampside. They fade..." % (GOAL - landed))
    print("Final: %d/%d landed." % (landed, GOAL))


if __name__ == "__main__":
    main()
