# Daily Terminal Drop
# Date: 2026-08-26
# Title: The Ash Road: The Mule-Runner's Ledger

#!/usr/bin/env python3
"""
THE ASH ROAD :: THE MULE-RUNNER'S LEDGER
=======================================
The Ash Road is no highway of kings — it is a long grey thread that the
mule-trains beat flat between the market towns of the high country. You
are a runner with one good mule, a leather ledger, and a sum of coin
burning a hole in your belt.

Between here and the terminus, the wagon, the change of season, and the
mood of each town market decide who eats and who walks. Buy where a good
sits low, sell where it fetches dear, keep the mule within her load, pay
the tolls and the toll-takers, and walk into the terminus square with
more coin than you started.

The four goods of the route:
  Salt    the dull eternal thing   (cheap, steady, always sellable)
  Wax     the night-market staple  (swings with the candle harvest)
  Copper  the smiths' hunger       (rises near the foundries)
  Spice   the gamble of the south  (dear, scarce, loves a fair)

Commands at a market:
  buy <good> <qty>   purchase at today's town price
  sell <good> <qty>  sell what the mule carries
  market             re-print today's prices
  ledger             show coin, load, and your holdings
  ride               saddle up and take the road to the next town
  quit               abandon the run
"""
import random
import sys

GOODS = [
    ("salt",   "SALT",   "\u25a1",  3,  6),   # cheap, narrow
    ("wax",    "WAX",    "\u2b22",  4,  9),
    ("copper", "COPPER", "\u25c9",  6, 12),
    ("spice",  "SPICE",  "\u2726",  9, 18),
]
CAPACITY = 20          # units the mule can carry
START_COIN = 60
LEGS = 5               # market towns, then the terminus = 6 stops total
TARGET = 170           # coin at the terminus that marks a proper run


def make_market(rng):
    """Return a dict good->price for today's town mood."""
    prices = {}
    for key, _name, _glyph, lo, hi in GOODS:
        swing = rng.uniform(-0.25, 0.35)
        p = int(round((lo + hi) / 2 * (1 + swing)))
        prices[key] = max(1, p)
    return prices


def tally(hold):
    return sum(hold.values())


def market_row(prices):
    head = "  {:<4} {:>7} {:>6}".format("good", "price", "load")
    rows = [head, "  " + "-" * 22]
    for key, name, glyph, _lo, _hi in GOODS:
        rows.append("  {} {:<6}{:>6}   {:>4}".format(
            glyph, name, prices[key], HOLD[key]))
    return "\n".join(rows)


def hold_weight():
    return sum(HOLD.values())


# globals mutated by helpers (kept simple)
HOLD = {g[0]: 0 for g in GOODS}


def ride_event(rng):
    """One road happening between towns."""
    roll = rng.random()
    if roll < 0.20:
        lost = rng.randint(2, 5)
        print("\n  Bandits wave the ledger, not the blade. A highway toll of\n"
              "  {} coin buys the road onward.".format(lost))
        return -lost
    if roll < 0.32:
        got = rng.randint(6, 14)
        print("\n  A stranded trader pays your good name. {} coin in your belt.".format(got))
        return got
    if roll < 0.44:
        print("\n  A broken axle pins you a morning. You pay a smith {} coin.".format(3))
        return -3
    if roll < 0.52:
        key = rng.choice([g[0] for g in GOODS])
        HOLD[key] += 1
        print("\n  A wrecked pack-mule gives up a stray unit of {} — yours now.".format(key))
        return 0
    print("\n  The road is empty, grey, and kind. Nothing asks for coin.")
    return 0


def banner():
    print("=" * 62)
    print("THE ASH ROAD :: THE MULE-RUNNER'S LEDGER")
    print("=" * 62)
    print("Five towns and the terminus circuit lie ahead. Buy low, sell")
    print("dear, keep the mule within her load, and reach the square rich.")
    print()
    for _key, name, glyph, lo, hi in GOODS:
        print("  {}  {:<6} {}-{} coin".format(glyph, name, lo, hi))
    print()
    print("  market | ledger | buy <g> <q> | sell <g> <q> | ride | quit")


def epitaph(coin, rng):
    if coin >= 260:
        return ("The traders strike your name from the ledger only to add it\n"
                "in ink that shines. They call the run yours for a decade.")
    if coin >= TARGET:
        return ("A clean, rich circuit. The mule is grained for life and the\n"
                "town watches your dust with respect.")
    if coin >= 100:
        return ("You keep your coat and your pride. A middling run that paid\n"
                "for the winter and not much more.")
    if coin >= START_COIN:
        return ("You walked home the richer, though no one will carve your name\n"
                "for it. The road keeps feeding those who watch the prices.")
    return ("The road takes most of it back, as roads do. Still you rode it,\n"
            "and the ledger remembers you walked out alive.")


