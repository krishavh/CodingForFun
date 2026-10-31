# Daily Terminal Drop
# Date: 2026-10-31
# Title: Fossil Quarry: Chisel the shale, unearth the dino bones before the cave-in

# Daily Terminal Drop
# Date: 2026-10-31
# Title: Fossil Quarry: Chisel the shale, unearth the dino bones before the cave-in
#!/usr/bin/env python3
"""FOSSIL QUARRY - chisel into the shale, unearth T-REX bones before cave-in!

Deep in a desert quarry a T-REX waits in the rock. You are a
PALEONTELL... a BONE HUNTER! Swing your chisel to break SHALE
BLOCKS -- but the dirt is UNSTABLE! Every swing may start a
CAVE-IN DUST CLOUD that fills the quarry. Clear it with FAN?

NO FAN! Just dig SMART: dirt settles each turn.

Legend:
  @  you (the bone hunter)
  #  shale (hard -- CHISEL it to break)
  .  dug dirt (safe, you may walk)
  b  bone (dig it for points!)
  x  skull (BIG points! 100! at the bottom)
  ~  dust cloud (spreads each turn! walk in = -3 air)

HOW IT WORKS:
  Stand NEXT to shale and press c to CHISEL it away.
  Walk with a/d/w/s. Each turn: dust CLOUDS SPREAD 1 block
  (into dug dirt only). Stand in dust? lose 3 air! Digging
  bones: b = 25 pts, x = 100 pts (skull at the bottom!).

CAVE-IN METER: every 8 swings a BIG DUST STORM! all dust
  grows 2 blocks wide! Air 100 -- stormy quarry digs slow.

GOAL: dig the SKULL (x) before air runs out!
COMMANDS: w/a/s/d move   c chisel   q quit
"""
import random

W, H = 32, 14
AIR_MAX = 100
STORM = 8

