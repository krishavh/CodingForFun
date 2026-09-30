# Daily Terminal Drop
# Date: 2026-09-30
# Title: Tide Cache: Stack driftwood before the sea takes it

#!/usr/bin/env python3
"""TIDE CACHE - an original terminal tower-stacking memory game.

A rising tide is coming. Build a driftwood tower by stacking pieces
on the beach -- but every piece, remembered from the last, costs.

Each round the tide shows you a PIECE (a letter tower) to memorize.
Then it hides it and asks WHICH FLOOR held a glimpse of it?.
Guess right -> the piece is yours, stack grows taller.
Guess wrong -> a wave steals the top of your stack.

The tide rises every round: more floors to search, less time to peek.

Commands at prompt:
  <n>       -> dive to floor n (1 = bottom, top floor = tallest number)
  map       -> show the tower floors again (costs 2 seconds of memory)
  quit      -> beach your bucket, end the shift, see final tower.

Stack 8 pieces high before the tide reaches the top of the screen!
"""

import random

WIN_HEIGHT = 8
START_FLOORS = 3

WAVE = r"""
        ~   ~   ~
      ~   ~   ~   ~        T I D E   C A C H E
    ~   ~   ~   ~   ~      stack driftwood before the sea takes it
  ~~~~~~~~~~~~~~~~~~~~~~
"""


def build_tower(floors):
    """Random tower: each floor is a piece-letter, some repeated."""
    pieces = ["c", "r", "a", "b", "s", "p", "k", "m"]
    return [random.choice(pieces) for _ in range(floors)]


def draw_tower(tower, reveal_floor=None, peek=False):
    """Print the tower bottom-up; reveal_floor shows its letter."""
    print("     top")
    for i in range(len(tower) - 1, -1, -1):
        marker = " <--" if i + 1 == reveal_floor else ""
        ch = tower[i] if (peek or i + 1 == reveal_floor) else "?"
        print(f"  {i + 1:>2} |{ch}|{marker}")
    print("  ___|_|___  beach")
    print("   ~ ~ ~ ~   tide line")


def print_tide_height(h):
    print("  " + "~" * (h * 3 + 4))


def main():
    print(WAVE)
    print("  The tide is coming in. Stack driftwood high enough to")
    print(f"  keep your cache dry. Reach {WIN_HEIGHT} pieces to win!\n")
    rounds = 0
    misses = 0
    stack = 0
    floors = START_FLOORS
    while True:
        tower = build_tower(floors)
        hidden = random.randint(1, len(tower))
        rounds += 1
        print(f"\n  ROUND {rounds}  stack {stack}/{WIN_HEIGHT}  "
              f"misses {misses}  floors {len(tower)}")
        print("  MEMORIZE THE TOWER!")
        draw_tower(tower, peek=True)
        input("  press ENTER when the wave hides it... ")
        print("\n" * 30)
        guess = None
        while guess is None:
            draw_tower(tower)
            print(f"\n  Wave riddle: which floor holds the "
                  f"'{tower[hidden - 1]}' piece?")
            raw = input("  floor> (1-"
                        f"{len(tower)}, map, quit) ").strip().lower()
            if raw == "quit":
                print("\n  You beach your bucket. The sea keeps the rest.")
                print_tide_height(len(tower))
                print(f"  FINAL  rounds {rounds}  stack {stack}  "
                      f"misses {misses}")
                return
            if raw == "map":
                print("  you sneak a peek (the tide notices...)")
                draw_tower(tower, peek=True)
                input("  press ENTER to hide it again... ")
                print("\n" * 8)
                continue
            if not raw.isdigit():
                print("  numbers and waves only. try again.")
                continue
            n = int(raw)
            if not 1 <= n <= len(tower):
                print(f"  floors run 1 to {len(tower)}. try again.")
                continue
            guess = n
        print("\n" * 30)
        if guess == hidden:
            stack += 1
            print(f"  SPLASH-DUNK! You fish the "
                  f"'{tower[hidden - 1]}' from floor {hidden}!")
            print(f"  Stack it! Tower height: {stack}")
        else:
            misses += 1
            stack = max(0, stack - 1)
            print(f"  WAVE CRASH! floor {guess} held "
                  f"'{tower[guess - 1]}', not "
                  f"'{tower[hidden - 1]}'. A piece washes away!")
            print(f"  Tower height: {stack}")
        floors = min(9, START_FLOORS + rounds // 2)
        if stack >= WIN_HEIGHT:
            print("\n  YOUR TOWER TOUCHES THE STORM CLOUDS!")
            print(f"  The tide retreats. Rounds {rounds}, "
                  f"misses {misses}. DRIFTWOOD BARON!")
            return
        if misses >= 5:
            print("\n  The tide claims the beach. Your tower is flotsam.")
            print(f"  Rounds {rounds}, stack {stack}. The sea remembers.")
            return


if __name__ == "__main__":
    main()
