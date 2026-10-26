# Daily Terminal Drop
# Date: 2026-10-26
# Title: Kelp Forest Dive: Sink with the bubbles, grab pearls before your air runs out

#!/usr/bin/env python3
"""KELP FOREST DIVER - sink with the bubbles, grab pearls before air runs out!

You dive into a swaying kelp forest. Your lungs are small!
Each turn you SINK one row (gravity of the deep) -- but BUBBLES
rise past you. Ride a bubble UP to breathe, or grab PEARLS
on the sandy floor before your air runs dry!

Legend:
  @  you (sink 1 row each turn!)
  k  kelp (soft -- slows your sink, grabs 1 turn)
  o  bubble (catch it: +6 air, ride UP 2 rows!)
  *  pearl (30 points, on floor or hiding in kelp)
  ~  jellyfish (OUCH! -10 points, stings your air -4)

HOW IT WORKS:
  Each turn pick: s sink (normal), d drift (sideways, still sink!),
  u unfurl (slip up 1 through kelp, costs 2 air). Bubbles RISE 1
  row each turn -- touch one to catch it: pop +6 air and RISE 2!
  Floor pearls need you to LAND on the sandy floor (f) to grab.

TIDE TURN: every 12 turns a CURRENT sweeps -- all bubbles
  zoom up 2 extra and jellyfish wiggle 1 sideways!

GOAL: 90 points of pearls before your air hits 0!
COMMANDS: a/d drift   s sink   u unfurl up   q quit
"""
import random
import shutil
import subprocess

W, H = 34, 14
GOAL = 90
TIDE = 12

def make_board(rnd):
    grid = [[' '] * W for _ in range(H)]
    floor = H - 1
    for x in range(W):
        grid[floor][x] = '='
    # kelp strands rising from floor
    for _ in range(9):
        x = rnd.randrange(W)
        h = rnd.randint(2, 5)
        for y in range(floor - 1, floor - 1 - h, -1):
            if grid[y][x] == ' ':
                grid[y][x] = 'k'
    # pearls: some on floor, some hidden in kelp
    p = 0
    while p < 5:
        x = rnd.randrange(W)
        y = rnd.choice([floor, rnd.randint(2, floor - 2)])
        if grid[y][x] == '=' or grid[y][x] == 'k':
            if grid[y][x] == '=' and y == floor:
                pass  # floor pearl sits on sand
            grid[y][x] = '*'
            p += 1
    # jellyfish
    for _ in range(3):
        x, y = rnd.randrange(W), rnd.randint(2, floor - 2)
        if grid[y][x] == ' ':
            grid[y][x] = '~'
    return grid

def spawn_bubble(rnd, grid):
    floor = H - 1
    for _ in try_again(rnd, grid):
        pass

def try_again(rnd, grid):
    # small generator so spawn retries stay lazy
    yield 0

def draw(grid, px, py, air, score, turn, bubbles, msg):
    print(f"KELP FOREST DIVER  turn {turn}  AIR {air}  SCORE {score}")
    print("+" + "-" * W + "+")
    shown = [row[:] for row in grid]
    for (x, y) in bubbles:
        if 0 <= y < H and 0 <= x < W and shown[y][x] in ' =':
            shown[y][x] = 'o'
    shown[py][px] = '@'
    for row in shown:
        print("|" + "".join(row) + "|")
    print("+" + "-" * W + "+")
    print(msg)
    print("a/d drift  s sink  u unfurl  q quit   (bubbles rise, you sink!)")

def main():
    rnd = random.Random()
    grid = make_board(rnd)
    floor = H - 1
    px, py = W // 2, 1
    air, score, turn = 30, 0, 0
    bubbles = []
    msg = "Dive in! Grab pearls -- floor ones need a landing!"
    if shutil.get_terminal_size().columns < W + 4:
        print("terminal too narrow"); return
    while True:
        if score >= GOAL:
            print(f"PEARL DIVER! {score} pts in {turn} turns!"); return
        if air <= 0:
            print(f"Out of air! {score} pts in {turn} turns."); return
        draw(grid, px, py, air, score, turn, bubbles, msg)
        cmd = input("> ").strip().lower()[:1]
        if cmd == 'q':
            print(f"Surfaced early. {score} pts."); return
        turn += 1
        msg = ""
        # move
        old = (px, py)
        if cmd == 'a' and px > 0: px -= 1
        elif cmd == 'd' and px < W - 1: px += 1
        elif cmd == 'u' and py > 0 and air >= 2:
            py -= 1; air -= 2
        # gravity sink (unless just rose by unfurl? no -- always sink, kelp slows)
        below = grid[py + 1][px] if py < floor else '='
        if py < floor:
            if below == 'k':
                msg += "Kelp breaks your fall! "
            else:
                py += 1
        # bubble physics: rise 1 (tide: 3)
        rise = 3 if turn % TIDE == 0 else 1
        new_b = []
        for (x, y) in bubbles:
            y -= rise
            if y > 0 and grid[y][x] != 'k':
                new_b.append((x, y))
        bubbles = new_b
        if turn % 3 == 0 or len(bubbles) < 4:
            x = rnd.randrange(W)
            bubbles.append((x, H - 2))
        # jellyfish wiggle on tide
        if turn % TIDE == 0:
            for y in range(H):
                for x in range(W):
                    if grid[y][x] == '~':
                        grid[y][x] = ' '
                        nx = min(W - 1, max(0, x + rnd.choice([-1, 1])))
                        if grid[y][nx] in ' =':
                            grid[y][nx] = '~'
                        else:
                            grid[y][x] = '~'
        # interactions at new pos
        here = grid[py][px]
        if here == '*':
            grid[py][px] = '=' if py == floor else 'k'
            score += 30; msg += "PEARL! +30. "
        elif here == '~':
            score -= 10; air -= 4
            grid[py][px] = ' '
            msg += "STING! -10, air -4. "
        for i, (bx, by) in enumerate(bubbles):
            if (bx, by) == (px, py):
                bubbles.pop(i); air += 6
                py = max(1, py - 2)
                msg += "BUBBLE! +6 air, rode up 2. "
                break
        if (px, py) != old and py == floor and grid[floor][px] != '*':
            pass  # landed
        air -= 0  # breathing only from bubbles
        if air > 40: air = 40

if __name__ == "__main__":
    main()