def make_quarry(rnd):
    grid = [["#"] * W for _ in range(H)]
    # carve some dug dirt pockets
    for _ in range(26):
        r, c = rnd.randint(1, H - 2), rnd.randint(1, W - 2)
        grid[r][c] = "."
    # top row open air (you drop in)
    for c in range(W):
        grid[0][c] = "."
    # bottom row: mostly shale, skull hides deep
    bones = []
    for _ in range(9):
        r, c = rnd.randint(H // 2, H - 2), rnd.randint(1, W - 2)
        if grid[r][c] == "#":
            grid[r][c] = "b"
            bones.append((r, c))
    sr, sc = H - 2, rnd.randint(4, W - 5)
    grid[sr][sc] = "x"
    return grid, bones, (sr, sc)


def draw(grid, player, air, pts, swings, dust, msg):
    print("FOSSIL QUARRY  air:%d  pts:%d  swings:%d  dust:%d" %
          (air, pts, swings, len(dust)))
    top = "+" + "-" * W + "+"
    print(top)
    for r, row in enumerate(grid):
        line = ""
        for c, ch in enumerate(row):
            if (r, c) == player:
                line += "@"
            elif (r, c) in dust:
                line += "~"
            else:
                line += ch
        print("|" + line + "|")
    print(top)
    if msg:
        print(msg)


def adjacent(p):
    r, c = p
    return [(r, c), (r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]


def spread_dust(dust, grid, rnd):
    new = list(dust)
    for (r, c) in dust:
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W and grid[nr][nc] != "#":
                if (nr, nc) not in new:
                    new.append((nr, nc))
    return new


def main():
    rnd = random.Random()
    grid, bones, skull = make_quarry(rnd)
    player = (0, rnd.randint(2, W - 3))
    air = AIR_MAX
    pts = 0
    swings = 0
    dust = []
    msg = "dig deep! the skull waits below."
    digs = 0
    while air > 0:
        # input
        cmd = input("cmd [w/a/s/d/c/q] > ").strip().lower()
        if cmd == "q":
            print("you climb out of the quarry. %d pts, %d digs." % (pts, digs))
            return
        r, c = player
        moved = False
        if cmd in ("w", "a", "s", "d"):
            dr, dc = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}[cmd]
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W and grid[nr][nc] != "#":
                player = (nr, nc)
                moved = True
            else:
                msg = "solid shale that way."
        elif cmd == "c":
            # chisel shale NEXT to player
            hit = None
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < H and 0 <= nc < W and grid[nr][nc] == "#":
                    hit = (nr, nc)
                    break
            if hit:
                nr, nc = hit
                grid[nr][nc] = "."
                digs += 1
                swings += 1
                msg = "crunch! shale breaks."
                if rnd.random() < 0.45:
                    # new dust puff spawns where shale was
                    dust.append((nr, nc))
                    msg += " dust puffs in!"
                if swings % STORM == 0:
                    for _ in range(2):
                        dust = spread_dust(dust, grid, rnd)
                    msg += " BIG DUST STORM!"
            else:
                msg = "no shale beside you."
        else:
            msg = "huh? (w/a/s/d/c/q)"
        # pickups
        pr, pc = player
        if grid[pr][pc] == "b":
            grid[pr][pc] = "."
            pts += 25
            msg = "BONE! +25 pts."
        elif (pr, pc) == skull and grid[pr][pc] == "x":
            grid[pr][pc] = "."
            pts += 100
            print("THE SKULL! T-REX LIVES! %d pts, %d digs, %d air left!" %
                  (pts, digs, air))
            return
        # dust spread + air
        dust = spread_dust(dust, grid, rnd)
        if player in dust:
            air -= 3
            msg += " dust in your lungs! -3 air."
        air -= 1  # hot desert sun, each turn dries you
        draw(grid, player, max(air, 0), pts, swings, dust, msg)
        if air <= 0:
            print("parched & dusty! you exhume %d pts with %d digs." % (pts, digs))
    return


if __name__ == "__main__":
    try:
        rnd = random.Random()
        grid, bones, skull = make_quarry(rnd)
        player = (0, rnd.randint(2, W - 3))
        air = AIR_MAX
        pts = 0
        swings = 0
        dust = []
        msg = "dig deep! the skull waits below."
        print("FOSSIL QUARRY -- chisel shale, find the T-REX skull!")
        draw(grid, player, air, pts, swings, dust, msg)
        while air > 0:
            cmd = input("cmd [w/a/s/d/c/q] > ").strip().lower()
            if cmd == "q":
                print("you climb out. %d pts." % pts)
                break
            r, c = player
            if cmd in ("w", "a", "s", "d"):
                dr, dc = {"w": (-1, 0), "s": (1, 0),
                          "a": (0, -1), "d": (0, 1)}[cmd]
                nr, nc = r + dr, c + dc
                if 0 <= nr < H and 0 <= nc < W and grid[nr][nc] != "#":
                    player = (nr, nc)
                    msg = ""
                else:
                    msg = "solid shale."
            elif cmd == "c":
                hit = None
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < H and 0 <= nc < W and grid[nr][nc] == "#":
                        hit = (nr, nc)
                        break
                if hit:
                    nr, nc = hit
                    grid[nr][nc] = "."
                    swings += 1
                    msg = "crunch!"
                    if rnd.random() < 0.45:
                        dust.append((nr, nc))
                        msg = "crunch! dust puffs in!"
                    if swings % STORM == 0:
                        for _ in range(2):
                            dust = spread_dust(dust, grid, rnd)
                        msg += " STORM!"
                else:
                    msg = "no shale beside you."
            else:
                msg = "huh?"
            pr, pc = player
            if grid[pr][pc] == "b":
                grid[pr][pc] = "."
                pts += 25
                msg = (msg + " " if msg else "") + "BONE! +25."
            elif grid[pr][pc] == "x":
                grid[pr][pc] = "."
                pts += 100
                print("THE SKULL! T-REX LIVES! %d pts, %d swings!" % (pts, swings))
                break
            dust = spread_dust(dust, grid, rnd)
            if player in dust:
                air -= 3
                msg = (msg + " " if msg else "") + "dust! -3 air."
            air -= 1
            draw(grid, player, max(air, 0), pts, swings, dust, msg)
            if air <= 0:
                print("parched! %d pts, %d swings." % (pts, swings))
    except KeyboardInterrupt:
        print("\n[quarry closed]")
