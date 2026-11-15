# Daily Terminal Drop
# Date: 2026-11-15
# Title: Penguin Slide: Glide across the ice, eat every fish

# Daily Terminal Drop
# Date: 2026-11-15
#!/usr/bin/env python3
"""PENGUIN SLIDE - glide across the ice, collect every fish!

You are a penguin on a frozen pond. When you slide, you
do NOT stop until you hit a rock, a wall, or a fish?
No -- fish are slippery too! You stop on WALLS and ROCKS
only. Grab every fish to win.

Watch out: the water at the bottom is COLD.
Actually it is fine. Penguins love it.

COMMANDS: w up  a left  s down  d right   q quit
"""
import random
import sys

W, H = 9, 7

ICONS = {"p": "P", "wall": "#", "rock": "O", "fish": "f"}


def gen_level():
    while True:
        grid = [["." for _ in range(W)] for _ in range(H)]
        spots = [(x, y) for x in range(W) for y in range(H)]
        random.shuffle(spots)

        def take():
            return spots.pop()

        px, py = take()
        walls = []
        for _ in range(8):
            x, y = take()
            grid[y][x] = ICONS["wall"]
            walls.append((x, y))
        rocks = []
        for _ in range(4):
            x, y = take()
            grid[y][x] = ICONS["rock"]
            rocks.append((x, y))
        fish = []
        for _ in range(5):
            x, y = take()
            grid[y][x] = ICONS["fish"]
            fish.append((x, y))
        if solvable(px, py, grid, fish):
            return (px, py), grid, fish


def solvable(px, py, grid, fish):
    # flood-fill stops: positions where penguin can be at rest
    seen = set()
    stack = [(px, py)]
    seen.add((px, py))
    while stack:
        x, y = stack.pop()
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x, y
            while True:
                tx, ty = nx + dx, ny + dy
                if not (0 <= tx < W and 0 <= ty < H) or grid[ty][tx] in "#O":
                    break
                nx, ny = tx, ty
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                stack.append((nx, ny))
    return all((fx, fy) in seen for fx, fy in fish)


def draw(px, py, grid, fish, moves):
    fish_set = {(fx, fy) for fx, fy in fish}
    print("   MOVES: %d   FISH LEFT: %d" % (moves, len(fish)))
    print()
    print("   " + " ".join(str(i + 1) for i in range(W)))
    for y in range(H):
        row = []
        for x in range(W):
            if (x, y) == (px, py):
                row.append("P")
            elif grid[y][x] != ".":
                row.append(grid[y][x])
            elif (x, y) in fish_set:
                row.append("f")
            else:
                row.append(".")
        print(" %d " % (y + 1) + " ".join(row))
    print()


def slide(px, py, grid, dx, dy):
    while True:
        tx, ty = px + dx, py + dy
        if not (0 <= tx < W and 0 <= ty < H) or grid[ty][tx] in "#O":
            return px, py
        px, py = tx, ty


def main():
    (px, py), grid, fish = gen_level()
    moves = 0
    msg = "Slide to every fish! w/a/s/d"
    while True:
        print()
        draw(px, py, grid, fish, moves)
        if msg:
            print(msg)
        if not fish:
            print()
            print("GLIDE! You ate every fish in %d moves!" % moves)
            return 0
        try:
            line = input("move> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if line in ("q", "quit", "exit"):
            return 0
        dirs = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
        if line not in dirs:
            msg = "w up  a left  s down  d right"
            continue
        dx, dy = dirs[line]
        nx, ny = slide(px, py, grid, dx, dy)
        if (nx, ny) == (px, py):
            msg = "Blocked! You did not move."
            continue
        px, py = nx, ny
        moves += 1
        msg = ""
        for f in list(fish):
            if (f[0], f[1]) == (px, py):
                fish.remove(f)
                msg = "Slurp! Fish eaten."


if __name__ == "__main__":
    sys.exit(main())
