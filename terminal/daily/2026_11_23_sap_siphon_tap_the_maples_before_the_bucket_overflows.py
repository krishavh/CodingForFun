# Daily Terminal Drop
# Date: 2026-11-23
# Title: Sap Siphon: Tap the maples before the bucket overflows

#!/usr/bin/env python3
"""SAP SIPHON - tap the tallest trees before the sap bucket overflows!

A tiny maple-forest idle-tapper.
Trees sprout with hidden sap speeds. Tap a tree to collect its sap.
Watch the bucket: it fills, and overflows waste everything!
Spend sap on taller ladders to reach the big maples.
"""
import random
import sys
import time

# tree sizes -> tap sap + ladder needed
TREES = [
    ("sapling", 1, 0),
    ("young", 2, 1),
    ("mature", 4, 2),
    ("ancient", 7, 3),
]


def new_tree():
    """Every tree starts small, but hidden speed grows."""
    size = 0
    speed = random.randint(1, 3)
    return {"size": size, "progress": 0, "speed": speed, "sap": 0}


def main():
    random.seed()
    bucket = 0
    sap = 0
    ladders = 0
    taps = 0
    trees = [new_tree()]
    overflowed = 0
    start = time.time()
    DURATION = 90  # seconds

    print("\n  SAP SIPHON")
    print("  Tap tree numbers to collect sap. B = bucket. L = ladder (+1).")
    print("  Trees grow on their own. Bigger tree = more sap per tap.")
    print("  Bucket OVERFLOWS at 50 (wasted!). Ladders cost 10 sap.")
    print("  You have %d seconds. Q = quit.\n" % DURATION)

    last = time.time()
    while True:
        now = time.time()
        if now - last >= 1.0:
            dt = now - last
            last = now
            for t in trees:
                t["progress"] += t["speed"] * dt
                while t["progress"] >= 10:
                    t["progress"] -= 10
                    if t["size"] < len(TREES) - 1:
                        t["size"] += 1
                    else:
                        t["sap"] += 1  # max trees drip bonus sap
                t["speed"] += random.choice([0, 0, 1])
            # bucket drips a little every second
            bucket += len(trees)
            if bucket > 50:
                overflowed += bucket - 50
                bucket = 50
                print("  *** BUCKET OVERFLOW! %d sap wasted ***" % overflowed)

        if (now - start) > DURATION:
            print("\n  TIME UP!")
            break

        # render
        total = sum(t["sap"] for t in trees)
        print("\r  %ds | trees: %d | bucket: %2d/50 | sap: %3d | ladders: %d "
              "| overflow: %d " % (
                  int(DURATION - (now - start)), len(trees), bucket, sap,
                  ladders, overflowed), end="", flush=True)
        cmd = input()
        cmd = cmd.strip().lower()
        if cmd == "q":
            print()
            break
        elif cmd == "b":
            sap += bucket
            print("\r  Collected %d sap from bucket!%s" % (bucket, " " * 20))
            bucket = 0
        elif cmd == "l":
            if sap >= 10:
                sap -= 10
                ladders += 1
                trees.append(new_tree())
                print("\r  New tree sprouted!%s" % (" " * 20))
            else:
                print("\r  Need 10 sap for a ladder!%s" % (" " * 20))
        elif cmd.isdigit():
            i = int(cmd) - 1
            if 0 <= i < len(trees):
                t = trees[i]
                need = TREES[t["size"]][2]
                if ladders >= need:
                    amt = TREES[t["size"]][1]
                    sap += amt
                    taps += 1
                    print("\r  +%d sap from the %s tree%s" % (
                        amt, TREES[t["size"]][0], " " * 10))
                else:
                    print("\r  Need %d ladders for the %s tree%s" % (
                        need, TREES[t["size"]][0], " " * 10))
            else:
                print("\r  No such tree%s" % (" " * 30))
        else:
            print("\r  ? (tree# | b | l | q)%s" % (" " * 30))

    mins = time.time() - start
    print("\n  --- RESULT ---")
    print("  Sap collected:   %d" % sap)
    print("  Bucket left:     %d" % bucket)
    print("  Sap overflowed:  %d" % overflowed)
    print("  Trees tapped:    %d" % taps)
    print("  Trees grown:     %d" % len(trees))
    print("  Ladders left:    %d" % ladders)
    grade = sap + bucket - overflowed
    if grade >= 200:
        print("  SYRUP MASTER! The pancakes are drowning!")
    elif grade >= 120:
        print("  Sticky sweet harvest!")
    elif grade >= 60:
        print("  A decent drizzle of sap.")
    elif grade >= 20:
        print("  Barely a drip.")
    else:
        print("  The trees laughed at you.")
    print("  (%.0f seconds in the grove)\n" % mins)


if __name__ == "__main__":
    main()
