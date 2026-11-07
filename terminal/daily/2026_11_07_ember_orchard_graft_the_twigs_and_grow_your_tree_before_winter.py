# Daily Terminal Drop
# Date: 2026-11-07
# Title: Ember Orchard: Graft the Twigs and Grow Your Tree Before Winter

# Daily Terminal Drop
# Date: 2026-11-07
# Title: Ember Orchard: Graft the Twigs and Grow Your Tree Before Winter

#!/usr/bin/env python3
"""EMBER ORCHARD - graft twigs onto your tree before winter frost!

Late autumn in the orchard. You are the grafter. Each turn the
wind blows in a SCION (a twig) -- graft it onto your tree in the
right SPOT or the frost takes it. Your tree grows ring by ring.

Legend:
  T  your tree (grows taller each ring you complete)
  .  orchard grass

HOW IT WORKS:
  Each round shows a TWIG with 3 notches and a PATTERN.
  Type the missing notch letters (like ab) to graft it.
  Right letters -> tree grows +1 ring, new twig arrives!
  Wrong letters -> the twig cracks, 1 frost point.
  Skip (ENTER) -> twig blows away, 1 frost point.

  3 frost points and winter wins -- the orchard freezes!
  Graft 12 rings and your tree wins autumn!

PATTERN RULE: each twig shows ab?c?d -- ? spots need the
  letters that keep the ladder climbing (a,b,c,d,...)
  Watch the pattern, fill the gaps!

COMMANDS: letters graft   ENTER skip   q quit
"""
import random

FROST_MAX = 3
GOAL = 12


def crack():
    print("\007", end="")


def make_pattern(rng, spots):
    """Build a twig pattern with `spots` missing letters."""
    start = rng.randint(0, 8)
    letters = [chr(ord("a") + start + i) for i in range(spots + 3)]
    show = []
    answers = []
    for i, ch in enumerate(letters):
        if i in (1, 3) or (spots > 2 and i == 4):
            show.append("?")
            answers.append(ch)
        else:
            show.append(ch)
    return "".join(show), "".join(answers)


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.rings = 0
        self.frost = 0
        self.round_no = 0
        self.msg = "autumn wind blows. graft the first twig!"
        self.over = False
        self.won = False
        self.new_twig()

    def new_twig(self):
        spots = 2 if self.rings < 6 else 3
        self.pattern, self.answers = make_pattern(self.rng, spots)
        self.round_no += 1

    def tree(self):
        """Draw the tree with one T per ring."""
        rows = []
        h = max(2, min(8, 2 + self.rings // 2))
        for i in range(h):
            width = 1 + i
            pad = " " * (12 - width)
            rows.append(pad + "T" * (2 * width - 1) if False else pad + "T" * width)
        trunk = " " * 12 + "T"
        rows.append(trunk)
        return rows

    def render(self):
        print()
        print("  EMBER ORCHARD -- late autumn grafting")
        print("  " + "-" * 44)
        for line in self.tree():
            print("  " + line)
        print()
        print("  rings grown: %d/%d    frost: %d/%d    round %d"
              % (self.rings, GOAL, self.frost, FROST_MAX, self.round_no))
        print()
        print("  TWIG:  %s   (fill the ? spots)" % self.pattern)
        print()
        print("  %s" % self.msg)
        print("  letters graft   ENTER skip   q quit")

    def graft(self, guess):
        if guess == self.answers:
            self.rings += 1
            self.msg = "grafted! tree rings: %d" % self.rings
            if self.rings >= GOAL:
                self.over = True
                self.won = True
            else:
                self.new_twig()
        else:
            self.frost += 1
            crack()
            self.msg = "crack! frost nips the twig (%d/%d)" % (self.frost, FROST_MAX)
            if self.frost >= FROST_MAX:
                self.over = True
            else:
                self.new_twig()


def main():
    rng_seed = None
    g = Game(rng_seed)
    print("\033[2J\033[H", end="")
    while not g.over:
        g.render()
        try:
            raw = input("\n  graft > ").strip().lower()
        except EOFError:
            break
        if raw == "q":
            print("\n  Autumn ends early. Tree rings: %d" % g.rings)
            return
        if raw == "":
            g.frost += 1
            g.msg = "twig blown away! frost %d/%d" % (g.frost, FROST_MAX)
            if g.frost >= FROST_MAX:
                g.over = True
            else:
                g.new_twig()
        else:
            g.graft(raw)
        print("\033[2J\033[H", end="")
    if g.won:
        print("\n  WINTER WAITS. Your tree stands %d rings tall!" % g.rings)
        for line in g.tree():
            print("  " + line)
        print("\n  AUTUMN HARVEST WIN!")
    else:
        print("\n  FROST TAKES THE ORCHARD. Tree rings: %d" % g.rings)
        for line in g.tree():
            print("  " + line)


if __name__ == "__main__":
    main()
