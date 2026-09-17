# Daily Terminal Drop
# Date: 2026-09-17
# Title: Cellar of Nine Faucets: Dice on Draft

# Daily Terminal Drop
# Date: 2026-09-17
# Title: Cellar of Nine Faucets: Dice on Draft

#!/usr/bin/env python3
"""CELLAR OF NINE FAUCETS - an original terminal push-your-luck dice game.

You are the cellar-keeper of a rickety brewhouse. Nine faucets sit in a
row above your copper, each dispensing a different brew. Every NIGHT
you draw dice from the keg, roll them, and assign each die to a faucet.
When a faucet's held dice sum to EXACTLY its THIRST, it drains into the
copper and you bank that thirst as GLORY. Overflow a faucet and the
brew goes SOUR, washing away everything you gained that night.

THE KEG
  Each night the keg rolls 6 dice (faces 1-6). You assign them ONE AT
  A TIME to faucets, or spill them into the bucket. Dice you pass on
  are lost to the slop drain.

THE FAUCETS (each has a thirst, and a quirk)
  1 Trickle      thirst 4   - safe and steady, drains often.
  2 The Weasel   thirst 6   - after it drains, the keg's NEXT roll is
                              one die short (the weasel drinks first).
  3 Iron Gut     thirst 8   - a 6 assigned here counts DOUBLE (12).
  4 Old Brass    thirst 10  - once per game, 'b' rerolls every held die.
  5 Hollow Leg   thirst 5   - 'm' moves its top held die elsewhere.
  6 The Twin     thirst 7   - also drains on an exact PAIR (7 Glory).
  7 Barley Cork  thirst 3   - drains pay +1 extra Glory (cork tax).
  8 Black Tap    thirst 9   - a 1 assigned here is WILD: name 1-6.
  9 Grandfather  thirst 12  - drain it and you win the game outright.

THE SPILL BUCKET
  's' dumps the current die into the bucket. It holds 3 slop dice; a
  4th sour-floods every faucet (night Glory lost, faucets reset).

NIGHTS & WINNING
  You have 6 nights. Unbanked held dice persist between nights, so a
  half-filled faucet is a committed brew - and a growing risk.
  Reach 30 Glory (or drain the Grandfather) to win.

Commands while placing a die:
  1-9   assign the current die to that faucet
  s     spill the die into the bucket
  m     move a held die off Hollow Leg (faucet 5)
  b     Old Brass re-tap: reroll all held dice (once per game)
  p     pass: end the night (remaining dice are lost)
  help  this list        q   quit
"""
import random
import sys

GOAL = 30
NIGHTS = 6
KEG = 6
BUCKET_MAX = 3

FAUCETS = [
    {"thirst": 4, "name": "Trickle"},
    {"thirst": 6, "name": "The Weasel"},
    {"thirst": 8, "name": "Iron Gut"},
    {"thirst": 10, "name": "Old Brass"},
    {"thirst": 5, "name": "Hollow Leg"},
    {"thirst": 7, "name": "The Twin", "pair": True},
    {"thirst": 3, "name": "Barley Cork", "bonus": 1},
    {"thirst": 9, "name": "Black Tap", "wild": True},
    {"thirst": 12, "name": "Grandfather"},
]

ART = r"""
      _______________________
     |  CELLAR OF NINE       |
     |  FAUCETS              |
     | ~ ~ ~  brew & risk  ~ |
     |_______________________|
        [1][2][3][4][5][6][7][8][9]
         \  \  |  |  |  /  /  /
          `-- copper --'
"""


def show(facets, bucket, glory, night, keg_left, brass_used):
    print("\n" + "=" * 64)
    print("NIGHT %d of %d   Glory: %d/%d   Keg dice left: %d" %
          (night, NIGHTS, glory, GOAL, keg_left))
    print("Bucket (%d/%d slop): %s" % (len(bucket), BUCKET_MAX,
                                       bucket or "-"))
    for i, f in enumerate(facets, 1):
        marks = " ".join(str(d) for d in f["dice"])
        extra = ""
        if f.get("pair"):
            extra += "  [pair]"
        if i == 4 and not brass_used:
            extra += "  [b once]"
        if i == 5:
            extra += "  [m move]"
        if i == 8:
            extra += "  [1=wild]"
        print("  %d %-13s thirst %-2d  held: %-11s%s" %
              (i, f["name"], f["thirst"], marks or "-", extra))
    print("=" * 64)


def sour_flood(facets, glory, reason):
    print("\n  !! SOUR FLOOD: %s !!  Night glory of %d washes away." %
          (reason, glory))
    for f in facets:
        f["dice"].clear()
    return 0


def drain(f, idx, facets, glory):
    gain = f["thirst"] + f.get("bonus", 0)
    print("  >> %s drains! +%d Glory" % (f["name"], gain))
    f["dice"].clear()
    if idx == 1:  # The Weasel: next keg roll is one die short
        print("  (the Weasel licks its lips - next roll is a die short)")
        f["skip_next"] = True
    return glory + gain


def handle_drains(facets, glory):
    for i, f in enumerate(facets, 1):
        s = sum(f["dice"])
        if s == f["thirst"] or (f.get("pair") and len(f["dice"]) >= 2
                                and f["dice"][-1] == f["dice"][-2]):
            glory = drain(f, i - 1, facets, glory)
            if i == 9:
                print("\n  *** THE GRANDFATHER DRAINS - the cellar is "
                      "yours! ***")
                return glory, True
    return glory, False


