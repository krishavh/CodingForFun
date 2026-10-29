# Daily Terminal Drop
# Date: 2026-10-29
# Title: Glasswing Aviary: Flutter up the glass tower before dusk runs out

#!/usr/bin/env python3
"""GLASSWING AVIARY - a terminal tower-climb about a moth's short flight!

Dusk fills a glass aviary. You are a tiny MOTH, fluttering UP a tower
of glass panes. Each press of f FLUTTERS you up 1 row -- but fluttering
burns DUST, and every 3 flutters a DRAFT shoves you sideways! Sip from
Nectar Cups, rest on Ledges, and dodge the hungry FLY TRAP below.

Legend:
  @  you (the moth)
  =  glass pane (solid -- you cannot enter)
  _  ledge (safe, you may rest)
  o  nectar cup (sip +8 dust, +50 points!)
  v  fly trap (opens every 6 turns -- touch and lose 1 wing!)
  .  air (nothing)

HOW IT WORKS:
  Each turn you press f to flutter UP 1 row (costs 2 dust) or
  r to REST (costs 1 turn, +1 dust). While resting, the TRAP
  counts down! After every 3 flutters a DRAFT blows you 1 row
  sideways (into panes? you SLIDE down till you find a spot).

DUST & WINGS:
  Dust is your fuel -- no dust, no flutter. You have 3 wings.
  Touch a trap and lose 1 wing (respawn at bottom).

THE TOP:
  Reach row 1 (the sun roof) to WIN the flight! 40 turns of
  dusk before the glass darkens forever.

COMMANDS: f flutter   r rest   q quit
"""
import random
import sys

W, H = 32, 18
TRAP_PERIOD = 6
DRAFT_EVERY = 3
TURNS = 40
START_DUST = 10

TRAP_ART = ["\\_V_/", "\\_u_/", "\\_U_/", "\\_U_/"]


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.wings = 3
        self.score = 0
        self.dust = START_DUST
        self.turn = 0
        self.flut = 0
        self.trap_t = 0
        self.msg = "dusk settles. press f to flutter."
        self.dead = False
        self.won = False
        self.px, self.py = W // 2, H - 2
        self.grid = self.build()
        self.trapx = self.rng.randrange(2, W - 2)
        self.trap_open = False

    def build(self):
        g = [["." for _ in range(W)] for _ in range(H)]
        # top row = sun roof (win row) -- open mid, panes at edges
        for x in range(W):
            g[0][x] = "=" if x < 3 or x > W - 4 else "."
        for y in range(2, H - 1, 3):  # glass rows
            gap = self.rng.randrange(3, W - 6)
            width = self.rng.randint(3, 6)
            for x in range(W):
                g[y][x] = "="
            for x in range(gap, min(W, gap + width)):
                g[y][x] = "."
            # ledge sometimes in gap
            if self.rng.random() < 0.6:
                lx = self.rng.randint(gap, min(W - 1, gap + width - 1))
                g[y][lx] = "_"
        # nectar cups
        for _ in range(7):
            while True:
                x, y = self.rng.randrange(W), self.rng.randrange(2, H - 1)
                if g[y][x] == ".":
                    g[y][x] = "o"
                    break
        return g

    def free(self, x, y):
        if x < 0 or x >= W or y < 0 or y >= H:
            return False
        if self.grid[y][x] == "=":
            return False
        return True

    def slide(self, x, y):
        """fall down till a free spot (used after draft shove)"""
        while not self.free(x, y) and y < H - 1:
            y += 1
        return x, y

    def trap_glyph(self):
        return TRAP_ART[min(self.trap_t, 3)] if self.trap_open else " v "

    def draw(self):
        out = ["+" + "-" * W + "+"]
        trap_g = self.trap_glyph()
        for y in range(H):
            row = ["|"]
            for x in range(W):
                if x == self.px and y == self.py:
                    row.append("@")
                elif y == H - 1 and abs(x - self.trapx) <= 1:
                    i = x - (self.trapx - 1)
                    row.append(trap_g[i] if 0 <= i < 3 else " ")
                else:
                    row.append(self.grid[y][x])
            while len(row) < W + 1:
                row.append(" ")
            row.append("|")
            out.append("".join(row))
        out.append("+" + "-" * W + "+")
        print("\n".join(out))
        print(f"dust {self.dust}  wings {self.wings}  pts {self.score}  "
              f"turn {self.turn}/{TURNS}  trap {self.trap_t}/{TRAP_PERIOD}")
        print(f">> {self.msg}")

    def trap_step(self):
        self.trap_t += 1
        if self.trap_t >= TRAP_PERIOD:
            self.trap_t = 0
            self.trap_open = not self.trap_open
            self.msg = "the fly trap snaps " + ("OPEN!" if self.trap_open else "shut.")
        # creep EVERY turn toward the moth's column (slow but steady)
        if self.px < self.trapx:
            self.trapx -= 1
        elif self.px > self.trapx:
            self.trapx += 1
        if self.trap_open and self.py >= H - 2 and abs(self.px - self.trapx) <= 1:
            self.wings -= 1
            self.dust = max(2, self.dust - 4)
            self.score = max(0, self.score - 10)
            self.msg = f"CHOMP! {self.wings} wings left."
            if self.wings <= 0:
                self.dead = True
            # respawn on floor, away from trap
            self.py = H - 2
            if self.px > self.trapx + 2:
                self.px = max(0, self.trapx + 4)
            else:
                self.px = min(W - 1, self.trapx - 4)
            while not self.free(self.px, self.py):
                self.px += 1
                if self.px >= W:
                    self.px = 0

    def flutter(self):
        if self.dust < 2:
            self.msg = "no dust! rest (r) to rub wings."
            return
        self.dust -= 2
        self.turn += 1
        self.flut += 1
        # straight up, else nearest open column (same row, py-1 only)
        placed = False
        nx, ny = self.px, self.py - 1
        if self.free(nx, ny):
            placed = True
        else:
            for d in range(1, W):
                for nx in (self.px - d, self.px + d):
                    if self.free(nx, self.py - 1):
                        placed = True
                        break
                if placed:
                    break
        if not placed:
            nx, ny = self.px, self.py  # sealed in (never: roof row air)
        self.px, self.py = nx, ny
        self.land()
        if self.flut % DRAFT_EVERY == 0 and not self.dead and not self.won:
            d = self.rng.choice([-1, 1])
            self.msg += " | DRAFT! shoved " + ("west" if d < 0 else "east")
            nx2 = self.px + d
            if self.free(nx2, self.py):
                self.px, self.py = self.slide(nx2, self.py)
                self.land(True)
        if not self.dead:
            self.trap_step()

    def rest(self):
        self.turn += 1
        self.dust = min(30, self.dust + 3)
        self.msg = "you rest, wings rub. +3 dust."
        self.trap_step()

    def land(self, from_draft=False):
        c = self.grid[self.py][self.px]
        if c == "o":
            self.grid[self.py][self.px] = "."
            self.dust = min(30, self.dust + 8)
            self.score += 50
            self.msg = "nectar! +8 dust, +50 pts."
        elif c == "_":
            self.msg = "on a ledge. safe." if not from_draft else "draft slammed you on a ledge!"
        else:
            self.msg = "fluttering." if not from_draft else "shoved!"
        if self.py == 0:
            self.won = True
            self.msg = "YOU REACH THE SUN ROOF! dawn pours in!"

    def loop(self):
        while not self.dead and not self.won and self.turn <= TURNS:
            print("\033[2J\033[H", end="")
            self.draw()
            try:
                cmd = input("moth> ").strip().lower()
            except EOFError:
                print("\n[fuse blown]")
                return
            if cmd in ("f", "flutter"):
                self.flutter()
            elif cmd in ("r", "rest"):
                self.rest()
            elif cmd in ("q", "quit"):
                print("you land on the glass floor. dusk ends.")
                return
        print("\033[2J\033[H", end="")
        self.draw()
        if self.won:
            print(f"\nDAWN! you reach the roof with {self.score} pts and {self.wings} wings!")
        elif self.dead:
            print(f"\nthe fly trap feast ends your flight. {self.score} pts.")
        else:
            print(f"\ndusk ends. glass darkens. {self.score} pts.")
            print(f"final: {self.score} pts, {self.wings} wings, row {self.py}")


if __name__ == "__main__":
    import os
    os.system("stty sane 2>/dev/null" if os.name != "nt" else "cls")
    print("GLASSWING AVIARY -- moth, flutter up the glass tower!")
    print("f flutter (2 dust)   r rest (+3 dust)   q quit")
    print("draft every 3 flutters! trap opens every 6 turns!")
    Game(seed=None).loop()
