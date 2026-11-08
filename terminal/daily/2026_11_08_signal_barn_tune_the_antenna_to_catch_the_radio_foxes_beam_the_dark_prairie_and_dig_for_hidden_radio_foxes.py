# Daily Terminal Drop
# Date: 2026-11-08
# Title: Signal Barn: Tune the Antenna to Catch the Radio Foxes: Beam the dark prairie and dig for hidden radio foxes

# Daily Terminal Drop
# Date: 2026-11-08
# Title: Signal Barn: Tune the Antenna to Catch the Radio Foxes
#!/usr/bin/env python3
"""SIGNAL BARN - swing the radio antenna to catch the foxes!

Night falls on the Kansas prairie. Hidden RADIO FOXES beep
somewhere in the dark. Your old barn antenna SWINGS on a
pivot -- point it, PING the dial, and time the echoes to
triangulate each fox!

Legend (prairie map):
  B  your barn (pivot, fixed center)
  f  radio fox (found! +50 pts)
  *  your beam (sweeps the whole line!)
  .  prairie grass

HOW IT WORKS:
  You see the map WITHOUT foxes. Type a beam letter (n/s/e/w)
  or a diag (ne/nw/se/sw) to POINT the antenna.
  The beam SHOOTS the whole line from the barn!
  Every fox on that line PINGS -- you hear the COUNT
  and the FARTHEST distance! (no positions!)

  Then GUESS a cell (like c4) to dig for a fox!
  Right? +50 pts, fox hops out! Wrong? dirt pile -5.

RADIO TIP: beam first, listen, then dig! Each beam
  costs 1 spark. Every 8 sparks the wind WHISTLES
  and all foxes SCRAMBLE 1 cell (they hide again!)

NIGHT ENDS: 24 sparks. Find 300 pts of foxes to WIN
  the prairie night! (4 foxes roam, 5 max spawn)

COMMANDS: n/s/e/w/ne/nw/se/sw beam   c4 dig   q quit
"""
import random
import sys

W, H = 26, 12
MAX_SPARKS = 24
GOAL = 300
START_FOXES = 4
MAX_FOXES = 5
SCRAMBLE_EVERY = 8


def clear():
    print("\033[2J\033[H", end="")


