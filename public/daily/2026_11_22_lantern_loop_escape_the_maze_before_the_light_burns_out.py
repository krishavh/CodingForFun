# Daily Terminal Drop
# Date: 2026-11-22
# Title: Lantern Loop: Escape the maze before the light burns out

#!/usr/bin/env python3
"""LANTERN LOOP - escape the hedge maze before your lantern burns out!

You wander a dark hedge maze holding a tiny lantern.
Each step burns 1 fuel. Walk onto L to refill (+15).
Find the gate (G) before the fuel hits 0.
Arrows / WASD to move. Q to quit.
"""
import os
import random
import sys

W, H = 21, 13  # odd sizes for maze carving
START_FUEL = 60


def carve_maze():
    grid = [["#"] * W for _ in range(H)]
    stack = [(1, 1)]
    grid[1][1] = "."
    while stack:
        x, y = stack[-1]
        dirs = []
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            nx, ny = x + dx, y + dy
            if 1 <= nx < W - 1 and 1 <= ny < H - 1 and grid[ny][nx] == "#":
                dirs.append((nx, ny))
        if dirs:
            nx, ny = random.choice(dirs)
            grid[(y + ny) // 2][(x + nx) // 2] = "."
            grid[ny][nx] = "."
            stack.append((nx, ny))
        else:
            stack.pop()
    return grid


def place_items(grid):
    open_cells = [(x, y) for y in range(H) for x in range(W)
                  if grid[y][x] == "." and (x, y) != (1, 1)]
    far = max(open_cells, key=lambda c: c[0] + c[1])
    gx, gy = far
    grid[gy][gx] = "G"
    lamps = 0
    while lamps < 5:
        x, y = random.choice(open_cells)
        if grid[y][x] == "." and (x, y) != (gx, gy):
            grid[y][x] = "L"
            lamps += 1


def draw(grid, px, py, fuel, steps, msg):
    os.system("" if os.name != "posix" else "clear")
    vis = 3
    print("LANTERN LOOP  |  fuel: %d  steps: %d" % (fuel, steps))
    print("Reach G before fuel runs out. L = lantern refill.")
    print("+" + "-" * W + "+")
    for y in range(H):
        row = "|"
        for x in range(W):
            if (x, y) == (px, py):
                row += "@"
            elif abs(x - px) <= vis and abs(y - py) <= vis:
                row += grid[y][x]
            else:
                row += " "
        row += "|"
        print(row)
    print("+" + "-" * W + "+")
    if msg:
        print(msg)
    print("Move: w/a/s/d  (q)uit -> ", end="", flush=True)


def main():
    random.seed()
    grid = carve_maze()
    place_items(grid)
    px, py = 1, 1
    fuel, steps = START_FUEL, 0
    msg = "Find the gate G!"
    while True:
        draw(grid, px, py, fuel, steps, msg)
        keys = input().strip().lower()
        if not keys:
            keys = "s"
        for k in keys:
            if k == "q":
                print("\nYou quit after %d steps. Bye!" % steps)
                return
            dx, dy = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}.get(k, (0, 0))
            if dx or dy:
                nx, ny = px + dx, py + dy
                if 0 <= nx < W and 0 <= ny < H and grid[ny][nx] != "#":
                    px, py = nx, ny
                    steps += 1
                    fuel -= 1
                    msg = ""
                    if grid[py][px] == "L":
                        grid[py][px] = "."
                        fuel += 15
                        msg = "Lantern refilled +15!"
                    elif grid[py][px] == "G":
                        print("\nYOU ESCAPED in %d steps with %d fuel left!" % (steps, fuel))
                        return
                    if fuel <= 0:
                        print("\nOut of fuel! Darkness wins after %d steps." % steps)
                        return


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
