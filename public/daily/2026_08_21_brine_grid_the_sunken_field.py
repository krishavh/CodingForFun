# Daily Terminal Drop
# Date: 2026-08-21
# Title: Brine Grid: The Sunken Field

#!/usr/bin/env python3
"""
BRINE GRID: THE SUNKEN FIELD
============================
War ended forty years ago, but the ocean forgot. Beneath the drowned
freighter _Ironclaw Dawn_ lies a grid of rusted demolition charges,
half-lost in silt and kelp.

You are a free-diver sent down to clear the field so the salvage crew can
settle the old wreck. Tap each cell to gauge how many charges sit nearby.
Mark the ones you believe are live. Open every safe cell without setting a
charge off, and the sea floor is yours to claim.

How to play:
  wasd / arrows   move your dive-float around the field
  space / enter   pry open a cell  (charges detonate -> you sink)
  f               flag / un-flag a cell you believe is a charge
  c               chord: when an OPEN cell's neighbour flags equal its
                  number, open the remaining un-flagged neighbours at once
  q               surface and give up

Legend:
  .   silt (unopened)      <n>  n charges in the 8 cells around here
  F   flagged charge       *   the sea you met the hard way
"""
import os
import random
import sys

ROWS, COLS = 8, 8
MINES = 10
HIDDEN, FLAGGED, MINE = ".", "F", "*"


def neighbors(r, c):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                yield nr, nc


def build(rng, safe_r, safe_c):
    """Place mines anywhere except the first-pry cell, then count neighbours."""
    pos = [(r, c) for r in range(ROWS) for c in range(COLS)
           if (r, c) != (safe_r, safe_c)]
    rng.shuffle(pos)
    mines = set(pos[:MINES])
    counts = {}
    for r in range(ROWS):
        for c in range(COLS):
            counts[(r, c)] = sum(1 for nr, nc in neighbors(r, c)
                                 if (nr, nc) in mines)
    return mines, counts


