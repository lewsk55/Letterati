#!/usr/bin/env python3
"""0.51g -> 0.51h: golden letter challenge reward had no Confirm bar, so a picked
tile could never be applied. usage: patch_051h.py in.html out.html"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51g"', 'gameVersion:"0.51h"')
m = re.findall(r'const VERSION *= *"0\.51g"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51g","0.51h"))
rep('''  freegild:"Gild", department:''', '''  freegild:"Gild", freegolden:"Make golden:", department:''')
rep('''  if(mode==="freegild"){ const v=effValue(c); extra=`<small>${v} points → ${v*2} points</small>`; }''',
'''  if(mode==="freegild"){ const v=effValue(c); extra=`<small>${v} points → ${v*2} points</small>`; }
  else if(mode==="freegolden"){ extra=`<small>Every word with it scores ×${G._goldenMult||1.25}</small>`; }   // v0.51h''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
