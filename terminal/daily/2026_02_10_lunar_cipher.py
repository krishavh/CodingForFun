# Daily Terminal Drop
# Date: 2026-02-10
# Title: Lunar Cipher: Vault Code

#!/usr/bin/env python3
import random


def score_guess(secret, guess):
    exact = sum(1 for a, b in zip(secret, guess) if a == b)
    shared = sum(min(secret.count(d), guess.count(d)) for d in set(guess))
    return exact, shared - exact


def main():
    rng = random.Random(20260210)
    digits = [str(rng.randint(0, 9)) for _ in range(4)]
    secret = "".join(digits)
    tries = 8
    print("Vault Code")
    print("Guess the 4-digit code. Duplicates allowed.")

    while tries > 0:
        guess = input(f"[{tries} tries] > ").strip()
        if guess.lower() == "q":
            print("Vault sealed.")
            return
        if not (len(guess) == 4 and guess.isdigit()):
            print("Enter exactly 4 digits.")
            continue

        exact, near = score_guess(secret, guess)
        if exact == 4:
            print("Vault opened.")
            return
        print(f"Exact: {exact} | Near: {near}")
        tries -= 1

    print(f"Lockdown. Code was {secret}.")


if __name__ == "__main__":
    main()
