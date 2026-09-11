# Daily Terminal Drop
# Date: 2026-09-10
# Title: Hollow Compass: Tide Ledger

#!/usr/bin/env python3
"""Hollow Compass: Tide Ledger - balance the ledger as the tide turns."""
import random, sys

def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 10)
    coin = 0
    day = 1
    print("Ledger the tides! Guess rise(r)/fall(f) each dawn; right guesses bank coin.")
    while day <= 7:
        tide = rng.choice(["r", "f"])
        guess = input("Day %d (coin=%d) r/f> " % (day, coin)).strip().lower()
        if guess not in ("r", "f"):
            print("r or f."); continue
        if guess == tide:
            coin += rng.randint(2, 5); print("The tide %s - you banked." % ("ROSE" if tide == "r" else "FELL"))
        else:
            coin -= 1; print("Missed. The tide %s." % ("rose" if tide == "r" else "fell"))
        day += 1
    print("Final ledger:", coin, "coin -", "solvent!" if coin > 0 else "washed out.")

main()
