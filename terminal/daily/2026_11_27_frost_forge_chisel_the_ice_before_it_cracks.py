# Daily Terminal Drop
# Date: 2026-11-27
# Title: Frost Forge: Chisel the ice before it cracks

#!/usr/bin/env python3
"""FROST FORGE - chisel the ice before it cracks!

Copy the frost spirit's chisel pattern.
Arrows (or wasd) tap the chisel in that direction.
Each round adds one more tap. Tap wrong and the ice cracks!
Survive 8 rounds to finish the sculpture.
"""
import os
import random
import sys
import time
import tty
import termios

ROUNDS = 8
SPEED = 0.45
ICONS = {"a": "<", "d": ">", "w": "^", "s": "v"}
NAMES = {"a": "LEFT", "d": "RIGHT", "w": "UP", "s": "DOWN"}


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def draw_top(msg, cracks, rnd):
    clear()
    print("FROST FORGE  |  round %d/%d  cracks: %d/3" %
          (rnd, ROUNDS, cracks))
    print()
    # ice block
    print("   _______   ")
    print("  /       \\  ")
    for _ in range(3):
        print("  |  ***  |  ")
    print("  |  ***  |  ")
    print("  \\_______/  ")
    print()
    print(msg)


def read_key():
    fd = sys.stdin.fileno()
    if not sys.stdin.isatty():
        return ""
    old = tty.setraw(fd)
    try:
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, tty.TCSADRAIN, old)
    if ch == "\x1b":
        # arrow sequence
        seq = sys.stdin.read(2) if select_have_input() else ""
        if seq == "[A":
            return "w"
        if seq == "[B":
            return "s"
        if seq == "[C":
            return "d"
        if seq == "[D":
            return "a"
        return ""
    if ch in ("q", "\x03"):
        raise KeyboardInterrupt
    if ch in ("r", "R"):
        return "r"
    if ch in "wasd":
        return ch
    return ""


def select_have_input():
    import select
    r, _, _ = select.select([sys.stdin], [], [], 0.1)
    return bool(r)


def show_pattern(pattern):
    for d in pattern:
        draw_top("Chisel: %s   %s" % (NAMES[d], ICONS[d] * 9), 0, 0)
        time.sleep(SPEED)
        draw_top("", 0, 0)
        time.sleep(0.08)


def main():
    random.seed()
    cracks = 0
    pattern = []
    rnd = 0
    draw_top("Press any chisel key (wasd/arrows) to start. q quits.",
             cracks, rnd)
    while True:
        try:
            k = read_key()
        except KeyboardInterrupt:
            print("\nFrozen out. Goodbye!")
            return
        if k:
            break
    while rnd < ROUNDS:
        rnd += 1
        pattern.append(random.choice("wasd"))
        draw_top("Watch the frost spirit...", cracks, rnd)
        time.sleep(0.5)
        # spirit taps (hide cursor not needed; redraw)
        show_pattern(pattern)
        draw_top("Your turn! Repeat the %d taps." % len(pattern), cracks, rnd)
        for i, want in enumerate(pattern):
            while True:
                try:
                    k = read_key()
                except KeyboardInterrupt:
                    print("\nFrozen out. Goodbye!")
                    return
                if k == "r":
                    show_pattern(pattern)
                    draw_top("Your turn! Repeat the %d taps." %
                             len(pattern), cracks, rnd)
                    continue
                if k:
                    break
            if k != want:
                cracks += 1
                if cracks >= 3:
                    draw_top("CRACK! The ice shattered!", cracks, rnd)
                    print("\nThe sculpture cracked after %d rounds."
                          % (rnd - 1))
                    print("Pattern was: %s" %
                          " ".join(NAMES[d] for d in pattern))
                    return
                draw_top("CRACK! Wrong tap! (%d/3 cracks)" % cracks,
                         cracks, rnd)
                time.sleep(1.2)
                # retry same round with same pattern
                break
        else:
            draw_top("Smooth ice! Round %d done." % rnd, cracks, rnd)
            time.sleep(0.8)
    draw_top("", cracks, rnd)
    print("\nMASTER CHISELER! All %d rounds done, %d cracks." %
          (ROUNDS, cracks))
    print("The ice swan sparkles in the morning light!")


if __name__ == "__main__":
    main()
