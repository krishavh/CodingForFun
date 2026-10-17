# Daily Terminal Drop
# Date: 2026-10-17
# Title: Noodle Wobble Wok: Stir the dragon before the broth boils over

# Daily Terminal Drop
# Date: 2026-10-17
# Title: Noodle Wobble Wok: Stir the dragon before the broth boils over

#!/usr/bin/env python3
"""NOODLE WOBBLE WOK - keep the wok level, feed the noodle dragon!

A balancing act in a bustling noodle bar. Your giant WOK of broth
sits on a wobbly bamboo pole. NOODLE PIECES (+) fall from the sky --
catch them in the wok! But every catch WOBBLES the pole toward the
catch side, and every miss SPLASHES broth (-broth).

Legend:
  W  your wok (3 cells wide, catches falling noodles)
  +  flying noodle piece (worth 10 broth-points!)
  .  empty steamy air

Each turn noodles FALL 1 row. You slide the wok:
  a  slide left  (costs 1 steam)
  d  slide right (costs 1 steam)
  s  stay put    (costs 0, but wobble keeps pulling!)
  q  quit the kitchen

Wobble: a needle swings -10..+10; catches push it toward the catch
side, misses toward center-collapse. If |wobble| hits 20 the
whole wok tips -- GAME OVER! Broth starts 100; boiling broth loses
1 each turn (the pot is HOT!). Catch 15 noodles to WIN the night!
"""
import random
import subprocess
import shutil

W = 40
H = 18
WOK_W = 3
CATCH_GOAL = 15
TIP_WOBBLE = 20


def clear():
    subprocess.run(["clear"], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def draw(rows, wx, broth, wobble, caught, turns, msg):
    clear()
    cols = min(max(term_cols(), 40), 100)
    print("NOODLE WOBBLE WOK".center(cols))
    print(("broth:%d  wobble:%+d  caught:%d/%d  turns:%d" %
           (broth, wobble, caught, CATCH_GOAL, turns)).center(cols))
    print()
    # sky rows (noodles fall) -- draw wok on last row
    for y, row in enumerate(rows):
        line = "".join(row)
        if y == len(rows) - 1:
            # overlay wok
            line = list(line)
            for i in range(WOK_W):
                x = wx + i
                if 0 <= x < W:
                    line[x] = "W"
            line = "".join(line)
        print("  " + line)
    # wobble meter
    meter = ["-"] * 41
    pos = 20 + max(-20, min(20, wobble))
    if 0 <= pos < 41:
        meter[pos] = "O"
    print()
    print("  wobble [" + "".join(meter) + "]  (O = pole tilt, +/-20 tips!)")
    print()
    if msg:
        print("  >> " + msg)
    print()
    print("  a/d slide | s stay | q quit")


def build_row():
    row = ["."] * W
    if random.random() < 0.55:
        x = random.randrange(W)
        row[x] = "+"
    return row


def main():
    random.seed()
    rows = [build_row() for _ in range(H - 1)]
    rows.append(["."] * W)  # floor row (wok lives here)
    wx = W // 2 - 1
    broth = 100
    wobble = 0
    caught = 0
    turns = 0
    msg = "Feed the dragon! Catch %d noodles." % CATCH_GOAL
    won = False
    while True:
        draw(rows, wx, max(broth, 0), wobble, caught, turns, msg)
        if broth <= 0:
            msg = "Broth boiled away! Kitchen closed."
            break
        if abs(wobble) >= TIP_WOBBLE:
            direction = "LEFT" if wobble < 0 else "RIGHT"
            msg = "WOK TIPPED %s! Noodles everywhere!" % direction
            break
        if caught >= CATCH_GOAL:
            won = True
            msg = "DRAGON FED! The wok rests. YOU WIN!"
            break
        cmd = input("move> ").strip().lower()
        if cmd == "q":
            msg = "Kitchen closed early."
            break
        if cmd not in ("a", "d", "s", ""):
            msg = "Use a/d/s or q."
            continue
        # move wok
        if cmd == "a" and wx > 0:
            wx -= 1
            broth -= 1
        elif cmd == "d" and wx < W - WOK_W:
            wx += 1
            broth -= 1
        elif cmd == "a" or cmd == "d":
            msg = "Wall! No slide."
        # noodles fall
        floor = rows[-1]
        caught_this = 0
        missed = 0
        for x in range(W):
            if floor[x] == "+":
                if wx <= x < wx + WOK_W:
                    caught_this += 1
                else:
                    missed += 1
        new_row = build_row()
        rows.pop()
        rows.insert(0, new_row)
        # wobble physics: catch pushes toward center, miss pulls outward
        if caught_this:
            wobble -= (1 if wobble > 0 else -1) * caught_this
            broth += 10 * caught_this
            caught += caught_this
            msg = "Slurp! +%d noodle%s (+%d broth)" % (
                caught_this, "s" if caught_this > 1 else "",
                10 * caught_this)
        if missed:
            broth -= 2 * missed
            # misses wobble the pole toward the wok side (heavy splash)
            splash_side = 1 if wx + WOK_W / 2.0 > W / 2.0 else -1
            wobble += splash_side * min(missed, 2)
            if not caught_this:
                msg = "Splash! %d noodle%s hit the floor (-%d broth)" % (
                    missed, "s" if missed > 1 else "", 2 * missed)
        # boiling broth: pot loses 1 every 3 turns
        turns += 1
        if turns % 3 == 0:
            broth -= 1
        # keep wobble in range for display; tip check next loop
        wobble = max(-25, min(25, wobble))
    draw(rows, wx, max(broth, 0), wobble, caught, turns, msg)
    print("  FINAL: %d noodles caught, %d broth, %d turns -- %s" %
          (caught, max(broth, 0), turns,
           "WIN! Dragon fed!" if won else "Game over."))
    print()


if __name__ == "__main__":
    main()
