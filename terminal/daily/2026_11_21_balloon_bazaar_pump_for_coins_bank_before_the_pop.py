# Daily Terminal Drop
# Date: 2026-11-21
# Title: Balloon Bazaar: Pump for coins, bank before the POP

#!/usr/bin/env python3
"""BALLOON BAZAAR - inflate balloons for coins, but don't let them POP!

Each pump earns you 1 coin. But every pump risks the balloon
POP!ing. A popped balloon pays NOTHING. Choose:
  b)low away with your coins (bank them, new balloon)
  p)ump again (risk it!)
  q)uit
Every 3rd balloon is a CLOUD balloon (faster to pop, pays 3x!)
How rich can you get before the bazaar closes (10 balloons)?
"""
import random
import sys

TOTAL_BALLOONS = 10
CLOUD_EVERY = 3  # balloon 3, 6, 9 are cloud balloons


def pop_chance(pumps, cloud):
    """Chance the NEXT pump pops."""
    base = 0.10 + 0.09 * pumps
    return base * (2 if cloud else 1)


def draw(balloon, bank, pumps, num, coins, msg):
    print()
    size = min(pumps, 10)
    print("+" + "-" * 30 + "+")
    rows = 10
    for r in range(rows, -1, -1):
        line = "|" + " " * 30 + "|"
        if r <= size:
            w = r * 2
            left = (30 - w) // 2
            inner = "o" * w
            if r == 0:
                inner = "^"
            elif r == 1:
                inner = "o"
            line = "|" + " " * left + inner + " " * (30 - left - w) + "|"
        if r == 5:
            tag = " CLOUD! " if balloon == "cloud" else "        "
            line = line[:14] + tag + line[22:]
        print(line)
    print("+" + "-" * 30 + "+")
    print(f"Balloon {num}/{TOTAL_BALLOONS} ({balloon})  pumps: {pumps}")
    print(f"This balloon: {coins} coins   Banked: {bank}")
    if msg:
        print(msg)
    print("b)ank it  p)ump  q)uit  -> ", end="", flush=True)


def main():
    random.seed()
    bank = 0
    balloon_no = 1
    print("=== BALLOON BAZAAR ===")
    print("Pump balloons for coins. POP = lose the balloon!")
    while balloon_no <= TOTAL_BALLOONS:
        cloud = balloon_no % CLOUD_EVERY == 0
        pumps = 0
        coins = 0
        popped = False
        msg = ""
        while True:
            draw("cloud" if cloud else "plain", bank, pumps,
                 balloon_no, coins * (3 if cloud else 1), msg)
            choice = input().strip().lower()
            if choice == "q":
                print(f"\nYou walk away with {bank} coins. Bye!")
                return
            if choice == "b":
                bank += coins * (3 if cloud else 1)
                msg = f"Banked! Balloon {balloon_no} safe."
                break
            if choice != "p":
                msg = "? use b, p or q"
                continue
            pumps += 1
            if random.random() < pop_chance(pumps, cloud):
                popped = True
                msg = f"POP! Lost {coins} coins."
                break
            coins += 1
            msg = "pump..."
        if popped or choice == "b":
            balloon_no += 1
    print()
    print(f"=== BAZAAR CLOSED ===")
    print(f"Final bank: {bank} coins")
    ranks = [(0, "Clumsy Cloudtoucher"), (10, "Pump Apprentice"),
             (20, "Balloonist"), (30, "Coin Pumper"),
             (40, "Bazaar Baron"), (999999, "Balloon Legend")]
    for t, name in ranks:
        if bank < t + 10 or t == 999999:
            pass
    for t, name in reversed(ranks):
        if bank >= t:
            print(f"Rank: {name}")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
        sys.exit(0)
