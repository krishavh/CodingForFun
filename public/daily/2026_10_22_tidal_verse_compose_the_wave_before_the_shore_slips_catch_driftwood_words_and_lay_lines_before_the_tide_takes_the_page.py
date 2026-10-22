# Daily Terminal Drop
# Date: 2026-10-22
# Title: Tidal Verse: Compose the wave before the shore slips: Catch driftwood words and lay lines before the tide takes the page

# Daily Terminal Drop
# Date: 2026-10-22
# Title: Tidal Verse: Compose the wave before the shore slips
#!/usr/bin/env python3
"""TIDAL VERSE - compose a poem on the tide before it washes away!

You stand on a beach of drifting WORDS. Waves roll in and SCATTER
them -- but you catch words and lay your own verse on the sand.
Each turn the tide SHIFTS: unanchored words drift one way,
your laid words STAY -- unless a BIG wave (~~) wipes the line!

Legend:
  @  you (the poet)
  w  loose word (walk onto it to catch it!)
  #  driftwood (blocks you, words ride over it)
  .  wet sand

PLAY:
  You hold ONE word. Walk into a loose word to SWAP it into
  your hand (old drops on your tile). Press ENTER (empty)
  to LAY your word on the sand. Laid words in a row SCORE:
  3+ in a row = line! Rows wave-shift each turn: words on
  sand DRIFT toward the sea (bottom), words off BEACH drown.

SCORE: each laid word 10, each full line (3+) bonus 50.
GOAL: 300 points before 45 turns -- or the tide takes all!
COMMANDS: a/d/w/s move   e lay word   q quit
"""
import random
import shutil
import subprocess

W = 36
H = 14
GOAL = 300
TURNS = 45
WORDS = ["moon", "tide", "salt", "wave", "mist", "reef", "foam",
         "pearl", "drift", "shore", "coral", "sail", "krill", "dune"]


def clear():
    subprocess.run(["clear"], shell=False)


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def new_beach():
    """Sand, driftwood, scattered words, poet center."""
    g = [["."] * W for _ in range(H)]
    spots = random.sample(range(W * H), 20)
    for s in spots[:6]:
        g[s // W][s % W] = "#"
    return g


def draw(g, px, py, held, laid, turn, pts, msg):
    print(f"TIDAL VERSE  turn {turn}/{TURNS}  points {pts}  (goal {GOAL})")
    print("a/d/w/s move  e lay word  q quit")
    print("+" + "-" * W + "+")
    for y in range(H):
        row = []
        for x in range(W):
            ch = g[y][x]
            if (x, y) == (px, py):
                ch = "@"
            row.append(ch[0] if ch != "." else ".")
        print("|" + "".join(row) + "|")
    print("+" + "-" * W + "+")
    print("Hand: " + (held or "(empty)"))
    if laid:
        print("Your verse: " + " ".join(laid))
    if msg:
        print(msg)
    print("")


def scatter(g, n):
    """Drop n random words on empty sand."""
    out = []
    for _ in range(n):
        for _try in range(200):
            x = random.randrange(W)
            y = random.randrange(H)
            if g[y][x] == ".":
                g[y][x] = random.choice(WORDS)
                out.append((x, y))
                break
    return out


def drift(g, px, py):
    """Tide pulls every loose word 1 cell down (sea = bottom)."""
    for y in range(H - 2, -1, -1):
        for x in range(W):
            ch = g[y][x]
            if ch != "." and ch != "#" and len(ch) > 1 and (x, y) != (px, py):
                if g[y + 1][x] == ".":
                    g[y + 1][x] = ch
                    g[y][x] = "."
    # words pushed off the bottom (sea) wash away: row H-1 clears words
    for x in range(W):
        if g[H - 1][x] not in (".", "#") and len(g[H - 1][x]) > 1:
            g[H - 1][x] = "."


def line_score(g):
    """Count laid words (len>1, not #) + longest run on rows."""
    total = 0
    best = []
    for y in range(H):
        run = []
        for x in range(W):
            ch = g[y][x]
            if ch not in (".", "#") and len(ch) > 1:
                run.append(ch)
            else:
                if len(run) > best.__len__():
                    best = run[:]
                if len(run) >= 3:
                    total += 50
                run = []
        if len(run) > len(best):
            best = run[:]
        if len(run) >= 3:
            total += 50
    words = 0
    for y in range(H):
        for x in range(W):
            ch = g[y][x]
            if ch not in (".", "#") and len(ch) > 1:
                words += 1
    return total + words * 10, best


def main():
    random.seed()
    g = new_beach()
    px, py = W // 2, H // 2
    g[py][px] = "."
    scatter(g, 14)
    held = None
    laid = []
    pts = 0
    turn = 1
    msg = "Catch words. Lay lines. Race the tide!"

    while turn <= TURNS:
        gained, best = line_score(g)
        pts += gained
        if pts >= GOAL:
            break
        drift(g, px, py)
        if random.random() < 0.4:
            scatter(g, 2)
        draw(g, px, py, held, best, turn, pts, msg)
        if gained:
            print(f"  +{gained} pts -- the tide reads your verse!")
        cmd = input("poet> ").strip().lower()
        msg = ""
        if cmd == "q":
            print(f"\nThe tide rests. Final verse: {pts} pts")
            return
        elif cmd in "adws" and len(cmd) == 1:
            dx, dy = {"a": (-1, 0), "d": (1, 0), "w": (0, -1), "s": (0, 1)}[cmd]
            nx, ny = px + dx, py + dy
            if 0 <= nx < W and 0 <= ny < H and g[ny][nx] != "#":
                px, py = nx, ny
                ch = g[ny][nx]
                if ch not in (".", "#") and len(ch) > 1:
                    old = held
                    held = ch
                    g[ny][nx] = old if (old and len(old) > 1) else "."
                    msg = f"Caught '{ch}'!" + (f" Dropped '{old}'." if old else "")
        elif cmd == "e":
            if held and len(held) > 1:
                if g[py][px] in (".", "#"):
                    g[py][px] = held
                    laid.append(held)
                    msg = f"Laid '{held}'. The beach remembers."
                    held = None
                else:
                    msg = "Tile full!"
            else:
                msg = "No word to lay."
        else:
            msg = "? a/d/w/s, e, q"
        turn += 1

    draw(g, px, py, held, [], TURNS, pts, "")
    if pts >= GOAL:
        print(f"\nTHE SEA READS ALOUD! Verse of {pts} pts in {turn} turns!")
    else:
        print(f"\nThe tide takes the page. Final verse: {pts} / {GOAL}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nThe tide closes the book. Bye!")
