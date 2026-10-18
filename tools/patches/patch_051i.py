#!/usr/bin/env python3
"""0.51h -> 0.51i: fusion offered more, triple fusion never alone, common Q+U tile,
curated 2-letter words for everyone, Short King 2-letter tier x2.5 with per-run
repeat decay. usage: patch_051i.py in.html out.html [skCurveJSON]"""
import sys, re, json
SRC, OUT = sys.argv[1], sys.argv[2]
SK_CURVE = json.loads(sys.argv[3]) if len(sys.argv) > 3 else [1.3, 1.3, 1.3, 1.3, 1.25, 1.15]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51h"', 'gameVersion:"0.51i"')
m = re.findall(r'const VERSION *= *"0\.51h"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51h","0.51i"))

# ---- 1. curated two-letter words (live play only; the seed predictor keeps the old set)
TWO = ("aa ab ad ae ag ah ai al am an ar as at aw ax ay ba be bi bo by da de do ed ef eh el em en er es et ew ex "
       "fa fe gi go ha he hi hm ho id if in is it jo ka ki la li lo ma me mi mm mo mu my na ne no nu od oe of oh oi ok "
       "om on op or os ow ox oy pa pe pi po qi re sh si so ta te ti to uh um un up us ut we wo xi xu ya ye yo za")
rep('''WORD_DENYLIST.forEach(w=>WORDS.delete(w.toLowerCase()));''',
'''WORD_DENYLIST.forEach(w=>WORDS.delete(w.toLowerCase()));
/* v0.51i: two-letter words come from a curated list (the standard word-game
   two-letter list). The dictionary also carried abbreviations (qs, qy, ft, vd...),
   which made Q and other rare letters far too easy to dump. The dropped words are
   kept aside so the pinned seed predictor still sees the old word set. */
const TWO_LETTER_OK = new Set("%s".split(" "));
const TWO_LETTER_DROPPED = [];
[...WORDS].forEach(w=>{ if(w.length===2 && !TWO_LETTER_OK.has(w)){ WORDS.delete(w); COMMON.delete(w); VERBS.delete(w); TWO_LETTER_DROPPED.push(w); } });''' % TWO)
rep('''function predRoll(seed){''', '''let _ANA_PRED=null;
function anaSetPred(){   // v0.51i: the predictor's word set, frozen to the pre-0.51i dictionary
  if(_ANA_PRED) return _ANA_PRED;
  _ANA_PRED=new Set(anaSet()); TWO_LETTER_DROPPED.forEach(w=>_ANA_PRED.add(w.split("").sort().join("")));
  return _ANA_PRED;
}
function predRoll(seed){''')
# the predictor block uses anaSet() in two places; point both at the frozen set
blk_start = s.index('function predRoll(seed){')
blk_end = s.index('function predictSeed(seed,opts){')
blk_end = s.index('\nfunction ', blk_end+10)
blk = s[blk_start:blk_end]
n = blk.count('anaSet()')
assert n >= 2, n
s = s[:blk_start] + blk.replace('anaSet()', 'anaSetPred()') + s[blk_end:]

# ---- 2. Short King: 2-letter tier x2.5, repeat decay per run
rep('''  shortTiers:{2:3.5,3:3,4:2}''', '''  shortTiers:{2:2.5,3:3,4:2}   // v0.51i: 2-letter was x3.5''')
rep('''  targetCurve:[1.3, 1.3, 1.3, 1.3, 1.25, 1.15],''', '''  targetCurve:%s,   // v0.51i (was 1.3 x4, 1.25, 1.15)''' % json.dumps(SK_CURVE).replace(",", ", "))
rep('''  { const T=charDef().shortTiers; if(T && T[effLen]) total*=T[effLen]; }''',
'''  { const T=charDef().shortTiers; if(T && T[effLen]) total*=T[effLen]; }
  // v0.51i: Short King's 2-letter words wear out. Same word again this run: x0.6, then x0.3.
  let skDecay=1;
  if(charDef().shortTiers && effLen===2 && res.every(r=>r.letter)){
    const w2=res.map(r=>r.letter.toLowerCase()).join(""), n=(G.wordPlays&&G.wordPlays[w2])||0;
    if(n>0){ skDecay = n===1 ? 0.6 : 0.3; total*=skDecay; } }''')
rep('''shortHit,shortMult,kernHit,''', '''shortHit,shortMult,skDecay,kernHit,''')
rep('''  if(sc.shortHit) parts.push(`×${multLabel(sc.shortMult)} short`);''',
'''  if(sc.shortHit) parts.push(`×${multLabel(sc.shortMult)} short`);
  if(sc.skDecay && sc.skDecay<1) parts.push(`×${sc.skDecay} played before`);   // v0.51i''')
rep('''  boon:"2, 3 and 4 letter words score ×3.5, ×3 and ×2. Five words a round.",''',
    '''  boon:"2, 3 and 4 letter words score ×2.5, ×3 and ×2. Five words a round.",''')
rep('''  bane:"No word longer than 5 letters. Targets run 30 percent higher in rounds 1 to 4, 25 percent in round 5 and 15 percent in round 6.",''',
    '''  bane:"No word longer than 5 letters. Higher targets. A 2-letter word played again this run scores ×0.6, then ×0.3.",''')

# ---- 3. fusion offered more; triple fusion leans back
rep('''        ? [{make:()=>trioUpgradeOffer(),  weight:1.2},
           {make:()=>trioFusionOffer(rng), weight:0.3}]
        : [{make:()=>trioFusionOffer(rng), weight:0.6}]),''',
'''        ? [{make:()=>trioUpgradeOffer(),  weight:0.5},    // v0.51i: was 1.2
           {make:()=>trioFusionOffer(rng), weight:0.2}]   // v0.51i: was 0.3
        : [{make:()=>trioFusionOffer(rng), weight:0.4}]),  // v0.51i: was 0.6''')
rep('''    {make:()=>fusionOffer(),       weight:1.8},''', '''    {make:()=>fusionOffer(),       weight:5.0},   // v0.51i: was 1.8''')
rep('''    {make:()=>fusedEROffer(),      weight:1.8},''', '''    {make:()=>fusedEROffer(),      weight:1.8},
    {make:()=>fusedQUOffer(),      weight:1.4},   // v0.51i''')
rep('''function fusedEROffer(){''', '''function fusedQUOffer(){   // v0.51i: a common Q+U tile
  return {kind:"Tile",rarity:"common",name:"Fused Q+U",
    desc:"One tile fusing Q and U. Play it as either letter, or as QU.",
    price:fuseTilePrice(px(7)),
    art:`<span class="mini-tile" style="background:linear-gradient(180deg,#EAF3EF,#D8E8E0);border-color:#A9CcBD;font-size:.74rem;font-family:var(--serif)">QU<span class="mv">11</span></span>`,
    d:{type:"fusedPair", a:"Q", b:"U"}};
}
function fusedEROffer(){''')
# a triple fusion upgrade never stands alone on the shelf: swap it for a plain fusion
rep('''  const shelfOut=offers.slice(0,N).map(o=>({...o,sold:false}));''',
'''  const shelfOut=offers.slice(0,N).map(o=>({...o,sold:false}));
  { const ti=shelfOut.findIndex(o=>o.d&&o.d.type==="trioUpgrade");   // v0.51i
    if(ti>=0 && !shelfOut.some(o=>o.d&&o.d.type==="fuse")) shelfOut[ti]={...fusionOffer(),sold:false}; }''')

open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s), "pred anaSet uses:", n)
