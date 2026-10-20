#!/usr/bin/env python3
"""0.51r -> 0.51s:
(1) Space Bar leaves the Scholar's starting deck and becomes an expensive legendary
    shop card open to every desk. It carries 3 charges like Lucky 7: each word set with
    it spends one, and at 0 it is gone for good. Only offered while you don't hold one.
(2) In a Space Bar play the second word's letters score at 50%. The length bonus still
    counts both words.
(3) The word bank prefers two rows of larger tiles over one row of small ones: one row
    is kept only while its tiles stay within 90% of the full size.
Live only: the pinned daily predictor is untouched.
usage: patch_051s.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51r"', 'gameVersion:"0.51s"')
m = re.findall(r'const VERSION *= *"0\.51r"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51r","0.51s"))

# ---------- (1) Scholar no longer starts with it ----------
rep('''  blurb:"Reads everything, wastes nothing. A deep hand, a few borrowed word parts, and a Space Bar that joins two words into one.",
  boon:"10-tile hand. Words of 5 or more letters earn a steeper length bonus. Starts with RE-, -ER, -ED and -ING tiles and a Space Bar.",''',
'''  blurb:"Reads everything, wastes nothing. A deep hand and a few borrowed word parts.",
  boon:"10-tile hand. Words of 5 or more letters earn a steeper length bonus. Starts with RE-, -ER, -ED and -ING tiles.",''')
rep('''longBoost:0.4, shortFlat:5, affixes:["re","er","ed","ing"], spaceBar:true''',
    '''longBoost:0.4, shortFlat:5, affixes:["re","er","ed","ing"]   // v0.51s: the Space Bar moved to the shop''')

# charges on the card
rep('''function makeSpaceCard(){ return {id:++cardSeq, kind:"space", letter:null, base:0, upLevel:0, mult:1}; }''',
    '''function makeSpaceCard(){ return {id:++cardSeq, kind:"space", letter:null, base:0, upLevel:0, mult:1, charges:3}; }   // v0.51s: 3 charges''')
rep('''const s=document.createElement("span"); s.className="glyph-sub"; s.textContent="SPACE"; t.appendChild(s);''',
    '''const s=document.createElement("span"); s.className="glyph-sub"; s.textContent="SPACE · "+(typeof c.charges==="number"?c.charges:3)+"/3"; t.appendChild(s);''', 2)

# shop offer, legendary, priced above the other legendaries
rep('''function lucky7Offer(){''',
'''/* v0.51s: Space Bar, now a legendary shop card for every desk. */
function spaceBarOffer(){
  return {kind:"Card",rarity:"legendary",name:"Space Bar",
    desc:"Play it between two words to set both as one: the length bonus counts every letter, and the second word's letters score half. 3 uses across the run.",
    price:px(20),
    art:`<span class="mini-tile" style="background:linear-gradient(180deg,#F3EEF9,#E2D9F2);border-color:#B9A9DB">␣</span>`,
    d:{type:"spaceBar"}};
}
function lucky7Offer(){''')
rep('''    {make:()=>lucky7Offer(),       weight:0.15},   // v492c legendary; v492d rarer with the rest of the tier
  ];''',
'''    {make:()=>lucky7Offer(),       weight:0.15},   // v492c legendary; v492d rarer with the rest of the tier
    ...(G.deck.some(c=>c.kind==="space") ? [] : [{make:()=>spaceBarOffer(), weight:0.15}]),   // v0.51s: one at a time
  ];''')
rep('''    case "lucky7":       G.deck.push(makeLucky7Card()); break;''',
    '''    case "lucky7":       G.deck.push(makeLucky7Card()); break;
    case "spaceBar":     G.deck.push(makeSpaceCard()); break;   // v0.51s''')
rep('''    if(c.kind==="lucky7"){lucky++;return;}''',
    '''    if(c.kind==="lucky7"){lucky++;return;}
    if(c.kind==="space"){spaces++;return;}   // v0.51s''')
rep('''let pts=0, clones=0, wilds=0, wconst=0, copies=0, fused=0, trios=0, combos=0, lucky=0, dealer=0, trip=0;''',
    '''let pts=0, clones=0, wilds=0, wconst=0, copies=0, fused=0, trios=0, combos=0, lucky=0, dealer=0, trip=0, spaces=0;''')
rep('''  if(lucky)  extras.push(`${lucky} Lucky 7`);''',
    '''  if(lucky)  extras.push(`${lucky} Lucky 7`);
  if(spaces) extras.push(`Space Bar`);''')

# spend a charge on every word it sets
rep('''  if(standingForme()){
    /* The forme stays standing. Tiles are NOT returned to the pile, so the next''',
'''  /* v0.51s: each word set with the Space Bar spends a charge. At 0 it leaves the run. */
  G.canvas.filter(c=>c.kind==="space").forEach(c=>{
    if(typeof c.charges!=="number") c.charges=3;   // a Scholar save from 0.51r migrates here
    c.charges--;
    if(c.charges<=0){
      G.deck=G.deck.filter(x=>x.id!==c.id);
      G.canvas=G.canvas.filter(x=>x.id!==c.id);
      toast("Space Bar spent");
    }
  });
  if(standingForme()){
    /* The forme stays standing. Tiles are NOT returned to the pile, so the next''')

# ---------- (2) second word at 50% ----------
rep('''    if(r.card&&r.card.serif && (i===0||i===res.length-1)) v*=2;      // Serif Stamp: double at either end
    letterVals.push(v);''',
'''    if(r.card&&r.card.serif && (i===0||i===res.length-1)) v*=2;      // Serif Stamp: double at either end
    if(res.spaceAt && res.spaceAt.length && i>=res.spaceAt[0]) v*=0.5;   // v0.51s: the second word scores half
    letterVals.push(v);''')
rep('''tailHit,proofMult};''', '''tailHit,proofMult,spaceHit:!!(res.spaceAt&&res.spaceAt.length)};''')
rep('''  if(sc.ligHit) parts.push(`×1.75 ligature`);''',
    '''  if(sc.spaceHit) parts.push(`second word ×0.5`);   // v0.51s
  if(sc.ligHit) parts.push(`×1.75 ligature`);''')

# ---------- (3) bank: two rows of big tiles beat one row of small ones ----------
rep('''  let fit=null;
  for(let r=1;r<=maxRows && !fit;r++){''',
'''  let fit=null;
  /* v0.51s: in "big" mode the bank takes whichever row count gives the larger tiles,
     so a full hand goes to two rows instead of shrinking. A second row has to buy at least 10% more tile size. */
  if(o.preferBig){
    let best=null;
    for(let r=1;r<=maxRows;r++){ const f=packWidth(units, avail, r, o); if(f && (!best || f.w>=best.w*1.1)) best=f; }   // a second row has to buy at least 10% more size
    fit=best;
  }
  for(let r=1;r<=maxRows && !fit;r++){''')
rep('''function fitHand(){ fitUnits($("hand"), G.hand, "hand", 2, Object.assign({},HAND_FIT,{max:Math.min(HAND_FIT.max, _fitCap.hand)})); }''',
    '''let _bankBig=false;   // v0.51s: chosen once per round by fitScreen
function fitHand(){ fitUnits($("hand"), G.hand, "hand", 2, Object.assign({},HAND_FIT,{max:Math.min(HAND_FIT.max, _fitCap.hand), preferBig:_bankBig})); }''')
# fitScreen: on a fresh round, run the fit both ways and keep whichever ends with bigger bank tiles
rep('''  if(fresh){ _fitKey=key; _fitLevel=0; $("app").style.removeProperty("--hand-h"); }   // each round starts from the largest size
  applyFitLevel(_fitLevel); fitHand(); fitCanvas();
  if(fresh) reserveHandRows(false);
  while(playOverflow()>0 && _fitLevel<FIT_LEVELS.length-1){ _fitLevel++; applyFitLevel(_fitLevel); fitHand(); fitCanvas(); reserveHandRows(false); }''',
'''  if(fresh){ _fitKey=key; _fitLevel=0; $("app").style.removeProperty("--hand-h"); }   // each round starts from the largest size
  /* v0.51s: try the round both ways (bank on the old one-row rule, and bank taking two
     rows whenever that means bigger tiles). Keep two rows only if its tiles end up
     at least 10% larger, so a hand that lands on the same size never squeezes the header. */
  const settle=()=>{ applyFitLevel(_fitLevel); fitHand(); fitCanvas();
    if(fresh) reserveHandRows(false);
    while(playOverflow()>0 && _fitLevel<FIT_LEVELS.length-1){ _fitLevel++; applyFitLevel(_fitLevel); fitHand(); fitCanvas(); reserveHandRows(false); } };
  const bankW=()=>parseFloat(getComputedStyle($("hand")).getPropertyValue("--tw"))||0;
  if(fresh){
    _bankBig=false; _fitLevel=0; $("app").style.removeProperty("--hand-h"); settle();
    const w1=bankW(), l1=_fitLevel;
    _bankBig=true; _fitLevel=0; $("app").style.removeProperty("--hand-h"); settle();
    const w2=bankW();
    if(!(w2>=w1*1.1)){ _bankBig=false; _fitLevel=l1; $("app").style.removeProperty("--hand-h"); settle(); }
  } else settle();''')

open(OUT, "w", encoding="utf-8").write(s)
print("wrote", OUT)
