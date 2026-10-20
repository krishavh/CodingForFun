# Daily Terminal Drop
# Date: 2026-10-20
# Title: Echo Garden: Grow the chord before the dusk falls: plant notes that ring, stand in the sound

#!/usr/bin/env python3
"""ECHO GARDEN - dig a pond of whispers, grow the chord before it fades!

You are a gardener of sounds. Your garden is a silent grid -- but when
you PLANT a note, it ECHOES in expanding rings each turn!

Legend:
  .  silent soil
  *  your wheelbarrow (you)
  1-7  blooming notes (each hums its number)
  #  stone (blocks sound and you)

HOW ECHOES WORK:
  Every turn, each planted note rings out -- then spreads its sound
  ONE ring wider (steps, bending around stones). RING 1 hums +5,
  ring 2 +10, ring 3 +15 -- then wraps back to 1 (pulse!). A note
  sings 8 turns, then sleeps forever.

YOU grow when soil SOAKS in sound: stand in an echo ring to gain
  that ring's points! Spend 20 growth to PLANT a new note (1-7)
  at your feet -- choose wisely, notes near stones sing REFLECTED
  (rings bend around them!).

GOAL: grow the garden chord to 300 before 40 turns of dusk!
  a/d/w/s move (1 growth)   p<1-7> plant note   q quit
"""
import heapq
import random
import shutil
import subprocess

W, H = 34, 16
GOAL = 300
TURNS = 40
PLANT_COST = 20
NOTE_LIFE = 8
START_GROWTH = 30

DIRS = {"a": (-1, 0), "d": (1, 0), "w": (0, -1), "s": (0, 1)}
NOTES = "1234567"


def clear():
    subprocess.run(["clear"], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def new_grid():
    """Garden with a few scattered stones."""
    g = [["."] * W for _ in range(H)]
    spots = random.sample(range(W * H), 14)
    for s in spots:
        x, y = s % W, s // W
        if (x, y) != (W // 2, H // 2):
            g[y][x] = "#"
    return g


def bfs_dist(grid, sx, sy):
    """Sound spreads around stones: BFS Manhattan-ish steps."""
    dist = [[-1] * W for _ in range(H)]
    dist[sy][sx] = 0
    pq = [(0, sx, sy)]
    while pq:
        d, x, y = heapq.heappop(pq)
        if d > dist[y][x]:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H:
                nd = d + (2 if grid[ny][nx] == "#" else 1)
                if dist[ny][nx] == -1 or nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    heapq.heappush(pq, (nd, nx, ny))
    return dist


def ring_pts(dist, ring):
    """All cells exactly this echo ring away."""
    return [(x, y) for y in range(H) for x in range(W) if dist[y][x] == ring]


def ring_value(ring):
    """Rings pulse 1,2,3,1,2,3... (echo bounces back)."""
    return {1: 5, 2: 10, 3: 15}[((ring - 1) % 3) + 1]


def draw(grid, px, py, notes, turn, growth, msg):
    print("\n" * 0)
    print(f"ECHO GARDEN  turn {turn}/{TURNS}  growth {growth}  (goal {GOAL})")
    print("a/d/w/s move  p<n> plant  q quit")
    print("+" + "-" * W + "+")
    for y in range(H):
        row = []
        for x in range(W):
            ch = grid[y][x]
            if (x, y) == (px, py) and ch == ".":
                ch = "*"
            row.append(ch)
        print("|" + "".join(row) + "|")
    print("+" + "-" * W + "+")
    alive = [(n, t) for n, t in notes if t > 0]
    if alive:
        print("Singing: " + ", ".join(f"note {n} ({t} turns left)" for n, t in alive))
    else:
        print("Silence... (plant a note! p1-p7)")
    if msg:
        print(msg)
    print("")


def main():
    random.seed()
    grid = new_grid()
    px, py = W // 2, H // 2
    if grid[py][px] == "#":
        grid[py][px] = "."
    notes = []  # (char, turns_left)
    next_id = 1
    growth = START_GROWTH
    msg = "Plant notes. Stand in their rings. Grow the chord!"
    turn = 1

    while turn <= TURNS:
        # --- echo phase: rings expand, pulse 1-2-3, score where you stand ---
        gained = 0
        for (n, t) in notes:
            if t <= 0:
                continue
            dist = bfs_dist(grid, *note_pos(n, notes, grid, px, py))
            d = dist[py][px]
            if 0 <= d <= 8:
                gained += ring_value(((d - 1) % 3) + 1)
        growth += gained

        # --- age notes ---
        notes = [(n, t - 1) for (n, t) in notes]
        notes = [(n, t) for (n, t) in notes if t > 0]

        if growth >= GOAL:
            break

        draw(grid, px, py, notes, turn, growth, msg)
        if gained:
            print(f"  +{gained} growth from the echoing chord!")
        cmd = input("move/plant> ").strip().lower()
        msg = ""

        if cmd == "q":
            print(f"\nYou leave at turn {turn}. Final growth: {growth}")
            return
        elif cmd.startswith("p") and len(cmd) == 2 and cmd[1] in NOTES:
            n = cmd[1]
            if growth < PLANT_COST:
                msg = "Not enough growth to plant (need 20)!"
            elif any(nn == n for nn, _ in notes):
                msg = f"Note {n} is already singing!"
            elif grid[py][px] == "#":
                msg = "Cannot plant on a stone!"
            else:
                grid[py][px] = n
                notes.append((n, NOTE_LIFE))
                growth -= PLANT_COST
                msg = f"Note {n} planted! It sings {NOTE_LIFE} turns."
        elif cmd in DIRS:
            dx, dy = DIRS[cmd]
            nx, ny = px + dx, py + dy
            if 0 <= nx < W and 0 <= ny < H and grid[ny][nx] != "#":
                px, py = nx, ny
                growth = max(0, growth - 1)
            else:
                msg = "Blocked!"
        else:
            msg = "? use a/d/w/s, p1-7, q"

        turn += 1

    draw(grid, px, py, notes, TURNS, growth, "")
    if growth >= GOAL:
        print(f"\nTHE GARDEN SINGS! Chord grown to {growth} in {turn} turns!")
    else:
        print(f"\nDusk falls. Final chord: {growth} / {GOAL}")


def note_pos(n, notes, grid, px, py):
    """Find note char on grid (planted where gardener stood)."""
    for y in range(H):
        for x in range(W):
            if grid[y][x] == n:
                return (x, y)
    return (px, py)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGarden sleeps. Bye!")
