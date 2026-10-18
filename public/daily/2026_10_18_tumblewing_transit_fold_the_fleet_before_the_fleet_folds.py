# Daily Terminal Drop
# Date: 2026-10-18
# Title: Tumblewing Transit: Fold the fleet before the fleet folds

# Daily Terminal Drop
# Date: 2026-10-18
# Title: Tumblewing Transit: Fold the fleet before the fleet folds
#!/usr/bin/env python3
"""TUMBLEWING TRANSIT - race paper planes across a folding sky!

You fly a fleet of paper planes (P) through a windy canyon.
Each turn the WIND blows (arrows <<< >>> show it). Your plane
DRIFTS with the wind unless you FLAP against it. Land on rings (O)
to score, dodge storm cells (#) -- they crumple your plane!

Legend:
  P  your plane (1, start of 3 in the fleet)
  O  ring -- land here for 100 points, next plane launches!
  #  storm cell -- hits cost 1 plane (crumpled!)
  .  empty sky

COMMANDS each turn (plane moves DOWN 1 row too):
  a  flap left,  d  flap right,  s  drift straight,  q  quit

WIND shifts each turn: -2..+2 columns. 3 planes per fleet.
Score 3 rings before the fleet is crumpled -- or canyon floor!
Rows 12 tall, 40 wide. Floor = row 11 (land soft or CRASH).
"""
import random
import shutil
import subprocess

W = 40
H = 12
FLEET = 3
RINGS_GOAL = 3


def clear():
    subprocess.run(["clear"], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def fresh_rows():
    rows = [["."] * W for _ in range(H)]
    spots = random.sample(range(W * H), 6)
    for s in spots[:3]:
        rows[s // W][s % W] = "#"
    for s in spots[3:]:
        rows[s // W][s % W] = "O"
    return rows


def draw(rows, px, py, wind, pts, planes, rings, msg):
    clear()
    cols = min(max(term_cols(), 40), 100)
    print("TUMBLEWING TRANSIT".center(cols))
    print(("points:%d  planes:%d  rings:%d/%d  wind:%+d" %
           (pts, planes, rings, RINGS_GOAL, wind)).center(cols))
    print()
    grid = [list(r) for r in rows]
    if 0 <= py < H and 0 <= px < W:
        grid[py][px] = "P"
    for r in grid:
        print("  " + "".join(r))
    print()
    arrow = ("<" * abs(wind)) if wind < 0 else (">" * wind) if wind > 0 else "|"
    print("  wind [%s%s%s]" % ("." * (10 + min(0, wind)),
                                arrow or "|",
                                "." * (10 - max(0, wind))))


def main():
    random.seed()
    rows = fresh_rows()
    px, py = W // 2, 0
    pts, planes, rings = 0, FLEET, 0
    msg = "Flap a/d, drift s. Land on O rings, dodge # storms!"
    while True:
        wind = random.randint(-2, 2)
        draw(rows, px, py, wind, pts, planes, rings, msg)
        cmd = input("  [a/d/s/q] wind%+d> " % wind).strip().lower()
        if cmd == "q":
            print("Fleet grounded. Final: %d pts, %d rings." % (pts, rings))
            return
        if cmd not in ("a", "d", "s"):
            msg = "? use a/d/s (or q quit)"
            continue
        dx = {"a": -1, "d": 1, "s": 0}[cmd]
        nx = max(0, min(W - 1, px + dx + wind))
        ny = py + 1
        msg = "drift..."
        if ny >= H:
            msg = "Touchdown on the canyon floor!"
            pts += 10
            planes -= 1
            if planes <= 0:
                draw(rows, px, H - 1, wind, pts, planes, rings, msg)
                print("  FLEET DOWN! Final: %d pts, %d rings." % (pts, rings))
                return
            rows = fresh_rows()
            px, py = W // 2, 0
            continue
        cell = rows[ny][nx]
        px, py = nx, ny
        if cell == "#":
            pts = max(0, pts - 20)
            planes -= 1
            msg = "CRUMPLED in a storm cell! -20"
            if planes <= 0:
                draw(rows, px, py, wind, pts, planes, rings, msg)
                print("  FLEET DOWN! Final: %d pts, %d rings." % (pts, rings))
                return
            rows = fresh_rows()
            px, py = W // 2, 0
        elif cell == "O":
            pts += 100
            rings += 1
            msg = "RING LANDING! +100 -- next plane up!"
            if rings >= RINGS_GOAL:
                draw(rows, px, py, wind, pts, planes, rings, msg)
                print("  FLEET SOARS! Final: %d pts, all %d rings!" % (pts, rings))
                return
            rows = fresh_rows()
            px, py = W // 2, 0
        else:
            pts += 1


if __name__ == "__main__":
    main()
