# Daily Terminal Drop
# Date: 2026-08-31
# Title: The Windmill: Ballast & Grain

#!/usr/bin/env python3
"""
THE WINDMILL :: BALLAST & GRAIN
===============================
You are the miller of the last windmill on the Zandwacht flats. On the
night the grain barges arrive, the wind does not ask permission — it
gusts from whichever quarter it pleases, and it wants to spin your
sails to splinters. You must bring the load home: grind the grain,
deliver the flour, and keep the great brake from burning.

The sails face one of four quarters. The wind blows from its own
quarter. Sails square to the wind GAIN speed; sails edge-on to it LOSE
speed; sails in between HOLD roughly steady. Too slow and the millstone
stalls — the barges wait for no one. Too fast and the cap strains
toward burnout. Somewhere in between is the sweet band where flour is
ground at full rate.

Each turn the wind gleans a forecast quarter (mostly true). Steer the
sails, feather them, or brake. Every point of speed grinds grain; every
point of strain ages the brake.

Commands:
  steer <n>       set sail quarter relative to the wind
                  (-2 = run, +2 = hard edge-on; 0 = square)
                  >0 feathers against the wind (slows, cools)
                  <0 runs before it (speeds, heats)
  brake <n>       apply n points of brake (1-3) to shed speed
  bake            end the day: bank your flour and tally the barges
  look            show the mill, the wind, and your numbers
  quit            strike the flag

Terms:
  SPEED    turn speed of the sails (1-12). Sweet band: 6..8
  STRAIN   how hard the cap fights the bearings (0-10)
  HEAT     brake temperature (0-10). At 10 the brake fails.
  GRAIN    sacks left to grind today (start 16)
  FLOUR    sacks ground and banked
"""
import random
import sys

WINDS = {1: "north", 2: "east", 3: "south", 4: "west"}
ARROWS = {1: "^", 2: ">", 3: "v", 4: "<"}

GRAIN_START = 16
MAX_SPEED = 12
MAX_STRAIN = 10
MAX_HEAT = 10
SWEET_LO = 6
SWEET_HI = 8

BANNER = r"""
      \\  |  //
   '--   \\|/   --'
  *      .-.      *     ~ ~ ~
   '--  (   )  --'      ~ the Zandwacht flats ~
  *      '-'      *     ~ ~ ~
   '--   /|\\   --'
      //  |  \\
"""


def clamp(n, lo, hi):
    return max(lo, min(hi, n))


def bar(value, hi, fill="#", empty="."):
    return fill * value + empty * (hi - value)


class Mill:
    def __init__(self, rng):
        self.rng = rng
        self.speed = rng.randint(4, 6)
        self.strain = 2
        self.heat = 0
        self.grain = GRAIN_START
        self.flour = 0
        self.wind = rng.randint(1, 4)
        self.forecast = self.wind
        self.trim = 0            # last steer relative to wind
        self.brake_on = 0
        self.gusts_survived = 0
        self.day = 1

    def forecast_wind(self):
        """Mostly-true forecast: 2 of 3 turns it is right."""
        if self.rng.random() < 2.0 / 3.0:
            self.forecast = self.wind
        else:
            wrong = [q for q in WINDS if q != self.wind]
            self.forecast = self.rng.choice(wrong)

    def gust(self):
        """The wind may swing a quarter. Returns a message."""
        if self.rng.random() < 0.30:
            old = self.wind
            self.wind = (self.wind + self.rng.choice([-1, 1]) - 1) % 4 + 1
            if self.wind != old:
                return "The wind swings a quarter — it now blows from the %s!" % WINDS[self.wind]
        return ""

    def resolve(self):
        """Physics of one turn. Trim: -2 run ... +2 feather."""
        t = self.trim
        if t < 0:      # running before the wind
            self.speed += 2
            self.strain += 1
            self.heat -= 1 if self.heat > 0 else 0
        elif t == 0:   # square to the wind: sweet harness
            self.speed += 1 if self.speed < 7 else (-1 if self.speed > 8 else 0)
        else:          # feathering against it
            self.speed -= t
            self.strain -= 1
            self.heat += 0

        # brake always drags a little if applied earlier this turn
        if self.brake_on:
            self.speed -= self.brake_on
            self.heat += self.brake_on
            self.brake_on = 0

        # wind pressure on the cap
        self.strain += 1 if self.speed > 8 else 0
        self.strain = clamp(self.strain, 0, MAX_STRAIN)
        self.heat = clamp(self.heat, 0, MAX_HEAT)
        self.speed = clamp(self.speed, 1, MAX_SPEED)

        # grinding
        ground = 0
        if SWEET_LO <= self.speed <= SWEET_HI:
            ground = 2
            note = "The stone sings — full rate."
        elif 4 <= self.speed <= 5 or self.speed in (9, 10):
            ground = 1
            note = "The stone grinds, but grudgingly."
        elif self.speed <= 3:
            note = "The stone stalls and sulks."
        else:
            note = "The stone races, flour scorches."
            if self.grain > 0 and self.rng.random() < 0.4:
                self.grain -= 1
                note += " A sack is wasted!"

        ground = min(ground, self.grain)
        self.grain -= ground
        self.flour += ground
        return ground, note

    def overheat(self):
        return self.heat >= MAX_HEAT

    def broken(self):
        return self.strain >= MAX_STRAIN


