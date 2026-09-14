# Daily Terminal Drop
# Date: 2026-09-14
# Title: Belltower Siege: Wave Defense

#!/usr/bin/env python3
"""BELLTOWER SIEGE - an original terminal tower-defense for one player.

The village bells must keep ringing until dawn. Waves of raiders march
up the causeway toward the belltower. You command the tower's
DEFENDERS, hired onto lanes that cover the causeway, and each beat the
closest raider in an armed lane takes the hit.

Hiring costs GRIT, which drips in one point per beat:
  a = archer       (4 grit) - hits lane, 1 damage every 2 beats
  c = bell-caster  (7 grit) - hits lane, 2 damage every 4 beats + stun
  w = wallwright   (5 grit) - no shot; patches the gate for +2 instead

Raids come in three waves, each longer and meaner than the last.
Survive all three and the dawn belongs to you.

Commands at each beat:
  a / c / w    hire that defender (you'll be asked which lane, 1-3)
  pass         hold your grit and let the beat resolve
  look         redraw the causeway
  quit         lower the banner

Legend: r = raider  D = defender on a ledge  . = empty causeway
The gate is at the left edge; raiders spawn at the right.
"""
import random
import sys

LANES = 3
STEPS = 11
GATE_HP = 10
WAVES = 3
WAVE_BEATS = {1: 14, 2: 18, 3: 22}

DEFENDERS = {
    "a": {"name": "archer", "cost": 4, "range": 5, "dmg": 1, "cd": 2},
    "c": {"name": "bell-caster", "cost": 7, "range": 4, "dmg": 2, "cd": 4},
}
WALLWRIGHT_COST = 5

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class Defender:
    LEDGE = 1  # defenders sit one step out from the gate
    def __init__(self, kind, lane):
        spec = DEFENDERS[kind]
        self.kind = kind
        self.lane = lane
        self.step = self.LEDGE
        self.dmg = spec["dmg"]
        self.range = spec["range"]
        self.cd = spec["cd"]
        self.ready = 0

def draw(defenders, raiders, grit, gate_hp, wave, beat, beats, log_lines):
    print()
    print(f"BELLTOWER SIEGE   wave {wave}/{WAVES}   beat {beat}/{beats}"
          f"   grit {grit}   gate {gate_hp}/{GATE_HP}")
    print("gate << causeway")
    for lane in range(LANES):
        cells = []
        for s in range(STEPS):
            if any(r["lane"] == lane and r["step"] == s for r in raiders):
                cells.append("r")
            elif any(d.lane == lane and d.step == s for d in defenders):
                cells.append("D")
            else:
                cells.append(".")
        print(" ".join(cells))
    for line in log_lines[-3:]:
        print("  " + line)

def spawn(wave, rng):
    """Maybe spawn a raider at the far edge; later waves spawn more."""
    chance = 0.28 + 0.09 * wave
    if rng.random() < chance:
        return {"lane": rng.randrange(LANES), "step": STEPS - 1,
                "hp": 2 + wave, "stun": 0}
    return None

def fire(defenders, raiders, log):
    """Each defender with a loaded shot hits the closest raider in range."""
    for d in defenders:
        if d.ready > 0:
            d.ready -= 1
            continue
        targets = [r for r in raiders
                   if r["lane"] == d.lane and r["step"] <= d.range]
        if not targets:
            continue
        tgt = min(targets, key=lambda r: r["step"])
        tgt["hp"] -= d.dmg
        if d.kind == "c":
            tgt["stun"] = 1
            log.append(f"bell tolls on lane {d.lane + 1}: raider stunned")
        d.ready = d.cd
        if tgt["hp"] <= 0:
            raiders.remove(tgt)
            log.append(f"lane {d.lane + 1}: raider down")

def march(raiders, gate_hp, log):
    """Move every raider one step toward the gate; stuns hold them."""
    for r in list(raiders):
        if r["stun"] > 0:
            r["stun"] -= 1
            continue
        r["step"] -= 1
        if r["step"] < 0:
            raiders.remove(r)
            gate_hp -= 1
            log.append("a raider reaches the gate!")
    return gate_hp

def main():
    rng = random.Random()
    grit = 6
    gate_hp = GATE_HP
    defenders = []
    raiders = []
    log = []
    print(__doc__)
    for wave in range(1, WAVES + 1):
        beats = WAVE_BEATS[wave]
        for beat in range(1, beats + 1):
            new = spawn(wave, rng)
            if new:
                raiders.append(new)
                log.append(f"wave {wave}: raider advances on lane {new['lane'] + 1}")
            grit += 1
            fire(defenders, raiders, log)
            gate_hp = march(raiders, gate_hp, log)
            if gate_hp <= 0:
                draw(defenders, raiders, grit, gate_hp, wave, beat, beats, log)
                print("THE GATE FALLS. The bells go silent.")
                return
            print(f"beat {beat} (wave {wave}) - a/c/w, pass, look, quit")
            cmd = input("> ").strip().lower()
            if cmd in ("quit", "q"):
                print("You lower the banner. The siege stands unended.")
                return
            if cmd == "look":
                draw(defenders, raiders, grit, gate_hp, wave, beat, beats, log)
            elif cmd in DEFENDERS:
                cost = DEFENDERS[cmd]["cost"]
                if grit < cost:
                    print("not enough grit")
                    continue
                lane_txt = input("lane 1-3> ").strip()
                try:
                    lane = clamp(int(lane_txt), 1, 3) - 1
                except ValueError:
                    print("no lane chosen; hire cancelled")
                    continue
                defenders.append(Defender(cmd, lane))
                grit -= cost
                log.append(f"{DEFENDERS[cmd]['name']} takes a ledge on lane {lane + 1}")
            elif cmd == "w":
                if grit < WALLWRIGHT_COST:
                    print("not enough grit")
                    continue
                grit -= WALLWRIGHT_COST
                gate_hp = min(GATE_HP, gate_hp + 2)
                log.append("wallwright re-tars the gate (+2)")
            elif cmd in ("pass", ""):
                pass
            else:
                print("say a, c, w, pass, look, or quit")
    draw(defenders, raiders, grit, gate_hp, WAVES, WAVE_BEATS[WAVES],
         WAVE_BEATS[WAVES], log)
    if gate_hp > 0:
        print(f"DAWN. The bells ring on. Gate held at {gate_hp}/{GATE_HP}.")
    else:
        print("THE GATE FALLS as the sky lightens.")

if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nThe causeway goes quiet.")
        sys.exit(0)