def main():
    facets = [{"name": f["name"], "thirst": f["thirst"], "dice": [],
               **{k: v for k, v in f.items() if k not in ("name", "thirst")}}
              for f in FAUCETS]
    total, brass_used, bucket = 0, False, []

    print(ART)
    if "-v" in sys.argv:
        print(__doc__)
    else:
        print("  Reach %d Glory in %d nights. Type 'help' while placing "
              "a die for the command list." % (GOAL, NIGHTS))

    won = False
    for night in range(1, NIGHTS + 1):
        glory, keg = 0, KEG
        while True:
            show(facets, bucket, glory, night, keg, brass_used)
            if keg <= 0:
                print("\n  The keg is empty. Night %d ends." % night)
                break
            n_roll = max(1, keg - (1 if any(f.get("skip_next")
                                            for f in facets) else 0))
            for f in facets:
                f.pop("skip_next", None)
            roll = [random.randint(1, 6) for _ in range(n_roll)]
            print("\n  The keg rolls: %s   (%d die%s to place)"
                  % (roll, len(roll), "s" if len(roll) > 1 else ""))

            placed_all = True
            for di, die in enumerate(roll):
                while True:
                    cmd = input("  die %d/%d = %d > (1-9, s, m, b, p, "
                                "help): " % (di + 1, len(roll), die)
                                ).strip().lower()
                    if cmd == "help":
                        print("  1-9 assign | s spill | m move (faucet 5)"
                              " | b reroll (faucet 4, once)"
                              " | p pass/end night | q quit")
                        continue
                    if cmd == "q":
                        print("\n  You hang up your apron. Final Glory: %d"
                              % total)
                        return
                    if cmd == "p":
                        print("  You pass. %d unplaced die(s) go to slop."
                              % (len(roll) - di))
                        placed_all = False
                        break
                    if cmd == "b":
                        if brass_used:
                            print("  Old Brass is worn out (once per "
                                  "game).")
                            continue
                        if not any(f["dice"] for f in facets):
                            print("  Nothing held to reroll.")
                            continue
                        brass_used = True
                        for f in facets:
                            f["dice"] = [random.randint(1, 6)
                                         for _ in f["dice"]]
                        print("  Old Brass shudders - all held dice "
                              "reroll!")
                        glory, w = handle_drains(facets, glory)
                        if w:
                            won = True
                        break
                    if cmd == "m":
                        src = facets[4]
                        if not src["dice"]:
                            print("  Hollow Leg holds nothing.")
                            continue
                        dest = input("  move die %s to faucet (1-9, "
                                     "not 5): " % src["dice"][-1]).strip()
                        if not (dest.isdigit() and 1 <= int(dest) <= 9
                                and int(dest) != 5):
                            print("  Bad faucet.")
                            continue
                        d = src["dice"].pop()
                        facets[int(dest) - 1]["dice"].append(d)
                        print("  Moved %d to %s." %
                              (d, facets[int(dest) - 1]["name"]))
                        glory, w = handle_drains(facets, glory)
                        if w:
                            won = True
                        break
                    if cmd == "s":
                        bucket.append(die)
                        if len(bucket) > BUCKET_MAX:
                            glory = sour_flood(facets, glory,
                                               "bucket overflow")
                            bucket.clear()
                        else:
                            print("  Slop! %d in the bucket (%d/%d)." %
                                  (die, len(bucket), BUCKET_MAX))
                        break
                    if not (cmd.isdigit() and 1 <= int(cmd) <= 9):
                        print("  ? try 1-9, s, m, b, p, help")
                        continue
                    f = facets[int(cmd) - 1]
                    if cmd == "8" and die == 1 and f.get("wild"):
                        wv = input("  WILD on Black Tap! name a value "
                                   "1-6: ").strip()
                        if wv.isdigit() and 1 <= int(wv) <= 6:
                            die = int(wv)
                            print("  The 1 flows as %d." % die)
                    f["dice"].append(die)
                    s = sum(f["dice"])
                    print("  %s holds %s (sum %d / thirst %d)." %
                          (f["name"], f["dice"], s, f["thirst"]))
                    if f["thirst"] == 8 and die == 6:
                        f["dice"].append(6)
                        s = sum(f["dice"])
                        print("  Iron Gut doubles the six! (sum %d)" % s)
                    if s > f["thirst"] and not f.get("pair"):
                        glory = sour_flood(facets, glory,
                                           "%s overflowed (%d > %d)" %
                                           (f["name"], s, f["thirst"]))
                    else:
                        glory, w = handle_drains(facets, glory)
                        if w:
                            won = True
                    break
                if won or not placed_all:
                    break
            if won or not placed_all:
                break

        total += glory
        print("\n  --- Dawn of night %d: +%d Glory banked (total %d/%d)."
              % (night, glory, total, GOAL))
        if won or total >= GOAL:
            break

    print("\n" + "=" * 64)
    if won or total >= GOAL:
        print("  VICTORY! The copper sings with %d Glory." % total)
    else:
        print("  The cellar keeps its secrets. Final Glory: %d/%d." %
              (total, GOAL))
    print("=" * 64)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n  The taps run dry. Farewell.")
