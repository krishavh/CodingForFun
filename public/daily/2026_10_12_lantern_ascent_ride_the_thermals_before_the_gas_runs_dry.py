# Daily Terminal Drop
# Date: 2026-10-12
# Title: Lantern Ascent: Ride the thermals before the gas runs dry

# Daily Terminal Drop
#!/usr/bin/env python3
"""LANTERN ASCENT - an original terminal game of balloon and burner.

You pilot a hot-air balloon. The sky is a vertical strip: your basket
starts on the GROUND and the clouds pour in from the top. The wind
pushes your balloon LEFT or RIGHT each turn -- you fire the BURNER
to rise and release to sink. Catch THERMALS (rising air) for FREE
lift, dodge STORM CLOUDS (they zap your gas)!

Legend (each row of sky, top to bottom):
  ^  thermal (ride it: +2 lift this turn)
  #  storm cloud (hit it: -15 gas, bounce down 1)
  .  open sky
  =  ground (start here, land here to finish)

Each TURN the sky FALLS 1 row and you pick ONE:
  b  BURN (rise 1 row) costs 2 gas
  f  FLOAT (hold height) costs 1 gas
  v  VENT (sink 1 row) gains 3 gas (hot air out, cool air in!)
  q  quit the sky

Gas starts 100. Storm clouds zap 10 (no bump -- just hot gas!)
If gas hits 0 you drop like a stone!
Reach 40 rows of climb (ALTITUDE 40) to WIN the sky.
Land softly: gas left + score = your final!
"""
import random

HEIGHT = 14
WIDTH = 30
GOAL = 40
GROUND = 0

WIND = ["left", "right", "still"]
THERMAL, STORM, OPEN, GND = "^", "#", ".", "="


def new_row():
    """Build one row of sky (top edge coming down)."""
    row = [OPEN] * WIDTH
    for _ in range(random.randint(0, 3)):
        row[random.randrange(WIDTH)] = THERMAL
    for _ in range(random.randint(1, 3)):
        row[random.randrange(WIDTH)] = STORM
    return row


def draw(rows, alt, x, gas, score, wind, msg):
    print()
    print(f"ALT {alt}/{GOAL}   gas:{gas}   score:{score}   wind:{wind}")
    print("  +" + "-" * WIDTH + "+")
    # rows list index 0 = top of screen (highest sky shown)
    screen_top = alt + 6  # rough: show sky above and below balloon
    for s in range(HEIGHT - 1, -1, -1):
        sky_alt = alt + s - 4  # balloon sits 4 rows up from bottom
        if sky_alt < 0:
            row = [GND] * WIDTH
        elif sky_alt < len(rows):
            row = rows[sky_alt]
        else:
            row = [OPEN] * WIDTH  # sky yet to come (hidden mystery!)
        line = "|" + "".join(row) + "|"
        if s == 4:
            # balloon marker on this row
            line = "|" + "".join(
                "O" if i == x else c for i, c in enumerate(row)
            ) + "|"
        print(f"{s:>2}{line}")
    print("  +" + "-" * WIDTH + "+")
    if msg:
        print(msg)
    print("b=burn(fire)  f=float  v=vent(sink)  q=quit", end="")


def main():
    random.seed()
    rows = []
    for _ in range(80):
        rows.append(new_row())
    alt = 0
    x = WIDTH // 2
    gas = 100
    score = 0
    msg = "Fire the burner! Climb to altitude 40."
    while True:
        wind = random.choice(WIND)
        draw(rows, alt, x, gas, score, wind, msg)
        cmd = input(" > ").strip().lower()
        if cmd == "q":
            print(f"You quit the sky. Final score: {score}")
            return
        if cmd not in ("b", "f", "v"):
            msg = "? pick b, f, v or q"
            continue
        # gas cost / gain
        if cmd == "b":
            gas -= 2
            alt += 1
        elif cmd == "f":
            gas -= 1
        else:
            gas += 3
            if alt > 0:
                alt -= 1
        # thermal lift (free +1 if floating/burning in a thermal)
        here = rows[alt] if 0 <= alt < len(rows) else None
        if here and here[x] == THERMAL and cmd != "v":
            alt += 1
            msg = "Thermal lift! +1 extra row up."
            while 0 <= alt < len(rows) and rows[alt][x] == THERMAL:
                alt += 1
                score += 1
            if not (0 <= alt < len(rows) and rows[alt][x] == THERMAL):
                pass  # thermal chain ends here, msg stays set
        else:
            msg = None
        # storm zap (check AFTER move)
        here = rows[alt] if 0 <= alt < len(rows) else None
        if here and here[x] == STORM:
            gas -= 10
            score = max(0, score - 10)
            msg = "STORM ZAP! -10 gas, -10 score."
        # wind drift (after move, before next draw)
        if wind == "left" and x > 0:
            x -= 1
        elif wind == "right" and x < WIDTH - 1:
            x += 1
        # score altitude climbed
        score += 1
        # gas check
        if gas <= 0:
            print()
            print("GAS EMPTY! You drop like a stone!")
            print(f"Final altitude: {alt}. Score: {score}")
            return
        # win check
        if alt >= GOAL:
            print()
            print(f"SKY WON! Altitude {alt}! Gas left: {gas}")
            print(f"FINAL SCORE: {score + gas}")
            return
        # rows scroll DOWN the screen as you climb: drop lowest,
        # extend sky above (climb higher, sky never ends)
        if len(rows) < alt + 40:
            for _ in range(20):
                rows.append(new_row())


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Blue yonder forever. Bye!")
