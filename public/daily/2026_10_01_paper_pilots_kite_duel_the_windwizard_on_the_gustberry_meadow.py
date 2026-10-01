# Daily Terminal Drop
# Date: 2026-10-01
# Title: Paper Pilots: Kite-duel the Windwizard on the gustberry meadow

#!/usr/bin/env python3
"""PAPER PILOTS - an original terminal battle-kite dogfight game.

The great kite festival of Copperfield Meadow. You fly a paper kite,
and the windwizard has challenged every kiteling to a DUEL IN THE SKY.

Two kites: YOU (yellow) and the WINDWIZARD (purple). The field is 40
spools of string wide and 12 clouds high. Wind blows across the meadow:
  >  tailwind pushes east        <  headwind pushes west
  ^  updraft lifts north (up)    v  downdraft sinks south (down)
  *  gustberry - land on it and the wind bursts you 3 steps!

Each TURN both kites move with the wind, THEN you pick a move:
  n/s/e/w  steer 1 step that way (costs 1 stitch)
  t        TANGLE: shoot string at the nearest kite in a straight
           line (row or column). Hits cost the foe 2 stitches and
           snarl them (they skip their next steer).
  x       X-CUT: dashed cloud-to-cloud dash 2 steps! (costs 2 stitches,
           damages 3 if you crash into the foe!)
  c       cast: read the clouds (show wind again, free)
  q       quit the meadow

Stitches are your string. Start with 10. When a kite has 0 stitches,
it falls into the clover. LAST KITE FLYING wins the festival!

Winds blow EVERY turn, so plan your drift -- the meadow edge wraps
around (fly east off the edge, appear west!).
"""
import os
import random

import sys

if os.name == "nt":
    import msvcrt
else:
    import termios
    import tty

W, H = 40, 12
WIN_STITCHES = 0  # not used, fall = 0 stitches


class Kite:
    def __init__(self, x, y, ch, name):
        self.x = x
        self.y = y
        self.ch = ch
        self.name = name
        self.stitches = 10
        self.snarled = 0

    def alive(self):
        return self.stitches > 0


WINDS = {
    ">": (1, 0),
    "<": (-1, 0),
    "^": (0, -1),
    "v": (0, 1),
    ".": (0, 0),
}


def make_field():
    """Scatter winds and gustberries."""
    field = {}
    for y in range(H):
        for x in range(W):
            r = random.random()
            if r < 0.30:
                c = ">"
            elif r < 0.50:
                c = "<"
            elif r < 0.65:
                c = "^"
            elif r < 0.80:
                c = "v"
            else:
                c = "."
            field[(x, y)] = c
    # a few gustberries
    berries = random.sample(list(field), 6)
    for b in berries:
        field[b] = "*"
    return field


def wrap(p):
    return (p[0] % W, p[1] % H)


def wind_step(kite, field):
    dx, dy = WINDS[field[(kite.x, kite.y)]]
    kite.x = (kite.x + dx) % W
    kite.y = (kite.y + dy) % H


def draw(field, you, foe):
    print("+" + "-" * W + "+")
    grid = {}
    for (x, y), c in field.items():
        grid[(x, y)] = c
    # kites drawn over wind
    grid[(you.x, you.y)] = "Y"
    grid[(foe.x, foe.y)] = "W"
    for y in range(H):
        row = "".join(grid[(x, y)] for x in range(W))
        print("|" + row + "|")
    print("+" + "-" * W + "+")
    print(f"  YOU(y) stitches={you.stitches} snarled={you.snarled}   "
          f"WINDWIZARD(w) stitches={foe.stitches} snarled={foe.snarled}")


def line_of_sight(a, b):
    return a.x == b.x or a.y == b.y


def nearest_foe_dir(a, b):
    if a.x == b.x:
        return "n" if b.y < a.y else "s"
    return "w" if b.x < a.x else "e"


def tangle(shooter, target, name):
    if not line_of_sight(shooter, target):
        print(f"  {name}: no kite in a straight line. String flutters.")
        return False
    dist = abs(shooter.x - target.x) + abs(shooter.y - target.y)
    target.stitches -= 2
    target.snarled = 1
    print(f"  {name} TANGLES the {target.name}! (-2 stitches, snarled)")
    print(f"    string stretches {dist} spools across the sky!")
    return True


def xcut(kite, foe, dx, dy, name):
    cost = 2
    if kite.stitches <= cost:
        print(f"  {name}: not enough stitches to X-CUT!")
        return
    kite.stitches -= cost
    for _ in range(2):
        kite.x = (kite.x + dx) % W
        kite.y = (kite.y + dy) % H
    print(f"  {name} X-CUTS through the clouds!")
    if kite.x == foe.x and kite.y == foe.y:
        foe.stitches -= 3
        print(f"  CRASH! The {foe.name} is clipped! (-3 stitches)")
    gust = gust_check(kite, name)
    if gust:
        pass


def gust_check(kite, name):
    # handled by field check after move in main loop
    return False


BERRY_MIN = 1
BERRY_MAX = 3


