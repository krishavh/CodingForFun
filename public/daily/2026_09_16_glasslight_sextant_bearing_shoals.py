# Daily Terminal Drop
# Date: 2026-09-16
# Title: Glasslight Sextant: Bearing & Shoals

#!/usr/bin/env python3
"""GLASSLIGHT SEXTANT - an original terminal navigation game for one player.

You are the navigator of a lantern-ship crossing the Night Archipelago.
The fleet is strung out behind you in the fog, and it follows YOUR
bearing light. Every round the sea shoves your bearing off true north.
You must re-trim the ship and call a bearing for the fleet.

THE DIAL
  The ship's compass card has 8 points:
    n, ne, e, se, s, sw, w, nw
  Hidden at the start: one point is TRUE NORTH (the pole star's spike).
  The card also hides 1-2 WRECK POINTS - call a bearing on those and the
  fleet steers onto the shoals.

THE TWIST - THE GLASSLIGHT
  Each round you get ONE shimmer. You aim it at any point of the card.
  The glass answers with a faint tone:
    a low toll  ....... the true spike is CLOSE to where you aimed
    a high tink  ...... the true spike is FAR from where you aimed
  (Distance is counted in steps around the 8-point ring. Toll if the
  ring distance is 0 or 1, tink if it is 2, 3, or 4.)
  Aim the shimmer at a wreck point and the wreck simply hums - no
  information, one shimmer wasted.

A ROUND
  1. shimmer <point>   - fire your one reading
  2. trim <point>      - set the ship's trim (your guess for true north)
  3. call              - announce the bearing. The fleet sails one leg.
                         If your trim was the true spike, the fleet gains
                         a hull; if you called a wreck, you lose a hull;
                         either way the sea knocks the trim off true.

YOU LOSE when the fleet's hulls run out. WIN by reaching 8 hulls
(full strength) or surviving FOGDRAFT legs in the black.
"""
import random
import sys

POINTS = ["n", "ne", "e", "se", "s", "sw", "w", "nw"]
FULL = {p: i for i, p in enumerate(POINTS)}
NAMES = {
    "n": "north", "ne": "northeast", "e": "east", "se": "southeast",
    "s": "south", "sw": "southwest", "w": "west", "nw": "northwest",
}
LEGS = 7
HULL_WIN = 8

ART = r"""
      .  *  .          GLASSLIGHT SEXTANT
   .       *  .     the fleet follows your bearing
 *   N
     | \  ne         shimmer = one glasslight reading
  w --+-- e          trim    = set the ship's heading
     | /  se         call    = the fleet sails one leg
 *   S      .
"""

def ring_dist(a, b):
    """Steps between two points on the 8-point compass ring."""
    d = abs(FULL[a] - FULL[b])
    return min(d, 8 - d)

def norm(word):
    w = word.strip().lower()
    if w in POINTS:
        return w
    for p, name in NAMES.items():
        if w == name or w == name[:3]:
            return p
    return None

def pick_board(rng):
    true_spike = rng.choice(POINTS)
    wrecks = set()
    while len(wrecks) < rng.choice([1, 2]):
        cand = rng.choice(POINTS)
        if cand != true_spike and ring_dist(cand, true_spike) > 1:
            wrecks.add(cand)
    return true_spike, wrecks

def draw(wrecks_known, hulls, leg, legs, shimmer_used, tone_log):
    print(ART)
    print("  Leg %d of %d    hulls %d/8    shimmer %s" % (
        leg, legs, hulls, "SPENT" if shimmer_used else "ready"))
    print("  card: " + "  ".join(POINTS))
    if wrecks_known:
        print("  wreck points logged: " + ", ".join(sorted(wrecks_known)))
    else:
        print("  wreck points logged: none yet")
    if tone_log:
        print("  last tones: " + " | ".join(tone_log[-3:]))
    print()

def main():
    rng = random.Random()
    print(__doc__)
    input("Press Enter to raise the glasslight... ")
    true_spike, wrecks = pick_board(rng)
    hulls = 5
    tone_log = []
    found = set()

    for leg in range(1, LEGS + 1):
        shimmer_used = False
        last_tone = None
        while True:
            draw(found, hulls, leg, LEGS, shimmer_used, tone_log)
            cmd = input("shimmer <pt> / trim <pt> / call / look / quit > ").strip().lower()
            parts = cmd.split()
            if cmd in ("quit", "q"):
                print("You strike the colors. The fleet scatters into the fog.")
                return
            if cmd == "look" or not parts:
                continue
            if parts[0] == "shimmer" and not shimmer_used and len(parts) == 2:
                pt = norm(parts[1])
                if pt is None:
                    print("That point is not on the card.\n")
                    continue
                shimmer_used = True
                if pt in wrecks:
                    tone = "WRECK HUM (no reading)"
                    found.add(pt)
                else:
                    d = ring_dist(pt, true_spike)
                    tone = "LOW TOLL (spike near)" if d <= 1 else "HIGH TINK (spike far)"
                    last_tone = pt
                tone_log.append("%s->%s" % (pt, tone.split(" (")[0]))
                print("  The glass sings: %s\n" % tone)
                continue
            if parts[0] == "shimmer":
                print(shimmer_used and "The glass is spent this leg.\n"
                      or "Use: shimmer <point>\n")
                continue
            if parts[0] == "trim" and len(parts) == 2:
                pt = norm(parts[1])
                if pt is None:
                    print("That point is not on the card.\n")
                    continue
                last_tone = pt
                print("  Trim set to the %s point.\n" % NAMES[pt])
                continue
            if parts[0] == "trim":
                print("Use: trim <point>\n")
                continue
            if parts[0] == "call":
                if last_tone is None:
                    print("Trim the ship before you call.\n")
                    continue
                break
            print("Unknown order. The helmsman waits.\n")

        # The fleet sails one leg on your bearing.
        if last_tone == true_spike:
            hulls += 1
            print("  >> TRUE BEARING. The fleet closes up, hulls now %d/8." % hulls)
        elif last_tone in wrecks:
            hulls -= 2
            print("  >> SHOALS! The %s point was a wreck. Two hulls stove." % NAMES[last_tone])
        else:
            hulls -= 1
            print("  >> Off bearing. The fleet stretches, one hull strains (hulls %d/8)." % hulls)

        # The sea shoves the trim off true each leg.
        shove = rng.choice(POINTS)
        while shove == true_spike:
            shove = rng.choice(POINTS)
        last_tone = shove
        print("  The sea shoves the trim toward the %s point.\n" % NAMES[shove])
        if hulls <= 0:
            print("The fleet breaks apart in the dark. The archipelago keeps its ships.")
            print("Legs survived: %d of %d." % (leg - 1, LEGS))
            return
        if hulls >= HULL_WIN:
            print("FULL HULLS. The fleet shapes up bright and whole behind you.")
            break

    if hulls > 0:
        print("\nThe fog lifts at dawn. Every sail is still on the horizon.")
        print("The pole star's spike was the %s point all along." % NAMES[true_spike].upper())
        print("YOU WIN - navigator of the Night Archipelago.")

if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n\nThe fog closes in. Fair winds, navigator.")
        sys.exit(0)
