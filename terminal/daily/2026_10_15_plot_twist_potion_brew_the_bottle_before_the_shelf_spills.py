# Daily Terminal Drop
# Date: 2026-10-15
# Title: Plot Twist Potion: Brew the bottle before the shelf spills

#!/usr/bin/env python3
"""PLOT TWIST POTION - an original terminal game of brews and blunders.

Old Mizzi's potion shop. Customers order potions, but your SHELF
holds only 5 bottles -- and every new brew SHOVES the oldest out
(ruining it!). Each customer wants ONE bottle by SHELF SPOT:
the bottle aged there the LONGEST (left) or SHORTEST (right) time.

Legend:
  .  empty shelf spot
  A-Z brew bubbles (letters show AGE: A = fresh, later = older)

COMMANDS:
  brew <X>    brew potion letter X (A-Z) -- shoved onto the RIGHT,
              if 5 bottles: LEFTMOST spoils (-5 points, splat!)
  sell <l|r> <n>  sell from spot by age: l = longest-kept (left),
                  r = shortest-kept (right), n = spot 1-5 (1=left)
  pass        next customer, no sale (-2 patience)
  q           close shop (quit)

SCORE a sale: potion letter must MATCH the order +50, wrong -10.
Patience starts 50, drains 1 per customer. 12 customers win!
Serve 3 to a single customer? BONUS cauldron +30!
"""
import random
import shutil
import subprocess

SHELF = 5
CUSTOMERS = 12
START_PATIENCE = 50

FLAVORS = "ABCDEFGH"


def clear():
    subprocess.run(["clear"], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def draw(shelf, pts, patience, cust, orders, msg):
    clear()
    cols = min(max(term_cols(), 40), 100)
    print("PLOT TWIST POTION".center(cols))
    print(("points:%d  patience:%d  customer:%d/%d" %
           (pts, patience, cust, CUSTOMERS)).center(cols))
    print()
    print("  SHELF: [" + " ".join(shelf) + "]")
    print("  spots:  " + " ".join(str(i + 1) for i in range(SHELF)) + "   (1=oldest)")
    print()
    print("  WANTED: " + " & ".join(orders) if orders else "  WANTED: (none)")
    print()
    if msg:
        print("  >> " + msg)
    print()
    print("  brew <X> | sell <l|r> <n> | pass | q")


def new_orders():
    """1-3 potions this customer craves."""
    n = random.choice([1, 1, 2, 2, 3])
    return [random.choice(FLAVORS) for _ in range(n)]


def main():
    random.seed()
    shelf = ["."] * SHELF
    pts = 0
    patience = START_PATIENCE
    orders = new_orders()
    served_this = 0
    msg = "Welcome! Brew potions, fill orders!"
    cust = 1
    while cust <= CUSTOMERS and patience > 0:
        draw(shelf, pts, patience, cust, orders, msg)
        raw = input("> ").strip().lower()
        msg = ""
        if raw == "q":
            print("Shop closed! Final points: %d" % pts)
            return
        elif raw.startswith("brew "):
            p = raw[5:].strip().upper()
            if len(p) != 1 or p not in FLAVORS:
                msg = "Brew what? Letters %s." % FLAVORS
                continue
            if "." in shelf:
                shelf[shelf.index(".")] = p
                msg = "Bubbling %c onto the shelf!" % p
            else:
                spoiled = shelf[0]
                shelf = shelf[1:] + [p]
                pts -= 5
                msg = "Shelf full! %c spoiled down the drain! (-5)" % spoiled
        elif raw.startswith("sell "):
            parts = raw.split()
            if len(parts) != 3 or parts[1] not in ("l", "r") or \
                    not parts[2].isdigit() or not (1 <= int(parts[2]) <= SHELF):
                msg = "Sell how? sell <l|r> <1-5>"
                continue
            n = int(parts[2])
            if parts[1] == "l":
                spot = n - 1  # left = oldest
            else:
                filled = [i for i, c in enumerate(shelf) if c != "."]
                if not filled:
                    msg = "Shelf is empty!"
                    continue
                # right = youngest FILLED spot (count from right of filled)
                spot = filled[-n] if n <= len(filled) else filled[0]
            if shelf[spot] == ".":
                msg = "Spot %d is empty!" % (spot + 1)
                continue
            p = shelf[spot]
            shelf[spot] = "."
            if p in orders:
                orders.remove(p)
                pts += 50
                served_this += 1
                msg = "Sold %c! +50 (%d this customer)" % (p, served_this)
                if not orders:
                    pts += 30
                    msg += " ALL DONE! +30 bonus!"
                    cust += 1
                    served_this = 0
                    orders = new_orders()
                    patience -= 1
            else:
                pts -= 10
                msg = "Wrong potion! -10"
        elif raw == "pass":
            pts -= 2
            patience -= 2
            cust += 1
            served_this = 0
            orders = new_orders()
            msg = "Passed! -2 points, -2 patience"
        else:
            msg = "?  brew <X> | sell <l|r> <n> | pass | q"
        if patience <= 0:
            break
    draw(shelf, pts, max(patience, 0), min(cust, CUSTOMERS), orders, "")
    print()
    if pts >= 300:
        print("MASTER BREWER! %d points!" % pts)
    elif pts >= 150:
        print("Solid shop keep! %d points." % pts)
    else:
        print("Shop shuts early... %d points." % pts)


if __name__ == "__main__":
    main()
