# Daily Terminal Drop
# Date: 2026-11-17
# Title: Deep Sea Sonar: Find the wrecks with your pings

# Daily Terminal Drop
# Date: 2026-11-17
#!/usr/bin/env python3
"""DEEP SEA SONAR - find the wrecks with your ping device!

A foggy sea hides 3 wrecks on a 10x10 grid. Each turn you drop
a sonar ping anywhere. The ping tells you the EXACT distance
(Min moves: up/down/left/right) to EVERY wreck you have not
found yet. Found wrecks show as W.

Pinpoint all 3 in as few pings as you can. Par is 12!

COMMANDS: x y   (0-9 each, e.g. "5 3")     q quit
"""
import random
import sys

W, H = 10, 10
WRECKS = 3
PAR = 12


def new_game():
    spots = random.sample(range(W * H), WRECKS)
    return [(s % W, s // W) for s in spots]


def draw(pings, found, wrecks):
    print()
    print("    " + "".join(str(x) for x in range(W)))
    for y in range(H):
        row = []
        for x in range(W):
            if (x, y) in found:
                row.append("W")
            elif (x, y) in pings:
                row.append("*")
            else:
                row.append(".")
        print("  %d " % y + "".join(row))
    print()


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def ping_at(pos, pings, found, wrecks):
    pings.add(pos)
    lines = []
    for i, w in enumerate(wrecks):
        if w in found:
            continue
        d = dist(pos, w)
        if d == 0:
            lines.append("CLUNK! Wreck %d found at %d,%d!" % (i + 1, w[0], w[1]))
            found.add(w)
        else:
            arrow = "N" if pos[1] > w[1] else "S" if pos[1] < w[1] else ""
            arrow += "W" if pos[0] > w[0] else "E" if pos[0] < w[0] else ""
            lines.append("Wreck %d: %d pings %s" % (i + 1, d, arrow or "HERE"))
    return lines


def main():
    wrecks = new_game()
    pings, found = set(), set()
    turns = 0
    print(__doc__)
    while len(found) < WRECKS:
        draw(pings, found, wrecks)
        remaining = WRECKS - len(found)
        print("Pings used: %d   Wrecks found: %d/%d   Par: %d"
              % (turns, len(found), WRECKS, PAR))
        try:
            raw = input("Ping where (x y)> ").strip().lower()
        except EOFError:
            break
        if raw in ("q", "quit"):
            print("Fog wins. Byeee!")
            return
        parts = raw.replace(",", " ").split()
        if len(parts) != 2:
            print("  ? Use: x y   (like 5 3)")
            continue
        try:
            x, y = int(parts[0]), int(parts[1])
        except ValueError:
            print("  ? Numbers only (0-9)")
            continue
        if not (0 <= x < W and 0 <= y < H):
            print("  ? Grid is 0-9 by 0-9")
            continue
        turns += 1
        for line in ping_at((x, y), pings, found, wrecks):
            print("  " + line)
    print()
    draw(pings, found, wrecks)
    verdict = "AMAZING" if turns <= 6 else "GREAT" if turns <= PAR else "soggy"
    print("All %d wrecks found in %d pings! Par was %d. That is %s!"
          % (WRECKS, turns, PAR, verdict))
    rating = "Fog Admiral" if turns <= 6 else "Sonar Ace" if turns <= PAR else "Bilge Pump"
    print("Rank: %s" % rating)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
