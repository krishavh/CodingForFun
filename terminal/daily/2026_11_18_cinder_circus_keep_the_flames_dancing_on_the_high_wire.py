# Daily Terminal Drop
# Date: 2026-11-18
# Title: Cinder Circus: Keep the flames dancing on the high wire

#!/usr/bin/env python3
"""CINDER CIRCUS - juggle the flames, keep the tent alive!

You are the ringmaster of a tiny fire circus. Three torches burn
on the high wire. Every second the flames DROP a little. Toss
spark logs on a torch to feed it, but each log costs a beat and
the OTHER torches keep falling. Score points for every second
ALL torches stay lit. The tent closes when any torch dies.

How long can you keep the flames dancing?

COMMANDS: 1 2 3   (feed a torch)      q quit
"""
import random
import sys
import time

TORCHES = 3
START = 100
DROP_MIN, DROP_MAX = 3, 9
COST = 12           # feed cost taken from OTHER torches beat
BOOST = 26
WIN_SCORE = 300

def clamp(v):
    return max(0, min(100, v))

def draw(flames, score, ticks):
    print()
    bars = []
    for i, f in enumerate(flames):
        full = f // 5
        bars.append("[" + "#" * full + " " * (20 - full) + "]")
    print("  Torch 1      Torch 2      Torch 3")
    for row in range(20):
        print("   " + "   ".join(
            b[row] if False else
            ("#" if (f // 5) > row else ("." if (f // 5) + 1 > row else " "))
            for f, b in zip(flames, bars)))
    print()
    for i, f in enumerate(flames):
        print("  Torch %d: %3d" % (i + 1, f), end="")
    print()
    print("  Score: %d   Beats: %d   (feed 1 2 3, q quit)" % (score, ticks))

def main():
    random.seed()
    flames = [START // 2 + random.randint(-10, 10) for _ in range(TORCHES)]
    score = 0
    ticks = 0
    print(__doc__)
    while True:
        draw(flames, score, ticks)
        if any(f <= 0 for f in flames):
            print()
            print("  A torch died! The tent closes at %d points in %d beats." % (score, ticks))
            return 0
        if score >= WIN_SCORE:
            print()
            print("  GRAND FINALE! %d points in %d beats. The crowd goes wild!" % (score, ticks))
            return 0
        try:
            raw = input("  > ").strip().lower()
        except EOFError:
            print()
            return 0
        if raw == "q":
            print("  Thanks for the show! %d points in %d beats." % (score, ticks))
            return 0
        if raw in ("1", "2", "3"):
            i = int(raw) - 1
            if flames[i] <= 0:
                print("  That torch is out!")
                continue
            flames[i] = clamp(flames[i] + BOOST)
            for j in range(TORCHES):
                if j != i:
                    flames[j] = clamp(flames[j] - COST // 3)
        elif raw == "":
            pass
        else:
            print("  Use 1 2 3 or q")
            continue
        # time passes
        ticks += 1
        score += 5
        for i in range(TORCHES):
            flames[i] = clamp(flames[i] - random.randint(DROP_MIN, DROP_MAX))
        if all(f > 60 for f in flames):
            score += 10
            print("  ! Triple Blaze! +10 bonus")

if __name__ == "__main__":
    sys.exit(main())
