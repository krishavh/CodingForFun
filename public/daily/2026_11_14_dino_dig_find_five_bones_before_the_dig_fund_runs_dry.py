# Daily Terminal Drop
# Date: 2026-11-14
# Title: Dino Dig: Find five bones before the dig fund runs dry

#!/usr/bin/env python3
"""DINO DIG - excavate the buried bones before the dig fund runs out!

A dust storm hit the desert. Five DINO BONES are buried in
a 8x8 grid of sand. You are a paleontologist with a very
bad map. Dig a square to find a bone!

  .  sand (undug)
  *  dug, nothing there
  B  BONE! (found)

After every dig, your ancient BONE-O-METER beeps:
it tells how many bones are in the 8 squares
touching your dig (horizontal, vertical, diagonal).

Find all 5 bones in 12 digs to win the
GOLDEN TROWEL. Run out of digs and the
museum fires you (but shows the map).

COMMANDS: type col,row like 3,5   q quit
"""
import random
import sys

W, H = 8, 8
BONES = 5
DIGS = 12


def neighbors(x, y):
    out = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H:
                out.append((nx, ny))
    return out


def main():
    bones = set()
    while len(bones) < BONES:
        bones.add((random.randrange(W), random.randrange(H)))
    dug = set()
    found = set()
    digs_left = DIGS
    msg = "Dig a square! Type col,row (example 3,5)"
    while True:
        print()
        print("  DIGS LEFT: %d   BONES FOUND: %d/%d" % (digs_left, len(found), BONES))
        print()
        print("     " + " ".join(str(i + 1) for i in range(W)))
        for y in range(H):
            row = []
            for x in range(W):
                if (x, y) in found:
                    row.append("B")
                elif (x, y) in dug:
                    row.append("*")
                else:
                    row.append(".")
            print("   %d %s" % (y + 1, " ".join(row)))
        print()
        print("  BONE-O-METER last beep: %s" % msg)
        if len(found) == BONES:
            print()
            print("  YOU WIN! All bones in the museum! GOLDEN TROWEL!")
            return
        if digs_left <= 0:
            print()
            print("  OUT OF DIGS! The museum fires you.")
            print("  Bones were at: %s" % sorted(
                (x + 1, y + 1) for x, y in bones))
            return
        try:
            raw = input("  dig (col,row) > ").strip().lower()
        except EOFError:
            return
        if raw in ("q", "quit", "exit"):
            print("  Bye! Bones were at: %s" % sorted(
                (x + 1, y + 1) for x, y in bones))
            return
        parts = raw.replace(" ", "").split(",")
        if len(parts) != 2:
            msg = "? Type col,row like 3,5"
            continue
        try:
            x, y = int(parts[0]) - 1, int(parts[1]) - 1
        except ValueError:
            msg = "? Numbers only, like 3,5"
            continue
        if not (0 <= x < W and 0 <= y < H):
            msg = "? Grid is 1-8 for both, like 3,5"
            continue
        if (x, y) in dug:
            msg = "Already dug there! Pick new sand."
            continue
        digs_left -= 1
        dug.add((x, y))
        if (x, y) in bones:
            found.add((x, y))
            left = BONES - len(found)
            msg = "BONE! %d to go!" % left if left else "BONE! That is ALL 5!"
        else:
            near = sum(1 for n in neighbors(x, y) if n in bones)
            msg = "Dust. %d bone(s) touch this square." % near


if __name__ == "__main__":
    main()
