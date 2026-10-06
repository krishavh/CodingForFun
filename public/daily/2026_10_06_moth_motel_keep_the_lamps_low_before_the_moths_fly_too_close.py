# Daily Terminal Drop
# Date: 2026-10-06
# Title: Moth Motel: Keep the lamps low before the moths fly too close

#!/usr/bin/env python3
"""MOTH MOTEL - an original terminal game of lamps, moths and mistakes.

You run a roadside motel for moths. Every night a new moth checks in
and flies toward the BRIGHTEST lamp still glowing. Lamps burn out
fast, and moths crash into burning lamps!

You manage 7 lamps on a wire. Each night you may:
  <n>      set lamp n's brightness (1-9) before dusk
  s        SKIP dusk (moth sleeps in lobby, no score)
  q        close the motel (quit)

At DUSK the moth picks the lamp with highest brightness
(ties: lowest number) and flies to it.
  brightness 1-3  -> moth is SAFE, you score COZY points (lamp level)
  brightness 4-6  -> moth is SIZZLED, lamp loses 2 glow
  brightness 7-9  -> moth goes POOF, lamp burns out (0 glow)

Each lamp starts glowing 5. Burnt lamps recharge +1 per night
(up to 5) but score nothing while dark. Last 12 nights.

Moths love bright lights. Keep them LOW to keep them ALIVE!
"""
import random

NIGHTS = 12
NUM = 7


class Lamp:
    def __init__(self, i):
        self.num = i + 1
        self.glow = 5

    def bright(self, level):
        self.glow = max(0, self.glow - (2 if 4 <= level <= 6 else 0))
        if level >= 7:
            self.glow = 0


def draw(lamps, night, score, choice, msg):
    print()
    print(f"NIGHT {min(night, NIGHTS)} of {NIGHTS}   cozy score: {score}")
    print("  lamp    " + "  ".join(str(l.num) for l in lamps))
    glows = []
    for l in lamps:
        if l.glow <= 0:
            glows.append("dead")
        else:
            glows.append(str(l.glow))
    print("  glow    " + "  ".join(glows))
    print("  legend  glow 1-3 cozy  4-6 sizzle  7-9 POOF")
    if msg:
        print("  " + msg)
    if choice is None:
        print("set 1-9 on a lamp / s skip / q quit >")


def dusk(lamps, choice, score):
    """Moth flies to brightest lit lamp. Returns (score, msg)."""
    alive = [l for l in lamps if l.glow > 0]
    if not alive:
        return score, "No lamps glowing! Moth sleeps in the lobby."
    # moths pick HIGHEST CHOSEN glow first, then highest resting glow.
    # ties go to lowest lamp number. chosen = lamps you set tonight.
    def key(l):
        return (-choice.get(l.num, l.glow), l.glow, l.num)

    target = min(alive, key=key)
    n = target.num
    # chosen brightness (player's pick or current glow)
    level = choice.get(n, target.glow)
    # apply burn to the lamp the moth hit
    for l in lamps:
        if l.num == n:
            if 4 <= level <= 6:
                l.glow = max(0, l.glow - 2)
            elif level >= 7:
                l.glow = 0
            break
    if level <= 3:
        pts = level
        return score + pts, f"Moth safe at lamp {n}! +{pts} cozy."
    if level <= 6:
        return score, f"Moth sizzled at lamp {n}! Ouch. (0 pts)"
    return score, f"Moth went POOF at lamp {n}! Poor moth. (0 pts)"


def recharge(lamps):
    """Lamps drift toward glow 3 (moth-safe) when not watched."""
    for l in lamps:
        if l.glow <= 0:
            l.glow = 1  # dead lamps slowly relight
        elif l.glow < 3:
            l.glow += 1  # burnt down lamps recover a little
        elif l.glow > 3:
            l.glow -= 1  # bright lamps burn down a little


def main():
    random.seed()
    lamps = [Lamp(i) for i in range(NUM)]
    score = 0
    msg = "Welcome! Moths love bright lights. Keep them LOW to keep them ALIVE!"
    for night in range(1, NIGHTS + 1):
        choice = {}
        while True:
            draw(lamps, night, score, choice, msg)
            try:
                raw = input().strip().lower()
            except EOFError:
                print(f"\nMotel closed early. Final cozy score: {score}")
                return
            msg = ""
            if raw == "q":
                print(f"\nMotel closed. Nights: {night}. Final cozy score: {score}")
                return
            if raw == "s":
                break
            parts = raw.replace(",", " ").split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                ln, lv = int(parts[0]), int(parts[1])
                if 1 <= ln <= NUM and 1 <= lv <= 9:
                    choice[ln] = lv
                    msg = f"Lamp {ln} set to glow {lv} for tonight."
                    continue
            msg = "Set a lamp: <lamp 1-7> <glow 1-9>. Or s skip, q quit."
        score, msg = dusk(lamps, choice, score)
        recharge(lamps)
    draw(lamps, NIGHTS + 1, score, None, "The sun rises. Motel closed!")
    print(f"\nSEASON DONE! Final cozy score: {score}")
    rank = ("GOLD MOTH MOTEL" if score >= 30 else
            "SILVER MOTH MOTEL" if score >= 18 else
            "BRONZE MOTH MOTEL" if score >= 8 else "NO VACANCY")
    print(f"Rank: {rank}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nNo vacancy. Bye!")
