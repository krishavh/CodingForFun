# Daily Terminal Drop
# Date: 2026-10-28
# Title: Ember Cellar: Fan the coals and roast the marshmallows before the pit goes cold

# Daily Terminal Drop
# Date: 2026-10-28
# Title: Ember Cellar: Fan the coals and roast the marshmallows before the pit goes cold

#!/usr/bin/env python3
"""EMBER CELLAR - fan the coals, roast every marshmallow before the pit dies!

Down in the ember cellar a fire pit glows faint. MARSHMALLOWS
on long sticks hover high -- they FALL each turn. Only flames
hotter than 4 can roast them (heat = tallest flame)! FAN the
coals to raise the heat -- every fan burns FUEL. Gusts steal!

Legend:
  .  cellar floor / fire pit (bottom row)
  1-9  flames (height -- tallest is your HEAT)
  o  marshmallow (falls 1 row per turn, 2 on gust!)
  +  fuel chunk (grab it: +4 fuel)
  @  you (move along the pit, catch fuel, roast 'mallows)

HOW IT WORKS:
  Each turn: e FAN (+2 heat, costs 1 fuel) or '.' rest.
  Then flames FLICKER: tallest flame may grow/shrink 1.
  A fresh marshmallow spawns and ALL fall 1 row (2 on gust)!
  When one lands on the bottom: if YOU stand under it and
  heat 5+ -- ROASTED! 25 points. If you miss -- soggy splat,
  lose a stick! Standing on a fuel chunk grabs it.

WIND GUST: every 9 turns -- flames shrink 2 and marshmallows
  fall 2 rows! Grab fuel BEFORE the pit breathes cold.

GOAL: roast 8 marshmallows before sticks snap (3 splats)
  or 50 turns burn out!
COMMANDS: a/d move   e fan   . rest   q quit
"""
import random
import subprocess

try:
    import shutil
    def term_cols(default=80):
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return default
except Exception:
    def term_cols(default=80):
        return default


W = 34
H = 14
PIT = H - 1
GOAL = 8
TURNS = 50
START_FUEL = 6
STICKS = 3


def clear():
    subprocess.run(["clear"], shell=False)


