# Daily Terminal Drop
# Date: 2026-08-22
# Title: Nocturne Array: Ghost Frequencies

#!/usr/bin/env python3
"""
NOCTURNE ARRAY: GHOST FREQUENCIES
=================================
A dead relay station on the rim of the dark grid still hums. Somewhere in
its four empty bays a phantom broadcast is waiting to be locked — a string
of four old frequencies, each from a palette of six, order mattered.

You are a signal-watcher sent to tune the array. Guess a four-frequency
setting. The station answers honestly:
    *  a peg is exact — that frequency and that bay are locked
    o  a peg drifts — that frequency exists, but in another bay

Lock every bay before the static eats the dial (finite attempts) and you
resolve the ghost broadcast. Listen close; the dead pulse answers.

Commands:
  tune <code>    try a setting, e.g.  tune RFGY
  history        redraw the guess log
  trace <color>  once per watch: learn how many bays hold that color
  legend         re-list the frequency palette
  quit           abandon the watch
"""
import random
import sys

LEN = 4               # bays to lock
PALETTE = ["R", "A", "Z", "G", "V", "O"]   # Rad Amber Zinc Green Violet Onyx
FULL = {
    "R": "Rad (red)",
    "A": "Amber (burning gold)",
    "Z": "Zinc (pale grey)",
    "G": "Green (moss)",
    "V": "Violet (deep iris)",
    "O": "Onyx (black glass)",
    "C": "Cinder (ash)",
    "P": "Pale (moon)",
}
NAME = {k: v.split(" (")[0] for k, v in FULL.items()}
ATTEMPTS = 11         # guesses before the static eats the dial
TRACES = 1            # trace tokens


def make_secret(rng):
    return [rng.choice(PALETTE) for _ in range(LEN)]


def evaluate(guess, secret):
    """Return (exact, drifting) counts — fairness both ways, no double count."""
    exact = sum(1 for g, s in zip(guess, secret) if g == s)
    # number of position-mismatched tokens that still exist somewhere unused
    unmatched_secret = []
    unmatched_guess = []
    for g, s in zip(guess, secret):
        if g == s:
            continue
        unmatched_secret.append(s)
        unmatched_guess.append(g)
    drift = 0
    used = [False] * len(unmatched_secret)
    for g in unmatched_guess:
        for i, s in enumerate(unmatched_secret):
            if not used[i] and s == g:
                used[i] = True
                drift += 1
                break
    return exact, drift


def render_log(history):
    if not history:
        return "  (the bays are silent — tune a setting)"
    lines = ["  guess     pegs"]
    for entry in history:
        code = "".join(entry["code"])
        ex, dr = entry["exact"], entry["drift"]
        pegs = ("*" * ex) + ("o" * dr)
        lines.append(f"  {code:<10s}{pegs if pegs else '.'}")
    return "\n".join(lines)


def main():
    rng = random.Random()
    secret = make_secret(rng)
    history = []
    traces = TRACES
    trace_used = set()

    print("=" * 58)
    print("NOCTURNE ARRAY :: GHOST FREQUENCIES")
    print("=" * 58)
    print("Four bays await a phantom stream. Palette (order is everything):")
    for k in PALETTE:
        print(f"    [{k}] {NAME[k]}/{FULL[k].split(' (')[1][:-1]}")
    print()
    print(f"You have {ATTEMPTS} tunes before the static eats the dial.")
    print("Pegs: * = exact bay   o = right frequency, wrong bay")
    print("Commands: tune <code> | history | trace <color> | legend | quit")
    print()

    while len(history) < ATTEMPTS:
        print("-" * 58)
        print(render_log(history))
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nThe static eats the dial. The phantom broadcasts on untuned.")
            sys.exit(0)
        if not raw:
            continue
        parts = raw.split()
        word = parts[0].lower()

        if word == "quit":
            print("You step from the array. The bays go back to humming wrong.")
            sys.exit(0)
        elif word == "legend":
            for k in PALETTE:
                print(f"  [{k}] {NAME[k]} — {FULL[k].split(' (')[1][:-1]}")
            continue
        elif word == "history":
            continue  # already redrawn each loop
        elif word == "trace":
            if traces <= 0:
                print("  No trace tokens remain this watch.")
                continue
            if len(parts) < 2 or parts[1].upper() not in PALETTE:
                print("  Trace which color? " + " ".join(PALETTE))
                continue
            color = parts[1].upper()
            if color in trace_used:
                print(f"  You already traced {NAME[color]}.")
                continue
            trace_used.add(color)
            traces -= 1
            n = secret.count(color)
            print(f"  The dead pulse holds {NAME[color]} in {n} bay(s).")
            continue
        elif word == "tune":
            if len(parts) < 2:
                print("  tune <code> — four frequencies, e.g. tune RFGY")
                continue
            code = parts[1].upper()
            code = [c for c in code if c.isalpha()][:LEN]
            if len(code) != LEN:
                print(f"  Give exactly {LEN} frequencies, one per bay (e.g. RFGY).")
                continue
            if any(c not in PALETTE for c in code):
                print("  Use only the palette: " + " ".join(PALETTE))
                continue
            ex, dr = evaluate(code, secret)
            history.append({"code": code, "exact": ex, "drift": dr})
            if ex == LEN:
                print(render_log(history))
                break
            pegs = ("*" * ex) + ("o" * dr)
            print(f"  pegs: {pegs or '.'}  ({ex} locked, {dr} drifting)")
        else:
            print("  Unknown. Try: tune <code> | history | trace <color> | legend | quit")
        print()

    final = history[-1] if history else None
    won = final and final["exact"] == LEN
    print("=" * 58)
    if won:
        code = "".join(final["code"])
        used = len(history)
        streak = ATTEMPTS - used
        print(f"BAY-BY-BAY PULSE LOCKED on tune {used}: {code}")
        print("The phantom broadcast resolves into a clean, warm carrier wave.")
        print("Ghost frequencies, made flesh. The dead relay sings again.")
        print(f"  Locked with {streak} tune(s) to spare — a clean resolve.")
    else:
        print("The static eats the dial. The watch is over.")
        print("The true stream was: " + "".join(secret))
        print("Somewhere in the black, the array hums on, waiting for a sharper ear.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nThe static eats the dial. The phantom broadcasts on untuned.")
        sys.exit(0)
