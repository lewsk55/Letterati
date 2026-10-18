#!/usr/bin/env python3
"""PROTOTYPE: the Short King character on top of letterati_v0.51a.html, with the
balance knobs passed in, so the simulator can sweep them. Not a release build.
usage: patch_sk.py in.html out.html '{"hands":1,"discards":0,"hand":0,"target":1.0,"t2":4,"t3":3.5,"t4":2.5}'"""
import sys, json
SRC, OUT, P = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:120]))
    s = s.replace(a, b)

# character definition
rep('''const CHAR_ORDER = ["writer","detective","editor"];''',
'''CHARACTERS.shortking = {
  id:"shortking", name:"Short King", art:"\\uD83D\\uDC51", tag:"Short words",
  blurb:"Small words, big numbers. Two to four letters hit hard, and he works fast.",
  boon:"2, 3 and 4 letter words score x%(t2)s, x%(t3)s and x%(t4)s. %(boonx)s",
  bane:"No word longer than 5 letters.",
  targetMult:%(target)s, hearts:3, maxWordLen:5, handsDelta:%(hands)s, discardsDelta:%(discards)s, handSizeDelta:%(hand)s,
  shortTiers:{2:%(t2)s,3:%(t3)s,4:%(t4)s}
};
const CHAR_ORDER = ["writer","detective","editor","shortking"];''' % dict(P, boonx=P.get("boonx","")))
# helper: the live word cap
rep('function charHas(k){ return !!charDef()[k]; }',
    'function charHas(k){ return !!charDef()[k]; }\nfunction wordCap(){ return charDef().maxWordLen || 99; }')
# hand size
rep('G.level=1; G.hearts=startHearts(); G.coins=0; G.handSize=START_HAND;',
    'G.level=1; G.hearts=startHearts(); G.coins=0; G.handSize=START_HAND+(charDef().handSizeDelta||0);')
# hard block on the press
rep('''  const minL=challengeMinLen();
  if(minL && res.length<minL) return false;''',
'''  const minL=challengeMinLen();
  if(minL && res.length<minL) return false;
  if(res.length>wordCap()) return false;''')
# dead-hand checks respect the cap
rep('''function multisetIsLegal(sortedLetters, commonOnly){
  const n=sortedLetters.length; if(n<2) return false;''',
'''function multisetIsLegal(sortedLetters, commonOnly){
  const n=sortedLetters.length; if(n<2) return false;
  if(n>wordCap()) return false;''')
rep('''  const ana=anaSet(), cap=Math.min(n,12);''', '''  const ana=anaSet(), cap=Math.min(n,12,wordCap());''')
# signature scoring, before Shorty (the old perk)
rep('''  // Short King: tiered boost for short words (see SHORT_KING_MULT)
  let shortHit=false, shortMult=1;''',
'''  // Short King (character): built-in tiers for 2 to 4 letters
  { const T=charDef().shortTiers; if(T && T[effLen]) total*=T[effLen]; }
  // Short King: tiered boost for short words (see SHORT_KING_MULT)
  let shortHit=false, shortMult=1;''')
# Longform never offered to him (live path only; predictor untouched)
rep('''function challengeTypeFor(level){
  const rng=makeRng("challenge:"+level);
  const pool=CHALLENGE_ORDER.filter(t=>!(CHALLENGE_EARLY_ONLY.has(t) && level>4));   // v0.5a: rounds 2 and 4 are the early pair
  return pool[Math.floor(rng()*pool.length)];
}''',
'''function challengeTypeFor(level){
  const rng=makeRng("challenge:"+level);
  const pool=CHALLENGE_ORDER.filter(t=>!(CHALLENGE_EARLY_ONLY.has(t) && level>4));   // v0.5a: rounds 2 and 4 are the early pair
  return pool[Math.floor(rng()*pool.length)];
}
function liveChallengeTypeFor(level){
  const t=challengeTypeFor(level);
  if(t!=="longform" || !wordCap() || wordCap()>=99) return t;
  const rng=makeRng("challenge-sk:"+level);
  const pool=CHALLENGE_ORDER.filter(x=>x!=="longform" && !(CHALLENGE_EARLY_ONLY.has(x) && level>4));
  return pool[Math.floor(rng()*pool.length)];
}''')
rep('  const type=challengeTypeFor(lvl);', '  const type=liveChallengeTypeFor(lvl);')
# bosses: no Ghost for him; Perfect Type asks 3+ instead of 5+
rep('''function bossActive(){''',
'''function liveBossTypeFor(seed, stage){
  const t=bossTypeFor(seed, stage);
  if(t!=="ghost" || wordCap()>=99) return t;
  const pool=BOSS_ORDER.filter(x=>x!=="ghost" && x!==(stage?bossTypeFor(seed,0):null));
  const rng=makeRng("boss-sk:"+seed+":"+(stage||0));
  return pool[Math.floor(rng()*pool.length)];
}
function bossActive(){''')
rep('    G.boss.type=bossTypeFor(G.seed); G.boss.introSeen=false;', '    G.boss.type=liveBossTypeFor(G.seed); G.boss.introSeen=false;')
rep('  const def=BOSS_TYPES[bossTypeFor(G.seed, G.proofStage||0)];', '  const def=BOSS_TYPES[liveBossTypeFor(G.seed, G.proofStage||0)];')
rep('      const bt=bossTypeFor(G.seed, stage);', '      const bt=liveBossTypeFor(G.seed, stage);')
rep('''    if(G.boss.type==="perfect") m=Math.max(m,5);''', '''    if(G.boss.type==="perfect") m=Math.max(m, wordCap()<99 ? 3 : 5);''')
# side job that needs 7+ letters
rep('''    if(k===G.lastSideJobKey) return false;''', '''    if(k===G.lastSideJobKey) return false;
    if(k==="longHaul" && wordCap()<7) return false;''')
# dead offers out of his shop
rep('''    {make:()=>pressMultOffer(rng), weight:1.3},''', '''    ...(wordCap()<6 ? [] : [{make:()=>pressMultOffer(rng), weight:1.3}]),''')
rep('''  if(!G.perks.bigWords)          e.push''', '''  if(!G.perks.bigWords && wordCap()>=6)          e.push''')
rep('''  if(!G.perks.shortKing)         e.push''', '''  if(!G.perks.shortKing && wordCap()>=99)         e.push''')
rep('function forChar(list){ return list.filter(x=>!x.char || x.char===G.character); }',
    'const SK_DEAD=new Set(["bigWords","pressMult","shortKing"]);\nfunction forChar(list){ return list.filter(x=>(!x.char || x.char===G.character) && !(wordCap()<6 && x.d && SK_DEAD.has(x.d.type))); }')
# No Reprints: lengths past the cap are not reachable, so the reset must know the cap
rep('  for(let L=minL; L<=Math.min(12,maxLen); L++) if(!used.includes(L)) out.push(L);',
    '  for(let L=minL; L<=Math.min(12,maxLen,wordCap()); L++) if(!used.includes(L)) out.push(L);')
# optional per-round target curve for the character (multiplies the flat targetMult)
if P.get("curve"):
    rep('function runTargetMult(){ return (charDef().targetMult||1) * ascTargetMult(); }',
        'function runTargetMult(){ const c=charDef().targetCurve; const k=c ? (c[Math.min(G.level||1, c.length)-1]||1) : 1; return (charDef().targetMult||1) * k * ascTargetMult(); }')
    rep('  shortTiers:{2:', '  targetCurve:%s,\n  shortTiers:{2:' % json.dumps(P["curve"]))
open(OUT, "w", encoding="utf-8").write(s)
print("ok")
