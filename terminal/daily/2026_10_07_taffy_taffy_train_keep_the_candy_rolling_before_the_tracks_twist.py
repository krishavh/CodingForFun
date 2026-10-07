# Daily Terminal Drop
# Date: 2026-10-07
# Title: Taffy Taffy Train: Keep the candy rolling before the tracks twist

# Daily Terminal Drop
# Date: 2026-10-07
# Title: Taffy Taffy Train: Keep the candy rolling before the tracks twist

#!/usr/bin/env python3
"""TAFFY TAFFY TRAIN - an original terminal game of candy and cargo.

You drive the old taffy train through Sugar Gulch. Each station orders
taffy by FLAVOR and by HOW WELL WRAPPED it is. Your candy cars hold
one stack: last car loaded, FIRST car unloaded -- and the wrapper
ratings twist as you roll!

CANDY (flavor, wrapper):
  lemon  L   wrapper 1-5 (5 = twistiest)
  grape  G   mint    M
  peach  P   cola    C
  apple  A   berry   B
  mango  N? no -- orange O   (7 flavors, 7 letters: LGMPCAOB)

COMMANDS:
  load <F> <w>   push candy onto the train (flavor letter, wrapper 1-5)
  drop           unload the TOP car at the station (score it!)
  skip           conductor whistles: station passes (next orders twist)
  map            peek at the tracks (free, 1 per station)
  q              park the train (quit)

SCORE a drop: flavor must MATCH an order, wrapper must be EXACTLY
the twist the order asks for. Orders TWIST every 2 stations:
  wrapper +1 each twist (5 wraps back to 1 -- sticky, huh?)

Fill 3 orders per station. Miss a station 3 times and the
Sugar Gulch tracks jam -- GAME OVER. 12 stations to glory!
"""
import random

STATIONS = 12
FLAVORS = "LGMPCAOB"
NAMES = {"L": "lemon", "G": "grape", "M": "mint", "P": "peach",
         "C": "cola", "A": "apple", "O": "orange", "B": "berry"}
ORDERS_PER = 3
TWIST_EVERY = 2


def twist(w):
    return (w % 5) + 1


def new_orders(station):
    """Orders = list of [flavor, wrapper]."""
    base = 1 + (station // TWIST_EVERY) % 5
    out = []
    for _ in range(ORDERS_PER):
        out.append([random.choice(FLAVORS), random.randint(1, 5) if station else base])
    if station == 0:
        for o in out:
            o[1] = base
    return out


def draw(cars, station, score, misses, orders, msg, peek=False):
    print()
    print(f"STATION {min(station + 1, STATIONS)} of {STATIONS}   "
          f"taffy score: {score}   jams: {misses}/3")
    print("  ORDERS:")
    for i, (f, w) in enumerate(orders):
        print(f"    {i + 1}. {NAMES[f]:6} twist {w}")
    print("  TRAIN (top = first out): "
          + (" ".join(f"{c[0]}{c[1]}" for c in reversed(cars)) or "(empty)"))
    if peek:
        print("  next twist: station {}".format(
            ((station // TWIST_EVERY) + 1) * TWIST_EVERY + 1))
    if msg:
        print("  " + msg)
    print("load F w / drop / skip / map / q >")


def main():
    random.seed()
    cars = []          # list of [flavor, wrapper]; index 0 = bottom
    station = 0
    score = 0
    misses = 0
    msg = "All aboard the taffy train!"
    peeked = False
    orders = new_orders(0)
    while station < STATIONS and misses < 3:
        draw(cars, station, score, misses, orders, msg, peeked)
        peeked = False
        try:
            line = input("").strip().lower()
        except EOFError:
            print("\n tracks jammed (input gone) -- final score " + str(score))
            return
        msg = ""
        if line.startswith("q"):
            print("\n parked at station " + str(station + 1) +
                  " -- final taffy score " + str(score))
            return
        if line == "map":
            peeked = True
            msg = "You check the tracks. Twisty!"
            continue
        if line.startswith("load"):
            parts = line.split()
            if len(parts) != 3 or parts[1].upper() not in NAMES or not parts[2].isdigit():
                msg = "load <flavor letter> <wrapper 1-5>"
                continue
            f = parts[1].upper()
            w = int(parts[2])
            if not 1 <= w <= 5:
                msg = "wrapper must be 1-5"
                continue
            if len(cars) >= 8:
                msg = "train is full! drop some taffy."
                continue
            cars.append([f, w])
            msg = NAMES[f] + " loaded, twist " + str(w)
            continue
        if line == "drop":
            if not cars:
                msg = "no taffy on the train!"
                continue
            candy = cars.pop()
            hit = None
            for i, (f, w) in enumerate(orders):
                if f == candy[0] and w == candy[1]:
                    hit = i
                    break
            if hit is None:
                msg = (NAMES[candy[0]] + " twist " + str(candy[1]) +
                       " -- no order fits! -1 sticky")
                score -= 1
                continue
            orders.pop(hit)
            pts = 10 + candy[1] * 2
            score += pts
            msg = ("Order filled! " + NAMES[candy[0]] + " twist " +
                   str(candy[1]) + " +{}".format(pts))
            if not orders:
                station += 1
                if station < STATIONS:
                    orders = new_orders(station)
                    msg += "  -- station clear! whistle WHOO WHOO"
                else:
                    msg += "  -- LAST STATION! Sugar Gulch cheers!"
            continue
        if line == "skip":
            misses += 1
            station += 1
            if station < STATIONS:
                orders = new_orders(station)
                msg = "Station skipped! " + str(misses) + "/3 jams"
            else:
                msg = "Station skipped! End of the line."
            continue
        msg = "load F w / drop / skip / map / q"
    if misses >= 3:
        print("\nTRACKS JAM! three stations missed -- final score " + str(score))
    else:
        print("\nTRIP COMPLETE! 12 stations of taffy -- final score " + str(score))
    print("candy left on train: " + str(len(cars)))


if __name__ == "__main__":
    main()
