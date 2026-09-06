# Daily Terminal Drop
# Date: 2026-09-06
# Title: The Moultering Deep: Shed Your Skin or Be Shed

#!/usr/bin/env python3
"""
THE MOULTERING DEEP :: SHED YOUR SKIN OR BE SHED
=================================================
You are a young deep-diver in a borrowed hardsuit, dropped into the
MOULTERING: a flooded mining shaft the old crews abandoned when the
walls started to shrink. Something down here molts -- and it hunts
by the heat your suit bleeds.

Reach the ESCENT SHAFT (>) on the far side of the level before your
AIR runs out. The shaft door is sealed: you must carry at least one
POWER CELL (collect the * cells and 'charge' one) to open it.

The water is dark and the map is unknown -- you only see as far as
your TORCH reaches. Lit torch = see far, but your heat blooms and the
MOULTER (M) homes in on you. Dark = near-blind, but it loses your scent.

Resources:
  AIR    every move costs air; a LIT torch burns extra each move.
  LAMP   torch battery; drains while lit. Refill on a * with 'charge'.
  STIMS  a few shots of sedative; 'sedate' staggers the creature.

Commands:
  w a s d        move up / left / down / right
  wait           hold still (cheaper air, but the dark presses on)
  light / dark   toggle the torch
  sedate         fire a stim (stuns the Moulter for a few turns)
  charge         on a *, siphon a cell into your lamp (counts as carried)
  look           redraw the board
  quit           surface empty-handed

Legend:  # wall   . water   @ you   * cell   > eshaft   M moulter
"""
import sys, random
from collections import deque

W, H = 16, 12
DIRS = ((1,0),(-1,0),(0,1),(0,-1))

