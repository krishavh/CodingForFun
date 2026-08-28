# Daily Terminal Drop
# Date: 2026-08-28
# Title: Ember Watch: The Lantern-Keeper's Night

#!/usr/bin/env python3
"""
EMBER WATCH :: THE LANTERN-KEEPER'S NIGHT
=========================================
You keep the last lantern tower on the moth-road. Every night the moths
come in from the dark, hungry for the flame, and every night you bank
the fire, trim the wick, and decide what the light is worth.

Each night you have a handful of actions and a dwindling store of oil.
Spend it wisely: a wide glow turns moths, a focused beam burns them,
and a dark tower is a dead tower.

Commands:
  pour <n>     pour n oil into the lantern (raises glow)
  focus        narrow the flame — burns moths at the glass
  widen        spread the flame — turns moths from the light
  watch        peer into the dark and count what comes
  bank         seal the fire for the night (ends the turn)
  quit         abandon the tower
"""
import random
import sys
import time

OIL_START = 12
NIGHTS = 7
WING = "🦋"
FLAME = "🔆"

def clamp(n, lo, hi):
    return max(lo, min(hi, n))

class Tower:
    def __init__(self):
        self.oil = OIL_START
        self.glow = 5          # 0..10 how bright the lantern burns
        self.focus = 3         # 1..5 — low=wide, high=focused
        self.night = 0
        self.score = 0
        self.alive = True

    def draw_moths(self, moths):
        return " ".join(WING for _ in range(moths)) or "(the dark is still)"

    def draw_glow(self):
        return FLAME * self.glow + "·" * (10 - self.glow)

def spawn_moths(rng, night):
    base = 2 + night
    return rng.randint(base, base + 3)

def play():
    rng = random.Random()
    t = Tower()
    print("=" * 50)
    print("EMBER WATCH :: THE LANTERN-KEEPER'S NIGHT")
    print("=" * 50)
    print(f"You have {OIL_START} measures of oil. {NIGHTS} nights to hold.")
    print()

    while t.alive and t.night < NIGHTS:
        t.night += 1
        moths = spawn_moths(rng, t.night)
        print(f"\n--- Night {t.night} of {NIGHTS} ---")
        print(f"Oil: {t.oil}   Glow: {t.draw_glow()}   Focus: {t.focus}/5")
        print(f"From the dark, wings stir... {t.draw_moths(moths)}")

        acted = False
        while True:
            cmd = input("watch> ").strip().lower().split()
            if not cmd:
                continue
            verb = cmd[0]
            if verb == "pour" and len(cmd) == 2 and cmd[1].isdigit():
                n = int(cmd[1])
                if n > t.oil:
                    print("Not enough oil.")
                elif t.glow >= 10:
                    print("The lantern burns as bright as it can.")
                else:
                    poured = min(n, 10 - t.glow)
                    t.oil -= poured
                    t.glow += poured
                    print(f"You pour {poured} oil. Glow: {t.draw_glow()}")
                    acted = True
            elif verb == "focus":
                if t.focus < 5:
                    t.focus += 1
                    print(f"You narrow the flame. Focus: {t.focus}/5")
                    acted = True
                else:
                    print("The beam is as tight as it will go.")
            elif verb == "widen":
                if t.focus > 1:
                    t.focus -= 1
                    print(f"You spread the flame. Focus: {t.focus}/5")
                    acted = True
                else:
                    print("The glow already fills the glass.")
            elif verb == "watch":
                mood = ("ravenous" if moths > 5 else
                        "curious" if moths > 2 else "thin tonight")
                print(f"You peer out: {t.draw_moths(moths)} — the swarm feels {mood}.")
            elif verb == "bank":
                break
            elif verb == "quit":
                print("You let the tower go dark. The moths thank you, in their way.")
                return
            else:
                print("Try: pour <n> | focus | widen | watch | bank | quit")

            if acted and moths > 0 and rng.random() < 0.3 * t.focus / 5:
                burn = min(moths, t.focus)
                moths -= burn
                print(f"At the glass, the focused flame sears {burn} moth(s).")

        # Night resolves
        if t.glow == 0:
            print("The tower is dark. The moths do not even slow down.")
            print("They carry the last ember away into the dark. Your watch is over.")
            t.alive = False
            break
        turned = max(0, t.glow - 2 * t.focus)
        burned = min(moths, t.focus)
        moths -= turned + burned
        if moths <= 0:
            print("Dawn comes. Every moth is turned or burned. The flame holds.")
            t.score += 10
        else:
            drain = moths
            t.glow = clamp(t.glow - drain, 0, 10)
            t.score += 2
            print(f"{drain} moth(s) drink the light. Glow drops: {t.draw_glow()}")
        if t.glow == 0:
            print("The lantern gutters out at dawn's edge. Too close.")
            t.alive = False
        t.oil = max(0, t.oil - 1)  # the lamp always drinks a little
        t.focus = 3                # the wick resets each night

    if t.alive:
        print(f"\nYou held the tower all {NIGHTS} nights. Watch-score: {t.score}")
        print("The moth-road is quiet. For now.")
    else:
        print(f"\nThe dark took the tower on night {t.night}. Watch-score: {t.score}")

if __name__ == "__main__":
    try:
        play()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodnight, keeper.")
        sys.exit(0)
