# Daily Terminal Drop
# Date: 2026-10-04
# Title: Sushi Sprint: Match the pairs before the patience runs dry

#!/usr/bin/env python3
"""SUSHI SPRINT - an original terminal memory-match recipe game.

The rush is on at the Tiny Pine sushi bar! Customers order combos of
nigiri. You must SERVE each order by finding the matching pairs of
sushi hidden behind the bamboo screen -- before the patience timer
runs out.

The board is 4 rows of 6 plates. Each plate hides a sushi:
  B  Ikura (salmon roe)      S  Spicy Tuna
  T  Toro (fatty tuna)       U  Unagi (eel)
  E  Unadon (eel bowl)       I  Inari (tofu pouch)
  M  Maguro (bluefin)        K  Kappa (cucumber roll)
  A  Awabi (abalone)         O  Otoro (fatty belly)
  N  Nori (seaweed)          G  Gunkan (warship roll)

Each TURN you flip TWO plates:
  <row> <col> <row> <col>   flip two plates (rows 1-4, cols 1-6)
  map                       peek at the board again (costs 5 patience)
  q                         close the bar early

Match them: the customer is fed! (+150 patience and plate stays up)
Miss them:   customer waits!  (-20 patience)
Patience starts at 100 and drains 2 per turn. Serve all 24 plates
(12 pairs) before it hits 0. KAMPai!
"""

import random
import shutil
import subprocess

ROWS, COLS = 4, 6
FISH = "BSTUEIMKAONG"


def term_cols(default=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def clear():
    subprocess.run(["clear"] if True else [], shell=False)


def fresh_board():
    """12 pairs of sushi behind 24 plates."""
    plates = []
    for ch in FISH:
        plates.append(ch)
        plates.append(ch)
    random.shuffle(plates)
    return [plates[r * COLS:(r + 1) * COLS] for r in range(ROWS)]


def draw(board, up, patience, turns, msg=""):
    clear()
    print("=" * 49)
    print("        S U S H I   S P R I N T")
    print("    match the pairs, feed the customers!")
    print("=" * 49)
    print()
    print("      " + "  ".join(str(c + 1) for c in range(COLS)))
    for r in range(ROWS):
        cells = []
        for c in range(COLS):
            ch = board[r][c] if (r, c) in up else "?"
            cells.append(ch)
        print(f"   {r + 1}  " + "  ".join(cells))
    print()
    bar = "#" * (patience // 5) + "." * (20 - patience // 5)
    print(f"  patience [{bar}] {patience}/100   turn {turns}")
    if msg:
        print("  " + msg)
    print("  flip: <r> <c> <r> <c>   map: peek   q: quit")


def parse_flip(tok):
    """Return (r1,c1,r2,c2) 0-based or None."""
    try:
        nums = [int(x) for x in tok]
    except ValueError:
        return None
    if len(nums) != 4:
        return None
    r1, c1, r2, c2 = nums
    if not all(1 <= r <= ROWS for r in (r1, r2)):
        return None
    if not all(1 <= c <= COLS for c in (c1, c2)):
        return None
    if (r1, c1) == (r2, c2):
        return None
    return (r1 - 1, c1 - 1, r2 - 1, c2 - 1)


def main():
    random.seed()
    board = fresh_board()
    up = set()
    patience, turns = 100, 0
    msg = "Welcome to the Tiny Pine! Match all 12 pairs."
    while len(up) < ROWS * COLS and patience > 0:
        draw(board, up, patience, turns, msg)
        raw = input("  flip > ").strip().lower()
        if raw in ("q", "quit", "exit"):
            msg = "Arigato! The bar closes early."
            break
        if raw in ("map", "m", "peek"):
            patience = max(0, patience - 5)
            msg = "You peek behind the bamboo. (-5 patience)"
            continue
        turn_input = raw.replace(",", " ").split()
        if len(turn_input) == 8:
            # allow "1 2 3 4" as r1 c1 r2 c2? no -- 2 coords = 4 nums
            turn_input = turn_input[:4]
        flip = parse_flip(turn_input)
        if flip is None:
            msg = "Rows 1-4, cols 1-6. Two plates! (e.g. 1 2 4 5)"
            continue
        r1, c1, r2, c2 = flip
        turns += 1
        patience = max(0, patience - 2)
        a, b = board[r1][c1], board[r2][c2]
        if a == b:
            up.add((r1, c1))
            up.add((r2, c2))
            patience = min(100, patience + 15)
            msg = f"OMURICE! {a} matches {b}! Customer fed. (+15)"
        else:
            msg = f"{a} is not {b}. The customer waits. (-2)"
        # show the flip for a breath
        draw(board, up | {(r1, c1), (r2, c2)}, patience, turns, msg)
        if a != b:
            try:
                input("  (press enter) ")
            except EOFError:
                break
    win = len(up) == ROWS * COLS
    draw(board, up, patience, turns, msg)
    print()
    if win:
        print(f"  ICHI-BAN! All 12 pairs served in {turns} turns!")
        print(f"  Final patience: {patience}/100")
        grade = "GOLD SUSHI CHEF" if patience >= 80 else \
            "SILVER SUSHI CHEF" if patience >= 50 else "BRONZE SUSHI CHEF"
        print(f"  Rank: {grade}")
    else:
        print(f"  The customers left hungry. {len(up) // 2}/12 pairs served.")
        print(f"  Turns: {turns}   Patience: {patience}/100")
    print()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n  Sayounara!")