DIRS = {
    "n": (0, -1), "s": (0, 1), "e": (1, 0), "w": (-1, 0),
    "ne": (1, -1), "nw": (-1, -1), "se": (1, 1), "sw": (-1, 1),
}


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.sparks = 0
        self.score = 0
        self.digs = 0
        self.msg = "night falls. beam the prairie, listen for foxes!"
        self.over = False
        self.won = False
        self.barn = (W // 2, H // 2)
        self.found = []
        self.hidden = []
        self.beam_cells = []
        self.spawn_foxes()

    def spawn_foxes(self):
        while len(self.hidden) < START_FOXES:
            self.spawn_one()

    def spawn_one(self):
        while True:
            x = self.rng.randint(0, W - 1)
            y = self.rng.randint(0, H - 1)
            if (x, y) == self.barn:
                continue
            if [x, y] not in self.hidden and [x, y] not in self.found:
                self.hidden.append([x, y])
                return

    def cells_on_beam(self, d):
        dx, dy = DIRS[d]
        cells = []
        x, y = self.barn
        while True:
            x += dx
            y += dy
            if not (0 <= x < W and 0 <= y < H):
                break
            cells.append((x, y))
        return cells

    def beam(self, d):
        self.sparks += 1
        self.digs = 0
        self.beam_cells = self.cells_on_beam(d)
        hits = [c for c in self.beam_cells if list(c) in self.hidden]
        if hits:
            far = max(abs(c[0] - self.barn[0]) + abs(c[1] - self.barn[1])
                      for c in hits)
            self.msg = ("beep! %d fox%s on the %s line, farthest %d cells"
                        % (len(hits), "es" if len(hits) > 1 else "", d, far))
        else:
            self.msg = "static... no foxes on the %s line" % d
        if self.sparks % SCRAMBLE_EVERY == 0:
            self.scramble()
            self.msg += " | wind whistle! foxes scramble!"
        if self.sparks >= MAX_SPARKS:
            self.over = True
            self.won = self.score >= GOAL

    def scramble(self):
        new_hidden = []
        for x, y in self.hidden:
            dirs = list(DIRS.values())
            self.rng.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (0 <= nx < W and 0 <= ny < H
                        and (nx, ny) != self.barn
                        and [nx, ny] not in new_hidden
                        and [nx, ny] not in self.found):
                    x, y = nx, ny
                    break
            new_hidden.append([x, y])
        self.hidden = new_hidden

    def parse_dig(self, tok):
        try:
            x = int(tok[1:]) - 1
            y = ord(tok[0]) - ord("a")
        except (ValueError, IndexError, TypeError):
            return False
        if not (0 <= x < W and 0 <= y < H):
            return False
        self.dig(x, y)
        return True

    def dig(self, x, y):
        self.digs += 1
        if self.digs > 3:
            self.msg = "easy! beam first, then dig (3 digs per beam)"
            return
        if [x, y] in self.hidden:
            self.hidden.remove([x, y])
            self.found.append([x, y])
            self.score += 50
            self.msg = "FOX! +50 pts (%d foxes found)" % len(self.found)
            if len(self.hidden) < 2 and len(self.found) + len(self.hidden) < MAX_FOXES:
                self.spawn_one()
                self.msg += " | new fox sneaks in!"
            if self.score >= GOAL:
                self.over = True
                self.won = True
        else:
            self.score -= 5
            self.msg = "dirt pile... no fox (-5). listen to the beeps!"

    def render(self, show_foxes=False):
        print()
        print("  SIGNAL BARN -- radio fox hunt on the prairie")
        print("  " + "-" * 44)
        print("     " + "".join(chr(ord("a") + i) for i in range(H)))
        for x in range(W):
            row = "%2d " % (x + 1)
            for y in range(H):
                row += "%s" % (
                    "B" if (x, y) == self.barn else
                    "f" if [x, y] in self.found or (show_foxes and [x, y] in self.hidden) else
                    "*" if (x, y) in self.beam_cells else ".")
            print(row)
        print()
        print("  sparks: %d/%d    score: %d/%d    foxes hidden: %d"
              % (self.sparks, MAX_SPARKS, self.score, GOAL, len(self.hidden)))
        if self.beam_cells:
            print("  last beam: %s" % ("*" * len(self.beam_cells)))
        print()
        print("  %s" % self.msg)
        print("  digs left this beam: %d" % max(0, 3 - self.digs))
        print("  COMMANDS: n/s/e/w/ne/nw/se/sw beam   c4 dig   q quit")


def main():
    seed = None
    for i, a in enumerate(sys.argv):
        if a == "--seed":
            seed = int(sys.argv[i + 1])
    g = Game(seed)
    clear()
    g.render()
    while not g.over:
        try:
            tok = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        clear()
        if tok in ("q", "quit", "exit"):
            print("73! (radio bye!)")
            return
        elif tok in DIRS:
            g.beam(tok)
        elif len(tok) >= 2 and tok[0].isalpha() and tok[1:].isdigit():
            if not g.parse_dig(tok):
                g.msg = "off the prairie! (a1 to %s%d)" % (
                    chr(ord("a") + H - 1), W)
        else:
            g.msg = "? beam n/s/e/w/ne/nw/se/sw or dig like c4"
        g.render(show_foxes=g.over)
        if g.over:
            print()
            if g.won:
                print("  NIGHT WIN! %d pts! the prairie sings! (foxes shown)"
                      % g.score)
            else:
                print("  dawn... %d pts. foxes were: (shown) " % g.score)
            return


if __name__ == "__main__":
    main()
