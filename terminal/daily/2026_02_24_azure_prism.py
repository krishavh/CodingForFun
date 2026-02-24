# Daily Terminal Drop
# Date: 2026-02-24
# Title: Azure Prism: Signal Chase

#!/usr/bin/env python3
import random

WIDTH = 9
HEIGHT = 7
PLAYER = "@"
TARGET = "*"
TRAP = "^"
EMPTY = "."


def clamp(val, low, high):
    return max(low, min(high, val))


def draw(px, py, tx, ty, traps, moves_left):
    print(f"Moves left: {moves_left}")
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            if x == px and y == py:
                row.append(PLAYER)
            elif x == tx and y == ty:
                row.append(TARGET)
            elif (x, y) in traps:
                row.append(TRAP)
            else:
                row.append(EMPTY)
        print(" ".join(row))


def main():
    rng = random.Random(20260224)
    px, py = 0, HEIGHT - 1
    tx, ty = WIDTH - 1, 0
    traps = set()
    while len(traps) < 8:
        x = rng.randint(1, WIDTH - 2)
        y = rng.randint(1, HEIGHT - 2)
        if (x, y) in ((px, py), (tx, ty)):
            continue
        traps.add((x, y))

    moves_left = 18
    while moves_left > 0:
        draw(px, py, tx, ty, traps, moves_left)
        cmd = input("Move (W/A/S/D) or Q: ").strip().lower()
        if not cmd:
            continue
        if cmd[0] == "q":
            print("Signal lost.")
            return
        dx = dy = 0
        if cmd[0] == "w":
            dy = -1
        elif cmd[0] == "s":
            dy = 1
        elif cmd[0] == "a":
            dx = -1
        elif cmd[0] == "d":
            dx = 1
        else:
            print("Unknown command.")
            continue

        px = clamp(px + dx, 0, WIDTH - 1)
        py = clamp(py + dy, 0, HEIGHT - 1)
        moves_left -= 1

        if (px, py) in traps:
            print("You hit a trap. Signal lost.")
            return
        if px == tx and py == ty:
            print("Signal captured. You win.")
            return

    print("Out of moves. Signal fades.")


if __name__ == "__main__":
    main()
