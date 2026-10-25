# Daily Terminal Drop
# Date: 2026-10-25
# Title: Moonlight Marionette: Cut the strings before the stage goes dark

# Daily Terminal Drop
# Date: 2026-10-25
#!/usr/bin/env python3
"""MOONLIGHT MARIONETTE - cut the strings before the stage goes dark!

You are a puppeteer on a moonlit stage. Your MARIONETTE hangs
from CLOUDS above by strings. Each turn you may CUT one string:
the puppet FALLS -- but wind shoves it while airborne! Land it
softly on a STAR to catch moonbeams, or splat on the BOARDS!

Legend:
  o  your marionette (falls after each cut!)
  =  cloud (string anchor, holds puppet up)
  *  star (safe landing, 20 points, star fades)
  #  boards (safe too, but only 5 points)
  ^  spike rug (OUCH! -10 and a new puppet!)

PLAY:
  The puppet hangs below its CLOUD. Press e to CUT the
  nearest string -- puppet drops straight down, BUT the
  midnight wind blows it: each row it falls, it drifts
  1 sideways (wind arrow shows way). Land on stars for
  big points -- chains of stars DOUBLES the drop score!

NEW PUPPET: each catch or splat spawns a fresh puppet
  hanging from a new cloud. 40 turns till dawn!

GOAL: 150 points of moonbeams before the curtain falls!
COMMANDS: a/d wind-wish (nudge fall)   e cut   q quit
"""
import random
import shutil
import subprocess

W, H = 36, 14
GOAL = 150
TURNS = 40


def clear():
    subprocess.run(["clear"], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def new_stage():
    """Stage: clouds top rows, stars/boards/spikes below."""
    g = [["."] * W for _ in range(H)]
    for x in range(W):
        g[0][x] = "="
    spots = random.sample(range(W * (H - 2)), 26)
    k = iter(spots)
    stars = []
    for _ in range(9):
        pos = next(k)
        y = 2 + pos // W
        x = pos % W
        g[y][x] = "*"
        stars.append((y, x))
    for _ in range(9):
        pos = next(k)
        y = 2 + pos // W
        x = pos % W
        g[y][x] = "#"
    floor = ["^" if i % 3 == 0 else "#" for i in range(W)]
    px = random.randrange(W)
    return g, stars, floor, px


def draw(g, stars, floor, px, py, turn, pts, msg, wind):
    print(f"MOONLIGHT MARIONETTE  turn {turn}/{TURNS}  moonbeams {pts}/{GOAL}")
    print(f"wind blows {'<-left' if wind < 0 else 'right->' if wind > 0 else 'STILL'}   a/d wish  e cut  q quit")
    top = list(g[0])
    if py == 0:
        top[px] = "o"
    print("".join(top))
    for y in range(1, H - 1):
        row = list(g[y])
        if py == y:
            row[px] = "o"
        print("".join(row))
    brow = list(floor)
    if py == H - 1:
        brow[px] = "o"
    print("".join(brow))


def spawn(g):
    """New puppet on a random cloud column."""
    return random.randrange(W), 0


def cut_and_fall(g, stars, floor, px, wish):
    """Fall one row at a time, wind drifts. Returns (px,py,gain,stars)."""
    py = 0
    gain = 0
    chain = 0
    wind = random.choice([-1, 0, 0, 1])
    while py < H - 1:
        py += 1
        px = max(0, min(W - 1, px + wind + wish))
        wish = 0
        c = g[py][px] if py < H - 1 else floor[px]
        if c == "*":
            chain += 1
            gain += 20 * (2 ** (chain - 1))
            stars.discard((py, px))
            g[py][px] = "."
        elif c == "#":
            gain += 5
            break
        elif c == "^":
            gain -= 10
            break
    else:
        c = floor[px]
        if c == "^":
            gain -= 10
        else:
            gain += 5
    return px, py, gain, stars, wind


def main():
    random.seed()
    g, stars_l, floor, px = new_stage()
    stars = {(y, x) for y, x in stars_l}
    py = 0
    turn = 0
    pts = 0
    msg = "cut a string! (e)"
    while turn < TURNS and pts < GOAL:
        draw(g, stars, floor, px, py, turn, pts, msg, 0)
        cmd = input(f"\n{msg} > ").strip().lower()
        if cmd == "q":
            print(f"curtain! moonbeams {pts}")
            return
        if cmd == "e" and py == 0:
            turn += 1
            px, py, gain, stars, wind = cut_and_fall(g, stars, floor, px, 0)
            pts += gain
            msg = f"{gain:+d} moonbeams! wind {'<-' if wind < 0 else '->' if wind > 0 else 'still'}"
            px, py = spawn(g)
            for _ in range(1):
                if len(stars) < 6:
                    y = random.randrange(2, H - 1)
                    x = random.randrange(W)
                    if g[y][x] == ".":
                        g[y][x] = "*"
                        stars.add((y, x))
        elif cmd in ("a", "d") and py > 0:
            px = max(0, min(W - 1, px + (-1 if cmd == "a" else 1)))
            msg = "nudged mid-air! (needs fall)"
        elif cmd in ("a", "d"):
            px = max(0, min(W - 1, px + (-1 if cmd == "a" else 1)))
            msg = "slid along the clouds"
        else:
            msg = "? (a/d/e/q)"
    print(f"CURTAIN! final moonbeams {pts}" + (" -- SHOW STOPPED!" if pts >= GOAL else " -- dusk fell short"))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\ncurtain!")