def carve(rng):
    grid = [['#']*W for _ in range(H)]
    stack = [(1,1)]
    grid[1][1] = '.'
    while stack:
        y,x = stack[-1]
        opts = [(y+dy, x+dx) for dy,dx in ((2,0),(-2,0),(0,2),(0,-2))
                if 1 <= y+dy < H-1 and 1 <= x+dx < W-1 and grid[y+dy][x+dx]=='#']
        if not opts:
            stack.pop(); continue
        ny,nx = rng.choice(opts)
        grid[y+(ny-y)//2][x+(nx-x)//2] = '.'
        grid[ny][nx] = '.'
        stack.append((ny,nx))
    # braid a few loops so it's not a perfect maze
    for _ in range(W):
        y = rng.randrange(1,H-1); x = rng.randrange(1,W-1)
        if grid[y][x]=='#': grid[y][x]='.'
    return grid

def bfs_reach(grid, sy, sx):
    q = deque([(sy,sx)]); seen = {(sy,sx)}
    while q:
        y,x = q.popleft()
        for dy,dx in DIRS:
            ny,nx = y+dy, x+dx
            if 0<=ny<H and 0<=nx<W and grid[ny][nx]!='#' and (ny,nx) not in seen:
                seen.add((ny,nx)); q.append((ny,nx))
    return seen

def man(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

class Game:
    def __init__(self):
        self.rng = rng = random.Random()
        while True:
            self.grid = grid = carve(rng)
            open_t = [(y,x) for y in range(H) for x in range(W) if grid[y][x]=='.']
            self.py,self.px = 1,1
            self.ey,self.ex = max(open_t, key=lambda t: man(t,(1,1)))
            if man((self.ey,self.ex),(1,1)) < 10: continue
            grid[self.ey][self.ex] = '>'
            reach = bfs_reach(grid,1,1)
            if (self.ey,self.ex) not in reach: continue
            pool = [t for t in open_t if t not in ((1,1),(self.ey,self.ex)) and t in reach]
            if len(pool) < 8: continue
            rng.shuffle(pool)
            self.cells = set(pool[:6])
            self.mo = max(pool[6:], key=lambda t: man(t,(1,1))) if len(pool)>6 else (H-2,W-2)
            break
        self.air, self.lamp, self.stims = 240, 120, 3
        self.lit, self.seen, self.heat, self.stun = True, set(), 0, 0
        self.carried = False; self.won = False
    def see(self):
        r = 3 if (self.lit and self.lamp>0) else 1
        for dy in range(-r,r+1):
            for dx in range(-r,r+1):
                if abs(dy)+abs(dx) <= r:
                    y,x = self.py+dy, self.px+dx
                    if 0<=y<H and 0<=x<W: self.seen.add((y,x))
    def moulter(self):
        if self.stun>0: self.stun-=1; return
        self.heat = min(9, self.heat+2) if (self.lit and self.lamp>0) else max(0,self.heat-1)
        reach = max(3, 14-self.heat)
        my,mx = self.mo
        opts = [(man((my+dy,mx+dx),(self.py,self.px)), my+dy, mx+dx)
                for dy,dx in DIRS
                if 0<=my+dy<H and 0<=mx+dx<W and self.grid[my+dy][mx+dx]!='#']
        if not opts: return
        opts.sort()
        if man(self.mo,(self.py,self.px)) <= reach: _,my,mx = opts[0]
        else: _,my,mx = self.rng.choice(opts)
        self.mo = (my,mx)
    def air_cost(self, base):
        self.air -= base + (3 if (self.lit and self.lamp>0) else 0)
        if self.lit and self.lamp>0:
            self.lamp -= 4
            if self.lamp<=0: print("  The lamp gutters dead -- you are dark."); self.lit=False
    def alive(self):
        if (self.py,self.px)==self.mo:
            print("\n  Something vast and wet folds over your helmet. The suit splits.\n"); sys.exit(0)
        if self.air<=0:
            print("\n  Your last breath fogs the glass. The deep keeps its ledger.\n"); sys.exit(0)
    def render(self):
        for y in range(H):
            row=[]
            for x in range(W):
                ch=self.grid[y][x]
                if (y,x)==(self.py,self.px): ch='@'
                elif (y,x)==self.mo and ((self.lit and self.lamp>0) or man((y,x),(self.py,self.px))<=2): ch='M'
                elif (y,x) in self.cells: ch='*'
                elif (y,x) not in self.seen: ch=' '
                row.append(ch)
            print(''.join(row))
        print("  AIR %d  LAMP %d  STIMS %d  TORCH %s  heat %d  cell %s"
              % (max(0,self.air), max(0,self.lamp), self.stims,
                 'LIT' if self.lit else 'DARK', self.heat, 'yes' if self.carried else 'no'))
    def step(self, dy, dx):
        ny,nx = self.py+dy, self.px+dx
        if not(0<=ny<H and 0<=nx<W) or self.grid[ny][nx]=='#':
            print("  Solid barnacle. No."); return
        self.py,self.px = ny,nx
        self.see(); self.air_cost(2); self.moulter(); self.check()
    def check(self):
        if self.grid[self.py][self.px]=='>' and self.carried:
            self.won=True
        self.alive()
    def run(self):
        print(__doc__)
        self.see()
        while not self.won:
            self.render()
            try: cmd = input("  > ").strip().lower()
            except EOFError: return
            if not cmd: continue
            h = cmd.split()[0]
            if h in ('w','a','s','d'):
                self.step(*{'w':(-1,0),'s':(1,0),'a':(0,-1),'d':(0,1)}[h])
            elif h=='wait': self.see(); self.air_cost(1); self.moulter(); self.check()
            elif h=='light': self.lit=True
            elif h=='dark': self.lit=False
            elif h=='sedate':
                if self.stims<=0: print("  No stims left."); continue
                self.stims-=1; self.stun=3; print("  Sedative clouds the water; the thing goes slack.")
            elif h=='charge':
                if (self.py,self.px) in self.cells:
                    self.cells.discard((self.py,self.px)); self.lamp=120; self.carried=True
                    print("  A cell hums into your pack. Lamp full.")
                else: print("  Stand on a '*' to charge.")
            elif h=='look': self.render()
            elif h=='quit':
                print("  You surface empty-handed. The shaft keeps its secret."); return
        print("\n  The eshaft swallows you; you rise with the tide, prize in hand.\n")

if __name__=='__main__':
    Game().run()
