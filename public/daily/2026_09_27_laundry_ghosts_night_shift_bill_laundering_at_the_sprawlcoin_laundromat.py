# Daily Terminal Drop
# Date: 2026-09-27
# Title: Laundry Ghosts: Night-shift bill laundering at the Sprawlcoin laundromat

#!/usr/bin/env python3
"""LAUNDRY GHOSTS - an original terminal turn-based laundering game.

Night shift at the Sprawlcoin laundromat. You feed dirty bills through
the machine, but every pass stokes HEAT and AURA:

  TUB  - your stash of clean money. First to $2,000 wins.
  HEAT - how hard the dryers run. Hit 10 and a dryer MELTS: the tub is
         confiscated and the shift ends.
  AURA - how suspicious you look. Hit 10 and the feds AUDIT you: tub
         seized, shift over.

Commands:
  wash <n>  -> scrub the n GRIMIEST bills in the machine. Big money,
               small heat, but AURA climbs fast (auditors smell bleach).
  dry  <n>  -> a modest pass that LOOKS like ordinary business: slower
               money, more heat, but AURA cools a little.
  rinse     -> tiny money, no heat, big AURA drop. Also reloads the
               machine with a fresh batch of filthy bills.
  bail      -> stop the shift now. Ship what you have; no win, no loss.
  status    -> look at the machine.
  quit      -> walk out mid-shift with your tub.

The machine holds 4 bills at a time; grimier bills pay far more, so
washing the worst ones first is the whole game -- if your aura survives.
"""

import random

WIN_TUB = 2_000
CAP = 10  # heat/aura cap

TEMPLATES = [
    ("linty", 0.10), ("grimy", 0.20), ("sticky", 0.35),
    ("rusted", 0.55), ("sludged", 0.80),
]
BILLS = [5, 10, 20, 50, 100]
COUNTERFEIT_CHANCE = 0.10

BANNER = r"""
    _    ___ _                __ _
   / \  |_ _| |_ ___ _ _ ___/ _| |__ _ __ ___ ___
  / _ \ | ||  _/ -_) '_(_-<  _| / _` \ V  V _(_-<
 /_/ \_\___|\__\___|_| /__/|_| \__,_|\_/\_/ /__/
        night shift at the Sprawlcoin laundromat
"""


def hand_in():
    """Deal a fresh handful of dirty bills."""
    hand = []
    for _ in range(4):
        d, frac = random.choice(TEMPLATES)
        hand.append({"bill": random.choice(BILLS), "dirty": d, "frac": frac})
    return hand


def draw(tub, heat, aura, shift, hand, msg):
    print()
    print(f"  shift #{shift}   TUB ${tub:,} / ${WIN_TUB:,}")
    print(f"  HEAT [{'#' * heat}{'.' * (CAP - heat)}] {heat}/10   "
          f"AURA [{'#' * aura}{'.' * (CAP - aura)}] {aura}/10")
    print("  -- in the machine ---------------------------------")
    for i, b in enumerate(hand, 1):
        bar = "#" * int(b["frac"] * 10)
        print(f"   {i}. ${b['bill']:>3} {b['dirty']:<8} griminess {bar}")
    if msg:
        print(f"  >> {msg}")
    print("  wash <n> | dry <n> | rinse | bail | status | quit")


def turn(state, msg):
    hand, tub, heat, aura, shift = state
    draw(tub, heat, aura, shift, hand, msg)
    parts = input("\n> ").strip().lower().split()
    verb = parts[0] if parts else ""

    if cmd_status(verb):
        return state, "still spinning. give the machine a job."
    if verb in ("q", "quit"):
        return state, "__QUIT__"
    if verb == "bail":
        return state, "__BAIL__"

    if verb == "rinse":
        profit = sum(int(b["bill"] * b["frac"] * 0.3) for b in hand)
        tub += profit
        aura = max(0, aura - 3)
        return (hand_in(), tub, heat, aura, shift + 1), \
            f"rinsed everything: +${profit} clean, aura cooled"

    if verb not in ("wash", "dry"):
        return state, "say: wash 2 / dry 3 / rinse / bail"

    try:
        n = int(parts[1]) if len(parts) > 1 else len(hand)
    except ValueError:
        return state, "pick real coins, like: wash 2"
    n = max(1, min(n, len(hand)))
    # the machine always processes the GRIMIEST bills first - the real
    # decision is HOW MANY to run per pass.
    batch = sorted(hand, key=lambda b: -b["frac"])[:n]
    remaining = [b for b in hand if b not in batch]

    profit, counterfeits = 0, 0
    for b in batch:
        if random.random() < COUNTERFEIT_CHANCE:
            counterfeits += 1
            continue
        profit += int(b["bill"] * b["frac"])

    if verb == "wash":
        profit = int(profit * 1.5)
        heat += random.randint(1, 2)
        aura += random.randint(2, 3)
        note = "washed"
    else:
        profit = int(profit * 0.7)
        heat += random.randint(2, 3)
        aura = max(0, aura - random.randint(1, 2))
        note = "dried"

    out = f"{note} {n} bill(s): +${profit} clean"
    if counterfeits:
        out += f", {counterfeits} turned out COUNTERFEIT!"
    tub += profit
    new_hand = remaining if remaining else hand_in()
    return (new_hand, tub, heat, aura, shift + 1), out


def cmd_status(verb):
    return verb == "status"


def main():
    print(BANNER)
    state = (hand_in(), 0, 0, 0, 1)
    msg = "get the tub to $2,000 clean without melting the dryers or getting audited."
    while True:
        state, msg = turn(state, msg)
        _, tub, heat, aura, shift = state
        if msg == "__BAIL__":
            print(f"\n  bailed after shift {shift - 1}. TUB ${tub:,} shipped.")
            print("  salary intact, but you never hit the real score.")
            return
        if msg == "__QUIT__":
            print(f"\n  night over. final TUB ${tub:,}.")
            return
        if tub >= WIN_TUB:
            print(f"\n  TUB HIT ${tub:,}! The Sprawlcoin books look SPOTLESS.")
            print(f"  survived {shift - 1} shifts. you are the ghost.")
            return
        if heat >= CAP:
            print(f"\n  HEAT {heat}/10 - a dryer MELTS. the tub is confiscated.")
            print(f"  you lose ${tub:,} and walk home damp.")
            return
        if aura >= CAP:
            print(f"\n  AURA {aura}/10 - the feds AUDIT you. everything seized.")
            print(f"  you lose ${tub:,}.")
            return


if __name__ == "__main__":
    main()
