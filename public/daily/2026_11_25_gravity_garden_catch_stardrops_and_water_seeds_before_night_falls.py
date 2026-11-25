# Daily Terminal Drop
# Date: 2026-11-25
# Title: Gravity Garden: Catch stardrops and water seeds before night falls

#!/usr/bin/env python3
"""GRAVITY GARDEN - plant seeds and steer falling stardrops into beds!

A tiny physics garden. Seeds sprout into beds of flowers.
Stardrops fall from the sky - catch them in your watering can
and pour them on seeds to grow flowers before night ends!
Keys: a/d = move can, s = pour (while over a seed), q = quit.
Grow 8 flowers before the 60-second night is over? Bloom! Zzz... sleepy.
"""
import os
import random
import sys
import time

W = 60
GROUND = 20
NIGHT = 60  # seconds
GOAL = 8


class Seed:
    def __init__(self):
        self.x = random.randint(3, W - 4)
        self.growth = 0  # 0..100
        self.drop = None  # falling y or None

    def row(self):
        if self.growth >= 100:
            return "   \\|/   "
        if self.growth >= 50:
            return "   |.    "
        return "   .     "


def draw(seeds, can_x, water, drops, secs, msg):
    os.system("clear" if os.name == "posix" else "cls")
    print("GRAVITY GARDEN  |  night left: %2ds  water: %d  flowers: %d/%d"
          % (NIGHT - int(secs), water, sum(1 for s in seeds if s.growth >= 100), GOAL))
    grid = [[" "] * W for _ in range(GROUND + 1)]
    for y, x in drops:
        y = int(y)
        if 0 <= y <= GROUND:
            grid[y][x] = "*"
    for s in seeds:
        grown = s.growth >= 100
        h = 4 if grown else (2 if s.growth >= 50 else 1)
        for i in range(1, h + 1):
            if GROUND - i >= 0:
                grid[GROUND - i][s.x] = "|" if not grown or i < h else "Y"
        if grown:
            grid[GROUND - h][s.x] = "\\|/"[1] if False else "*"
    for i, ch in enumerate("\\|/"):
        pass
    for s in seeds:
        if s.growth >= 100:
            for dx, ch in ((-1, "\\"), (0, "|"), (1, "/")):
                x = s.x + dx
                if 0 <= x < W:
                    grid[GROUND - 4][x] = ch
    for x, ch in ((can_x - 1, "("), (can_x, "U"), (can_x + 1, ")")):
        if 0 <= x < W:
            grid[GROUND][x] = ch
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * W + "+")
    print("a/d move  s pour water  q quit")
    if msg:
        print(msg)


def main():
    random.seed()
    seeds = [Seed() for _ in range(4)]
    can_x = W // 2
    water = 5
    drops = []  # [y, x] falling stardrops
    spawn = 0.0
    start = time.time()
    last = time.time()
    msg = "Catch stardrops in your can (U). Stand over a seed and pour (s)!"
    flowers = 0

    while True:
        now = time.time()
        dt = now - last
        last = now
        secs = now - start
        if secs >= NIGHT:
            msg = "Night ends! You grew %d flowers. %s" % (
                flowers, "BLOOM! Winner!" if flowers >= GOAL else "Too sleepy...")
            draw(seeds, can_x, water, drops, secs, msg)
            break

        # spawn stardrops
        spawn += dt
        if spawn > 1.4:
            spawn = 0
            drops.append([0, random.randint(1, W - 2)])

        # move drops
        for d in drops:
            d[0] += dt * 12
        caught = [d for d in drops if int(d[0]) >= GROUND - 1 and abs(d[1] - can_x) <= 1]
        drops = [d for d in drops if int(d[0]) < GROUND]
        for d in caught:
            water += 1
        # missed drops hit ground and vanish
        splash = [d for d in drops if int(d[0]) >= GROUND]
        drops = [d for d in drops if int(d[0]) < GROUND]
        for d in splash:
            for s in seeds:
                if abs(s.x - d[1]) <= 1 and s.growth < 100:
                    s.growth = min(100, s.growth + 3)  # rain helps a little
                    if s.growth >= 100:
                        flowers += 1

        # input (non-blocking)
        import select
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            ch = sys.stdin.read(1)
            if ch == "q":
                msg = "Bye! Flowers grown: %d" % flowers
                draw(seeds, can_x, water, drops, secs, msg)
                return
            elif ch == "a" and can_x > 1:
                can_x -= 1
            elif ch == "d" and can_x < W - 2:
                can_x += 1
            elif ch == "s" and water > 0:
                for s in seeds:
                    if abs(s.x - can_x) <= 1 and s.growth < 100:
                        water -= 1
                        s.growth = min(100, s.growth + 25)
                        if s.growth >= 100:
                            flowers += 1
                        break

        # new seed when one blooms big
        alive = [s for s in seeds if s.growth < 100]
        if len(alive) < 2 and flowers + len(seeds) - len(alive) < GOAL + 6:
            seeds.append(Seed())

        draw(seeds, can_x, water, drops, secs, msg if secs < 2 else "")
        time.sleep(0.05)


if __name__ == "__main__":
    try:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)
    except Exception:
        fd = None
        old = None
    try:
        main()
    finally:
        try:
            if fd is not None:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass
