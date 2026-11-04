# Daily Terminal Drop
# Date: 2026-11-04
# Title: Lantern Flight: Light the dark lamps before your oil burns out

#!/usr/bin/env python3
"""LANTERN FLIGHT - carry your lantern through the night, light the dark lamps!

You are a NIGHT WATCHER with a hand LANTERN. Dark LAMPS line a winding
path through the sleeping village. Each lamp you LIGHT needs fuel --
and your lantern BURNS OIL every step you take! Light ALL the lamps
before dawn, but dawn is coming FAST: midnight chimes steal steps!

Legend (side view):
  Y  you (night watcher, holding lantern)
  #  hedge ( impassable! go around )
  o  dark lamp (WALK INTO IT to light it! +40)
  *  lit lamp (glowing warm)
  .  cobblestone path (safe to walk)
  ~  pond (fall in = lose 10 oil! splash!)

HOW IT WORKS:
  Walk with w/a/s/d. EVERY step burns 1 oil (start 70).
  Step into a DARK lamp? LIGHT IT! +40 pts and it glows!
  Step into a POND? splash! -10 oil, stay dry-ish.

  MIDNIGHT CHIME: every 15 steps the clock TOLLS --
  dawn creeps closer: -5 steps off your LAMP CLOCK!
  (you feel the chill: 3 chimes per night)

  DAWN RUSH: when oil drops to 10 or less, lantern dims!
  (move fast, watcher: 1 extra oil per step? NO -- 2!)

SCORE: lamp 40 pts. Light ALL 6 LAMPS before oil runs
  out? +100 pts and VILLAGE HERO! Run dry? night
  watch ends, dark lamps stay dark...

COMMANDS: w/a/s/d move   q quit
"""
import random

W, H = 28, 12
START_OIL = 70
LAMPS = 6
CHIME_EVERY = 15
CHIME_COST = 5


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.oil = START_OIL
        self.steps = 0
        self.chimes = 0
        self.score = 0
        self.msg = "night falls. light the dark lamps!"
        self.over = False
        self.won = False
        self.make_village()

    def make_village(self):
        while True:
            self.grid = [["."] * W for _ in range(H)]
            self.py = self.rng.randint(1, H - 2)
            self.px = 1
            self.grid[self.py][self.px] = "Y"
            # scatter hedges (not on start)
            for _ in range(26):
                r, c = self.rng.randint(0, H - 1), self.rng.randint(0, W - 1)
                if (r, c) != (self.py, self.px):
                    self.grid[r][c] = "#"
            # place lamps on path cells
            self.lamps = []
            spots = [(r, c) for r in range(H) for c in range(W)
                     if self.grid[r][c] == "." and (r, c) != (self.py, self.px)]
            self.rng.shuffle(spots)
            for r, c in spots[:LAMPS]:
                self.grid[r][c] = "o"
                self.lamps.append((r, c))
            # scatter 3 ponds
            for _ in range(3):
                spots2 = [(r, c) for r in range(H) for c in range(W)
                          if self.grid[r][c] == "."]
                if spots2:
                    r, c = self.rng.choice(spots2)
                    self.grid[r][c] = "~"
            # flood fill from start: all lamps reachable?
            if self.all_reachable():
                return

    def all_reachable(self):
        seen = {(self.py, self.px)}
        stack = [(self.py, self.px)]
        while stack:
            r, c = stack.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < H and 0 <= nc < W and (nr, nc) not in seen:
                    if self.grid[nr][nc] != "#":
                        seen.add((nr, nc))
                        stack.append((nr, nc))
        return all(lamp in seen for lamp in self.lamps)

    def move(self, dr, dc):
        if self.over:
            return
        nr, nc = self.py + dr, self.px + dc
        if not (0 <= nr < H and 0 <= nc < W):
            self.msg = "edge of the village. turn back!"
            return
        if self.grid[nr][nc] == "#":
            self.msg = "hedge blocks the way!"
            return
        cost = 1
        if self.oil <= 10:
            cost = 2  # dawn rush: lantern dims, burns fast!
        self.oil -= cost
        self.steps += 1
        self.py, self.px = nr, nc
        cell = self.grid[nr][nc]
        if cell == "o":
            self.grid[nr][nc] = "*"
            self.lamps.remove((nr, nc))
            self.score += 40
            left = len(self.lamps)
            self.msg = "lamp LIT! +%d! %d left" % (40, left)
            if left == 0:
                self.score += 100
                self.over = True
                self.won = True
                self.msg = "ALL LAMPS LIT! +100! VILLAGE HERO!"
        elif cell == "~":
            self.oil -= 10
            self.msg = "splash! pond! -10 oil"
        else:
            self.msg = "step... step... (-%d oil)" % cost
        # midnight chime?
        if self.steps % CHIME_EVERY == 0 and self.chimes < 3:
            self.chimes += 1
            self.oil -= CHIME_COST
            self.msg += " | CHIME! dawn creeps: -%d oil" % CHIME_COST
        if self.oil <= 0 and not self.over:
            self.over = True
            self.msg = "out of oil! dark lamps stay dark... (%d lit)" % (LAMPS - len(self.lamps))

    def render(self):
        rows = []
        for r in range(H):
            rows.append("".join(self.grid[r]))
        rows.append("oil:%d steps:%d chimes:%d lamps:%d score:%d" % (
            self.oil, self.steps, self.chimes, LAMPS - len(self.lamps), self.score))
        rows.append(self.msg)
        return "\n".join(rows)


def main():
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    g = Game(seed)
    print("LANTERN FLIGHT -- light all %d lamps before oil runs out!" % LAMPS)
    print("w/a/s/d move | q quit | oil burns per step! chimes steal oil!")
    print(g.render())
    while not g.over:
        try:
            line = input("move> ").strip().lower()
        except EOFError:
            print("bye")
            return
        if not line:
            continue
        if line == "q":
            print("night watch ends. score: %d" % g.score)
            return
        dirs = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}
        if line in dirs:
            g.move(*dirs[line])
            print(g.render())
        elif line == "map":
            print(g.render())
        else:
            print("w/a/s/d move | q quit")
    print("GAME OVER -- %s" % ("VILLAGE HERO! all lamps lit!" if g.won else "oil ran dry"))
    print("final score: %d | steps: %d | lamps: %d/%d" % (
        g.score, g.steps, LAMPS - len(g.lamps), LAMPS))


if __name__ == "__main__":
    main()
