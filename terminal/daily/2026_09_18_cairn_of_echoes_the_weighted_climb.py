# Daily Terminal Drop
# Date: 2026-09-18
# Title: Cairn of Echoes: The Weighted Climb

# Daily Terminal Drop
# Date: 2026-09-18
# Title: Cairn of Echoes: The Weighted Climb

#!/usr/bin/env python3
"""CAIRN OF ECHOES: THE WEIGHTED CLIMB - an original terminal resource-climb.

You are a stack-tender climbing the broken cliff-face of a buried tower,
raising a CAIRN of stones as you go. Every landing holds a STONE, and the
heights you can reach next depend entirely on the WEIGHT you carry.

THE CLIMB
  The mountain is 9 landings tall, but only your first 4 landings are
  revealed - everything above is hidden until you commit. Each landing
  holds one stone, one hazard, or a resting pool.

CARRY RULE
  You may carry at most 3 stones. When you climb while carrying 2 or 3,
  each extra stone costs you an extra STRENGTH (heavy loads burn fuel).

STONES (the interesting part)
  Bulwark    weight 4  - steady, heavy.
  Larkstone  weight 1  - feather-light, but a bird steals it if you rest.
  Ember      weight 2  - warms you: resting on an Ember refunds 1 strength.
  Wisp       weight 2  - whispers the contents of every landing directly
                         above and below you (reveals the fog).
  Ochre      weight 3  - takes 2 strength to pick UP (sticky mineral).
  Herald     weight 5  - too heavy to keep. Drop it at the MOUTH to win.

THE MOUTH (the cave mouth at the top, landing 9)
  Deposit a Herald stone there and the mountain opens - you win.
  Reach it carrying anything else and you may drop that junk and end
  your run with the score you banked.

FALLS
  Land on a loose-scree landing without a Bulwark and you slide down 2
  landings, losing 1 strength and scattering your top stone to the scree.

WIN if you deposit a Herald at the mouth.
LOSE if you run out of strength or you take a fall at the base.
"""
import random
import sys

HEIGHT = 9
CARRY_MAX = 3
STRENGTH = 12

STONES = {
    "Bulwark":   {"w": 4, "desc": "steady; anchors you on scree"},
    "Larkstone": {"w": 1, "desc": "light; a bird steals it when you rest"},
    "Ember":     {"w": 2, "desc": "resting here refunds 1 strength"},
    "Wisp":      {"w": 2, "desc": "whispers what lies above and below"},
    "Ochre":     {"w": 3, "desc": "costs 2 strength to pick up"},
    "Herald":    {"w": 5, "desc": "the key; carry it to the mouth"},
}
SCREE = {"Bulwark", "Herald", "Ochre"}   # landings that need a Bulwark


def build(rng):
    """9 landings: landing 1 (base) through landing 9 (the mouth)."""
    pool = (["Bulwark", "Larkstone", "Ember", "Wisp", "Ochre"] * 2
            + ["Herald", "Herald", "Herald", "scree", "scree",
               "pool", "pool", "pool", "scree", "scree"])
    rng.shuffle(pool)
    landings = [None] * HEIGHT
    landings[0] = "pool"          # base is always safe
    landings[HEIGHT - 1] = "mouth"
    order = [k for k in pool if k not in ("pool", "mouth")]
    rng.shuffle(order)
    it = iter(order)
    for i in range(1, HEIGHT - 1):
        landings[i] = next(it)
    heralds = [i for i, k in enumerate(landings) if k == "Herald"]
    if len(heralds) < 3:
        slots = [i for i in range(1, HEIGHT - 1) if landings[i] != "Herald"]
        rng.shuffle(slots)
        for i in slots[:3 - len(heralds)]:
            landings[i] = "Herald"
    return landings


def show(landings, known, pos, bag, strength, log):
    print()
    print("CAIRN OF ECHOES   strength %d/%d   carrying %d/%d"
          % (strength, STRENGTH, len(bag), CARRY_MAX))
    for i in range(HEIGHT - 1, -1, -1):
        n = i + 1
        here = " <= you" if i == pos else ""
        if n == HEIGHT:
            label = "9  THE MOUTH (deposit a Herald here to win)"
        elif i in known:
            k = landings[i]
            label = "%d  %s" % (n, STONES[k]["desc"] if k in STONES
                                else ("loose scree" if k == "scree"
                                      else "a resting pool"))
        else:
            label = "%d  ?" % n
        print("  " + label + here)
    for line in log[-3:]:
        print("  " + line)
    if bag:
        print("  bag: " + ", ".join("%s(%d)" % (s, STONES[s]["w"])
                                    for s in bag))


