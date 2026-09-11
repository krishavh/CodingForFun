# Daily Terminal Drop
# Date: 2026-09-09
# Title: Cinder Orchard: Graft Alchemist

#!/usr/bin/env python3
"""Cinder Orchard: Graft Alchemist - brew the graft before the fire spreads."""
import random, sys

ING = {"b": "bark", "s": "sap", "p": "petal", "r": "root", "m": "mist"}

def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
    target = rng.sample(list(ING.values()), 3)
    shelf = rng.choices(list(ING.values()), k=8)
    heat = 20
    pot = []
    print("Brew the graft:", " + ".join(target))
    while heat > 0:
        print("\nShelf:", ", ".join(shelf))
        print("Pot  :", ", ".join(pot) or "(empty)")
        print("Heat :", heat)
        cmd = input("add <letter>/brew/quit> ").strip().lower()
        if cmd == "quit":
            print("The orchard burns. Bye.")
            return
        if cmd == "brew":
            if sorted(pot) == sorted(target):
                print("PERFECT GRAFT! The alchemist bows. Heat left:", heat)
                return
            print("Wrong recipe. The pot curdles.")
            pot = []
            heat -= 3
            continue
        if cmd.startswith("add"):
            key = cmd.split()[-1] if len(cmd.split()) > 1 else ""
            if key in ING:
                pot.append(ING[key]); heat -= 1
            else:
                print("No such ingredient:", key)
            continue
        print("?", cmd)
    print("Out of heat. The graft never set.")

main()
