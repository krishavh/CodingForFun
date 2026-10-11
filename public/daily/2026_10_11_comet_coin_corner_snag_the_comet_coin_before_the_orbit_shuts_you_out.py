# Daily Terminal Drop
# Date: 2026-10-11
# Title: Comet Coin Corner: Snag the comet coin before the orbit shuts you out

#!/usr/bin/env python3
"""COMET COIN CORNER - snag the comet coin before the orbit shuts you out.

A tiny arcade of angles. You pilot a probe (P) around a tiny spinning
comet (C). Somewhere on the ring road glints a COMET COIN ($).

Grab the coin:  +100 and a fresh coin spawns.
Kiss the comet tail (too close!):  -25 and you bounce back.

You have 60 seconds of fuel. Burn it wisely, pilot!
"""
import math
import random
import time

W, H = 60, 22
CENTER = (W // 2, H // 2)
COMET_R = 4          # danger radius around the comet
FUEL_SECONDS = 60.0

# Precompute a ring of walkable points: TRUE circle walk, 90 steps around
import math as _m
RING = []
for i in range(90):
    a = 2 * _m.pi * i / 90
    x = int(CENTER[0] + math.cos(a) * 9 * 2)
    y = int(CENTER[1] + math.sin(a) * 9)
    if 0 < x < W - 1 and 0 < y < H - 1:
        RING.append((x, y))
_seen = []
for p in RING:
    if p not in _seen:
        _seen.append(p)
RING = _seen

POS0 = (W // 2 + 16, H // 2)  # ring right-most, x=46
if POS0 not in RING:
    POS0 = RING[0]


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def near_comet(p):
    return dist(p, CENTER) <= COMET_R


def next_on_ring(p, q):
    """Step from p toward q staying on the ring (choose best neighbor)."""
    best, bd = None, 1e9
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-1, 0, 1):
            n = (p[0] + dx, p[1] + dy)
            if n in RING:
                d = dist(n, q)
                if d < bd:
                    bd, best = d, n
    return best if bd < dist(p, q) else p


def draw(pos, comet_ang, coin, score, fuel):
    print("\033[2J\033[H", end="")
    grid = [[" "] * W for _ in range(H)]
    # orbit ring hint
    for (x, y) in RING:
        grid[y][x] = "."
    # comet
    cx, cy = CENTER
    for dx in range(-2, 3):
        for dy in range(-1, 2):
            if 0 <= cx + dx < W and 0 <= cy + dy < H:
                grid[cy + dy][cx + dx] = "*"
    grid[cy][cx] = "C"
    # player
    px, py = pos
    grid[py][px] = "P"
    # coin
    kx, ky = coin
    grid[ky][kx] = "$"
    # comet tail wobble
    tx = int(cx + math.cos(comet_ang) * (COMET_R + 1) * 2)
    ty = int(cy + math.sin(comet_ang) * (COMET_R + 1))
    if 0 <= tx < W and 0 <= ty < H and grid[ty][tx] == ".":
        grid[ty][tx] = "~"
    # border
    for x in range(W):
        grid[0][x] = grid[H - 1][x] = "-"
    for y in range(H):
        grid[y][0] = grid[y][W - 1] = "|"
    for row in grid:
        print("".join(row))
    print(f"fuel: {fuel:5.1f}s   score: {score}")


def read_cmd(timeout_s):
    """Non-blocking single-key read. Returns "" on timeout/EOF."""
    import select
    import sys
    old = None
    try:
        import termios
        import tty
        old = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
    except Exception:
        old = None  # not a tty (pipe) -- fall back to line reads
    r, _, _ = select.select([sys.stdin], [], [], timeout_s)
    if not r:
        if old:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        return ""
    ch = sys.stdin.read(1)
    if old:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
    if ch in ("\n", "\r", ""):
        return ""
    return ch


def main():
    random.seed()
    score = 0
    fuel = FUEL_SECONDS
    pos = POS0
    coin = random.choice([p for p in RING if dist(p, POS0) > 10])
    comet_ang = 0.0
    start = time.time()
    print("\033[2J\033[H", end="")
    print(__doc__)
    try:
        input("Press Enter to launch... ")
    except EOFError:
        return  # no stdin (pipe) -- launch instantly next time
    t_last = time.time()
    try:
        while fuel > 0:
            now = time.time()
            dt = now - t_last
            t_last = now
            fuel -= dt
            comet_ang += dt * 0.8
            draw(pos, comet_ang, coin, score, max(fuel, 0))
            cmd = read_cmd(0.12)
            if cmd == "q":
                break
            if cmd in ("w", "a", "s", "d"):
                dirs = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
                dx, dy = dirs[cmd]
                nx, ny = pos[0] + dx, pos[1] + dy
                if (nx, ny) in RING:
                    pos = (nx, ny)
                else:
                    # slide along ring: nearest ring pt in dir (dx,dy),
                    # preferring same x when moving vertical (ring is thin)
                    cand = []
                    for p in RING:
                        if p == pos:
                            continue
                        if dx > 0 and p[0] <= pos[0]:
                            continue
                        if dx < 0 and p[0] >= pos[0]:
                            continue
                        if dx == 0:
                            if dy > 0 and p[1] <= pos[1]:
                                continue
                            if dy < 0 and p[1] >= pos[1]:
                                continue
                        if dy > 0 and p[1] < pos[1]:
                            continue
                        if dy < 0 and p[1] > pos[1]:
                            continue
                        cand.append(p)
                    if cand:
                        pos = min(cand, key=lambda p: dist(p, pos))
            # spinning tail: touch it and lose 25, bounce toward start
            tail = (int(CENTER[0] + math.cos(comet_ang) * (COMET_R + 1) * 2),
                    int(CENTER[1] + math.sin(comet_ang) * (COMET_R + 1)))
            if pos == tail and score >= 25:
                score -= 25
                pos = next_on_ring(pos, POS0)  # bounce toward start
            if pos == coin:
                score += 100
                far = [p for p in RING if dist(p, pos) > 10]
                coin = random.choice(far) if far else random.choice(RING)
    except (EOFError, KeyboardInterrupt):
        pass
    draw(pos, comet_ang, coin, score, 0.0)
    print(f"\nFuel out! Final score: {score}")


if __name__ == "__main__":
    main()
