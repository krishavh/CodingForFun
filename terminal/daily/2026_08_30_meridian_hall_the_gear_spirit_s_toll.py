# Daily Terminal Drop
# Date: 2026-08-30
# Title: Meridian Hall: The Gear-Spirit's Toll

"""
MERIDIAN HALL :: THE GEAR-SPIRIT'S TOLL
=======================================
The Hall of Meridian was built by clockwrights who bound a gear-spirit
beneath the floor. The spirit feeds on motion, and the only way past it
is to time your steps against the turning of the great brass gears.

Each gear turns in a fixed cycle: OPEN teeth let you stand, BLOCKED
teeth will sweep you off the tile and back to the start of the hall.
You see the phase of each gear as a countdown bar. Step across the
hall, tile by tile, and reach the far door before the spirit's patience
runs out. Every step costs one tick of patience; a wrong step costs
three more.

Gear cycle: each gear counts down from its PERIOD to 1, then repeats.
At phase 1 the gear SNAPS — its teeth sweep every tile it covers. If
the tile you stand on is covered by a snapping gear, you are swept.

Commands:
  w / a / s / d    step up, left, down, right
  look             redraw the hall with gear phases
  gear <r> <c>     inspect the gear at row r, column c
  quit             surrender to the spirit
"""
import random
import sys

HALL_W = 7
HALL_H = 5
SNAP = 1          # the phase at which teeth sweep
START = (0, 0)
EXIT = (HALL_H - 1, HALL_W - 1)

TILE_OPEN = "."
TILE_GEAR = "o"
YOU = "@"

def build_gears(rng):
    """Place gears on interior tiles. Each has a phase and period."""
    gears = {}
    spots = []
    for r in range(HALL_H):
        for c in range(HALL_W):
            if (r, c) in (START, EXIT):
                continue
            spots.append((r, c))
    rng.shuffle(spots)
    chosen = spots[:9]
    for (r, c) in chosen:
        period = rng.choice([3, 4, 5])
        gears[(r, c)] = {"phase": rng.randint(1, period), "period": period}
    return gears

def draw(pos, gears, patience):
    print()
    head = []
    for c in range(HALL_W):
        head.append(str(c + 1))
    print("    " + " ".join(head))
    for r in range(HALL_H):
        row = []
        for c in range(HALL_W):
            if (r, c) == pos:
                row.append(YOU)
            elif (r, c) in gears:
                g = gears[(r, c)]
                if g["phase"] <= SNAP:
                    row.append("O")
                else:
                    row.append("o")
                row.append(str(g["phase"]))
            else:
                row.append(TILE_OPEN)
        print("  {} {}".format(chr(ord("A") + r), " ".join(row)))
    print("  patience: {}".format("|" * max(0, patience)))

def gear_covers(pos, gears):
    """A gear covers its own tile. (Simple: one gear per tile.)"""
    return pos in gears

def snap_hit(pos, gears):
    g = gears.get(pos)
    return g is not None and g["phase"] == SNAP

def play():
    rng = random.Random()
    pos = START
    patience = 30
    steps = 0
    sweeps = 0
    gears = build_gears(rng)
    print("=" * 52)
    print("MERIDIAN HALL :: THE GEAR-SPIRIT'S TOLL")
    print("=" * 52)
    print("Reach the far door at tile {}.".format(
        chr(ord("A") + EXIT[0]) + str(EXIT[1] + 1)))
    print("Lowercase o = gear waiting, O = about to snap.")
    print("w/a/s/d to step, look, gear <r> <c>, quit.")
    draw(pos, gears, patience)

    while True:
        raw = input("hall> ").strip().lower()
        if not raw:
            continue
        if raw in ("quit", "q"):
            print("The spirit keeps its hall. You back out the way you came.")
            return
        if raw == "look":
            draw(pos, gears, patience)
            continue
        if raw.startswith("gear"):
            parts = raw.split()
            if len(parts) == 3 and parts[1].isalpha() and parts[2].isdigit():
                r = ord(parts[1][0]) - ord("a")
                c = int(parts[2]) - 1
                if 0 <= r < HALL_H and 0 <= c < HALL_W:
                    g = gears.get((r, c))
                    if g:
                        print("  gear at {}{}: period {}, phase {} (snaps at phase {}).".format(
                            parts[1], parts[2], g["period"], g["phase"], SNAP))
                    else:
                        print("  that tile is plain stone; no gear turns there.")
                else:
                    print("  no such tile in the hall.")
            else:
                print("  use: gear <letter> <number>   e.g. gear B 3")
            continue
        if raw not in ("w", "a", "s", "d"):
            print("  w/a/s/d to step, look, gear <letter> <number>, quit.")
            continue

        dr, dc = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}[raw]
        nr, nc = pos[0] + dr, pos[1] + dc
        if not (0 <= nr < HALL_H and 0 <= nc < HALL_W):
            print("  The hall wall does not yield. You stay.")
            continue

        pos = (nr, nc)
        steps += 1
        patience -= 1

        # Gears tick after every step.
        for g in gears.values():
            g["phase"] -= 1
            if g["phase"] < 1:
                g["phase"] = g["period"]

        if snap_hit(pos, gears):
            sweeps += 1
            patience -= 3
            print("  TEETH SWEEP — you are thrown back to the hall's mouth!")
            pos = START
            patience -= 3
        elif gear_covers(pos, gears):
            g = gears[pos]
            print("  You stand atop a turning gear. It grinds underfoot (phase {}/{}).".format(
                g["phase"], g["period"]))

        if pos == EXIT:
            print()
            print("=" * 52)
            print("THE FAR DOOR YIELDS.")
            print("=" * 52)
            print("Steps taken : {}".format(steps))
            print("Sweeps      : {}".format(sweeps))
            print("Patience left: {}".format(max(0, patience)))
            if sweeps == 0 and patience >= 15:
                print("The clockwrights would call this a whisper-run. Few pass")
                print("so cleanly; the spirit marks your steps and lets you go.")
            elif sweeps <= 1:
                print("A solid crossing. One scrape of the teeth and no more.")
            else:
                print("You arrive ragged and gear-marked, but you arrive.")
            return

        if patience <= 0:
            print()
            print("The spirit's patience is spent. The floor tilts and the hall")
            print("reshuffles itself around you. Run over.")
            print("You reached tile {} in {} steps with {} sweeps.".format(
                chr(ord("A") + pos[0]) + str(pos[1] + 1), steps, sweeps))
            return
        draw(pos, gears, patience)

if __name__ == "__main__":
    try:
        play()
    except (KeyboardInterrupt, EOFError):
        print("\nYou slip out of Meridian Hall.")
        sys.exit(0)
