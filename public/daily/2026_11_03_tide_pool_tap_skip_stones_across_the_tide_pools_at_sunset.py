# Daily Terminal Drop
# Date: 2026-11-03
# Title: Tide Pool Tap: Skip stones across the tide pools at sunset

# Daily Terminal Drop
# Date: 2026-11-03
# Title: Tide Pool Tap: Flick pebbles to skip stones across the tide pools at sunset
#!/usr/bin/env python3
"""TIDE POOL TAP - flick PEBBLES to skip stones across the tide pools!

Sunset paints the shore. You stand at the beach with a bag of
PEBBLES. FLICK them to SKIP across TIDE POOLS -- each skip
splashes a WAVE that pushes your stone FARTHER! Reach the
far SHORE LINE in 12 flicks or the tide takes your stone!

Legend (top view):
  ~  tide pool water (your stone SKIPS on this!)
  #  tall rock (stone SINKS -- turn ends)
  o  shiny shell (+25 pts if your stone stops here!)
  =  far shore line (REACH IT to WIN BIG!)
  .  wet sand (stone DRAGS -- stops here)

HOW IT WORKS:
  Type a FLICK POWER 1-9 + ENTER. Your stone FLIES that many
  cells, SKIPPING once more for every pool it crosses!
  Skip chains = BIG distance! But watch the TIDE: every 4
  flicks the water RISES 1 row -- pools GROW, sand shrinks!

  Land on wet sand? stone stops (1 pt). Land on a shell?
  +25 pts! Stick the landing on the FAR SHORE? +100 pts
  and WIN! Hit a rock? SPLASH! stone sinks, 0 pts.

TIDE CLOCK: 12 flicks per game. Every 4 flicks the tide
  creeps UP -- rows 7, 6, 5... flood as you play!
  (flooded rows become tide pools -- more skips!)

SCORE: shore 100, shell 25, sand 1. 12 flicks, ONE stone
  per flick -- make each skip count!

COMMANDS: 1-9 flick power   q quit
"""
import random

W = 34
H = 10
SHORE_COL = W - 2
FLICKS = 12
SKIP_BOOST = 4  # extra cells each pool skip gives


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.flick = 0
        self.score = 0
        self.tide_row = 7  # rows >= tide_row are flooded (pools)
        self.msg = "sunset glows. flick a stone 1-9."
        self.over = False
        self.won = False
        self.make_beach()

    def make_beach(self):
        self.rocks = set()
        self.shells = set()
        while len(self.rocks) < 6:
            self.rocks.add((self.rng.randint(2, H - 2),
                            self.rng.randint(6, W - 8)))
        while len(self.shells) < 5:
            p = (self.rng.randint(1, H - 2),
                 self.rng.randint(6, W - 8))
            if p not in self.rocks:
                self.shells.add(p)

    def flooded(self, r):
        return r >= self.tide_row

    def surface(self, r, c):
        """char at cell (outside board = sand)"""
        if not (0 <= r < H and 0 <= c < W):
            return "."
        if c >= SHORE_COL:
            return "="
        if (r, c) in self.rocks:
            return "#"
        if (r, c) in self.shells:
            return "o"
        if self.flooded(r):
            return "~"
        return "."

    def draw(self, path):
        print("TIDE POOL TAP  flick:%d/12  pts:%d  tide floods rows %d+"
              % (self.flick, self.score, self.tide_row))
        print("sunset west <-- you flick EAST --> far shore")
        grid = []
        for r in range(H):
            row = []
            for c in range(W):
                row.append(self.surface(r, c))
            grid.append(row)
        for (r, c) in path:
            if 0 <= r < H and 0 <= c < W and grid[r][c] not in "=#":
                grid[r][c] = "*"
        grid[self.rng.randint(0, 0) if False else 0]  # keep grid list alive
        for r in range(H):
            print("".join(grid[r]))
        print("+" + "-" * (W - 2) + "+")  # shore line marker
        print(self.msg)

    def flick_stone(self, power):
        """throw 1 stone, return path it took"""
        r = self.rng.randint(1, H - 2)
        if self.surface(r, 1) == "#":
            for alt in range(1, H - 1):
                if self.surface(alt, 1) != "#":
                    r = alt
                    break
        c = 0
        skips = 0
        path = [(r, 0)]
        move = power
        while move > 0:
            c += 1
            move -= 1
            s = self.surface(r, c)
            if c >= SHORE_COL:
                path.append((r, min(c, W - 1)))
                # stuck the landing on far shore!
                self.score += 100
                self.msg = ("STICK THE LANDING! +100 -- your stone rests"
                            " on the far shore!")
                self.won = True
                self.flick += 1
                return path
            if s == "#":
                self.msg = "SPLASH! your stone sinks on a tall rock."
                pts = 0
                self.score += pts
                self.flick += 1
                return path
            path.append((r, c))
            if s == "o":
                pass  # shell bonus scored on stop, below
            if move == 0:
                # out of power -- SKIP if on pool, else stop
                if s == "~" and skips < 6:
                    move += SKIP_BOOST  # skip splash!
                    skips += 1
                else:
                    break
        # stone stopped
        s = self.surface(r, c)
        if s == "o":
            self.score += 25
            self.msg = "shell hit! your stone rests by a shiny shell +25"
        else:
            self.score += 1
            skips_word = "skip!" if skips else "drag."
            self.msg = "stone stops on wet sand (%d pt) after %d skip%s" % (
                1, skips, "s" if skips != 1 else "")
        self.flick += 1
        if self.flick % 4 == 0 and self.tide_row > 3:
            self.tide_row -= 1
            self.msg += " -- the TIDE RISES! row %d floods" % self.tide_row
        if self.flick >= FLICKS:
            self.over = True
        return path


def main():
    g = Game()
    print("TIDE POOL TAP -- skip stones across the tide pools at sunset!")
    print("type flick power 1-9 + ENTER (q quits). 12 flicks. reach")
    print("the far shore = for +100! shells o = +25. sand = 1 pt.")
    input("press ENTER to watch the sunset...")
    while not g.over and not g.won:
        g.draw([])
        raw = input("flick power 1-9 (q quit) > ").strip()
        if raw == "q":
            print("you pocket the pebbles. the tide sighs.")
            return
        if not raw.isdigit() or not (1 <= int(raw) <= 9):
            g.msg = "flick HARDER! (1-9)"
            continue
        path = g.flick_stone(int(raw))
        g.draw(path)
        if g.won or g.over:
            break
        try:
            input("-- press ENTER for next flick --")
        except EOFError:
            break
    g.draw([])
    if g.won:
        print("SUNSET SKIPPER! your stone rests on the far shore!")
    else:
        print("the tide takes your stone.")
    print("final score: %d  flicks used: %d" % (g.score, g.flick))


if __name__ == "__main__":
    main()