def draw(mill):
    print(BANNER)
    print("  Day %d   WIND from the %s %s   (forecast said %s %s)" % (
        mill.day, WINDS[mill.wind], ARROWS[mill.wind],
        WINDS[mill.forecast], ARROWS[mill.forecast]))
    print("  SPEED %2d  %s" % (mill.speed, bar(mill.speed, MAX_SPEED)))
    band = " " * 4 + " " * SWEET_LO + "[" + "~" * (SWEET_HI - SWEET_LO + 1) + "]"
    print("         " + band[4:])
    print("  STRAIN   %s  (%d/10)" % (bar(mill.strain, MAX_STRAIN, "@"), mill.strain))
    print("  HEAT     %s  (%d/10)" % (bar(mill.heat, MAX_HEAT, "*"), mill.heat))
    print("  GRAIN %2d left   FLOUR %2d banked" % (mill.grain, mill.flour))


def help_text():
    print(__doc__.split("Commands:")[1])


def play():
    rng = random.Random()
    mill = Mill(rng)
    print("\n--- THE WINDMILL :: BALLAST & GRAIN ---")
    draw(mill)
    print("Type 'help' for commands.")

    while True:
        try:
            line = input("miller> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nThe mill stands silent.")
            return

        if not line:
            continue

        if line in ("quit", "q"):
            print("You strike the flag with %d sacks of flour banked." % mill.flour)
            return

        if line in ("help", "?"):
            help_text()
            continue

        if line == "look":
            draw(mill)
            continue

        if line.startswith("steer"):
            try:
                t = int(line.split()[1])
            except (IndexError, ValueError):
                print("Usage: steer <n>   (-2 to +2)")
                continue
            mill.trim = clamp(t, -2, 2)
            print("You trim the sails %s the wind." % (
                "before" if mill.trim < 0 else "against" if mill.trim > 0 else "square to"))
            mill.forecast_wind()
            gust_msg = mill.gust()
            ground, note = mill.resolve()
            print("  %s" % note)
            if gust_msg:
                print("  " + gust_msg)
            if mill.broken():
                print("The cap seizes — the bearings scream and strip. The barges sail on.")
                print("FINAL: %d sacks of flour banked over %d day(s)." % (mill.flour, mill.day))
                return
            if mill.overheat():
                print("The brake band glows cherry-red and fails. The sails freewheel wild.")
                print("FINAL: %d sacks of flour banked over %d day(s)." % (mill.flour, mill.day))
                return
            if mill.grain == 0:
                print("All grain ground! You bake and tally the barges.")
                print("FINAL: %d sacks of flour banked over %d day(s). Well milled." % (mill.flour, mill.day))
                return
            mill.day += 1
            draw(mill)
            continue

        if line.startswith("brake"):
            try:
                b = int(line.split()[1])
            except (IndexError, ValueError):
                print("Usage: brake <n>   (1 to 3)")
                continue
            if b < 1 or b > 3:
                print("Brake takes 1 to 3 points.")
                continue
            mill.speed = clamp(mill.speed - b, 1, MAX_SPEED)
            mill.heat += b
            mill.heat = clamp(mill.heat, 0, MAX_HEAT)
            print("You set the brake — %d point(s). Speed %d, heat %d/10." % (b, mill.speed, mill.heat))
            if mill.overheat():
                print("The brake band glows cherry-red and fails. The sails freewheel wild.")
                print("FINAL: %d sacks of flour banked over %d day(s)." % (mill.flour, mill.day))
                return
            continue

        if line == "bake":
            print("You bank %d sacks of flour and tally the barges." % mill.flour)
            print("FINAL: %d sacks over %d day(s). The tide is kind." % (mill.flour, mill.day))
            return

        print("Unknown command. Try 'help', 'steer <n>', 'brake <n>', 'bake', 'look', 'quit'.")


if __name__ == "__main__":
    play()
