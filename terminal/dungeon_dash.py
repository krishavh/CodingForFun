#!/usr/bin/env python3
import argparse
import json
import os
import random
import sys
from dataclasses import dataclass

WIDTH = 28
HEIGHT = 14
WALL = "#"
FLOOR = "."
PLAYER = "@"
TREASURE = "$"
TRAP = "^"
EXIT = ">"
ENEMY = "E"

TREASURE_TARGET = 5
MAX_HP = 3
SCORES_FILE = os.path.join(os.path.dirname(__file__), ".scores.json")


@dataclass
class Pos:
    x: int
    y: int


class Game:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.grid = [[FLOOR for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.player = Pos(1, 1)
        self.enemy = Pos(1, 1)
        self.hp = MAX_HP
        self.treasure = 0
        self.turns = 0
        self.message = ""
        self._generate()

    def _generate(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if x == 0 or y == 0 or x == WIDTH - 1 or y == HEIGHT - 1:
                    self.grid[y][x] = WALL

        for _ in range(int(WIDTH * HEIGHT * 0.12)):
            x = self.rng.randint(1, WIDTH - 2)
            y = self.rng.randint(1, HEIGHT - 2)
            self.grid[y][x] = WALL

        self._place_items(TRAP, int(WIDTH * HEIGHT * 0.05))
        self._place_items(TREASURE, TREASURE_TARGET + 2)

        self._place_exit()
        self.player = self._random_empty()
        self.enemy = self._random_empty(avoid=[self.player])

    def _place_items(self, item: str, count: int):
        placed = 0
        while placed < count:
            pos = self._random_empty()
            self.grid[pos.y][pos.x] = item
            placed += 1

    def _place_exit(self):
        while True:
            pos = self._random_empty()
            if pos.x > WIDTH // 2 and pos.y > HEIGHT // 2:
                self.grid[pos.y][pos.x] = EXIT
                return

    def _random_empty(self, avoid=None):
        avoid = avoid or []
        while True:
            x = self.rng.randint(1, WIDTH - 2)
            y = self.rng.randint(1, HEIGHT - 2)
            if self.grid[y][x] != FLOOR:
                continue
            if any(a.x == x and a.y == y for a in avoid):
                continue
            return Pos(x, y)

    def draw(self):
        clear_screen()
        header = f"HP:{self.hp}  Treasure:{self.treasure}/{TREASURE_TARGET}  Turns:{self.turns}"
        print(header)
        print("-" * len(header))
        for y in range(HEIGHT):
            row = []
            for x in range(WIDTH):
                if self.player.x == x and self.player.y == y:
                    row.append(PLAYER)
                elif self.enemy.x == x and self.enemy.y == y:
                    row.append(ENEMY)
                else:
                    row.append(self.grid[y][x])
            print("".join(row))
        if self.message:
            print("\n" + self.message)
            self.message = ""

    def move_player(self, dx: int, dy: int):
        nx = self.player.x + dx
        ny = self.player.y + dy
        if self.grid[ny][nx] == WALL:
            self.message = "You bump into a wall."
            return
        self.player = Pos(nx, ny)
        cell = self.grid[ny][nx]
        if cell == TREASURE:
            self.treasure += 1
            self.grid[ny][nx] = FLOOR
            self.message = "Treasure collected."
        elif cell == TRAP:
            self.hp -= 1
            self.grid[ny][nx] = FLOOR
            self.message = "A trap! You lose 1 HP."
        elif cell == EXIT:
            if self.treasure >= TREASURE_TARGET:
                self.message = "You escape with the loot."
            else:
                self.message = f"Exit locked. Need {TREASURE_TARGET - self.treasure} more treasure."
        if self.enemy.x == self.player.x and self.enemy.y == self.player.y:
            self.hp -= 1
            self.message = "The shadow catches you! -1 HP."

    def move_enemy(self):
        options = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        self.rng.shuffle(options)
        for dx, dy in options:
            nx = self.enemy.x + dx
            ny = self.enemy.y + dy
            if self.grid[ny][nx] == WALL:
                continue
            self.enemy = Pos(nx, ny)
            return

    def is_won(self):
        return self.grid[self.player.y][self.player.x] == EXIT and self.treasure >= TREASURE_TARGET

    def is_lost(self):
        return self.hp <= 0


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_score(name: str, turns: int):
    scores = load_scores()
    scores.append({"name": name, "turns": turns})
    scores = sorted(scores, key=lambda s: s["turns"])[:10]
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)


def show_scores():
    scores = load_scores()
    if not scores:
        print("No scores yet. Be the first!")
        return
    print("Top Runs (fewest turns):")
    for i, s in enumerate(scores, 1):
        print(f"{i}. {s['name']} - {s['turns']} turns")


def help_text():
    return (
        "Controls: W/A/S/D to move, R to rest, Q to quit\n"
        "Goal: collect treasure and reach the exit. Avoid traps and the shadow."
    )


def main():
    parser = argparse.ArgumentParser(description="Dungeon Dash - a tiny terminal roguelike.")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--scores", action="store_true")
    args = parser.parse_args()

    if args.scores:
        show_scores()
        return

    rng = random.Random(args.seed)
    game = Game(rng)

    while True:
        game.draw()
        if game.is_won():
            print("\nYou win!")
            name = input("Name for leaderboard: ").strip() or "anon"
            save_score(name, game.turns)
            break
        if game.is_lost():
            print("\nYou were defeated. Try again.")
            break

        print("\n" + help_text())
        cmd = input("> ").strip().lower()
        if not cmd:
            continue
        if cmd[0] == "q":
            print("Goodbye.")
            break
        if cmd[0] == "r":
            game.turns += 1
            game.move_enemy()
            if game.enemy.x == game.player.x and game.enemy.y == game.player.y:
                game.hp -= 1
                game.message = "The shadow catches you! -1 HP."
            continue

        moves = {
            "w": (0, -1),
            "a": (-1, 0),
            "s": (0, 1),
            "d": (1, 0),
        }
        if cmd[0] in moves:
            dx, dy = moves[cmd[0]]
            game.move_player(dx, dy)
            game.turns += 1
            if not game.is_won():
                game.move_enemy()
                if game.enemy.x == game.player.x and game.enemy.y == game.player.y:
                    game.hp -= 1
                    game.message = "The shadow catches you! -1 HP."
        else:
            game.message = "Unknown command."


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