def berry_burst(kite, name):
    jump = random.randint(BERRY_MIN, BERRY_MAX)
    dirs = [(1, 0), (-1, 0), (0, -1), (0, 1)]
    dx, dy = random.choice(dirs)
    kite.x = (kite.x + dx * jump) % W
    kite.y = (kite.y + dy * jump) % H
    print(f"  {name} bursts a gustberry! Wind hurls them {jump} steps!")


def steer(kite, d, name):
    dx, dy = {"n": (0, -1), "s": (0, 1),
              "w": (-1, 0), "e": (1, 0)}[d]
    kite.x = (kite.x + dx) % W
    kite.y = (kite.y + dy) % H


def gut_dump():
    print(__doc__)


def ai_turn(foe, you, field):
    """The Windwizard picks a move."""
    if foe.snarled > 0:
        foe.snarled -= 1
        print("  The Windwizard's strings snarl. It drifts...")
        return
    if foe.stitches >= 6 and line_of_sight(foe, you) \
            and random.random() < 0.75:
        tangle(foe, you, "Windwizard")
        return
    if foe.stitches >= 8 and random.random() < 0.30:
        dx = (you.x - foe.x)
        dy = (you.y - foe.y)
        dx = (dx > 0) - (dx < 0)
        dy = (dy > 0) - (dy < 0)
        if dx != 0 or dy != 0:
            xcut(foe, you, dx, dy, "Windwizard")
            if foe.x == you.x and foe.y == you.y:
                pass
            return
    dirs = ["n", "s", "w", "e"]
    # drift toward you, chase!
    dx = you.x - foe.x
    dy = you.y - foe.y
    pref = []
    if dy != 0:
        pref.append("n" if dy < 0 else "s")
    if dx != 0:
        pref.append("w" if dx < 0 else "e")
    d = random.choice(pref + dirs)
    steer(foe, d, "foe")
    print(f"  Windwizard steers {d}.")


def main():
    random.seed()
    you = Kite(W // 4, H // 2, "Y", "Yellow Flash")
    foe = Kite(3 * W // 4, H // 2, "W", "Windwizard")
    field = make_field()
    print(__doc__)
    input("  press ENTER to launch your kite... ")
    turn = 0
    while you.alive() and foe.alive():
        turn += 1
        print("\n" * 2)
        print(f"  === TURN {turn} ===")
        # wind moves everyone
        wind_step(you, field)
        wind_step(foe, field)
        if (you.x, you.y) != (foe.x, foe.y):
            pass
        # berries burst under kites
        if field[(you.x, you.y)] == "*":
            berry_burst(you, "Yellow Flash")
        if field[(foe.x, foe.y)] == "*":
            berry_burst(foe, "Windwizard")
        draw(field, you, foe)
        # player move
        moved = False
        while not moved:
            cmd = input("  your move [n/s/e/w/t/x/c/q/?]: ").strip().lower()
            if cmd == "q":
                print("  You reel in your kite. The wizard cackles.")
                return
            if cmd == "?":
                print(__doc__)
                continue
            if cmd == "c":
                draw(field, you, foe)
                continue
            if cmd in ("n", "s", "w", "e"):
                if you.snarled > 0:
                    you.snarled -= 1
                    print("  Your strings snarl! You drift instead.")
                else:
                    steer(you, cmd, "you")
                    print(f"  You steer {cmd}.")
                moved = True
            elif cmd == "t":
                if you.snarled > 0:
                    you.snarled -= 1
                    print("  Snarled! Your tangle fizzles.")
                else:
                    tangle(you, foe, "You")
                moved = True
            elif cmd == "x":
                d = input("   x-cut direction [n/s/e/w]: ").strip().lower()
                if d in ("n", "s", "w", "e"):
                    if you.snarled > 0:
                        you.snarled -= 1
                        print("  Snarled! Your dash fizzles.")
                    else:
                        dx, dy = {"n": (0, -1), "s": (0, 1),
                                  "w": (-1, 0), "e": (1, 0)}[d]
                        xcut(you, foe, dx, dy, "You")
                else:
                    print("  The clouds ignore that. Turn lost.")
                moved = True
            else:
                print("  ? n/s/e/w steer, t tangle, x x-cut, c clouds, q quit")
        # berry check for player after move
        if field[(you.x, you.y)] == "*":
            berry_burst(you, "Yellow Flash")
        if not foe.alive() or not you.alive():
            break
        # wizard moves
        ai_turn(foe, you, field)
        if foe.x == you.x and foe.y == you.y and foe.alive():
            print("  Kites brush wings! Both lose 1 stitch.")
            you.stitches -= 1
            foe.stitches -= 1
    print("\n  === THE FESTIVAL ENDS ===")
    if you.alive() and not foe.alive():
        print("  The Windwizard spirals into the clover!")
        print("  YELLOW FLASH wins the kite festival!")
    elif foe.alive() and not you.alive():
        print("  Your kite falls into the clover. The wizard circles...")
        print("  WINDWIZARD wins. The meadow smells of lavender and loss.")
    else:
        print("  Both kites rest in the clover. A tie of tangled string!")
    print(f"  turns flown: {turn}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n  wind takes the kites. goodbye.")
        sys.exit(0)
