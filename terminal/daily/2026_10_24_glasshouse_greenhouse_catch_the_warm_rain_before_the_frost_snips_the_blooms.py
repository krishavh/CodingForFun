# Daily Terminal Drop
# Date: 2026-10-24
# Title: Glasshouse Greenhouse: Catch the warm rain before the frost snips the blooms

#!/usr/bin/env python3
"""GLASSHOUSE GREENHOUSE - raise the tropical blooms before winter snips them!

Under a crackling glass roof, rare blooms drink the warm rain.
You are the greenhouse keeper: CATCH falling raindrops in your
watering can, then POUR them on thirsty blooms before the
cold draft creeps along the floor!

Legend:
  @  you (push the ladder left/right along the roof)
  o  raindrops (fall slow, then fast!)
  1-4  thirsty blooms (each needs 4 sips)
  ~  puddle (catch drops here too, but blooms pay double!)

HOW IT WORKS:
  Rain falls from the glass roof. Move your can to catch a drop
  (1 sip) or let it splash the puddle (0 sips, wasted!). Stand
  beside a bloom and POUR to water it (1 sip per drop, up to 4).
  Watered blooms WARM the air -- winter snips any bloom that
  stays thirsty 6 turns in a row (it drops to 0 and wilts!).

COLD SNAP: every 10 turns the draft races along the floor --
  all blooms lose 1 sip unless WARM (recently watered)!

GOAL: grow all 4 blooms to full (16 sips) before 45 turns
  of winter! Build CASCades: caught drops warm the nearest bloom!
COMMANDS: a/d move   e pour   q quit
"""
import random
import shutil
import subprocess

W, H = 34, 15
GOAL = 4 * 4
TURNS = 45
WILT = 6
WARM_TURNS = 3

DIRS = {"a": -1, "d": 1}


def clear():
    subprocess.run(["clear"], shell=False)


def new_house():
    """Blooms sit on the floor, can starts center roof."""
    floor = [[random.randint(1, 4), 0, 0] for _ in range(4)]  # [sips, dry, warm]
    drops = []
    return floor, drops


def draw(floor, drops, px, cup, turn, pts, msg):
    print(f"GLASSHOUSE GREENHOUSE  turn {turn}/{TURNS}  sips {pts}/{GOAL}")
    print("a/d move  e pour  q quit")
    print("+" + "-" * W + "+")
    grid = [[" "] * W for _ in range(H - 2)]
    for (dx, dy) in drops:
        if 0 <= dy < H - 2:
            grid[dy][dx] = "o"
    if 0 <= px < W:
        grid[0][px] = "@" if grid[0][px] == " " else "@"
    rows = ["|" + "".join(r) + "|" for r in grid]
    rows.append("+" + "-" * W + "+")
    floor_line = []
    for i, (sips, dry, warm) in enumerate(floor):
        bx = 2 + i * 8
        floor_line.append(f"{bx}:{'*' * sips}{'.' * (4 - sips)}")
    print("\n".join(rows))
    print("Blooms: " + "  ".join(f"{i + 1}[{'*' * s}{'.' * (4 - s)}]" for i, (s, d, w) in enumerate(floor)))
    print(f"Can: {cup}/4 sips   Puddle catches: wasted")
    if msg:
        print(msg)
    print("")


def bloom_x(i):
    return 2 + i * 8


def nearest_bloom(px):
    best, bd = 0, 999
    for i in range(4):
        d = abs(bloom_x(i) - px)
        if d < bd:
            bd, best = d, i
    return best


def spawn(drops):
    if random.random() < 0.7:
        drops.append((random.randint(1, W - 2), 0))


def cold_snap(floor):
    for b in floor:
        b[0] = max(0, b[0] - 1)
        b[2] = 0


def main():
    random.seed()
    floor, drops = new_house()
    px = W // 2
    cup = 0
    pts = sum(b[0] for b in floor)
    turn = 1
    msg = "Catch rain. Pour blooms. Beat the frost!"

    while turn <= TURNS:
        if pts >= GOAL:
            break
        spawn(drops)
        # gravity
        new_drops = []
        for (dx, dy) in drops:
            ny = dy + 1
            if ny >= H - 2:
                continue  # splashes floor
            new_drops.append((dx, ny))
        drops = new_drops
        # catch: drop lands on can row (row 0) near px
        keep = []
        for (dx, dy) in drops:
            if dy == 1 and abs(dx - px) <= 1 and cup < 4:
                cup += 1
            else:
                keep.append((dx, dy))
        drops = keep
        draw(floor, drops, px, cup, turn, pts, msg)
        cmd = input("keeper> ").strip().lower()
        msg = ""
        acted = False
        if cmd == "q":
            print(f"\nThe glass fogs. Final sips: {pts}/{GOAL}")
            return
        elif cmd in DIRS and len(cmd) == 1:
            px = max(1, min(W - 2, px + DIRS[cmd]))
            acted = True
        elif cmd == "e":
            if cup <= 0:
                msg = "Can is empty!"
            else:
                # pour on bloom nearest to px
                i = nearest_bloom(px)
                if floor[i][0] < 4:
                    floor[i][0] += 1
                    floor[i][2] = WARM_TURNS
                    pts += 1
                    cup -= 1
                    msg = f"Bloom {i + 1} sips! ({floor[i][0]}/4)"
                else:
                    msg = "That bloom is full!"
        else:
            msg = "? a/d move, e pour, q"
        # dry count + warm decay
        for b in floor:
            if b[2] > 0:
                b[2] -= 1
            else:
                b[1] += 1
                if b[1] >= WILT and b[0] < 4:
                    b[0] = 0
                    b[1] = 0
                    msg = (msg + " " if msg else "") + "FROST SNIPPED a bloom!"
        # rain more when acted (pace)
        if acted and random.random() < 0.5:
            spawn(drops)
        if turn % 10 == 0:
            cold_snap(floor)
            msg = (msg + " " if msg else "") + "COLD SNAP! -1 sip all!"
        turn += 1

    draw(floor, drops, px, cup, turn, pts, "")
    if pts >= GOAL:
        print(f"\nTHE GLASSHOUSE BLOOMS! All warm in {turn} turns!")
    else:
        print(f"\nWinter wins. Final sips: {pts}/{GOAL}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nThe glasshouse door creaks shut. Bye!")
