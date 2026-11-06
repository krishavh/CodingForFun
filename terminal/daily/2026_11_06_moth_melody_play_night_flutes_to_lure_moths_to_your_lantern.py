# Daily Terminal Drop
# Date: 2026-11-06
# Title: Moth Melody: Play night flutes to lure moths to your lantern

#!/usr/bin/env python3
"""MOTH MELODY - play the night market flutes to lure moths to your lantern!

Autumn night, a paper lantern market. You play WOODEN FLUTES.
Each flute has a NOTE (a-g). Press a note to PLAY it: every
moth on the board FLIES toward your LANTERN -- but moths hate
LOUD noise! Each note also WAKES a CRICKET that hops around.

Legend:
  L  your lantern (fixed, center bottom)
  m  moth (flutter TOWARD lantern on each note!)
  c  cricket (hops 1 random dir every note, eats nectar)
  n  nectar drop (cricket eats it +0, you grab +15)
  .  night air

HOW IT WORKS:
  Press a-g to play a note. EVERY note:
    - each moth flutters 2 rows toward the lantern
      (dx too: zig-zag closest first)
    - the cricket HOPS 1 random dir
  Moth reaches lantern? +20 pts, new moth spawns top!
  Cricket lands on lantern? eats 1 moth egg -5!

NECTAR: press x to grab nectar under lantern light
  (row of lantern only, 1 per turn, +15)

MOTH BALL: every 10 notes a DRAFT -- all moths flutter
  1 EXTRA row! Notes 40: dawn comes, moths go home.

GOAL: 200 points before dawn (40 notes)!
COMMANDS: a-g play note   x grab nectar   q quit
"""
import random
import sys

W, H = 30, 14
GOAL = 200
MAX_NOTES = 40
MOTHS_START = 4
NOTES = "abcdefg"


def clear():
    print("\033[2J\033[H", end="")


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.lantern = (W // 2, H - 2)
        self.notes_played = 0
        self.score = 0
        self.msg = "autumn night. play a-g to call the moths!"
        self.over = False
        self.won = False
        self.moths = []
        self.cricket = None
        self.nectar = []
        self.spawn_moths()
        self.spawn_cricket()
        self.spawn_nectar()

    def spawn_moths(self):
        for _ in range(MOTHS_START):
            self.moths.append(self.new_moth())

    def new_moth(self):
        while True:
            x = self.rng.randint(1, W - 2)
            y = self.rng.randint(0, H - 5)
            if (x, y) != self.lantern:
                return [x, y]

    def spawn_cricket(self):
        while True:
            x = self.rng.randint(0, W - 1)
            y = self.rng.randint(0, H - 1)
            if (x, y) != self.lantern and all((x, y) != tuple(m) for m in self.moths):
                self.cricket = [x, y]
                return

    def spawn_nectar(self):
        self.nectar = []
        for _ in range(3):
            while True:
                x = self.rng.randint(0, W - 1)
                y = self.rng.randint(0, H - 1)
                occupied = ((x, y) == self.lantern or
                            (x, y) == tuple(self.cricket) or
                            (x, y) in [tuple(m) for m in self.moths] or
                            (x, y) in self.nectar)
                if not occupied:
                    self.nectar.append((x, y))
                    break

    def in_bounds(self, x, y):
        return 0 <= x < W and 0 <= y < H

    def move_moths(self, extra):
        lx, ly = self.lantern
        landed = False
        for m in self.moths:
            steps = 2 + extra
            for _ in range(steps):
                dx = 0 if m[0] == lx else (1 if lx > m[0] else -1)
                dy = 0 if m[1] == ly else (1 if ly > m[1] else -1)
                if dx == 0 and dy == 0:
                    break
                nx, ny = m[0] + dx, m[1] + dy
                if self.rng.random() < 0.25 and dx != 0:
                    nx = m[0]  # zig-zag: sometimes hover, no x move
                if self.in_bounds(nx, ny):
                    m[0], m[1] = nx, ny
                if (m[0], m[1]) == self.lantern:
                    landed = True
                    break
        self.land_moths(landed)

    def land_moths(self, landed_any):
        lx, ly = self.lantern
        survivors = []
        for m in self.moths:
            if (m[0], m[1]) == (lx, ly) and landed_any:
                self.score += 20
                self.msg = "moth landed! +20"
                survivors.append(self.new_moth())
            else:
                survivors.append(m)
        self.moths = survivors

    def hop_cricket(self):
        x, y = self.cricket
        dx, dy = self.rng.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        nx, ny = x + dx, y + dy
        if self.in_bounds(nx, ny):
            self.cricket = [nx, ny]
        if self.cricket == list(self.lantern):
            if self.moths:
                self.moths.pop()
                self.moths.append(self.new_moth())
                self.score -= 5
                self.msg = "cricket ate an egg! -5"

    def grab_nectar(self):
        lx, ly = self.lantern
        cx, cy = self.cricket
        grabbed = False
        for n in list(self.nectar):
            if abs(n[0] - lx) <= 2 and n[1] >= ly - 2:
                self.nectar.remove(n)
                self.score += 15
                self.msg = "nectar! +15"
                grabbed = True
                break
        if not grabbed:
            self.msg = "no nectar in the lantern light!"
        self.spawn_nectar() if len(self.nectar) < 3 else None

    def play_note(self, note):
        if note == "x":
            self.grab_nectar()
            return
        if note not in NOTES:
            self.msg = "notes: a-g  (x nectar, q quit)"
            return
        self.notes_played += 1
        extra = 1 if self.notes_played % 10 == 0 else 0
        if extra:
            self.msg = "DRAFT! moths flutter extra!"
        else:
            self.msg = "note %s hums..." % note
        self.move_moths(extra)
        self.hop_cricket()
        if self.score >= GOAL:
            self.over = True
            self.won = True
        elif self.notes_played >= MAX_NOTES:
            self.over = True

    def draw(self):
        grid = [["."] * W for _ in range(H)]
        for (x, y) in self.nectar:
            if self.in_bounds(x, y):
                grid[y][x] = "n"
        cx, cy = self.cricket
        if self.in_bounds(cx, cy):
            grid[cy][cx] = "c"
        for m in self.moths:
            x, y = m
            if self.in_bounds(x, y) and grid[y][x] in ".n":
                grid[y][x] = "m"
        lx, ly = self.lantern
        grid[ly][lx] = "L"
        print("=" * W)
        print("MOTH MELODY  notes:%d/40  score:%d/%d" % (self.notes_played, max(0, self.score), GOAL))
        print("=" * W)
        for row in grid:
            print("".join(row))
        print("=" * W)
        print(self.msg)
        print("a-g play   x nectar   q quit")

    def intro(self):
        clear()
        print(__doc__)


def main():
    seed = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        seed = int(sys.argv[1])
    g = Game(seed)
    g.intro()
    while not g.over:
        cmd = input("note> ").strip().lower()
        if cmd == "q":
            print("night ends early. moths drift home...")
            return
        for ch in cmd:
            if g.over:
                break
            if ch in NOTES or ch == "x":
                g.play_note(ch)
                g.draw()
    clear()
    g.draw()
    if g.won:
        print("DAWN! The market hums: %d points! MOTH MASTER!" % g.score)
    else:
        print("Dawn breaks. Final score: %d. The moths flutter home..." % max(0, g.score))


if __name__ == "__main__":
    main()
