# Daily Terminal Drop
# Date: 2026-02-16
# Title: Obsidian Harbor: Word Forge

#!/usr/bin/env python3
import random

WORDS = ['signal', 'cipher', 'ember', 'shadow', 'orbit', 'lantern', 'starlit', 'vector', 'flux', 'prism', 'echo', 'ember']


def scramble(word, rng):
    letters = list(word)
    rng.shuffle(letters)
    return "".join(letters)


def main():
    rng = random.Random(20260216)
    word = rng.choice(WORDS)
    scrambled = scramble(word, rng)
    tries = 5

    print("Word Forge")
    print("Unscramble the word. Type Q to quit.")
    print(f"Scramble: {scrambled}")

    while tries > 0:
        guess = input(f"[{tries} tries] > ").strip().lower()
        if guess == "q":
            print("Forge cools.")
            return
        if guess == word:
            print("Word reforged. You win.")
            return
        print("Not quite.")
        tries -= 1

    print(f"The word was '{word}'.")


if __name__ == "__main__":
    main()
