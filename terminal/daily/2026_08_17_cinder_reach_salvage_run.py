# Daily Terminal Drop
# Date: 2026-08-17
# Title: Cinder Reach: Salvage Run

# Daily Terminal Drop
# Title: Cinder Reach: Salvage Run
# Fly a salvage drone through a collapsed refinery grid, hunting the last
# reactor core while scavenging fuel cells and dodging volatile pockets.

#!/usr/bin/env python3
import random
import sys

SIZE = 7
FUEL_START = 14
STEP_COST = 1
CORE_ROW = 0


def new_board(rng):
    """Create a SIZE x SIZE grid, both dimensions odd so moves feel open."""
    grid = [["." for _ in range(SIZE)] for _ in range(SIZE)]
    grid[0][0] = "D"  # drone spawn
    # Scatter volatile pockets (they cost fuel if you step on them).
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)
             if not (r == 0 and c == 0)]
    rng.shuffle(cells)
    for _ in range(8):
        r, c = cells.pop()
        grid[r][c] = "X"
    # Scatter fuel cells.
    for _ in range(6):
        r, c = cells.pop()
        grid[r][c] = "+"
    # Plant the core somewhere reachable, lower-right-ish half.
    r, c = rng.choice(cells)
    grid[r][c] = "O"
    return grid, (r, c)


def render(grid, pr, pc, visited):
    # Cells you've reached stay revealed; everything else reads as blank
    # radar until you get close, keeping a little mystery without punishing.
    lines = []
    for r in range(SIZE):
        row = []
        for c in range(SIZE):
            if r == pr and c == pc:
                row.append("@")
            elif (r, c) in visited or (abs(pr - r) <= 1 and abs(pc - c) <= 1):
                row.append(grid[r][c])
            else:
                row.append(".")
        lines.append(" ".join(row))
    return "\n".join(lines)


def move(pr, pc, cmd):
    d = {"n": (-1, 0), "s": (1, 0), "w": (0, -1), "e": (0, 1)}
    dr, dc = d[cmd]
    return pr + dr, pc + dc


def in_bounds(r, c):
    return 0 <= r < SIZE and 0 <= c < SIZE


def main():
    rng = random.Random(20260817)
    grid, (core_r, core_c) = new_board(rng)
    pr, pc = 0, 0
    visited = {(0, 0)}
    fuel = FUEL_START
    score = 0
    steps = 0

    print("=" * 46)
    print("CINDER REACH :: SALVAGE RUN")
    print("=" * 46)
    print("The refinery collapsed years ago. A survivor cluster paid triple")
    print(f"for the reactor core buried somewhere in the {SIZE}x{SIZE} grid.")
    print("You fly the salvage drone @. Each step burns 1 fuel.")
    print(" '+' fuel cell | 'X' volatile pocket (-3) | 'O' the core.")
    print("Commands: n e s w | fuel | quit")
    print()

    while True:
        print(render(grid, pr, pc, visited))
        cell = grid[pr][pc]
        if cell == "O" and not (pr == 0 and pc == 0):
            print("You found the CORE. Salvage secured.")
            score += 200
            break
        if fuel <= 0:
            print("Fuel empty. The drone powers down mid-grid.")
            break

        cmd = input(f"[fuel {fuel} | {steps} steps] > ").strip().lower()
        if not cmd:
            continue
        if cmd == "quit":
            print("Salvage aborted. Drone recalled.")
            return
        if cmd == "fuel":
            print(f"Fuel: {fuel} | Steps: {steps} | Score: {score}")
            continue
        if cmd not in ("n", "e", "s", "w"):
            print("Commands: n e s w | fuel | quit")
            continue

        while True:
            nr, nc = move(pr, pc, cmd)
            if not in_bounds(nr, nc):
                print("The wall glows hot — no passage that way.")
                break
            pr, pc = nr, nc
            visited.add((pr, pc))
            steps += 1
            fuel -= STEP_COST

            target = grid[pr][pc]
            if target == "X":
                fuel -= 3
                print("You skim a volatile pocket. -3 fuel.")
                grid[pr][pc] = "."
            elif target == "+":
                fuel += 4
                score += 10
                print("Cell scavenged. +4 fuel.")
                grid[pr][pc] = "."
            elif target == "O" and pr != 0 and pc != 0:
                pass
            grid[0][0] = "D"
            break  # one move per command

    print()
    print(f"Final score: {score} across {steps} moves.")
    if score >= 200:
        print("The core lights the colony's last quadrant. Ran out? Run it again.")
    elif score:
        print("Partial salvage — the buyers pay in scrap, not stories.")
    else:
        print("Nothing recovered. The grid keeps its secrets.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nDrone signal lost. Ending salvage.")
        sys.exit(0)
