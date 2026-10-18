#!/usr/bin/env python3
"""0.51i -> 0.51j: triple fusion upgrade more common; when it rolls without a single
fusion on the shelf, a single fusion joins it (taking another perk seat) instead of
replacing it. usage: patch_051j.py in.html out.html [trioWeight]"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
W = sys.argv[3] if len(sys.argv) > 3 else "1.6"
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51i"', 'gameVersion:"0.51j"')
m = re.findall(r'const VERSION *= *"0\.51i"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51i","0.51j"))
rep('''        ? [{make:()=>trioUpgradeOffer(),  weight:0.5},    // v0.51i: was 1.2''',
    '''        ? [{make:()=>trioUpgradeOffer(),  weight:%s},    // v0.51j: was 0.5 (0.51i), 1.2 before''' % W)
rep('''  { const ti=shelfOut.findIndex(o=>o.d&&o.d.type==="trioUpgrade");   // v0.51i
    if(ti>=0 && !shelfOut.some(o=>o.d&&o.d.type==="fuse")) shelfOut[ti]={...fusionOffer(),sold:false}; }''',
'''  { const ti=shelfOut.findIndex(o=>o.d&&o.d.type==="trioUpgrade");   // v0.51j: a triple fusion brings a single fusion with it
    if(ti>=0 && !shelfOut.some(o=>o.d&&o.d.type==="fuse")){
      let seat=-1; for(let k=shelfOut.length-1;k>=N-perSide;k--){ if(k!==ti){ seat=k; break; } }   // the last other perk seat
      if(seat>=0) shelfOut[seat]={...fusionOffer(),sold:false}; } }''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