def load_weight(bag):
    return sum(STONES[s]["w"] for s in bag)


def main():
    rng = random.Random()
    landings = build(rng)
    pos, strength = 0, STRENGTH
    bag, known, log = [], {0}, []
    print(__doc__ if "-v" in sys.argv else
          "Climb to THE MOUTH with the Herald stone. Commands: u, d, g, "
          "r, drop <stone>, look, help, q")

    while True:
        show(landings, known, pos, bag, strength, log)
        cmd = input("command> ").strip().lower()
        if cmd in ("q", "quit"):
            print("You camp on the cliff. The mountain keeps its echo.")
            return
        if cmd in ("look", "l", ""):
            continue
        if cmd == "help":
            print("u climb | d descend | g take stone | r rest | "
                  "drop <stone> | look | q")
            continue
        if cmd == "u":
            if pos >= HEIGHT - 1:
                print("The sky is the last landing.")
                continue
            cost = 1 + max(0, len(bag) - 1)
            if strength < cost:
                print("Your legs give out - not enough strength to climb "
                      "with this load.")
                return
            strength -= cost
            pos += 1
            known.add(pos)
            k = landings[pos]
            if k == "scree" and "Bulwark" not in bag:
                log.append("SCREE! No Bulwark to anchor you.")
                stolen = bag.pop(0) if bag else None
                if pos >= 2:
                    pos -= 2
                strength -= 1
                log.append("you slide down to landing %d%s."
                           % (pos + 1,
                              ", dropping the %s" % stolen if stolen else ""))
                if strength <= 0:
                    print("The fall and the cold finish you. GAME OVER.")
                    return
            elif k == "pool":
                strength = min(STRENGTH, strength + 1)
                log.append("a cold pool: +1 strength.")
            continue
        if cmd == "d":
            if pos <= 0:
                print("You are at the base.")
                continue
            strength -= 1
            pos -= 1
            log.append("you lower yourself to landing %d." % (pos + 1))
            continue
        if cmd == "g":
            k = landings[pos]
            if k not in STONES:
                print("Nothing here to take.")
                continue
            if k == "Ochre":
                if strength < 3:
                    print("The ochre is stuck fast; you lack the strength "
                          "to pry it loose.")
                    continue
                strength -= 2
            if len(bag) >= CARRY_MAX:
                print("Your arms are full. Drop something first.")
                continue
            bag.append(k)
            landings[pos] = "pool"
            log.append("you pry loose the %s." % k)
            continue
        if cmd == "r":
            gain = 2
            if landings[pos] == "Ember":
                gain += 1
                log.append("the Ember warms you.")
            if "Larkstone" in bag:
                bag.remove("Larkstone")
                log.append("a lark lifts the Larkstone away while you "
                           "doze - gone.")
            strength = min(STRENGTH, strength + gain)
            log.append("you rest: +2 strength.")
            continue
        if cmd.startswith("drop"):
            parts = cmd.split()
            if not bag:
                print("Your bag is empty.")
                continue
            if len(parts) != 2:
                print("drop what? use: drop <stone name> (e.g. 'drop herald')")
                continue
            word = parts[1].lower()
            matches = [s for s in bag if s.lower().startswith(word)]
            if not matches:
                print("no such stone in your bag.")
                continue
            if len(matches) > 1:
                print("several %ss - dropping the lightest." % word)
            stone = min(matches, key=lambda s: STONES[s]["w"])
            bag.remove(stone)
            log.append("you set down the %s." % stone)
            if pos == HEIGHT - 1 and stone == "Herald":
                print("\nYou slot the Herald into the mouth. The cliff "
                      "rumbles open -")
                print("CAIRN OF ECHOES is yours. Strength remaining: %d. "
                      "YOU WIN." % strength)
                return
            continue
        print("? try u, d, g, r, drop <stone>, look, help, q")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nThe wind takes your name. Farewell, stack-tender.")
        sys.exit(0)
