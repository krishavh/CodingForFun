# Daily Terminal Drop
# Date: 2026-09-04
# Title: Lantern Lines: Chain-burst the lamp grid before your matches run out

# Daily Terminal Drop
# Date: 2026-09-04
# Title: Lantern Lines

#!/usr/bin/env python3
"""
LANTERN LINES
=============
You are a lamplighter racing the dark through the crooked streets of
Old Wick. Each night the Warden's board shows a GRID of unlit lamps.
Light one, and the flame SPREADS: every lamp in the same row and column
that shares its COLOUR also catches (a line burst), and each burst lamp
chains to its own colour... but the spread stops where colours differ.

You have a limited number of MATCHES. Quench every lamp before the
matches run out. Choosing WHICH colour to light is the whole game —
clear long same-colour lines for big chain reactions.

Commands:
  light <row> <col>    strike a match (the lamp's colour spreads)
  board                redraw the grid
  matches              how many you have left
  hint                 count lamps of each colour
  quit                 let the dark win

Legend: 6 colours shown as 1-6. A dot `.` is already dark (clear).
"""
import random
import sys

W, H = 7, 7
COLOURS = 6
MATCHES = 8

# lamp grid: value 1..6 lit, 0 = dark/cleared
grid = [[random.randint(1, COLOURS) for _ in range(W)] for _ in range(H)]
matches = MATCHES


def show():
    print()
    print("     " + " ".join(str(c) for c in range(W)))
    for r in range(H):
        cells = " ".join("." if v == 0 else str(v) for v in grid[r])
        print(f"  {r}  {cells}")
    left = sum(1 for row in grid for v in row if v)
    print(f"\n  matches left: {matches}   lamps remaining: {left}")
    if matches == 0 and left:
        print("  (out of matches — the dark has won)")


def burst(r0, c0, seen):
    """Light (r0,c0) and line-burst same-colour lamps in its row/column."""
    colour = grid[r0][c0]
    stack = [(r0, c0)]
    cleared = 0
    chain = 0
    while stack:
        r, c = stack.pop()
        if grid[r][c] != colour or (r, c) in seen:
            continue
        seen.add((r, c))
        grid[r][c] = 0
        cleared += 1
        chain += 1
        for x in range(W):
            if grid[r][x] == colour and (r, x) not in seen:
                stack.append((r, x))
        for y in range(H):
            if grid[y][c] == colour and (y, c) not in seen:
                stack.append((y, c))
    return cleared


def main():
    global matches
    print(__doc__)
    print("  The Warden hands you 8 matches. Good luck, lamplighter.\n")
    show()
    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nYou slip away into the fog.")
            return
        if not cmd:
            continue
        parts = cmd.split()
        if parts[0] in ("q", "quit"):
            print("The dark settles over Old Wick. Goodnight.")
            return
        if parts[0] == "board":
            show()
        elif parts[0] == "matches":
            print(f"  {matches} matches left.")
        elif parts[0] == "hint":
            counts = [0] * (COLOURS + 1)
            for row in grid:
                for v in row:
                    counts[v] += 1
            print("  " + "  ".join(f"{c}:{counts[c]}" for c in range(1, COLOURS + 1)))
        elif parts[0] == "light" and len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            r, c = int(parts[1]), int(parts[2])
            if not (0 <= r < H and 0 <= c < W):
                print("  That lamp isn't on the board.")
                continue
            if grid[r][c] == 0:
                print("  Already dark. Pick a lit lamp.")
                continue
            if matches <= 0:
                print("  Your matchbox is empty.")
                continue
            matches -= 1
            seen = set()
            cleared = burst(r, c, seen)
            left = sum(1 for row in grid for v in row if v)
            print(f"  FWOOSH — {cleared} lamps went dark in the chain.")
            show()
            if left == 0:
                print(f"\n  *** The whole of Old Wick is dark before its time. ***")
                print(f"  *** You win with {matches} matches to spare! ***")
                return
            if matches == 0:
                print("\n  Out of matches with lamps still burning. The Warden sighs.")
                print("  Press any key command to quit, or 'board' to admire the dark.")
        else:
            print("  Say: light <row> <col>, board, matches, hint, or quit.")


if __name__ == "__main__":
    main()
