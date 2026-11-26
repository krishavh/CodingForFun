# Daily Terminal Drop
# Date: 2026-11-26
# Title: Lighthouse Keeper: Guide ships home with your steady beam

#!/usr/bin/env python3
"""LIGHTHOUSE KEEPER - guide ships home with your steady beam!

A timing game. A beam of light sweeps across the dark sea.
Ships appear on the rocks and drift toward the reef.
Press SPACE (enter) when the beam sweeps over a ship
to guide it safely home. Miss, and ships crash!
Guide 8 ships before your oil runs out (45 seconds).
"""
import os
import random
import sys
import time
import tty
import termios

W = 60
SEA = 14
TIME_LIMIT = 45
GOAL = 8


def draw(beam, ships, saved, crashes, oil, secs, msg):
    os.system("clear" if os.name == "posix" else "cls")
    mins = oil - int(secs)
    print("LIGHTHOUSE KEEPER  |  oil: %2ds  saved: %d/%d  wrecks: %d"
          % (mins, saved, GOAL, crashes))
    grid = [[" "] * W for _ in range(SEA)]
    # lighthouse on left
    grid[0][0] = "("
    grid[0][1] = ")"
    # beam: a fan of light from left
    for dy in range(-2, 3):
        y = 1 + dy
        if 0 <= y < SEA:
            x = int(beam)
            for i in range(2, min(x + 1, W)):
                if abs(dy) <= (1 if i > x - 8 else 0):
                    pass
            for i in range(2, x + 1):
                if 0 <= (i // 8) <= 1 and abs(dy) <= 1 and i >= x - 8:
                    if grid[y][i] == " ":
                        grid[y][i] = "."
            if 0 <= x < W:
                grid[y][x] = "="
    # rocks on right
    for y in range(SEA):
        grid[y][W - 1] = "~"
    # ships drift near the rocks
    for s in ships:
        x = int(s["x"])
        if 0 <= x < W and 0 <= s["y"] < SEA:
            grid[s["y"]][x] = "⛵" if False else "<>"
    for row in grid:
        print("".join(row))
    print()
    print(msg)
    print("enter = flash beam | q = quit")


def main():
    random.seed()
    beam = 2.0
    direction = 1
    speed = 28.0  # columns per second
    ships = []
    spawn = 0.0
    saved = 0
    crashes = 0
    msg = "Press enter when the beam touches a ship!"
    start = time.time()
    fd = sys.stdin.fileno()
    old = None
    try:
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)
    except termios.error:
        old = None
        pass
    try:
        while True:
            t = time.time()
            secs = t - start
            if secs > TIME_LIMIT:
                break
            dt = 0.05
            # move beam
            beam += direction * speed * dt
            if beam > W - 3:
                beam = W - 3
                direction = -1
            if beam < 2:
                beam = 2
                direction = 1
            # spawn ships
            spawn -= dt
            if spawn <= 0 and len(ships) < 4:
                spawn = random.uniform(1.2, 2.5)
                ships.append({"x": float(random.randint(W - 25, W - 4)),
                              "y": random.randint(1, SEA - 1),
                              "life": 6.0})
            # drift and age ships
            for s in ships:
                s["x"] -= 3.0 * dt
                s["life"] -= dt
            crashed = [s for s in ships if s["x"] < 6 or s["life"] <= 0]
            for s in crashed:
                crashes += 1
                msg = "A ship crashed on the rocks!"
            ships = [s for s in ships if s not in crashed]
            if saved >= GOAL:
                break
            draw(beam, ships, saved, crashes, TIME_LIMIT - int(secs), secs, msg)
            # check input (tiny window)
            ready = False
            ch = None
            # simple poll using select
            import select
            r, _, _ = select.select([sys.stdin], [], [], 0.05)
            if r:
                ch = sys.stdin.read(1)
                ready = True
            if ready and ch == "q":
                break
            if ready and ch in ("\r", "\n", " "):
                hit = None
                for s in ships:
                    if abs(s["x"] - beam) < 6:
                        hit = s
                        break
                if hit:
                    ships.remove(hit)
                    saved += 1
                    msg = "Ship guided home! (%d/%d)" % (saved, GOAL)
                else:
                    msg = "The beam flashed on empty sea..."
        # end while
    finally:
        if old is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    os.system("clear" if os.name == "posix" else "cls")
    print("LIGHTHOUSE KEEPER - night over!")
    print("Ships guided home: %d/%d" % (saved, GOAL))
    print("Wrecks: %d" % crashes)
    if saved >= GOAL:
        print("The harbor is safe. Brilliant keeping, Keeper!")
    elif saved >= 5:
        print("A fine night's work, Keeper.")
    else:
        print("The sea was cruel tonight, Keeper.")
        sys.exit(1)


if __name__ == "__main__":
    main()
