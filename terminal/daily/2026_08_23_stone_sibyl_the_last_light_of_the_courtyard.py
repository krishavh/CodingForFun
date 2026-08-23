# Daily Terminal Drop
# Date: 2026-08-23
# Title: Stone Sibyl: The Last Light of the Courtyard

#!/usr/bin/env python3
"""
STONE SIBYL: THE LAST LIGHT OF THE COURTYARD
============================================
The courtyard of the Sibyl of Fallowhall is a ring of five stone plinths,
each heaped with pale stones that glow faintly at dusk. The Sibyl will
grant her prophecy to the visitor who takes the final stone off the last
plinth. But she plays for a thousand threads of sunlight, and she never
loses her composure.

Each turn you choose ONE plinth and take as many stones from it as you
like (one, some, or all). Whoever takes the very last stone from the
whole courtyard wins the prophecy. Take care — it is a deeper game than
it looks: the same principle that lets you win can be turned against you.

Commands:
  take <plinth> <n>   take n stones from plinth (1..its size)
  plinths             re-draw the courtyard
  gaze                once per match: the Sibyl shows you the winning move
  rule                a hint on the art of the courtyard
  surrender           set down your stones and leave
"""
import random
import sys

PLINTHS = 5
STONES = [4, 5, 7, 9]      # heaps drawn from this pool (odd values grant a
                            # path to win; a 4 can slip a board to even)


def xor_sum(heaps):
    x = 0
    for h in heaps:
        x ^= h
    return x


def winning_moves(heaps):
    """Return list of (plinth_idx, take_n) that move to a losing position."""
    total = xor_sum(heaps)
    if total == 0:
        return []
    moves = []
    for i, h in enumerate(heaps):
        target = h ^ total
        if target < h:
            moves.append((i, h - target))
    return moves


def ai_move(heaps, rng, skill):
    """Return (plinth_idx, take_n) or None if no stones remain.

    skill is the percent chance of playing an exact winning move from a
    winning position; otherwise the Sibyl slips and takes a loose chunk.
    """
    if not any(heaps):
        return None
    win = winning_moves(heaps)
    if win and rng.random() * 100 < skill:
        return rng.choice(win)
    # a slip: from a losing spot, or when her nerve fails — take a chunk
    legal = [(i, n) for i, h in enumerate(heaps) if h for n in range(1, h + 1)]
    i, _ = rng.choice(legal)
    h = heaps[i]
    n = rng.randint(1, h) if h > 1 else 1
    return (i, n)


def bar(heaps):
    lines = []
    for i, h in enumerate(heaps):
        glow = h * "\u25cf"
        lines.append("  plinth {}: {:<3d} {}".format(i + 1, h, glow))
    return "\n".join(lines)


def main():
    rng_seed = random.randrange(1 << 30)
    rng = random.Random(rng_seed)
    heaps = [rng.choice(STONES) for _ in range(PLINTHS)]
    skill = 78 if rng.random() < 0.5 else 60
    gazed = False
    turns = 0
    player_took_last = False

    print("=" * 58)
    print("STONE SIBYL :: THE LAST LIGHT OF THE COURTYARD")
    print("=" * 58)
    print("Five plinths, one rule: take any pleasure of stones from any")
    print("single plinth. The visitor who takes the final stone anywhere")
    print("in the courtyard claims the prophecy. The Sibyl plays with you.")
    print()
    print("Commands: take <plinth> <n> | plinths | gaze | rule | surrender")
    print()

    while any(heaps):
        print("-" * 58)
        print("  -- the courtyard at dusk --")
        print(bar(heaps))
        print()
        if xor_sum(heaps) == 0 and not gazed:
            print("  (the Sibyl's eyes narrow — the heaps lie even. Choose warily.)")
        try:
            raw = input("your move > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nYou set your last stone down and slip from the courtyard.")
            sys.exit(0)
        if not raw:
            continue
        parts = raw.split()
        word = parts[0].lower()

        if word == "surrender":
            print("You lay your stones in a neat row and go. The Sibyl keeps the dusk.")
            sys.exit(0)
        elif word == "plinths":
            print(bar(heaps))
            continue
        elif word == "rule":
            print("  The whole courtyard is the game — the nim-sum of all five heaps.")
            print("  If the nim-sum is not zero, a clean move keeps it zero for her.")
            print("  If it is zero, every move hands her the advantage. Watch, and")
            print("  always answer my move by returning the sum to zero.")
            continue
        elif word == "gaze":
            if gazed:
                print("  Her gaze is spent — the courtyard forgets what it must not show.")
                continue
            win = winning_moves(heaps)
            if win:
                i, n = win[0]
                print("  Her eyelids part. \u201cTake {} from plinth {}.\u201d".format(n, i + 1))
            else:
                print("  \u201cThe heaps lie even; no single move hands you the prophecy.")
                print("   Play with care and watch how I answer.\u201d")
            gazed = True
            continue
        elif word == "take":
            if len(parts) != 3:
                print("  take <plinth> <n> — e.g.  take 2 4")
                continue
            try:
                i = int(parts[1]) - 1
                n = int(parts[2])
            except ValueError:
                print("  Give two numbers: plinth then stones, e.g.  take 2 4")
                continue
            if not (0 <= i < PLINTHS):
                print("  No such plinth — there are {0}, numbered 1..{0}.".format(PLINTHS))
                continue
            if heaps[i] == 0:
                print("  Plinth {} is already bare.".format(i + 1))
                continue
            if n < 1 or n > heaps[i]:
                print("  Plinth {} holds {} stones — take between 1 and {}.".format(
                    i + 1, heaps[i], heaps[i]))
                continue
            heaps[i] -= n
            turns += 1
            print("  You lift {} stone(s) from plinth {} — they roll into the dark.".format(n, i + 1))
            if not any(heaps):
                print("  The last stone leaves the courtyard in your hand.")
                player_took_last = True
                break
            pi, pn = ai_move(heaps, rng, skill)
            heaps[pi] -= pn
            turns += 1
            print("  The Sibyl glides to plinth {}: {} stone(s) fall with a sigh.".format(pi + 1, pn))
            if not any(heaps):
                print("  Her hand closes on the final stone.")
                player_took_last = False
                break
        else:
            print("  Unknown. Try: take <plinth> <n> | plinths | gaze | rule | surrender")

    print("=" * 58)
    print("THE LAST STONE IS TAKEN.")
    print("=" * 58)
    if player_took_last:
        print("  The stones at your feet go quiet. The Sibyl bows, slowly.")
        print("  \u201cThe last light belongs to you, visitor. Hear your prophecy:\u201d")
        print()
        print("       You burnt {} turns, and I could not keep the dusk.".format(turns))
        print("       Go softly, and take what is yours by patience.")
        print()
        print("  The prophecy settles in your hand like warm stone.")
    else:
        print("  The Sibyl cradles the final stone against her palm.")
        print("  \u201cA fine match, visitor — but the dusk was mine all along.\u201d")
        print("  She lets the prophecy unravel into the falling light.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nThe courtyard waits for the next visitor.")
        sys.exit(0)
