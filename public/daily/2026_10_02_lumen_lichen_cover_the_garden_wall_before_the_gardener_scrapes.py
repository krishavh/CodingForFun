# Daily Terminal Drop
# Date: 2026-10-02
# Title: Lumen Lichen: Cover the garden wall before the gardener scrapes

#!/usr/bin/env python3
"""LUMEN LICHEN - a terminal game of moss, light, and slow growth.

You are a patch of lichen on a forgotten garden wall. Your only wish:
to cover the entire wall in soft green. But the gardener keeps scraping!

The wall is 40 stones wide and 14 stones tall. You spread by choosing
a spore from your patch and letting it BLOOM:
  .  bare stone
  o  your lichen (spread from these!)
  #  crusty rock (cannot grow there)
  s  sprouting seed ( blooms next turn automatically )
  G  the gardener's scraper (avoid! eats 3 lichen!)

Each TURN you pick ONE lichen to bloom from. It seeds up to 4
neighbors (n/s/e/w) that are bare stone. Each seed costs 1 SUNSHINE.
You gain sunshine equal to your lichen size / 3 each dawn.

Bloom smart: the gardener scrapes every 5 turns! He eats a 3x3
square of your lichen where he stands (marked G, moves randomly).

Cover 120 stones with lichen to WIN THE WALL.
Commands: n/s/e/w = move gardener view (free), <row> <col> = bloom,
          map = redraw, q = quit.
"""
import random

W, H = 40, 14
GOAL = 120

BARE, LICHEN, ROCK, SEED, GARDENER = ".", "o", "#", "s", "G"


def new_wall():
    wall = [[BARE] * W for _ in range(H)]
    # scatter some crusty rocks
    for _ in range(28):
        y = random.randrange(H)
        x = random.randrange(W)
        wall[y][x] = ROCK
    # start lichen in the middle-ish
    sy, sx = H // 2, W // 2
    if wall[sy][sx] == ROCK:
        wall[sy][sx] = BARE
    wall[sy][sx] = LICHEN
    return wall, sy, sx


def draw(wall, gy, gx, sun, turns, size, msg=""):
    print("+" + "-" * W + "+")
    for y in range(H):
        row = "".join(wall[y])
        print("|" + row + "|")
    print("+" + "-" * W + "+")
    print(f"  lichen {size}/{GOAL}   sunshine {sun}   turn {turns}")
    print(f"  gardener at row {gy} col {gx} (scrapes every 5 turns!)")
    if msg:
        print("  " + msg)
    print("  commands: '<row> <col>' bloom from nearest lichen,")
    print("  'map' redraw, 'q' quit")


def neighbors4(y, x):
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W:
            yield ny, nx


def nearest_lichen(wall, y, x):
    """Closest lichen to (y,x) by manhattan distance (BFS-lite)."""
    best = None
    bestd = 999
    for cy in range(H):
        for cx in range(W):
            if wall[cy][cx] == LICHEN:
                d = abs(cy - y) + abs(cx - x)
                if d < bestd:
                    bestd, best = d, (cy, cx)
    return best


def gardener_scrape(wall, gy, gx):
    eaten = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ny, nx = gy + dy, gx + dx
            if 0 <= ny < H and 0 <= nx < W:
                if wall[ny][nx] == LICHEN:
                    wall[ny][nx] = BARE
                    eaten += 1
                elif wall[ny][nx] == SEED:
                    wall[ny][nx] = BARE
    return eaten


def main():
    random.seed()
    wall, gy, gx = new_wall()
    sun = 3
    turns = 0
    msg = "welcome, little lichen. cover the wall!"
    while True:
        size = sum(row.count(LICHEN) for row in wall)
        seeds = sum(row.count(SEED) for row in wall)
        if size + seeds >= GOAL and seeds == 0:
            print("  THE WALL IS YOURS! soft green forever.")
            print(f"  final lichen: {size} in {turns} turns")
            return
        draw(wall, gy, gx, sun, turns, size + seeds, msg)
        msg = ""
        raw = input("  > ").strip().lower()
        if raw == "q":
            print("  the wall remains partly bare... goodbye.")
            return
        if raw == "map":
            continue
        parts = raw.replace(",", " ").split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            msg = "?? try: '12 20' (row col), map, q"
            continue
        ry, rx = int(parts[0]), int(parts[1])
        if not (0 <= ry < H and 0 <= rx < W):
            msg = "?? off the wall!"
            continue
        src = nearest_lichen(wall, ry, rx)
        if src is None:
            msg = "?? no lichen left to bloom from!"
            continue
        # bloom: seed bare neighbors of target IF close to src lichen
        dist = abs(src[0] - ry) + abs(src[1] - rx)
        if dist > 2:
            msg = "?? too far from nearest lichen (max 2)!"
            continue
        spread = 0
        cost = 0
        for ny, nx in neighbors4(ry, rx):
            if wall[ny][nx] == BARE and cost < sun:
                wall[ny][nx] = SEED
                cost += 1
                spread += 1
        if spread == 0:
            msg = "?? no bare stone neighbors to seed!"
            continue
        sun -= cost
        turns += 1
        msg = f"seeded {spread} spores (-{cost} sunshine)"
        # seeds bloom into lichen
        for cy in range(H):
            for cx in range(W):
                if wall[cy][cx] == SEED:
                    wall[cy][cx] = LICHEN
        # sunshine each dawn: size / 3
        size_now = sum(row.count(LICHEN) for row in wall)
        sun += max(1, size_now // 3)
        # gardener moves + scrapes every 5 turns
        if turns % 5 == 0:
            gy = max(0, min(H - 1, gy + random.randint(-2, 2)))
            gx = max(0, min(W - 1, gx + random.randint(-2, 2)))
            eaten = gardener_scrape(wall, gy, gx)
            if eaten:
                msg += f" | gardener scraped {eaten} lichen!"


if __name__ == "__main__":
    main()
