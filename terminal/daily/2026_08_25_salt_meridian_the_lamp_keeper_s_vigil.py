# Daily Terminal Drop
# Date: 2026-08-25
# Title: Salt Meridian: The Lamp-Keeper's Vigil

#!/usr/bin/env python3
"""
SALT MERIDIAN :: THE LAMP-KEEPER'S VIGIL
=======================================
The old lamp-house above Salt Meridian keeps a single law: the beacon
must answer the harbor in the order the night writes it. You are the new
keeper's apprentice, and tonight the wide lamp is yours.

Far out, the ferry's ruin-lamps read your signal back to you — a chain of
four colored lights, growing longer with every relay. Watch the flashes,
remember the order exactly, and strike the lamps in the same sequence.
Misremember once and the chain frays; fray it three times and the harbor
slides into silence. Hold the long chain as far as you can, and the
keepers below will carve your name at the foot of the stair.

The four lamps of the lamp-house:
  1  CITRINE   a warm sun-flash       \u25c9
  2  VERDANT   a green tide-blink      \u25ce
  3  CERULEAN  a cold sea-beam         \u25d0
  4  EMBER     a low forge-glow        \u25cd

Commands:
  flash <seq>   repeat the chain, e.g.  flash 1 3 2 1 4
  lamp          redraw the four lamps
  watch <n>     (once per round) re-show one flash of the chain
  give          abandon the vigil with what you have
"""
import random
import sys
import time

LAMPS = [
    ("1", "CITRINE",  "\u25c9"),
    ("2", "VERDANT",  "\u25ce"),
    ("3", "CERULEAN", "\u25d0"),
    ("4", "EMBER",    "\u25cd"),
]
GOOD = 12            # flashes in the longest chain worth attempting
LIVES = 3            # frayed chains before the harbor falls silent
PAUSE = 0.45         # base seconds each flash stays lit


def banner():
    print("=" * 60)
    print("SALT MERIDIAN :: THE LAMP-KEEPER'S VIGIL")
    print("=" * 60)
    print("The beacon must answer the harbor in the order the night")
    print("writes it. Watch, remember, and strike the lamps back.")
    print()
    print("  flash <seq>   |  lamp  |  watch <n>  |  give")
    print()
    for key, name, glyph in LAMPS:
        print("  {0}  {1:<9} {2}".format(key, name, glyph))
    print()


def draw(rng, chain, speed):
    """Flash the chain lamps in order, one at a time, to the player."""
    time.sleep(0.5)
    print()
    for n in chain:
        _, name, glyph = LAMPS[n]
        pads = ["   " for _ in LAMPS]
        pads[n] = " {}".format(glyph)
        row = "  |".join(pads)
        sys.stdout.write("\r" + row + "   <-- " + name)
        sys.stdout.flush()
        time.sleep(max(0.4, speed - 0.1))
    print()
    time.sleep(0.3)


def lamp_row():
    return "   " + "   ".join(glyph for _, _, glyph in LAMPS)


def score_name(score):
    if score >= 78:
        return ("The keepers light every window for you. Your name is cut\n"
                "  deep at the foot of the stair — the longest vigil in living\n"
                "  memory, and the harbor has never been safer.")
    if score >= 45:
        return ("The older keepers nod and shake your hand. The beacon holds\n"
                "  your rhythm past dawn, and children point up at the light.")
    if score >= 18:
        return ("A solid first night. The ferry comes in sure and warm, and\n"
                "  the night-watch signs your name in the log.")
    return ("The harbor is quiet tonight, but quiet is not yet safe. Keep\n"
            "  the vigil — every keeper started by losing a chain or two.")


def main():
    rng = random.Random()
    lives = LIVES
    score = 0
    chain = []

    banner()

    while len(chain) < GOOD:
        if lives <= 0:
            print("=" * 60)
            print("THE HARBOR SLIDES INTO SILENCE.")
            print("=" * 60)
            print("  Three frayed chains, and the wide lamp goes dark over\n"
                  "  Salt Meridian. The ferry limps in on memory alone.\n")
            print("  VIGIL THIS NIGHT: {} flashes held".format(score))
            sys.exit(0)

        chain.append(rng.randrange(len(LAMPS)))
        speed = PAUSE
        print("-" * 60)
        print("  chain {} of {}  |  {} flash(es)  |  lamps: {}".format(
            len(chain), GOOD, len(chain), lives))
        print(lamp_row())
        print()
        print("  The ruin-lamps write the new chain across the water...")
        draw(rng, chain, speed)

        watched = False
        while True:
            try:
                raw = input("your relay > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nYou set the lamp down and slip from the lamp-house.")
                sys.exit(0)
            if not raw:
                continue
            parts = raw.split()
            word = parts[0].lower()

            if word in ("give", "quit", "q"):
                print("  You bank the fires and turn the light down to dawn-low.")
                print("  VIGIL THIS NIGHT: {} flashes held".format(score))
                sys.exit(0)
            elif word == "lamp":
                print(lamp_row())
                print("  1 CITRINE | 2 VERDANT | 3 CERULEAN | 4 EMBER")
                continue
            elif word == "watch":
                if watched:
                    print("  You have already asked to re-read this chain once.")
                elif len(parts) > 1:
                    try:
                        i = int(parts[1]) - 1
                        if 0 <= i < len(chain):
                            key, name, glyph = LAMPS[chain[i]]
                            print("  Flash {} of {} was {} ({}).".format(
                                i + 1, len(chain), name, glyph))
                            watched = True
                        else:
                            print("  That fret of the chain is beyond what was written.")
                    except ValueError:
                        print("  watch <n> — which fret to re-read, e.g.  watch 2")
                else:
                    print("  watch <n> — which fret to re-read, e.g.  watch 2")
                continue
            elif word == "flash":
                seq = parts[1:]
                if not seq:
                    print("  flash <seq> — e.g.  flash 1 3 2 1 4")
                    continue
                try:
                    guess = [int(x) - 1 for x in seq]
                except ValueError:
                    print("  flash takes the lamp numbers, e.g.  flash 1 3 2 1 4")
                    continue
                if len(guess) != len(chain) or any(not (0 <= g < len(LAMPS)) for g in guess):
                    print("  That is {} flashes; the chain holds {} (lamps 1-4).".format(
                        len(guess), len(chain)))
                    continue
                if guess == chain:
                    score += len(chain)
                    print("  The harbor flares back in perfect order.")
                    if len(chain) == GOOD:
                        print("  The full beacon rings true — the longest vigil holds.")
                    else:
                        print("  The night writes one more fret to the chain.")
                else:
                    lives -= 1
                    print("  The chain frays in your hands — {} chain(s) of patience left.".format(
                        lives))
                    if lives <= 0:
                        print("  The ruin-lamps gutter, and the harbor goes quiet.")
                    else:
                        print("  Watch again; the same chain is still on the water.")
                break
            else:
                print("  Try: flash <seq> | lamp | watch <n> | give")

    print("=" * 60)
    print("THE BEACON HOLDS TO THE FULL CHAIN.")
    print("=" * 60)
    print("  The ruin-lamps answer every fret of the night, and the wide\n"
          "  light stands unbroken over Salt Meridian.\n")
    print("  VIGIL THIS NIGHT: {} flashes held".format(score))
    print(score_name(score))
    sys.exit(0)


if __name__ == "__main__":
    main()
