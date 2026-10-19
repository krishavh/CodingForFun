# Daily Terminal Drop
# Date: 2026-10-19
# Title: Lantern Moth: Chase the glow before the dusk runs dry

#!/usr/bin/env python3
"""LANTERN MOTH - a dusk-lit terminal game of wings and wire.

You are a MOTH (M) drawn to the GLOW (G) of lanterns. Each lantern
you reach FLICKERS out (-fuel) and you must flutter to the NEXT.
But BATS (B) hunt in the dark -- touch one and lose a wing!

Legend:
  M  you (3 wings)
  G  glowing lantern (reach it: +100, new lantern spawns)
  B  bat (dodge! hit = -1 wing)
  o  wisp (collect: +25, tiny trail of light)
  .  night air

Each turn EVERYTHING drifts DOWN 1 row (you stay, world scrolls).
Bats chase: they flutter toward you (dx or dy, closer each turn).
COMMANDS:
  a  flutter left   d  flutter right
  w  flutter up     s  flutter down
  q  quit the dusk

Dusk FUEL burns 1 per turn (100 start). Fuel 0 = wings too tired!
Score 500 before the dark folds in -- or flutter forever!
"""
import random
import shutil
import subprocess

W = 36
H = 14


def clear():
    subprocess.run(["clear"], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def new_grid():
    return [["."] * W for _ in range(H)]


def place(grid, ch, avoid=()):
    while True:
        x = random.randrange(W)
        y = random.randrange(H)
        if grid[y][x] == "." and (x, y) not in avoid:
            grid[y][x] = ch
            return x, y


def draw(grid, px, py, fuel, wings, pts, msg):
    view = [row[:] for row in grid]
    view[py][px] = "M"
    print("\n".join("".join(r) for r in view))
    print(f"fuel {fuel}  wings {wings}  pts {pts}")
    if msg:
        print(msg)
    print("w/a/s/d move, q quit")


def wrap(x, y):
    return x % W, y % H


def step_bats(grid, bats, px, py):
    for i, (bx, by) in enumerate(bats):
        grid[by][bx] = "."
        dx = (px > bx) - (px < bx)
        dy = (py > by) - (py < by)
        if random.random() < 0.5 and dx:
            nx, ny = bx + dx, by
        elif dy:
            nx, ny = bx, by + dy
        else:
            nx, ny = bx + random.choice((-1, 0, 1)), by
        nx = max(0, min(W - 1, nx))
        ny = max(0, min(H - 1, ny))
        if grid[ny][nx] == ".":
            bx, by = nx, ny
        bats[i] = (bx, by)
        grid[by][bx] = "B"


def scroll(grid):
    for y in range(H - 1, 0, -1):
        grid[y] = grid[y - 1][:]

    grid[0] = ["."] * W


def main():
    random.seed()
    grid = new_grid()
    px, py = W // 2, H - 2
    gx, gy = place(grid, "G", avoid=(px, py))
    bats = []
    wisps = []
    for _ in range(2):
        bats.append(place(grid, "B", avoid=(px, py)))
    for _ in range(2):
        wisps.append(place(grid, "o", avoid=(px, py)))
    fuel, wings, pts = 100, 3, 0
    msg = "flutter to the glow!"
    turn_no = 0
    while True:
        grid[py][px] = "."
        draw(grid, px, py, fuel, wings, pts, msg)
        if pts >= 500:
            print(f"\nDUSK MASTER! {pts} pts -- the moths salute you!")
            return
        if wings <= 0:
            print(f"\nAll wings crumpled! Final score {pts}.")
            return
        if fuel <= 0:
            print(f"\nFuel gone -- wings fold. Final score {pts}.")
            return
        cmd = input(f"fuel {fuel}> ").strip().lower()
        if cmd == "q":
            print(f"\nNight flight ends. Final score {pts}.")
            return
        dx, dy = {"a": (-1, 0), "d": (1, 0), "w": (0, -1), "s": (0, 1)}.get(cmd, (0, 0))
        if cmd and not (dx or dy):
            msg = "? use w/a/s/d or q"
            continue
        fuel -= 1
        px, py = wrap(px + dx, py + dy)
        msg = ""
        turn_no += 1
        if turn_no % 2 == 0:  # world scrolls every other beat: moth can catch up
            scroll(grid)
            # world scrolled: shift tracked coords down 1 (off-screen items vanish)
            bats = [(x, y + 1) for x, y in bats if y + 1 < H]
            wisps = [(x, y + 1) for x, y in wisps if y + 1 < H]
            gy += 1
            if not (0 <= gy < H) or grid[gy][gx] != "G":
                gx, gy = place(grid, "G")
        for x, y in bats:
            grid[y][x] = "B"
        step_bats(grid, bats, px, py)
        for x, y in wisps:
            grid[y][x] = "o"
        if random.random() < 0.25 and len(wisps) < 4:
            wx, wy = place(grid, "o")
            wisps.append((wx, wy))
        if len(bats) < 3 and pts >= 100 and random.random() < 0.3:
            bx, by = place(grid, "B")
            bats.append((bx, by))
        if grid[py][px] == "o":
            grid[py][px] = "."
            if (px, py) in wisps:
                wisps.remove((px, py))
            pts += 25
            msg = "+25 wisp! "
        if (px, py) in bats:
            wings -= 1
            bats.remove((px, py))
            msg += f"BAT! -1 wing ({wings} left) "
            if wings > 0:
                bx, by = place(grid, "B")
                bats.append((bx, by))
        if (px, py) == (gx, gy):
            pts += 100
            msg += "+100 lantern! "
            gx, gy = place(grid, "G", avoid=(px, py))
            fuel = min(100, fuel + 10)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nflight ends.")
    except Exception:
        print("\ndusk crumbles. (error)")
        raise