class Game:
    def __init__(self):
        self.cols = W
        self.turns = 0
        self.score = 0
        self.px = W // 2
        self.fuel = START_FUEL
        self.misses = 0
        self.roasted = 0
        self.msg = "Fan the coals! Roast needs heat 5+ (tallest flame)."
        self.flames = {}
        for x in range(W):
            if random.random() < 0.4:
                self.flames[x] = random.randint(1, 3)
        if not self.flames:
            self.flames[W // 2] = 2
        self.marsh = []      # [x, y]
        self.fuel_drops = []  # [x, y]

    # ----- helpers -----
    def heat(self):
        return max(self.flames.values()) if self.flames else 0

    def spawn(self):
        self.marsh.append([random.randrange(W), 1])
        if random.random() < 0.4:
            self.fuel_drops.append([random.randrange(W), 1])

    def gust(self):
        for x in list(self.flames):
            self.flames[x] = max(0, self.flames[x] - 2)
            if self.flames[x] == 0:
                del self.flames[x]
        return "WIND GUST! Flames shrink -- marshmallows dive!"

    def flicker(self):
        for x in list(self.flames):
            r = random.random()
            if r < 0.45:
                self.flames[x] = min(9, self.flames[x] + 1)
            elif r < 0.8:
                self.flames[x] -= 1
            if self.flames[x] <= 0:
                del self.flames[x]
        for x in range(W):
            if x not in self.flames and random.random() < 0.06:
                self.flames[x] = 1
        if not self.flames:
            self.flames[random.randrange(W)] = 1

    def turn(self, cmd):
        events = []
        # 1. player action
        if cmd == "a" and self.px > 0:
            self.px -= 1
        elif cmd == "d" and self.px < W - 1:
            self.px += 1
        elif cmd == "e":
            if self.fuel > 0:
                self.fuel -= 1
                for x in list(self.flames):
                    self.flames[x] = min(9, self.flames[x] + 1)
                events.append("FAN! The coals breathe +1 taller.")
            else:
                events.append("No fuel! Find + chunks.")
        elif cmd == ".":
            events.append("You rest. Coals settle.")
        # 2. coals flicker
        self.flicker()
        # 3. spawn new marshmallow
        self.spawn()
        # 4. gust?
        self.turns += 1
        if self.turns % 9 == 0:
            events.append(self.gust())
        fall = 2 if self.turns % 9 == 0 else 1
        # 5. move drops + marshmallows down
        for m in self.marsh:
            m[1] += fall
        for f in self.fuel_drops:
            f[1] += fall
        # 6. land things
        landed = [m for m in self.marsh if m[1] >= PIT]
        self.marsh = [m for m in self.marsh if m[1] < PIT]
        for m in landed:
            if m[0] == self.px and self.heat() >= 5:
                self.score += 25
                self.roasted += 1
                events.append("ROASTED! Golden brown! +25 (%d/%d)" % (self.roasted, GOAL))
            else:
                self.misses += 1
                sticks_left = STICKS - self.misses
                if m[0] == self.px:
                    events.append("Soggy! Heat %d too low. Sticks left: %d" % (self.heat(), sticks_left))
                else:
                    events.append("Missed it! Sticks left: %d" % sticks_left)
        landed_f = [f for f in self.fuel_drops if f[1] >= PIT]
        self.fuel_drops = [f for f in self.fuel_drops if f[1] < PIT]
        for f in landed_f:
            if f[0] == self.px:
                self.fuel += 4
                events.append("Grabbed fuel! +4")
        # flames on pit burn the player's feet a little: pop old marshmallows off top? no.
        return events

    def over(self):
        return self.roasted >= GOAL or self.misses >= STICKS or self.turns >= TURNS

    def draw(self):
        rows = []
        for y in range(H):
            line = ["."] * W
            if y == PIT:
                line = ["="] * W
            for x, h in self.flames.items():
                if y >= PIT - h:
                    d = str(h)
                    line[x] = d
            for x, y in self.marsh:
                if 0 <= y < H:
                    line[x] = "o"
            for x, y in self.fuel_drops:
                if 0 <= y < H:
                    line[x] = "+"
            if y == PIT:
                pass  # player drawn after flames (stands on pit)
            rows.append("".join(line))
        # overlay player on bottom
        bottom = list(rows[PIT])
        bottom[self.px] = "@"
        rows[PIT] = "".join(bottom)
        return rows

    def status(self):
        return ("Turn %2d/%d  Heat:%d  Fuel:%d  Score:%d (%d/%d roasted)  Sticks:%d" %
                (self.turns, TURNS, self.heat(), self.fuel,
                 self.score, self.roasted, GOAL, STICKS - self.misses))


def main():
    random.seed()
    g = Game()
    clear()
    print("EMBER CELLAR -- fan the coals, roast the marshmallows!")
    print("Roast needs HEAT 5+ (tallest flame) + stand under the 'o'!")
    print("Keys: a/d move   e fan (+1 all flames, -1 fuel)   . rest   q quit")
    input("Press Enter to fire up the pit... ")
    while not g.over():
        g.msg = ""
        clear()
        rows = g.draw()
        print("+" + "-" * W + "+")
        for i, r in enumerate(rows):
            print("|" + r + "|" + (str(i + 1) if (i + 1) % 5 == 0 else ""))
        print("+" + "-" * W + "+")
        print(g.status())
        if g.msg:
            print(g.msg)
        print(">> marshmallows fall next turn! (gust every 9)")
        try:
            cmd = input("cmd [a/d/e/./q]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if cmd == "q":
            print("Fire banked. Final: %d pts, %d roasted." % (g.score, g.roasted))
            return
        events = g.turn(cmd)
        for ev in events:
            print("* " + ev)
        clear()
        rows = g.draw()
        print("+" + "-" * W + "+")
        for r in rows:
            print("|" + r + "|")
        print("+" + "-" * W + "+")
        print(g.status())
        # small pause so events are readable
        try:
            input("-- Enter for next turn (q then Enter quits) --")
        except (EOFError, KeyboardInterrupt):
            print()
            return
    # game over
    clear()
    print("+" + "-" * W + "+")
    for r in g.draw():
        print("|" + r + "|")
    print("+" + "-" * W + "+")
    print("GAME OVER -- %s" % (
        "PIT MASTER! All %d marshmallows roasted!" % GOAL if g.roasted >= GOAL else
        "Sticks snapped! Soggy disaster." if g.misses >= STICKS else
        "Turns burned out. Pit cold."))
    print("Final score: %d pts, %d/%d roasted, %d turns" % (g.score, g.roasted, GOAL, g.turns))


if __name__ == "__main__":
    main()
