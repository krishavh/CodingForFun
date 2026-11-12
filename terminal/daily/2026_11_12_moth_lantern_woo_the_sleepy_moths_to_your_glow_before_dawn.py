# Daily Terminal Drop
# Date: 2026-11-12
# Title: Moth Lantern: Woo the sleepy moths to your glow before dawn

#!/usr/bin/env python3
"""MOTH LANTERN - lure sleepy moths to your lantern before dawn!

Midnight in the garden. Your LANTERN glows on a grass path.
Sleepy MOTHS flit around in the dark, lost in the moonlight.
Flash your lantern to make a GLOW RING -- any moth inside the
ring wakes up and flutters toward the light!

Legend:
  L  YOUR LANTERN (you!)
  m  moth (sleepy, 10 pts when roosted)
  M  golden moth (shy, 25 pts!)
  *  glow ring (lasts 2 turns)
  .  cool dark grass

HOW IT WORKS:
  Move (a/d/w/s) then press F to FLASH a glow ring!
  Moths INSIDE the ring get WOOED: they wake and drift
  toward your lantern. Touch a moth with the
  lantern to ROOST it -- +points!

  But watch out! Each turn DAWN CREEPS: the sky lightens
  1 row from the top. A moth in the dawn light flutters
  away fast! Woo 5 moths before the whole garden
  is bright to WIN!

COMMANDS: a/d/w/s move   f flash   q quit
"""
import random
import sys
import termios
import tty
import select
import os
import time

W, H = 30, 16
GOAL = 5
DAWN_START = 4  # rows lit when dawn begins


def read_key():
    fd = sys.stdin.fileno()
    try:
        old = termios.tcgetattr(fd)
    except termios.error:
        # no tty (piped/pytest): poll stdin raw, exit on any byte or EOF
        r, _, _ = select.select([sys.stdin], [], [], 0.1)
        if r:
            ch = sys.stdin.read(1)
            return ch if ch else "q"
        return ""
    try:
        tty.setraw(fd)
        r, _, _ = select.select([sys.stdin], [], [], 0.4)
        return sys.stdin.read(1) if r else ""
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def board(px, py, moths, glow, dawn, msg, score, roosted):
    grid = [["." for _ in range(W)] for _ in range(H)]
    for (x, y), kind in moths.items():
        grid[y][x] = kind
    for (x, y), life in glow.items():
        grid[y][x] = "*"
    for y in range(dawn):
        for x in range(W):
            if grid[y][x] == ".":
                grid[y][x] = ":"
    grid[py][px] = "L"
    out = []
    if msg:
        out.append(msg)
    out += ["+" + "-" * W + "+", "MOTHS ROOSTED %d/%d   SCORE %d" % (roosted, GOAL, score)]
    out += ["|" + "".join(grid[y]) + "|" for y in range(H)]
    out += ["+" + "-" * W + "+"]
    print("\n".join(out))


def main():
    random.seed()
    px, py = W // 2, H - 2
    moths = {}
    for _ in range(5):
        x, y = random.randint(1, W - 2), random.randint(1, H - 2)
        moths[(x, y)] = "m" if random.random() < 0.8 else "M"
    glow = {}
    dawn = 0
    turn = 0
    score = 0
    roosted = 0
    msg = "Woo 5 moths home before dawn floods the garden!"
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        board(px, py, moths, glow, dawn, msg, score, roosted)
        if roosted >= GOAL:
            print("\nALL MOTHES ROOSTED! You win the midnight garden!")
            return
        if dawn >= H:
            print("\nDAWN FLOODED THE GARDEN! Too bright to woo moths.")
            return
        k = read_key()
        turn += 1
        msg = ""
        if k == "q":
            print("\nBye! (%d roosted, %d pts)" % (roosted, score))
            return
        elif k in "aw sd".replace(" ", ""):
            dx, dy = {"a": (-1, 0), "d": (1, 0), "w": (0, -1), "s": (0, 1)}[k]
            px = max(0, min(W - 1, px + dx))
            py = max(0, min(H - 1, py + dy))
        elif k == "f":
            glow = {}
            for dy in (-3, -2, -1, 0, 1, 2, 3):
                for dx in (-3, -2, -1, 0, 1, 2, 3):
                    if abs(dx) + abs(dy) <= 4:
                        x, y = px + dx, py + dy
                        if 0 <= x < W and 0 <= y < H:
                            glow[(x, y)] = 8
            msg = "FLASH! The garden glows..."
        # glow fades
        for pos in list(glow):
            glow[pos] -= 1
            if glow[pos] <= 0:
                del glow[pos]
        # moths: flee dawn light, drift toward lantern if glowing near
        new_moths = {}
        for (x, y), kind in moths.items():
            speed = 1
            if y < dawn:
                speed = 2  # panicked by light!
            dx = dy = 0
            if (x, y) in glow:
                dx = (px - x)
                dy = (py - y)
                d = max(abs(dx), abs(dy)) or 1
                dx = int(dx > 0) - int(dx < 0)
                dy = int(dy > 0) - int(dy < 0)
            else:
                dx, dy = random.choice([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)])
            for _ in range(speed):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H:
                    x, y = nx, ny
            if (x, y) == (px, py):
                pts = 10 if kind == "m" else 25
                score += pts
                roosted += 1
                msg = msg or "A %s moth roosts! +%d" % ("golden" if kind == "M" else "", pts)
                continue
            new_moths[(x, y)] = kind
        moths = new_moths
        # fill empty spots with new sleepy moths (max 7)
        while len(moths) < 5 + (1 if turn % 10 == 0 else 0) and len(moths) < 7:
            x, y = random.randint(0, W - 1), random.randint(0, H - 1)
            if (x, y) not in moths and (x, y) != (px, py):
                moths[(x, y)] = "m" if random.random() < 0.8 else "M"
        # dawn creeps
        if turn % 10 == 0:
            dawn += 1
            if turn % 20 == 0:
                msg = msg or "The dawn creeps closer..."
        time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
