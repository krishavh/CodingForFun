# Daily Terminal Drop
# Date: 2026-08-16
# Title: Violet Core: Reactor Watch

# Daily Terminal Drop
# Title: Violet Core: Reactor Watch
# Keep a decaying plasma core alive long enough to charge the escape pod.

#!/usr/bin/env python3
import random
import sys

BAND_LO = 65
BAND_HI = 100
MAX_TURNS = 25
TARGET_CHARGE = 60


def clamp(x, lo=0, hi=200):
    return max(lo, min(hi, x))


def main():
    rng = random.Random()
    heat = 55
    coolant = 8
    rods = 5
    charge = 0
    turn = 0

    print("=" * 46)
    print("VIOLET CORE :: REACTOR WATCH")
    print("=" * 46)
    print("The plasma core is decaying. Hold temperature in the band")
    print(f"( {BAND_LO}-{BAND_HI} ) to charge the escape pod to {TARGET_CHARGE}%.")
    print(f"You have {MAX_TURNS} turns. Heat rises ~8/turn; each rod inserted")
    print("adds +4/turn. Coolant sprays -12 heat. Govern the core.")
    print("Commands: rods <0-5> | cool | status | quit")
    print()

    while turn < MAX_TURNS:
        turn += 1
        # Core heat dynamics
        heat += rng.randint(6, 10)          # passive rise
        heat += rods * 4                     # rod burn
        if rng.random() < 0.12:              # random vent
            heat -= rng.randint(4, 8)
            print("A vent whistles open; heat eases slightly.")
        heat = clamp(heat)

        in_band = BAND_LO <= heat <= BAND_HI
        if in_band:
            gain = 8
            charge = min(TARGET_CHARGE, charge + gain)
            marker = f"charging +{gain} -> {charge}%"
        elif heat > BAND_HI:
            marker = "CORE OVERHEATING (no charge)"
            heat = clamp(heat + 4)           # runaway decays faster
            if heat > 140:
                print("!!! CORE MELTDOWN !!! The pod is lost.")
                return
        else:
            marker = "CORE CRYOGENIC (no charge)"

        bar = "|" * (heat // 4) if heat // 4 else "."
        print(f"[T{turn:>2}] heat={heat:>3} {bar}")
        state = f"rods={rods} coolant={coolant} {marker}"
        print(" " * 8 + state)

        # Win / lose checks
        if charge >= TARGET_CHARGE:
            print()
            print(f"Pod charged to {TARGET_CHARGE}%! You eject in turn {turn}.")
            return
        if heat > 140:
            print("!!! CORE MELTDOWN !!! The pod is lost.")
            return

        if turn >= MAX_TURNS:
            break

        cmd = input("> ").strip().lower()
        if not cmd:
            continue
        if cmd == "quit":
            print("Core vented. Reactor offline.")
            return
        if cmd == "status":
            print(f"Turn {turn} | heat {heat} | rods {rods} | coolant {coolant} | charge {charge}%")
            print(f"Band {BAND_LO}-{BAND_HI} | budget {MAX_TURNS - turn} turns left")
            continue
        if cmd.startswith("rods"):
            try:
                n = int(cmd.split()[1])
            except (IndexError, ValueError):
                print("Usage: rods <0-5>")
                continue
            rods = clamp(n, 0, 5)
            print(f"Rods set to {rods}. (Heat +{rods * 4}/turn)")
            continue
        if cmd == "cool":
            if coolant <= 0:
                print("No coolant left. Rods are your only lever.")
                continue
            heat = clamp(heat - 12)
            coolant -= 1
            print(f"Coolant sprayed. Heat -12, {coolant} left.")
            continue
        print("Unknown command.")

    print()
    print(f"Core spent. Charge only reached {charge}%.")
    print("The pod drifts, dark.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nCore vented. Reactor offline.")
        sys.exit(0)