def main():
    rng = random.Random()
    coin = START_COIN
    for key, _n, _g, _l, _h in GOODS:
        HOLD[key] = 0
    town = 0
    target_name = None
    banner()

    # The terminus names the one good it will pay a premium for.
    if target_name is None:
        target = rng.choice(GOODS)
        target_name = target[0]

    while town < LEGS:
        town += 1
        print("\n" + "~" * 62)
        if town == LEGS:
            suffix = " — the terminus square at last"
        else:
            suffix = " — market town {}/{}".format(town, LEGS - 1)
        print("  TOWN {} of {}:{}".format(town, LEGS, suffix))
        print("~" * 62)
        prices = make_market(rng)

        while True:
            print()
            print(market_row(prices))
            print("    coin: {}    load: {}/{}".format(coin, hold_weight(), CAPACITY))
            try:
                raw = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nYou fold the ledger and walk off the Ash Road.")
                sys.exit(0)
            if not raw:
                continue
            parts = raw.split()
            cmd = parts[0].lower()

            if cmd in ("quit", "q"):
                print("  You turn the mule from the road and fade into the dust.\n"
                      "  final coin: {}".format(coin))
                sys.exit(0)
            elif cmd == "market":
                continue
            elif cmd == "ledger":
                for key, name, glyph, _l, _h in GOODS:
                    print("  {} {:<6} x{}".format(glyph, name, HOLD[key]))
                print("  coin: {}   load: {}/{}".format(coin, hold_weight(), CAPACITY))
                continue
            elif cmd in ("buy", "sell"):
                if len(parts) < 3:
                    print("    {} <good> <qty>  — e.g.  {} copper 3".format(cmd, cmd))
                    continue
                good = parts[1].lower()
                entry = next((g for g in GOODS if g[0] == good), None)
                if entry is None:
                    print("    no such good. try: salt wax copper spice")
                    continue
                try:
                    qty = max(0, int(parts[2]))
                except ValueError:
                    print("    that is not a number of units.")
                    continue
                if qty <= 0:
                    continue
                if cmd == "buy":
                    cost = prices[good] * qty
                    if hold_weight() + qty > CAPACITY:
                        print("    the mule cannot carry that much. load: {}/{}".format(
                            hold_weight(), CAPACITY))
                        continue
                    if cost > coin:
                        afford = min(qty, coin // prices[good], CAPACITY - hold_weight())
                        print("    you can afford only {} unit(s).".format(afford))
                        continue
                    HOLD[good] += qty
                    coin -= cost
                    print("    bought {} {} at {} = {} coin.".format(
                        qty, good, prices[good], cost))
                else:
                    if HOLD[good] < qty:
                        print("    you carry only {} unit(s) of {}.".format(HOLD[good], good))
                        continue
                    gained = prices[good] * qty
                    HOLD[good] -= qty
                    coin += gained
                    print("    sold {} {} at {} = {} coin.".format(qty, good, prices[good], gained))
                continue
            elif cmd == "ride":
                break
            else:
                print("    market | ledger | buy <g> <q> | sell <g> <q> | ride | quit")

        # road event between towns (none after the final market -> terminus? we
        # still ride to terminus) — always a leg between here and next town
        coin += ride_event(rng)

    # Arrive at the terminus
    print("\n" + "=" * 62)
    print("THE TERMINUS SQUARE")
    print("=" * 62)
    prices = make_market(rng)
    # The terminus is especially hungry for the named good.
    prices[target_name] += rng.randint(4, 9)
    print("  The square's buyers call today's prices. The whole terminus")
    print("  is thick for {} — it fetches a premium.\n".format(target_name.upper()))
    print(market_row(prices))
    for key, name, glyph, _l, _h in GOODS:
        if HOLD[key]:
            gained = prices[key] * HOLD[key]
            coin += gained
            print("  sold {} unit(s) of {} for {} coin.".format(HOLD[key], name, gained))
            HOLD[key] = 0
    print("\n" + "-" * 62)
    print("  FINAL COIN: {}".format(coin))
    print("  Starting coin was {}. Net change: {:+d}.".format(START_COIN, coin - START_COIN))
    if coin >= TARGET:
        print("  Run status: A PROPER RUN — over the {} mark.".format(TARGET))
    else:
        print("  Run status: short of the {} mark by {}.".format(
            TARGET, max(0, TARGET - coin)))
    print("-" * 62)
    print(epitaph(coin, rng))
    sys.exit(0)


if __name__ == "__main__":
    main()
