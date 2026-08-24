# Daily Terminal Drop
# Date: 2026-08-24
# Title: Umber Spire: Borrowed Light

#!/usr/bin/env python3
"""
UMBER SPIRE : BORROWED LIGHT
============================
The monastery's lantern holds one flame, and you have borrowed it for a
single night to climb the Umber Spire. Twelve ledges rise to the summit
bell, each cradling embers and reliquaries the higher you go — but the
winds of the heights take what they please, and your flame is short.

Climb at your own nerve. The deeper you press, the richer the take and
the harsher the gale. When the flame gutters out, the dark keeps
everything you earned. When you choose to descend, the climb you made
is the fortune you keep.

Commands:
  climb   attempt the next ledge (roll against the wind)
  brace   spend 1 light to steady yourself (+2 on your next climb)
  shrine  once: kneel at the eave-shrine to regain 2 light
  loot    abandon the climb now and carry down everything you hold
  quit    let the flame die and walk away empty
"""
import random
import sys

LEDGES = 12                 # ledges to the summit bell (0..11)
MAX_LIGHT = 6               # watches of borrowed flame
SHRINE_HEAL = 2
SUMMIT_BONUS = 5            # embers granted for reaching the bell


def hazard(ledge):
    """The wind's cruelty grows with height: 2,2,3,3 ... 7,7."""
    return 2 + ledge // 2


def loot(ledge):
    """Embers and reliquaries cradled on this ledge."""
    return 1 + ledge


def banner():
    print("=" * 58)
    print("UMBER SPIRE : BORROWED LIGHT")
    print("=" * 58)
    print("Twelve ledges, one borrowed flame. Press high for the great")
    print("reliquaries, but the gale bites where the wind looses its hold.")
    print()
    print("Commands: climb | brace | shrine | loot | quit")
    print()


def board(ledge, light, finesse, empty_below):
    spires = []
    for i in range(LEDGES - 1, -1, -1):
        marker = "@" if i == ledge else ("." if i <= empty_below else " ")
        spires.append("  [{:2d}] {} {}".format(LEDGES - i, marker, "#" * loot(i)))
    spires.append("  flame: " + ("\u25cb" * light) + ("\u25cd" * (MAX_LIGHT - light))
                  + ("   steady +{}".format(finesse) if finesse else ""))
    return "\n".join(spires)


def rating(taken, height, light):
    out = "\n  You climbed {0} ledges and carried down {1} embers of light.".format(
        height, taken)
    if taken >= 40:
        out += "\n  The monastery rings the bell for your name."
    elif taken >= 25:
        out += "\n  The abbot nods, slow and warm."
    elif taken >= 12:
        out += "\n  A fair night's climb. The monks set you a place by the hearth."
    else:
        out += "\n  You climb again another dusk — the spire keeps its patience."
    return out


def main():
    rng = random.Random()
    light = MAX_LIGHT
    ledge = 0                       # current ledge
    empty_below = -1                # ledges stripped by the gale
    taken = 0                       # reliquaries held this climb
    finesse = 0                     # next-climb steady bonus
    shrined = False
    reached_bell = False

    banner()

    while True:
        print("-" * 58)
        print(board(ledge, light, finesse, empty_below))
        print()
        if ledge == LEDGES - 1:
            print("  The summit bell sways above you. Take it and come down — or")
            print("  turn and claim what you hold. There is nothing higher.")
            print()
        try:
            raw = input("your move > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nYou let the flame die and slip back down the dark stair.")
            sys.exit(0)
        if not raw:
            continue
        word = raw.split()[0]

        if word in ("quit", "q"):
            print("  You pinch the flame out and vanish into the foothills, empty-handed.")
            sys.exit(0)

        elif word == "loot":
            print("  You tuck the lantern under your coat and go down the stair.")
            print("  Every ledge you held is yours to keep.")
            print(rating(taken, ledge, light))
            print("  FORTUNE THIS NIGHT: {} embers".format(taken))
            sys.exit(0)

        elif word == "shrine":
            if shrined:
                print("  The shrine has given all it will tonight.")
            else:
                light = min(MAX_LIGHT, light + SHRINE_HEAL)
                shrined = True
                print("  You kneel at the eave-shrine; the flame swells "
                      "({} light).".format(light))
            continue

        elif word == "brace":
            if light <= 0:
                print("  There is no light left to steady yourself with.")
                continue
            light -= 1
            finesse += 2
            print("  You set yourself against the wind (-1 light, +2 to climb).")
            continue

        elif word == "climb":
            if ledge == LEDGES - 1:
                # take the bell: a final prize, then the climb is done either way
                print("  You reach up and ring the great bell. It tolls once,")
                print("  deep and long, and the whole spire answers with light.")
                taken += SUMMIT_BONUS
                reached_bell = True
                print("  SUMMIT GAINED: +{} embers (now {}).".format(
                    SUMMIT_BONUS, taken))
                print(rating(taken, ledge, light))
                print("  FORTUNE THIS NIGHT: {} embers".format(taken))
                sys.exit(0)
            need = hazard(ledge)
            roll = rng.randint(1, 8) + finesse
            finesse = 0
            if roll >= need:
                ledge += 1
                taken += loot(ledge)
                print("  The wind howls past your ears, but your hand finds the\n"
                      "  next ledge. You gain {} embers (now {}).".format(
                          loot(ledge), taken))
                if ledge == LEDGES - 1:
                    print("  You haul yourself over the top. The bell hangs above you.")
            else:
                light -= 1
                if ledge >= 0:
                    taken -= loot(ledge)
                    taken = max(0, taken)
                    empty_below = max(empty_below, ledge)
                print("  The gale tears at you! You slip back to the ledge below")
                if ledge >= 0:
                    print("  and the reliquary there is lost to the dark (-1 light,"
                          " -{} embers).".format(loot(ledge)))
                else:
                    print("  but catch the sill by your fingertips (-1 light).")
                if light <= 0:
                    print()
                    print("=" * 58)
                    print("THE BORROWED FLAME GUTTERS OUT.")
                    print("=" * 58)
                    print("  The dark takes the spire, and everything you carried")
                    print("  from it. The bone-chill is all that is left to you.")
                    sys.exit(0)
        else:
            print("  Unknown. Try: climb | brace | shrine | loot | quit")


if __name__ == "__main__":
    main()
