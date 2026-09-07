# Daily Terminal Drop
# Date: 2026-09-07
# Title: Tide Atlas: Ford the drowned road before the second breath

#!/usr/bin/env python3
"""
TIDE ATLAS :: FORD THE DROWNED ROAD BEFORE THE SECOND BREATH
=============================================================
A one-screen logic dive. Each dive, the Atlas projects a grid of
TILES onto the seabed. Every tile hums a BEACON TONE -- a digit --
which tells you how far (in tiles, counting up/down/left/right only,
never diagonally) the nearest SAFE STONE is.

You start at the top-left stone and must reach the EXIT at the
bottom-right. Step on a stone whose tone says the exit is NOT that
many tiles away, and the drowned road takes you.

Your one gift: a handful of SONAR PINGS. A ping lifts the fog from a
whole row and column around a tile, so you can read tones before
you walk them.

Commands:
  w a s d        step up / left / down / right
  ping <r> <c>   sonar-ping tile (r,c are 1-based) -- costs one ping
  look           redraw the board
  quit           abandon the dive

Legend: digits = beacon tones   ? = fogged tone
        @ you   X exit (it is safe!)   ~ water
"""
import random
import sys

SIZE = 6
MAX_STEPS = 150

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def new_board():
    grid = [[random.randint(0, 2 * SIZE - 2) for _ in range(SIZE)]
            for _ in range(SIZE)]
    exit_pos = (SIZE - 1, SIZE - 1)
    for r in range(SIZE):
        for c in range(SIZE):
            grid[r][c] = manhattan((r, c), exit_pos)
    order = [(r, c) for r in range(SIZE) for c in range(SIZE)
             if (r, c) != exit_pos]
    random.shuffle(order)
    for r, c in order[:SIZE]:                      # scatter decoy tones
        grid[r][c] = random.choice(
            [t for t in range(2 * SIZE) if t != grid[r][c]])
    for r, c in [(0, 0), (0, 1), (1, 0), (0, 2), (2, 0)]:   # entry path
        if (r, c) != exit_pos:
            grid[r][c] = manhattan((r, c), exit_pos)
    return grid, exit_pos

def render(grid, fog, pos, exit_pos):
    lines = ["    T I D E   A T L A S"]
    lines.append("  " + " ".join(str(c + 1) for c in range(SIZE)))
    for r in range(SIZE):
        row = []
        for c in range(SIZE):
            if (r, c) == pos:
                row.append("@")
            elif (r, c) == exit_pos:
                row.append("X")
            elif fog[r][c]:
                row.append("?")
            else:
                row.append(str(grid[r][c] % 10))
        lines.append(f"{r + 1} " + " ".join(row))
    return "\n".join(lines)

def status(steps, pings, alive):
    return (f" steps {steps}/{MAX_STEPS}   pings {pings}"
            + ("   [the sea is patient]" if alive else ""))

def play():
    random.seed()
    grid, exit_pos = new_board()
    fog = [[(r, c) != (0, 0) for c in range(SIZE)] for r in range(SIZE)]
    pos = (0, 0)
    steps = 0
    pings = 3
    print("Dive the drowned road. Read the tones. Trust the exit.")
    print(render(grid, fog, pos, exit_pos))
    print(status(steps, pings, True))
    while True:
        try:
            raw = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nThe sea takes the question back.")
            return
        if not raw:
            continue
        parts = raw.split()
        cmd = parts[0]
        if cmd in ("quit", "q"):
            print("You surface empty-handed. The road keeps its secret.")
            return
        if cmd == "look":
            print(render(grid, fog, pos, exit_pos))
            continue
        if cmd == "ping":
            if pings <= 0:
                print("No pings left in the case.")
                continue
            if len(parts) != 3:
                print("Usage: ping <row> <col>  (1-based)")
                continue
            try:
                pr, pc = int(parts[1]) - 1, int(parts[2]) - 1
            except ValueError:
                print("The Atlas ignores your garbled numbers.")
                continue
            if not (0 <= pr < SIZE and 0 <= pc < SIZE):
                print("Off the projected seabed.")
                continue
            pings -= 1
            for i in range(SIZE):
                fog[pr][i] = False
                fog[i][pc] = False
            print(f"A sonar thread hums out from ({pr + 1},{pc + 1}).")
            print(render(grid, fog, pos, exit_pos))
            print(status(steps, pings, True))
            continue
        if cmd in ("w", "a", "s", "d"):
            dr, dc = {"w": (-1, 0), "a": (0, -1),
                     "s": (1, 0), "d": (0, 1)}[cmd]
            nr, nc = pos[0] + dr, pos[1] + dc
            if not (0 <= nr < SIZE and 0 <= nc < SIZE):
                print("The water past the edge is not a road.")
                continue
            steps += 1
            pos = (nr, nc)
            fog[nr][nc] = False                      # your own tone reveals
            if pos == exit_pos:
                print(render(grid, fog, pos, exit_pos))
                print(f"LANDED. You ford the drowned road in {steps} steps"
                      f" with {pings} ping(s) spared.")
                return
            tone = manhattan(pos, exit_pos)
            if grid[pos[0]][pos[1]] != tone:
                print(render(grid, fog, pos, exit_pos))
                print(f"DECOYED. The tile hummed {grid[pos[0]][pos[1]] % 10},"
                      f" but the exit was {tone} away.")
                print(f"The drowned road keeps you at step {steps}.")
                return
            if steps >= MAX_STEPS:
                print(render(grid, fog, pos, exit_pos))
                print("The second breath arrives. You never left the road.")
                return
            print(render(grid, fog, pos, exit_pos))
            print(status(steps, pings, True))
            continue
        print("The Atlas answers only: w a s d, ping r c, look, quit.")

if __name__ == "__main__":
    try:
        play()
    except Exception as exc:                        # noqa: last rites
        print(f"The sea is displeased: {exc}", file=sys.stderr)
        sys.exit(1)
