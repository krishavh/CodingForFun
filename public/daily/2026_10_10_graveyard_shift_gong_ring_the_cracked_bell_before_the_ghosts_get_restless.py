# Daily Terminal Drop
# Date: 2026-10-10
# Title: Graveyard Shift Gong: Ring the cracked bell before the ghosts get restless

#!/usr/bin/env python3
"""GRAVEYARD SHIFT GONG - ring the cracked bell before the ghosts get restless.

Midnight at the old cemetery. You ring the cracked bell to calm the
ghosts, but the bell has CRACKS. Each strike wears a crack wider,
and when 3 cracks snap, the bell breaks! Every ring also wakes
the ghosts -- they drift toward you. Survive 12 shifts (rings)!

Each ghost has a MOOD:
  calm   .  drifting slow (1 step every 2 rings)
  cross  x  drifting every ring
  livid  X  drifting TWICE every ring

COMMANDS (one key + Enter, or bare Enter to rest):
  w/a/s/d  move you (the caretaker @) one step
  b        ring the bell (wherever you stand) -- costs 1 wear
  q        quit

Ring CLOSE to a ghost (within 2 steps) to calm it back 1 step.
Ghosts touch you? You flee the graveyard. GAME OVER.
"""
import random
import shutil

WIDTH = 28
HEIGHT = 12
BELL = (14, 5)
WIN_RINGS = 12

# cracks: [wear, limit] -- 4+5+6=15 slots for 12 rings, but each strike
# wears ONE crack (round-robin). Dodge the ghosts, ring, survive till dawn!
CRACKS = {"north": [0, 4], "mid": [0, 5], "south": [0, 6]}
CRACK_ORDER = ["north", "mid", "south"]
crack_i = [0]  # next crack to wear (mutable so main() can use it)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def clear():
    print("\n" * 40)


def grid():
    return [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]


def dist(ax, ay, bx, by):
    return max(abs(ax - bx), abs(ay - by))


def new_ghosts():
    ghosts = []
    spots = [(0, 0), (WIDTH - 1, 0), (0, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1)]
    random.shuffle(spots)
    moods = ["calm", "cross", "calm", "livid"]
    for (x, y), m in zip(spots, moods):
        ghosts.append([x, y, m])
    return ghosts


def show(you, ghosts, rings, msg):
    clear()
    g = grid()
    bx, by = BELL
    g[by][bx] = "B"
    for x, y, m in ghosts:
        g[y][x] = m[0].upper() if m == "livid" else m[0]
    yx, yy = you
    g[yy][yx] = "@"
    bar = "+" + "-" * WIDTH + "+"
    print(bar)
    for row in g:
        print("|" + "".join(row) + "|")
    print(bar)
    wear = sum(c[0] for c in CRACKS.values())
    print(f"shifts rung: {rings}/{WIN_RINGS}   bell wear: {wear}   cols:{term_cols()}")
    for name, (w, lim) in CRACKS.items():
        print(f"  crack {name:6s} [{'#' * w}{'.' * (lim - w)}]")
    print(f"ghosts: {'  '.join(f'{m}({x},{y})' for x, y, m in ghosts)}")
    print(msg)
    print("cmd (w/a/s/d/b/q/Enter): ", end="", flush=True)


def step_ghosts(ghosts, you, rings):
    msgs = []
    yx, yy = you
    for gh in ghosts:
        x, y, m = gh
        speed = {"calm": 1, "cross": 2, "livid": 4}[m]  # half-steps per ring
        for _ in range(speed // 2 if rings % 2 == 0 else speed // 2 + speed % 2):
            if rings % 2 == 1 and m == "calm":
                continue
            dx = (yx > x) - (yx < x)
            dy = (yy > y) - (yy < y)
            if abs(yx - x) >= abs(yy - y) and dx:
                x += dx
            elif dy:
                y += dy
        gh[0], gh[1] = x, y
    return msgs


def caught(ghosts, you):
    yx, yy = you
    return any(x == yx and y == yy for x, y, _ in ghosts)


def step_toward(gh, you):
    """One greedy step toward you (diagonal via axis tie)."""
    x2, y2, _ = gh
    dx = (you[0] > x2) - (you[0] < x2)
    dy = (you[1] > y2) - (you[1] < y2)
    if abs(you[0] - x2) >= abs(you[1] - y2) and dx:
        x2 += dx
    elif dy:
        y2 += dy
    gh[0], gh[1] = x2, y2


def main():
    random.seed()
    you = [WIDTH // 2, HEIGHT // 2]
    if you == list(BELL):
        you[0] -= 1
    ghosts = new_ghosts()
    rings = 0
    msg = "Midnight. The cracked bell waits. Keep the ghosts calm!"
    while True:
        show(you, ghosts, rings, msg)
        cmd = input().strip().lower()[:1]
        if cmd == "q":
            print("\nYou hang up your lantern. Bye!")
            return
        x, y = you
        if cmd in ("w", "a", "s", "d"):
            nx, ny = x + (cmd == "d") - (cmd == "a"), y + (cmd == "s") - (cmd == "w")
            x, y = max(0, min(WIDTH - 1, nx)), max(0, min(HEIGHT - 1, ny))
            you = [x, y]
        elif cmd == "b":
            rings += 1
            name = CRACK_ORDER[crack_i[0] % len(CRACK_ORDER)]
            crack_i[0] += 1
            CRACKS[name][0] += 1
            if CRACKS[name][0] > CRACKS[name][1]:
                print(f"\nThe {name} crack snaps! The bell breaks! GAME OVER")
                return
            # calm ghosts near bell
            for gh in ghosts:
                if dist(gh[0], gh[1], BELL[0], BELL[1]) <= 2 and gh[2] != "calm":
                    gh[2] = "calm"
                    msg = f"A ghost calms at ({gh[0]},{gh[1]})."
                    break
            else:
                msg = "The bell tolls across the graveyard..."
            # ghosts step after each ring (calm 1, cross 2, livid 3)
            for gh in ghosts:
                m = gh[2]
                for _ in range({"calm": 1, "cross": 2, "livid": 3}[m]):
                    if caught([gh], you):
                        break
                    step_toward(gh, you)
            if rings >= WIN_RINGS:
                print("\nDawn breaks! The ghosts rest. YOU SURVIVE THE GRAVEYARD SHIFT!")
                return
        else:
            msg = "You rest a moment... the ghosts creep closer."
        if caught(ghosts, you):
            print("\nA ghost touches your shoulder! You flee the graveyard. GAME OVER")
            return


if __name__ == "__main__":
    main()
