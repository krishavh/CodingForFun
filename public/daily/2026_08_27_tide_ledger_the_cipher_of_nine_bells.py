# Daily Terminal Drop
# Date: 2026-08-27
# Title: Tide Ledger: The Cipher of Nine Bells

#!/usr/bin/env python3
"""
TIDE LEDGER :: THE CIPHER OF NINE BELLS
=======================================
The wreckers of Bellcoast light nine bells along the shore, and each bell
rings a number. The tide takes one thing from the town each night unless
someone can read the bells' pattern and speak the next number back.

You are the ledger-keeper. Each round the bells show a sequence. Read the
rule behind it and answer with the number that comes next. Nine bells,
nine rounds, one tide.

Commands:
  <number>      your answer for this bell
  hint          spend a sandglass to narrow the rule
  score         show how you stand
  quit          let the tide take it
"""
import random
import sys

ROUNDS = 9
GLASSES = 3

def rule_arith(rng, n):
    step = rng.choice([-5, -3, -2, 2, 3, 4, 5, 7])
    a = rng.randint(1, 9)
    seq = [a + step * i for i in range(n + 1)]
    return seq[:-1], seq[-1], "a steady step of %d" % step

def rule_geo(rng, n):
    r = rng.choice([2, 3])
    a = rng.choice([1, 2, 3])
    seq = [a * r ** i for i in range(n + 1)]
    return seq[:-1], seq[-1], "each bell times %d" % r

def rule_fib(rng, n):
    a, b = rng.randint(1, 4), rng.randint(2, 6)
    seq = [a, b]
    while len(seq) < n + 1:
        seq.append(seq[-1] + seq[-2])
    return seq[:-1], seq[-1], "each bell sums the two before it"

def rule_alt(rng, n):
    step = rng.randint(2, 6)
    a = rng.randint(2, 8)
    seq = [a]
    for i in range(1, n + 1):
        seq.append(seq[-1] + (step if i % 2 else -step))
    return seq[:-1], seq[-1], "it rises and falls by turns"

RULES = [rule_arith, rule_geo, rule_fib, rule_alt]

def play():
    rng = random.Random()
    score, glasses = 0, GLASSES
    print("=" * 50)
    print("TIDE LEDGER :: THE CIPHER OF NINE BELLS")
    print("=" * 50)
    print(f"{ROUNDS} bells. Read the rule. Speak the next number.")
    print()
    solved = 0
    for rnd in range(1, ROUNDS + 1):
        seq, ans, _why = rng.choice(RULES)(rng, 3 + rnd // 3)
        print(f"--- Bell {rnd} of {ROUNDS} ---")
        print("The bells ring: " + " ".join(str(s) for s in seq) + " , ___")
        while True:
            raw = input("ledger> ").strip().lower()
            if raw == "quit":
                print("The tide comes in. Farewell, keeper.")
                return
            if raw == "score":
                print(f"Solved {solved} of {rnd - 1} so far. Sandglasses: {glasses}")
                continue
            if raw == "hint":
                if glasses <= 0:
                    print("No sandglasses left to turn.")
                    continue
                glasses -= 1
                print(f"You turn a glass. The rule is {rng.choice(RULES)(rng,4)[2]}.")
                continue
            if raw == "2 1":
                continue
            try:
                guess = int(raw)
            except ValueError:
                print("Speak a number, keeper.")
                continue
            if guess == ans:
                print("The bell answers true. The tide draws back a step.")
                solved += 1
                score += 10
            else:
                print(f"The bell tolls low. It was {ans}. The tide takes its due.")
            break
    print(f"\nDawn on Bellcoast. You answered {solved} of {ROUNDS} bells. Score: {score}")
    if solved >= 7:
        print("The town stands. They will ring for you come spring.")
    elif solved >= 4:
        print("Some houses stand, some do not. The ledger is... mixed.")
    else:
        print("The sea takes what it is owed.")

if __name__ == "__main__":
    try:
        play()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodnight, keeper.")
        sys.exit(0)
