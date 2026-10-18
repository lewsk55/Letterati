#!/usr/bin/env python3
"""0.51p -> 0.51q: the hit stop after a word is set played a 150 Hz sawtooth buzz that
read as harsh and grating. It now plays a soft bell pickup on G (the fifth of the C major
word chime that follows), so the freeze sounds like a held breath that resolves into the
payoff. usage: patch_051q.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51p"', 'gameVersion:"0.51q"')
m = re.findall(r'const VERSION *= *"0\.51p"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51p","0.51q"))

# the new hit stop sound, defined next to the word chime it leads into
rep('''function wordChime(len){''',
'''/* v0.51q: hit stop pickup. A quiet bell on G5 with a softer G4 under it. G is the
   fifth of the C major chime that fires on release, so the freeze sets up the payoff
   instead of buzzing over it. Pure sines, gentle attack, short ring. */
function hitstopChime(){
  _bell(783.99, 0, 0.26, 0.06);
  _bell(392.00, 0.004, 0.22, 0.045);
}
function wordChime(len){''')

rep('''    _tone(150, 0.10, 0.085, "sawtooth");
    haptic(22);''',
'''    hitstopChime();   // v0.51q: was a 150 Hz sawtooth buzz
    haptic(22);''')

open(OUT, "w", encoding="utf-8").write(s)
print("wrote", OUT)
