#!/usr/bin/env python3
"""0.51l -> 0.51m: undo restores the shop's seen-list so a reroll after an undo shows
the same stock; the spotlight gild takes a plain-letter seat so the shelf holds 6
(8 with Super Store). usage: patch_051m.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51l"', 'gameVersion:"0.51m"')
m = re.findall(r'const VERSION *= *"0\.51l"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51l","0.51m"))

# 1. undo restores the seen-list (rerolls dedupe against it)
rep('''    offers:G.shopOffers.map(o=>({...o, d:{...o.d}}))
  };''', '''    offers:G.shopOffers.map(o=>({...o, d:{...o.d}})),
    shopSeen:(G.shopSeen||[]).slice()   // v0.51m: a reroll after an undo must roll the same shelf
  };''')
rep('''  G.fuseOfferIdx=(s.fuseOfferIdx!=null?s.fuseOfferIdx:null); G.fusePending=null; G.perks=s.perks; G.deck=s.deck; G.shopOffers=s.offers;''',
    '''  G.fuseOfferIdx=(s.fuseOfferIdx!=null?s.fuseOfferIdx:null); G.fusePending=null; G.perks=s.perks; G.deck=s.deck; G.shopOffers=s.offers;
  if(Array.isArray(s.shopSeen)) G.shopSeen=s.shopSeen.slice();   // v0.51m''')

# 2. six on the shelf: the spotlight takes a plain-letter seat instead of adding a seventh
rep('''  { const sp=spotlightGildOffer(rng, shelfOut);
    if(sp) shelfOut.push({...sp, sold:false}); }''',
'''  { const sp=spotlightGildOffer(rng, shelfOut);   // v0.51m: takes a plain-letter seat, so the shelf stays at 6 (8 with Super Store)
    if(sp){ const plain=o=>o.kind==="Letter" && o.d && o.d.type==="letter" && !o.d.foil && !(o.d.gild>0) && !((o.d.mult||1)>1);
      let seat=-1; for(let k=0;k<N-perSide;k++){ if(plain(shelfOut[k])){ seat=k; break; } }
      if(seat>=0) shelfOut[seat]={...sp, sold:false}; } }''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
