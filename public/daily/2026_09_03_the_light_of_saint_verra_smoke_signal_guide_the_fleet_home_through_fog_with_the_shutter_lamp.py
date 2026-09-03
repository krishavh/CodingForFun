# Daily Terminal Drop
# Date: 2026-09-03
# Title: The Light of Saint Verra: Smoke & Signal: guide the fleet home through fog with the shutter lamp

# Daily Terminal Drop
# Date: 2026-09-03

#!/usr/bin/env python3
"""
THE LIGHTHOUSE OF SAINT VERRA :: SMOKE & SIGNAL
===============================================
You are the keeper of the last manned lighthouse on the Verra coast.
Tonight the fog is thick and the fleet is coming home. The lamp must
burn bright, the fog bell must sound, and above all you must SPEAK
to the ships in light: the shutter in front of the lamp opens and
closes to spell code — long flashes and short — and every ship that
reads your message correctly will steer for the safe channel.

Each turn is a quarter-hour of the night (12 turns until dawn).
Three things demand you:

  SHIPS approach the reef. Each carries a signal request shown as a
  dotted/dashed pattern. Before the ship reaches the reef line
  (its DISTANCE hits 0), you must send its pattern exactly. A ship
  that reads its own signal steers safe; one that doesn't wrecks,
  and your keeper's heart takes the loss.

  OIL burns constantly. The lamp consumes oil every turn; a stoked
  lamp consumes more but lights farther (ships read you from
  farther away and read faster).

  YOUR HAND tires. Sending costs stamina; rest recovers it. A weary
  keeper fumbles the shutter and garbles letters.

Sending is the game's heart: type the pattern as dots (.) and dashes
(-), e.g.  ..-  You can send in pieces — a ship remembers what it has
received so far and matches against its request.

Commands:
  send <pattern>   flash the shutter in . and - (e.g. send .-.-)
  stoke            raise the lamp pressure (brighter, faster reading,
                   costs extra oil)
  rest             catch your breath (+3 stamina, ships keep coming)
  look             read the water: ships, distances, oil, lamp, hand
  dawn             end the night with whoever is still afloat
  quit             walk away from the light

Every ship you guide home is a life saved. The sea remembers both kinds.
"""
import random
import sys

TURNS = 12
SHIPS = 4

BANNER = r"""
      |
      |*
   ___|_*___          ~ the light of Saint Verra ~
  /___|___/|          the fog is on the water
      |*|
      |*|
     ~~~~~~~
"""

# lengths of requested patterns grow harder as the night deepens
def make_request(rng, turn):
    n = rng.choice([3, 3, 4]) if turn < 6 else rng.choice([4, 5, 5])
    return "".join(rng.choice("....--") for _ in range(n))


def render(pat):
    return " ".join("-" if c == "-" else "." for c in pat)


class Ship:
    def __init__(self, rng, turn):
        self.request = make_request(rng, turn)
        self.received = ""
        self.distance = rng.randint(4, 6)
        self.name = rng.choice(
            ["the Marigold", "the Kestrel", "old Salt Row",
             "the Pale Widow", "the Twice-Lucky", "the Cormorant"])
        self.fed = False  # got its exact signal -> safe

    def matched(self):
        return self.received == self.request


def main():
    rng = random.Random()
    print(BANNER)
    print("The fog bell swings. The fleet is out there in the grey.")
    oil, lamp, stamina, saved, lost = 30, 1, 10, 0, 0
    fleet, turn = [], 0
    fleet.append(Ship(rng, turn))

    while turn < TURNS:
        print()
        print(f"--- quarter-hour {turn + 1} of {TURNS} ---")
        print(f"OIL {oil}  LAMP {'bright' if lamp else 'low'}  "
              f"HAND {stamina}/10  saved {saved}  lost {lost}")
        for s in fleet:
            mark = "SAFE" if s.fed else ("reading" if s.received else "-")
            print(f"  {s.name:16s} dist {s.distance}   wants: "
                  f"{render(s.request)}   sent: {render(s.received) or 'nothing'}  [{mark}]")
        cmd = input("> ").strip().lower()
        if cmd.startswith("send "):
            pat = cmd[5:].replace(" ", "")
            if not pat or any(c not in ".-" for c in pat):
                print("The shutter sticks. Use only dots and dashes.")
                continue
            cost = 2 + len(pat) // 2 + (1 if lamp else 0)
            if stamina < cost:
                print("Your hand shakes too hard to work the shutter. rest first.")
                continue
            stamina -= cost
            if rng.random() > 0.9 - (0.1 if not stamina else 0):
                print("A cough at the wrong moment — the flash garbles!")
                pat = pat[:-1] + ("." if pat[-1] == "-" else "-")
            reach = 4 if lamp else 2
            for s in fleet:
                if s.fed:
                    continue
                if s.distance <= reach or len(s.received) > 0:
                    s.received += pat
                    if s.matched():
                        s.fed = True
                        saved += 1
                        print(f"  {s.name} reads its signal complete — "
                              f"it heaves about toward the channel!")
                    elif len(s.received) >= len(s.request):
                        s.received = s.received[-(len(s.request) - 1):] if len(s.request) > 1 else ""
                        print("  ...a wrong pattern. The ship's bell rings angrily.")
            print(f"  the lamp flashes: {render(pat)}")
        elif cmd == "stoke":
            if oil < 3:
                print("Not enough oil to build pressure.")
                continue
            oil -= 2
            lamp = 1
            print("Pressure climbs; the beam reaches farther into the fog.")
        elif cmd == "rest":
            stamina = min(10, stamina + 3)
            print("You lean on the rail and breathe.")
        elif cmd == "look":
            print(f"oil {oil}, lamp {'bright (reach 4)' if lamp else 'low (reach 2)'}, "
                  f"hand {stamina}/10, turn {turn + 1}/{TURNS}")
        elif cmd == "dawn":
            break
        elif cmd == "quit":
            print("You leave the light dark. The sea will not forgive it.")
            return
        else:
            print("send <pattern> | stoke | rest | look | dawn | quit")
            continue

        # time passes
        turn += 1
        oil -= 1 + (1 if lamp else 1)
        if oil <= 0:
            oil = 0
            lamp = 0
            print("The lamp gutters low — out of oil pressure!")
        if oil == 0 and rng.random() < 0.3:
            stamina = max(0, stamina - 1)
        for s in fleet:
            s.distance -= 1
            if s.distance <= 0 and not s.fed:
                lost += 1
                print(f"  {s.name} strikes the reef. You hear the hull go "
                      f"out like a candle.")
        fleet = [s for s in fleet if s.distance > 0 and not s.fed]
        if turn < TURNS and len(fleet) < 2 and saved + lost < SHIPS:
            fleet.append(Ship(rng, turn))
        if oil <= 3 and lamp == 0 and turn < TURNS:
            print("The oil tank is nearly dry. Stoking costs what you have left.")

    print()
    print(f"Dawn. The fog lifts off the Verra coast.")
    print(f"Ships guided home: {saved}   lost to the reef: {lost}")
    if saved >= 4:
        print("The fleet will drink to your name in every port tonight.")
    elif saved > lost:
        print("Most came home. The bell rings once for those who didn't.")
    else:
        print("A hard night. The light shone, but the sea is the sea.")
    sys.exit(0 if saved > lost else 1)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nThe night ends abruptly. The light keeps burning anyway.")
