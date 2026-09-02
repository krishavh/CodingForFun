# Daily Terminal Drop
# Date: 2026-09-02
# Title: The Glasshouse: Frost & Harvest

#!/usr/bin/env python3
"""
THE GLASSHOUSE :: FROST & HARVEST
=================================
The night frost is coming down the valley and you are the keeper of
the Emperor's glasshouse. The old heating pipes groan; the boiler
stokes on wood you must feed by hand; and outside, the cold gnaws
at the glass seams. Keep the tender things alive until dawn.

Each turn is one hour of the night (you have 8 hours until sunrise).
Every hour the OUTSIDE cold bites; the glasshouse TEMPERATURE falls
or rises depending on the fire and the vents. Plants have HARDINESS:
ferns are tender, figs are tougher. If a plant's zone freezes, you
lose it. But overheat the glass and the tender leaves scorch instead.

You also have a fixed supply of WOOD. Spend it wisely — the cold
deepens toward 4 AM and then relents toward dawn.

Commands:
  stoke <n>       shovel n logs into the boiler (1-3). Each log raises
                  heat for the next few hours (coals linger).
  vent <n>        open n vents (0-3) to dump heat. Vents also let a
                  little cold draught in.
  water <plant>   give a plant a drink (they drink three times a night —
                  keep them topped up or they wither)
  look            read the thermometers, coals, wood, and plants
  dawn            bank your survivors early and end the night
  quit            abandon the glasshouse

Reading the glass:
  TEMP    inside temperature, degrees of warmth above freezing (0-12)
  COALS   latent heat in the boiler (stoked logs burn off slowly)
  COLD    outside bite each hour (grows toward 4 AM, then fades)
  Plants show [ok] warm, [!] chilled, [X] lost
"""
import random
import sys

HOURS = 8
WOOD_START = 14
MAX_TEMP = 12

# name, hardiness (temp below which it takes freeze damage), scorch (temp above which it scorches)
PLANTS = [
    ("maiden fern", 4, 13),
    ("night orchid", 5, 13),
    ("lemon tree", 2, 13),
    ("old fig", 1, 13),
    ("jasmine", 3, 13),
]

BANNER = r"""
   .-~~~-.
 ,'  ___  `.      ~ the Emperor's glasshouse ~
 |  (___)  |        the frost comes tonight
  `.----.-'
  / |   | \\
 o  |  o|  o        ~ * . ~ * . ~
    |___|
"""

DEATHS = {
    "frost": "blackened by frost",
    "scorch": "scorched on hot glass",
    "drought": "withered dry",
}


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def cold_at(hour):
    # outside bite: peaks around hour 4-5
    return [3, 4, 5, 6, 7, 7, 6, 4][hour]


def bar(v, lo, hi, width=12, fill="=", empty="."):
    n = int(width * clamp((v - lo) / (hi - lo), 0, 1))
    return fill * n + empty * (width - n)


