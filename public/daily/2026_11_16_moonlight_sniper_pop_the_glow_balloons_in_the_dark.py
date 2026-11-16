# Daily Terminal Drop
# Date: 2026-11-16
# Title: Moonlight Sniper: Pop the glow balloons in the dark

#!/usr/bin/env python3
"""MOONLIGHT SNIPER - pop the glow balloons in the dark!

Balloons drift up the screen in the dark. You aim a dart gun
at the bottom. Type an angle (0-180) and press enter to fire.
Each balloon has a points value. Pop them all before your
20 darts run out!

Angles: 0 = far right, 90 = straight up, 180 = far left.
"""
import math
import random
import sys

W = 40          # playfield width (columns)
H = 12          # playfield height (rows, top = 0)
START_DARTS = 20


class Balloon:
    def __init__(self, n):
        self.x = random.uniform(2, W - 3)
        self.y = random.uniform(2, H - 2)
        self.vx = random.uniform(-0.15, 0.15)
        self.vy = random.uniform(-0.3, -0.1)  # drift up
        self.pts = random.choice([5, 5, 10, 10, 25])
        self.char = "o" if self.pts < 25 else "*"
        self.id = n


def new_wave(n):
    return [Balloon(i + 1) for i in range(n)]


def draw(gun_x, balloons, darts, score, msg):
    grid = [[" "] * W for _ in range(H)]
    for b in balloons:
        xi, yi = int(b.x), int(b.y)
        if 0 <= yi < H and 0 <= xi < W:
            grid[yi][xi] = b.char
    if 0 <= gun_x < W:
        grid[H - 1][gun_x] = "^"
    print("+" + "-" * W + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * W + "+")
    print(f"Darts: {darts}  Score: {score}")
    if msg:
        print(msg)
    print("Angle to fire (0-180), 'l'/'r' move gun, 'q' quit:")


def main():
    random.seed()
    balloons = new_wave(6)
    darts = START_DARTS
    score = 0
    gun_x = W // 2
    msg = ""
    trail = []

    while True:
        # move balloons
        for b in balloons:
            b.x += b.vx
            b.y += b.vy
            if b.x < 1 or b.x > W - 2:
                b.vx *= -1
            if b.y < 1:  # escaped top: wrap to bottom
                b.y = H - 2
        draw(gun_x, balloons, darts, score, msg)
        trail = []
        try:
            cmd = input("> ").strip().lower()
        except EOFError:
            print("Bye!")
            return
        msg = ""
        if cmd == "q":
            print(f"Final score: {score}")
            return
        if cmd in ("l", "r"):
            gun_x += -2 if cmd == "l" else 2
            gun_x = max(0, min(W - 1, gun_x))
            continue
        if cmd in ("a", "d"):
            gun_x += -1 if cmd == "a" else 1
            gun_x = max(0, min(W - 1, gun_x))
            continue
        try:
            angle = float(cmd)
        except ValueError:
            msg = "Type an angle 0-180, l/r to move, q quit."
            continue
        if not 0 <= angle <= 180:
            msg = "Angle must be 0-180."
            continue
        if darts <= 0:
            msg = "No darts left! q to quit."
            continue
        darts -= 1
        rad = math.radians(angle)
        dx, dy = math.cos(rad), -math.sin(rad)
        # fly dart from gun, step until off field
        x, y = float(gun_x), float(H - 1)
        hit = None
        while 0 <= x < W and 0 <= y < H:
            for b in balloons:
                if hit is None and int(x) == int(b.x) and int(y) == int(b.y):
                    hit = b
            if hit:
                break
            x += dx * 0.5
            y += dy * 0.5
            trail.append((int(x), int(y)))
        if hit:
            score += hit.pts
            msg = f"POP! +{hit.pts}"
            balloons.remove(hit)
            if not balloons:
                print(f"Wave cleared! Score: {score}")
                balloons = new_wave(6)
        else:
            msg = "Missed!"
        if darts == 0:
            print(f"Out of darts! Final score: {score}")
            return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
