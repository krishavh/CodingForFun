# Daily Terminal Drop
# Date: 2026-08-19
# Title: The Last Alchemist: Cinnabar's Rose

#!/usr/bin/env python3
"""
THE LAST ALCHEMIST: CINNABAR'S ROSE
===================================
The old workshop has run dry. You are the last alchemist left awake,
and the Rose of Cinnabar must be distilled before the clockwork dawn
locks the ovens for a hundred years.

Five base regents sit in the well. The well is bottomless — you may draw
any base regent freely, one per action. Four recipes are etched into the
workbench. Your cauldron holds only four reagents at a time — plan your
steps, make room, and burn a little luck. Distil Cinnabar and the rose
blooms. Waste your moves and the workbench goes cold.

Commands while working:
  combine <recipe>  use a recipe (takes its two ingredients into the cauldron)
  draw <name>       take a base regent from the well into the cauldron
  toss <name>       throw a reagent from the cauldron back into the well
  inventory     re-list your cauldron and recipes
  quit          abandon the workbench
"""
import random
import sys

CAPACITY = 4          # reagents the cauldron can hold at once
START_REAGENTS = 3    # bases you begin with
BUDGET = 15           # total actions before the dawn locks the ovens

# name -> single-letter tag used for compact display
BASES = {
    "saltpeter": "S",
    "sootshale": "B",
    "dewmoss": "D",
    "rootblood": "R",
    "emberstone": "E",
}

# recipe: product name -> (ingredient A, ingredient B)
RECIPES = {
    "quicksilver": ("dewmoss", "rootblood"),
    "brimstone": ("emberstone", "sootshale"),
    "mercurial": ("quicksilver", "saltpeter"),
    "cinnabar": ("mercurial", "brimstone"),
}

TARGET = "cinnabar"

FLAVOR = {
    "saltpeter": ("pale crystalline grit", "S"),
    "sootshale": ("soft black flake", "B"),
    "dewmoss": ("dew-glistening moss", "D"),
    "rootblood": ("dark amber root", "R"),
    "emberstone": ("still-warm stone", "E"),
    "quicksilver": ("a trembling silver bead", "Q"),
    "brimstone": ("sulphur-yellow clods", "F"),
    "mercurial": ("a coiled metallic spirit", "M"),
    "cinnabar": ("the blazing rose-gold heart", "C"),
}


def tag(name):
    return FLAVOR[name][1]


def describe(name):
    return "{:12s} [{}] — {}".format(name, tag(name), FLAVOR[name][0])


def show_cauldron(contents):
    if not contents:
        return "  (the cauldron is empty)"
    return "  ".join("[{} {}]".format(tag(c), c[0].upper()) for c in contents)


def main():
    rng = random.Random()
    rack = list(BASES.keys())
    rng.shuffle(rack)
    cauldron = rack[:START_REAGENTS]     # start with a random spread of bases
    actions_left = BUDGET

    def full():
        return len(cauldron) >= CAPACITY

    print("=" * 60)
    print("THE LAST ALCHEMIST :: CINNABAR'S ROSE")
    print("=" * 60)
    print("Distil Cinnabar, the blazing rose-gold heart, before the dawn")
    print("locks the ovens. The cauldron holds only %d reagents at a time." % CAPACITY)
    print("You have %d actions. Recipes never change — they are already known." % BUDGET)
    print()
    print("The four recipes etched on the workbench:")
    for name, (a, b) in RECIPES.items():
        print("  [{}] {} = {} + {}".format(name, name, a, b))
    print()
    print("The rack of base regents (draw freely, one per action):")
    for name in BASES:
        print("  " + describe(name))
    print()

    while actions_left > 0:
        print("-" * 60)
        print("ACTIONS LEFT: {}   CAULDRON:".format(actions_left))
        print("  " + show_cauldron(cauldron))
        if TARGET in cauldron:
            break
        for name in RECIPES:
            a, b = RECIPES[name]
            have = "x" if (a in cauldron and b in cauldron) else " "
            print("  [{}] {} = {} + {}".format(have, name, a, b))
        try:
            cmd = input("> ").strip().split()
        except (EOFError, KeyboardInterrupt):
            print("\nThe workbench goes cold. The rose sleeps another age.")
            sys.exit(0)
        if not cmd:
            continue
        word = cmd[0].lower()
        if word in ("inventory", "inv", "i"):
            pass
        elif word == "quit":
            print("You set down the ladle. The ovens cool to grey.")
            sys.exit(0)
        elif word == "draw":
            if full():
                print("  The cauldron is full — toss something first.")
                continue
            if len(cmd) < 2 or cmd[1].lower() not in BASES:
                print("  Draw which regent? " + ", ".join(BASES))
                continue
            b = cmd[1].lower()
            cauldron.append(b)
            actions_left -= 1
            print("  You add {} — {}".format(b, FLAVOR[b][0]))
        elif word == "toss":
            if len(cmd) < 2:
                print("  Toss which reagent?")
                continue
            t = cmd[1].lower()
            if t not in cauldron:
                print("  You don't hold {}.".format(t))
                continue
            cauldron.remove(t)
            actions_left -= 1
            print("  You cast {} back into the well.".format(t))
        elif word == "combine":
            if len(cmd) < 2:
                print("  Combine which recipe? " + ", ".join(RECIPES))
                continue
            name = cmd[1].lower()
            if name not in RECIPES:
                print("  No recipe named '{}'.".format(name))
                continue
            a, b = RECIPES[name]
            if a not in cauldron or b not in cauldron:
                print("  You need {} and {} for {} — you're missing one.".format(a, b, name))
                continue
            if a == b and cauldron.count(a) < 2:
                print("  {} requires two copies of {}.".format(name, a))
                continue
            cauldron.remove(a)
            cauldron.remove(b)
            cauldron.append(name)
            actions_left -= 1
            print("  {} and {} entwine into {}!".format(a, b, name))
            if name == TARGET:
                break
        else:
            print("  Unknown command. Try: combine <name> | draw <name> | toss <name> | quit")
        # extra blank for readability
        print()

    print("─" * 60)
    if TARGET in cauldron:
        print()
        print("CINNABAR — " + FLAVOR["cinnabar"][0] + " — blooms in your ladle.")
        print("The rose catches the first grey light; the ovens hum awake.")
        print("You have earned the dawn, Last Alchemist.")
        print()
        print("   * * *")
        print("  *     *")
        print("   * * *      CINNABAR'S ROSE BLOOMS")
        print("  *     *")
        print("   * * *")
        print()
        sys.exit(0)
    else:
        print()
        print("The workbench goes cold as the dawn clocks turn.")
        print("Where the rose should be, only ash and a question remain.")
        sys.exit(0)


if __name__ == "__main__":
    main()
