# Daily Terminal Drop
# Date: 2026-09-16
# Title: High Tide Heist: Tide Surge Heist

#!/usr/bin/env python3
"""Final High Tide Heist: cleaned and balanced. See docstring.

Accepts either a single wasd character per line or several moves on one
line (e.g. 'wwssdd'), so both new players and scripted drivers are happy.
"""
import random
import sys

W, H = 9, 7
SURGE_LIMIT = 7

RELICS = {"G": "gold gear", "O": "pearl", "$": "vault coin"}

# Live player position, kept module-level so draw() can render it.
player = [1, H // 2]


def blank_floor():
    return [["." for _ in range(W)] for _ in range(H)]


def build_level(rng):
    grid = blank_floor()
    exit_x, exit_y = 0, H // 2
    grid[exit_y][exit_x] = "X"

    free = [(x, y) for x in range(1, W) for y in range(H)
            if (x, y) != (exit_x, exit_y)]
    rng.shuffle(free)

    spots = {}
    currents = {}
    crates = []
    for relic in RELICS:
        pos = free.pop()
        spots[relic] = pos
        grid[pos[1]][pos[0]] = relic
    for _ in range(5):
        pos = free.pop()
        currents[pos] = rng.choice("><v^")
        grid[pos[1]][pos[0]] = currents[pos]
    for _ in range(4):
        pos = free.pop()
        crates.append(pos)
        grid[pos[1]][pos[0]] = "["

    px, py = free.pop()
    player[0], player[1] = px, py
    return grid, spots, currents, crates, px, py


def draw(grid, flooded, bag, tide, surge_no, exit_open):
    print(f"\nTide in {tide} turns | surge {surge_no}/{SURGE_LIMIT} "
          f"| bag: {', '.join(sorted(bag)) or 'empty'}")
    for y, row in enumerate(grid):
        line = []
        for x, ch in enumerate(row):
            if (x, y) == (player[0], player[1]):
                line.append("@")
            elif (x, y) in flooded:
                line.append("~")
            else:
                line.append(ch)
        print(" ".join(line))
    if exit_open:
        print("All three relics! The exit X is unlocked - run for it.")


def current_push(px, py, arrow):
    dx, dy = {">": (1, 0), "<": (-1, 0), "v": (0, 1), "^": (0, -1)}[arrow]
    return px + dx, py + dy


def step(grid, spots, crates, px, py, nx, ny):
    """Try to move onto (nx, ny). Returns (px, py, message)."""
    if not (0 <= nx < W and 0 <= ny < H):
        return px, py, "The wall stops you."
    if (nx, ny) in crates:
        bx, by = nx + (nx - px), ny + (ny - py)
        if (0 <= bx < W and 0 <= by < H and (bx, by) not in crates
                and grid[by][bx] in (".", "X")):
            crates[crates.index((nx, ny))] = (bx, by)
            grid[by][bx] = "["
        else:
            return px, py, "The crate will not budge."
    return nx, ny, ""


def surge(flooded, spots, bag, surge_no):
    for y in range(H):
        col_free = [x for x in range(W) if (x, y) not in flooded]
        if col_free:
            flooded.add((max(col_free), y))
            break
    lost = []
    for relic in list(RELICS):
        if relic not in bag and relic in spots and spots[relic] in flooded:
            del spots[relic]
            lost.append(RELICS[relic])
    if lost:
        print("The surge swallows the " + " and the ".join(lost) + "!")
    if surge_no >= SURGE_LIMIT:
        return "The seventh surge drowns the customs house. Lost to the sea."
    return ""


def resolve_move(grid, spots, currents, crates, px, py, cmd,
                 flooded, bag, exit_open):
    """Apply one wasd move plus current ride. Returns new (px, py)."""
    dx, dy = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}[cmd]
    px, py, msg = step(grid, spots, crates, px, py, px + dx, py + dy)
    if msg:
        print(msg)
    ride = currents.get((px, py))
    if ride and (px, py) not in flooded:
        cx, cy = current_push(px, py, ride)
        if 0 <= cx < W and 0 <= cy < H and (cx, cy) not in crates:
            px, py = cx, cy
            print("The current sweeps you a tile %s." % ride)
    return px, py


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else random.randrange(99999)
    rng = random.Random(seed)
    grid, spots, currents, crates, px, py = build_level(rng)
    flooded = set()
    bag = set()
    tide = 4
    surge_no = 0

    print("HIGH TIDE HEIST - three relics, one exit, a rising sea.")
    print("(seed %d) type 'look' any time to see the floor." % seed)

    while True:
        exit_open = len(bag) == len(RELICS)
        draw(grid, flooded, bag, tide, surge_no, exit_open)
        try:
            raw = input("move (wasd)> ").strip().lower()
        except EOFError:
            print("\nThe tide closes in while you hesitate. Lost to the sea.")
            return
        if raw == "quit":
            print("You wade away empty-handed.")
            return
        if raw == "look":
            continue
        moves = [ch for ch in raw if ch in "wasd"]
        if not moves:
            print("Use w/a/s/d, 'look', or 'quit'.")
            continue

        for cmd in moves:
            exit_open = len(bag) == len(RELICS)
            px, py = resolve_move(grid, spots, currents, crates,
                                  px, py, cmd, flooded, bag, exit_open)
            player[0], player[1] = px, py

            if exit_open and (px, py) == (0, H // 2):
                print("You slip through the exit as the wall buckles - RICH!")
                print("Seed %d, %d surges weathered." % (seed, surge_no))
                return

            for relic in list(RELICS):
                if relic in spots and spots[relic] == (px, py):
                    bag.add(relic)
                    del spots[relic]
                    print("You pocket the %s!" % RELICS[relic])

            if (px, py) in flooded:
                print("The water takes you. The heist is over.")
                return
            if not bag and len(spots) < len(RELICS):
                lost = [RELICS[r] for r in RELICS if r in spots]
                print("The sea claimed the " + " and the ".join(lost) + ".")
                return

        tide -= 1
        if tide <= 0:
            surge_no += 1
            tide = max(2, 5 - surge_no)
            fatal = surge(flooded, spots, bag, surge_no)
            if (px, py) in flooded:
                fatal = "The surge crashes over you. Lost to the sea."
            if fatal:
                print(fatal)
                return


if __name__ == "__main__":
    main()
