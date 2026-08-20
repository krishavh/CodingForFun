# Daily Terminal Drop
# Date: 2026-08-20
# Title: Threadbound: The Loom-Keeper's Gambit

# Daily Terminal Drop
# Date: 2026-08-20
# Title: Threadbound: The Loom-Keeper's Gambit

#!/usr/bin/env python3
"""
THREADBOUND: THE LOOM-KEEPER'S GAMBIT
=====================================
The great loom at the edge of the world has gone slack. The prophecy that
kept the seasons turning is woven from five rune-threads, and the wind has
scrambled them on the frame.

Your shuttle may only swap two neighbouring threads at a time, and each
swap costs one breath of your hearth-flame. Restore the prophecy's exact
pattern within your flame and the year spins true again — run out of flame
with the threads still wrong, and winter never ends.

Commands:
  swap <i>      swap threads at positions i and i+1 (1-based)
  set <i> <j>   swap any two positions (costs 2 flame — a bold bard's trick)
  loom          re-draw the board
  reason        spend 1 flame to see how many swaps remain (minimum)
  quit          walk away from the loom
"""
import random
import sys

THREADS = {
    "S": "Sow (green)",
    "F": "Flame (red)",
    "T": "Tide (blue)",
    "W": "Ward (grey)",
    "K": "King (amber)",
}
SIZE = 6
BASE_BUDGET = 9          # flame breaths for a size-6 weave
BOLD_COST = 2            # flame to swap any two non-neighbouring threads


def random_prophecy(rng):
    """Pick a target pattern and a scrambled starting frame (never solved)."""
    pool = ["S", "F", "T", "W", "K"]
    while len(pool) < SIZE:
        rng.shuffle(pool)
        pool = pool + [rng.choice(pool)]
    target = pool[:SIZE]
    scramble = target[:]
    while scramble == target:
        rng.shuffle(scramble)
    return target, scramble


def inversions(seq, target):
    """Minimum adjacent swaps to turn seq into target (position-mapping)."""
    order = {v: i for i, v in enumerate(target)}
    mapped = [order[v] for v in seq]
    inv = 0
    for i in range(len(mapped)):
        for j in range(i + 1, len(mapped)):
            if mapped[i] > mapped[j]:
                inv += 1
    return inv


def bar(seq):
    return "  ".join("[{}]".format(t) for t in seq)


def legend():
    return "   " + "   ".join("{}={}".format(k, THREADS[k].split(" (")[0])
                              for k in THREADS)


def show_legend():
    for k, v in THREADS.items():
        print("     [{}] {}".format(k, v))


def main():
    rng = random.Random()
    target, board = random_prophecy(rng)
    flame = BASE_BUDGET
    moves = 0
    min_at_start = inversions(board, target)

    print("=" * 58)
    print("THREADBOUND :: THE LOOM-KEEPER'S GAMBIT")
    print("=" * 58)
    print("The prophecy is fixed in the east alcove. Weave the frame to match.")
    print()
    show_legend()
    print()
    print("Prophesied pattern (the east alcove):")
    print("  " + bar(target))
    print()
    print("Your frame — {} threads, start with {} flame breaths.".format(SIZE, flame))
    print("Adjacent swaps cost 1. Bolder swaps cost {}. Reason costs 1.".format(BOLD_COST))
    print("Commands: swap <i> | set <i> <j> | loom | reason | quit")
    print()

    while flame >= 0:
        print("-" * 58)
        print("FLAME: {}   WEAVE MOVES: {}".format("|" * flame + "." * (BASE_BUDGET - flame), moves))
        print("  frame:  " + bar(board))
        if board == target:
            break
        try:
            cmd = input("> ").strip().split()
        except (EOFError, KeyboardInterrupt):
            print("\nYou leave the loom slack. The year stalls mid-autumn.")
            sys.exit(0)
        if not cmd:
            continue
        word = cmd[0].lower()
        if word == "quit":
            print("You draw your hand from the shuttle. The loom sighs empty.")
            sys.exit(0)
        elif word == "loom":
            print("  frame:  " + bar(board))
        elif word == "reason":
            if flame < 1:
                print("  Your hearth-flame is too low to reason.")
                continue
            flame -= 1
            print("  The weave-mind whispers: at least {} swaps remain.".format(
                inversions(board, target)))
        elif word == "swap":
            if flame < 1:
                print("  Your hearth-flame gutters out. The shuttle won't move.")
                continue
            if len(cmd) < 2:
                print("  swap which leading position (1..{})?".format(SIZE - 1))
                continue
            try:
                i = int(cmd[1]) - 1
            except ValueError:
                print("  Give a number, e.g. swap 3.")
                continue
            if i < 0 or i >= SIZE - 1:
                print("  Pos must be 1..{} (that's the left thread of the swap).".format(SIZE - 1))
                continue
            board[i], board[i + 1] = board[i + 1], board[i]
            flame -= 1
            moves += 1
            print("  You twist threads {} and {} — the loom creaks.".format(i + 1, i + 2))
        elif word == "set":
            if flame < BOLD_COST:
                print("  A bold swap costs {} flame — your hearth can't spare it.".format(BOLD_COST))
                continue
            if len(cmd) < 3:
                print("  set <i> <j> — swap any two positions (costs {} flame).".format(BOLD_COST))
                continue
            try:
                i, j = int(cmd[1]) - 1, int(cmd[2]) - 1
            except ValueError:
                print("  Give two numbers, e.g. set 1 5.")
                continue
            if not (0 <= i < SIZE and 0 <= j < SIZE) or i == j:
                print("  Positions must differ and lie in 1..{}.".format(SIZE))
                continue
            board[i], board[j] = board[j], board[i]
            flame -= BOLD_COST
            moves += 1
            print("  You snatch threads {} and {} across the frame (bold).".format(i + 1, j + 1))
        else:
            print("  Unknown. Try: swap <i> | set <i> <j> | loom | reason | quit")
        print()

    print("─" * 58)
    if board == target:
        rating = "masterful" if moves <= min_at_start else \
                 "steady" if moves <= min_at_start + SIZE else "workmanlike"
        print()
        print("The threads snap into place — the prophecy is whole.")
        print("Flame to spare: {}. Moves used: {} (a {} weave).".format(flame, moves, rating))
        print("The loom hums, and beyond the window the fields begin to green.")
        print()
        print("       ##")
        print("      ####")
        print("       ##        THE SEASONS TURN TRUE")
        print()
    else:
        reason = inversions(board, target)
        print()
        print("Your hearth-flame dies with the threads still crossed.")
        print("{} swaps of fate remain undone. The loom locks to iron.".format(reason))
        print("Somewhere east, winter settles in for a thousand years.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nThe loom goes cold.")
        sys.exit(0)
