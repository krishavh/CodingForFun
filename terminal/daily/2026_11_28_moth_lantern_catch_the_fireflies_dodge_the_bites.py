# Daily Terminal Drop
# Date: 2026-11-28
# Title: Moth Lantern: Catch the fireflies, dodge the bites

#!/usr/bin/env python3
"""MOTH LANTERN - catch the fireflies, dodge the moths!

Fireflies glow, moths bite.
Letters drift across the screen.
Tap the letter when a FIREFLY is on it.
Tap a letter with a MOTH and lose a wish.
Catch 10 fireflies to light the lantern.
"""
import os
import random
import sys
import time

WIDTH = 26
HEIGHT = 9
GOAL = 10
TICK = 0.25

COLORS = {"F": "\033[93m", "M": "\033[35m", "E": "\033[0m"}


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def new_bug(used):
    for _ in range(50):
        x = random.randrange(2, WIDTH - 2)
        y = random.randrange(2, HEIGHT - 1)
        if (x, y) not in used:
            return (x, y)
    return None


def draw(score, wishes, bugs, msg, flash):
    clear()
    print("MOTH LANTERN  |  fireflies %d/%d  wishes %d/3" %
          (score, GOAL, wishes))
    print()
    top = "  +" + "-" * WIDTH + "+"
    print(top)
    grid = [[" "] * WIDTH for _ in range(HEIGHT)]
    for (x, y), kind in bugs.items():
        grid[y][x] = kind
    for row in grid:
        print("  |" + "".join(row) + "|")
    print(top)
    print()
    if flash:
        print(COLORS.get(flash, "") + msg + COLORS["E"])
    else:
        print(msg)
    print("  Letters on screen: tap a letter key when a FIREFLY sits on it")
    print("  F = firefly (yellow)   M = moth (purple)")
    print("  q to quit")


def read_key():
    import termios
    import tty
    fd = sys.stdin.fileno()
    if not sys.stdin.isatty():
        return ""
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, tty.TCSADRAIN, old)
    return ch


def main():
    random.seed()
    score = 0
    wishes = 3
    bugs = {}
    msg = "Catch 10 fireflies. Moths bite!"
    flash = None
    while True:
        # spawn a bug sometimes
        if len(bugs) < 6 and random.random() < 0.6:
            spot = new_bug(set(bugs.keys()))
            if spot:
                bugs[spot] = random.choice("FFM")
        # bugs wander
        new_bugs = {}
        for (x, y), kind in bugs.items():
            dx = random.choice([-1, 0, 0, 1])
            dy = random.choice([-1, 0, 0, 1])
            nx, ny = x + dx, y + dy
            if 1 <= nx < WIDTH - 1 and 1 <= ny < HEIGHT - 1:
                new_bugs[(nx, ny)] = kind
            else:
                new_bugs[(x, y)] = kind
        bugs = new_bugs
        draw(score, wishes, bugs, msg, flash)
        flash = None
        # frame input (single key, no enter: small delay lets keys pile)
        start = time.time()
        pressed = None
        while time.time() - start < TICK:
            if sys.stdin.isatty():
                import select
                r, _, _ = select.select([sys.stdin], [], [], 0.05)
                if r:
                    ch = read_key()
                    if ch in ("q", "Q", "\x03"):
                        print("Lantern dark. Bye!")
                        return
                    if ch.isalpha():
                        pressed = ch.lower()
                        # find a bug on a column matching? use positions:
                        # letter index a..z maps across width
                        idx = ord(pressed) - ord("a")
                        x = 2 + (idx % (WIDTH - 4))
                        hit = None
                        for (bx, by), kind in bugs.items():
                            if abs(bx - x) <= 1:
                                hit = kind
                        if hit == "F":
                            score += 1
                            for key in list(bugs):
                                if abs(key[0] - x) <= 1:
                                    del bugs[key]
                            msg = "Caught one! %d/%d" % (score, GOAL)
                            flash = "F"
                            if score >= GOAL:
                                print("\nLANTERN LIT! You caught %d fireflies." % score)
                                return
                        elif hit == "M":
                            wishes -= 1
                            for key in list(bugs):
                                if abs(key[0] - x) <= 1:
                                    del bugs[key]
                            msg = "Ouch! Moth bite. %d wishes left" % wishes
                            flash = "M"
                            if wishes <= 0:
                                print("\nDark. The moths won. %d fireflies." % score)
                                return
                        else:
                            msg = "Empty air."
            else:
                time.sleep(0.05)
        # drift more when no tty: demo mode just cycles
        if not sys.stdin.isatty():
            time.sleep(0.1)


if __name__ == "__main__":
    main()