class Game:
    def __init__(self, rng):
        self.rng = rng
        self.pry0 = None            # first-pry cell (guaranteed safe)
        self.opened = set()
        self.flags = set()
        self.mines = set()
        self.counts = {}
        self.cursor = [ROWS // 2, COLS // 2]
        self.dead = None            # the cell that blew up (for the loss screen)
        self.won = False
        self.actions = 0

    def flood(self, r, c):
        """Open a cell; zero-cells open their whole empty region for free."""
        self.opened.add((r, c))
        if self.counts.get((r, c)) == 0:
            stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                for nr, nc in neighbors(cr, cc):
                    if (nr, nc) in self.opened or (nr, nc) in self.flags:
                        continue
                    if (nr, nc) in self.mines:
                        continue
                    self.opened.add((nr, nc))
                    if self.counts.get((nr, nc)) == 0:
                        stack.append((nr, nc))

    def pry(self, r, c):
        if self.pry0 is None:
            self.pry0 = (r, c)
            self.mines, self.counts = build(self.rng, r, c)
        if (r, c) in self.flags or (r, c) in self.opened:
            return "close"
        self.actions += 1
        if (r, c) in self.mines:
            self.dead = (r, c)
            self.opened.add((r, c))
            return "boom"
        self.flood(r, c)
        if len(self.opened) == ROWS * COLS - MINES:
            self.won = True
        return "ok"

    def chord(self, r, c):
        if (r, c) not in self.opened or self.counts.get((r, c), 0) == 0:
            return
        flagged = sum(1 for nr, nc in neighbors(r, c) if (nr, nc) in self.flags)
        if flagged != self.counts[(r, c)]:
            return
        results = [self.pry(nr, nc) for nr, nc in neighbors(r, c)
                   if (nr, nc) not in self.opened and (nr, nc) not in self.flags]
        if "boom" in results:
            self.dead = self.dead or next((nr, nc) for nr, nc in neighbors(r, c)
                                          if (nr, nc) in self.mines
                                          and (nr, nc) not in self.flags)

    def render(self):
        out = ["     " + " ".join("{:>2}".format(c + 1) for c in range(COLS))]
        for r in range(ROWS):
            row = ["{:>2}  ".format(r + 1)]
            for c in range(COLS):
                here = (r, c) == tuple(self.cursor)
                if (r, c) == self.dead:
                    sym, art = "*", "["
                elif (r, c) in self.opened:
                    n = self.counts.get((r, c), 0)
                    sym, art = (" " if n == 0 else str(n)), " "
                elif (r, c) in self.flags:
                    sym, art = "F", "["
                else:
                    sym, art = ".", " "
                token = "{} {} {}".format(art, sym, "]") if art == "[" else " {} ".format(sym)
                row.append("(" + sym + ")" if here else token)
            out.append(" ".join(row))
        return "\n".join(out)


def title_banner():
    return ("=" * 46 + "\n" +
            "BRINE GRID :: THE SUNKEN FIELD\n" +
            "=" * 46)


def main():
    rng = random.Random()
    game = Game(rng)
    flags_left = MINES
    print(title_banner())
    print("Clear %dx%d around the Ironclaw Dawn. %d rusted charges hide in the silt." % (ROWS, COLS, MINES))
    print("wasd/arrows move  |  space/enter pry open  |  f flag  |  c chord  |  q surface")
    print()

    while True:
        print(game.render())
        print("   flags left: %-3d   opened: %-3d/%d   " % (
            flags_left, len(game.opened), ROWS * COLS - MINES), end="")
        if game.won:
            break
        print()
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nYou surface; the field stays sown.")
            sys.exit(0)
        if not cmd:
            continue
        word = cmd.split()[0]
        if word in ("q", "quit", "leave"):
            print("You kick for the surface. The field stays sown.")
            sys.exit(0)
        if word in ("w", "k", "up"):
            game.cursor[0] = max(0, game.cursor[0] - 1)
        elif word in ("s", "j", "down"):
            game.cursor[0] = min(ROWS - 1, game.cursor[0] + 1)
        elif word in ("a", "h", "left"):
            game.cursor[1] = max(0, game.cursor[1] - 1)
        elif word in ("d", "l", "right"):
            game.cursor[1] = min(COLS - 1, game.cursor[1] + 1)
        elif word in ("space", "enter", "open", "pry", "e", ""):
            res = game.pry(*game.cursor)
            if res == "boom":
                break
        elif word == "f":
            r, c = game.cursor
            if (r, c) in game.opened:
                print("   A cleared cell can't carry a flag. Use c to chord.")
                continue
            if (r, c) in game.flags:
                game.flags.discard((r, c))
                flags_left += 1
            else:
                game.flags.add((r, c))
                flags_left -= 1
        elif word == "c":
            game.chord(*game.cursor)
            if game.won:
                break
            if game.dead:
                break
        else:
            print("   Try: wasd/arrows to move, space to pry, f flag, c chord, q to surface.")

    print()
    if game.dead:
        r, c = game.dead
        print("The starboard charge at (%d,%d) roars and the sea goes white." % (r + 1, c + 1))
        print("You wake on a beach in the shallows, ears ringing, a cold current")
        print("hungering for your last breath of air.")
    elif game.won:
        print("The last safe cell breaks open to clear water. The field is done.")
        print("Salvage hooks bite into the Ironclaw Dawn; dawn glints off the kelp.")
        print()
        print("   ~~~~~ ~ ~~~")
        print("   ~ ~~~~ ~~ ~     THE SUNKEN FIELD IS YOURS")
        print("   ~~~~~ ~ ~~~")
        print()
        print("You cleared it in %d pries." % game.actions)
    else:
        print("You surface quietly. The field endures another tide.")
    sys.exit(0)


if __name__ == "__main__":
    main()