class Glasshouse:
    def __init__(self):
        self.hour = 0
        self.wood = WOOD_START
        self.temp = 6
        self.coals = 2
        self.vents = 0
        self.plants = [
            {"name": n, "hard": h, "scorch": s, "water": 5, "alive": True,
             "cause": None}
            for (n, h, s) in PLANTS
        ]
        self.log = []

    def status(self):
        print(BANNER)
        print(f"  Hour {self.hour + 1} of {HOURS} (dawn at {HOURS})")
        print(f"  OUTSIDE COLD : {cold_at(self.hour)}  "
              f"[{bar(cold_at(self.hour), 0, 8, 8, '#')}]")
        print(f"  TEMP inside  : {self.temp}  "
              f"[{bar(self.temp, 0, MAX_TEMP)}]")
        print(f"  COALS        : {self.coals}  "
              f"[{bar(self.coals, 0, 8, 8, '*')}]")
        print(f"  VENTS        : {self.vents} open")
        print(f"  WOODPILE     : {self.wood} logs left")
        print()
        for p in self.plants:
            if not p["alive"]:
                print(f"    [X] {p['name']:<13} ({p['cause']})")
                continue
            mark = "[ok]"
            if self.temp < p["hard"]:
                mark = "[!]"
            elif self.temp > p["scorch"]:
                mark = "[!]"
            if p["water"] <= 1:
                mark = "[!]"
            risk = ""
            if p["water"] <= 0:
                risk = " (parched)"
            elif self.temp < p["hard"]:
                risk = " (chilled)"
            elif self.temp > p["scorch"]:
                risk = " (scorching)"
            print(f"    {mark} {p['name']:<13} water {p['water']}/5{risk}")
        print()

    def drink(self, name):
        for p in self.plants:
            if p["alive"] and p["name"].startswith(name.lower()):
                if p["water"] >= 3:
                    print(f"  The {p['name']} is already watered.")
                else:
                    p["water"] += 1
                    print(f"  You give the {p['name']} a slow drink.")
                return
        print("  No such plant here (try: fern, orchid, lemon, fig, jasmine).")

    def hour_passes(self):
        hour = self.hour
        bite = cold_at(hour)
        heat = self.coals
        # vents: dump heat but let in a draught
        heat -= self.vents
        bite += self.vents
        self.temp = clamp(self.temp + heat - bite, 0, MAX_TEMP)
        self.coals = max(0, self.coals - 1)
        self.hour += 1

        print(f"\n  --- hour {hour + 1} passes ---")
        for p in self.plants:
            if not p["alive"]:
                continue
            if self.temp < p["hard"]:
                p["alive"] = False
                p["cause"] = DEATHS["frost"]
                print(f"  * the {p['name']} is {DEATHS['frost']}.")
            elif self.temp > p["scorch"]:
                p["alive"] = False
                p["cause"] = DEATHS["scorch"]
                print(f"  * the {p['name']} is {DEATHS['scorch']}.")
            elif p["water"] <= 0:
                p["alive"] = False
                p["cause"] = DEATHS["drought"]
                print(f"  * the {p['name']} has {DEATHS['drought']}.")
            elif self.hour in (2, 4, 6):
                # plants drink three times a night — keep them topped up
                p["water"] = max(0, p["water"] - 1)

    def tally(self):
        alive = [p["name"] for p in self.plants if p["alive"]]
        print("\n" + "=" * 46)
        if len(alive) == len(self.plants):
            print("  DAWN. Every living thing in the glass survived.")
            print("  The Emperor will hear of this night.")
        elif alive:
            print("  DAWN. The glasshouse stands, but not whole.")
            for n in alive:
                print(f"    saved: {n}")
        else:
            print("  DAWN. The glasshouse is empty. Frost had its way.")
        print("=" * 46)


def main():
    g = Glasshouse()
    print("THE GLASSHOUSE :: FROST & HARVEST")
    print("(type 'look' for the state of the glass, 'quit' to flee)")
    g.status()
    while g.hour < HOURS:
        try:
            line = input("glasshouse> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        parts = line.split()
        cmd, args = parts[0], parts[1:]

        if cmd == "quit":
            print("  You leave the glasshouse to the frost.")
            return
        elif cmd == "look":
            g.status()
        elif cmd == "stoke":
            n = clamp(int(args[0]) if args and args[0].isdigit() else 0, 1, 3)
            if g.wood < n:
                print(f"  Only {g.wood} logs left — not enough.")
                continue
            g.wood -= n
            g.coals = clamp(g.coals + 2 * n, 0, 8)
            print(f"  You shovel {n} log(s) into the boiler. The coals "
                  f"roar ({g.coals}).")
            g.hour_passes()
        elif cmd == "vent":
            n = clamp(int(args[0]) if args and args[0].isdigit() else 0, 0, 3)
            g.vents = n
            print(f"  {n} vent(s) open. Cold draughts will find you.")
            g.hour_passes()
        elif cmd == "water":
            if args:
                g.drink(args[0])
            else:
                print("  Water what? (fern, orchid, lemon, fig, jasmine)")
        elif cmd == "dawn":
            print("  You bank the fire early and call for dawn.")
            break
        else:
            print("  ? try: stoke <1-3>, vent <0-3>, water <plant>, "
                  "look, dawn, quit")
    g.tally()


if __name__ == "__main__":
    main()
