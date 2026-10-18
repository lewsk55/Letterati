#!/usr/bin/env python3
"""0.51c: the Scholar (long words), Space Bar tile, affix tiles, 8 Scholar perks.
Applied on top of letterati_v0.51b.html.
usage: patch_051c.py in.html out.html '{"target":1.15,"boost":0.5,"hands":-1,"hand":3}'"""
import sys, json
SRC, OUT = sys.argv[1], sys.argv[2]
P = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
P = dict({"target": 1.15, "boost": 0.5, "hands": -1, "hand": 3}, **P)
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)

rep('const VERSION = "0.51b";', 'const VERSION = "0.51c";')
rep('gameVersion:"0.51b"', 'gameVersion:"0.51c"')

# ---------------------------------------------------------------- character
rep('const CHAR_ORDER = ["writer","detective","editor","shortking"];',
'''CHARACTERS.scholar = {
  id:"scholar", name:"The Scholar", art:"\\uD83D\\uDCDC", tag:"Long words",
  blurb:"Reads everything, wastes nothing. A deep hand, a few borrowed word parts, and a Space Bar that joins two words into one.",
  boon:"10-tile hand. Words of 5 or more letters earn a steeper length bonus. Starts with RE-, -ER, -ED and -ING tiles and a Space Bar.",
  bane:"Three words a round and higher targets. Words under 5 letters score face value, with no multipliers.",
  targetMult:%(target)s, hearts:3, handsDelta:%(hands)s, handSizeDelta:%(hand)s,
  longBoost:%(boost)s, shortFlat:5, affixes:["re","er","ed","ing"], spaceBar:true
};
const CHAR_ORDER = ["writer","detective","editor","shortking","scholar"];''' % P)

# ---------------------------------------------------------------- affix tiles and the Space Bar
rep('''  er:  { seq:["E","R"],     label:"-ER",  rarity:"rare", price:7  }   // retired from the shop (now sold as a fused E+R); kept so any old -ER tiles still render
};''', '''  er:  { seq:["E","R"],     label:"-ER",  rarity:"rare", price:7  },  // retired from the shop (now sold as a fused E+R); kept so any old -ER tiles still render
  re:  { seq:["R","E"],     label:"RE-",  rarity:"rare", price:7  },  // v0.51c: Scholar starting affix (not sold)
  ed:  { seq:["E","D"],     label:"-ED",  rarity:"rare", price:7  }   // v0.51c: Scholar starting affix (not sold)
};
function makeSpaceCard(){ return {id:++cardSeq, kind:"space", letter:null, base:0, upLevel:0, mult:1}; }   // v0.51c Space Bar''')
rep('''  G.deck=rollStartingDeck();
  statInit(G.seed);''', '''  G.deck=rollStartingDeck();
  scholarDeck();   // v0.51c: after the seeded roll, so the deck the predictor sees is untouched
  statInit(G.seed);''')
rep('function charHas(k){ return !!charDef()[k]; }', '''function charHas(k){ return !!charDef()[k]; }
/* v0.51c: the Scholar swaps one plain letter per affix tile (the most common letter
   in the deck each time, ties broken alphabetically, so it is the same for every
   player on a seed), then adds the Space Bar. Nothing here draws from the seed. */
function scholarDeck(){
  const d=charDef();
  (d.affixes||[]).forEach(key=>{
    const cnt={}; G.deck.forEach(c=>{ if(c.kind==="letter" && !(c.upLevel>0)) cnt[c.letter]=(cnt[c.letter]||0)+1; });
    const L=Object.keys(cnt).sort((a,b)=>cnt[b]-cnt[a] || (a<b?-1:1))[0];
    if(L){ const i=G.deck.findIndex(c=>c.kind==="letter" && c.letter===L && !(c.upLevel>0)); if(i>=0) G.deck.splice(i,1); }
    G.deck.push(makeComboCard(key));
  });
  if(d.spaceBar) G.deck.push(makeSpaceCard());
}''')
# the Space Bar on the canvas: contributes no letter, records where the split is
rep('''    } else if(c.kind==="combo"){
      const g=(typeof c.growth==="number")?c.growth:0;
      comboEntries(c).forEach''', '''    } else if(c.kind==="space"){
      (out.spaceAt=out.spaceAt||[]).push(out.length);   // v0.51c Space Bar: a split point, no letter
    } else if(c.kind==="combo"){
      const g=(typeof c.growth==="number")?c.growth:0;
      comboEntries(c).forEach''')
# dictionary check: one word, or two words joined by a single Space Bar
rep('''function isRealWord(){
  const res=resolvedCanvas();
  if(res.length<2 || res.some(r=>!r.letter)) return false;
  const w=res.map(r=>r.letter.toLowerCase()).join("");
  if(WORDS.has(w)) return true;
  return verbizedStem(w)!==null;   // Verbizer: word+ER / word+ING / word+ED counts
}''', '''function isRealWord(){
  const res=resolvedCanvas();
  if(res.length<2 || res.some(r=>!r.letter)) return false;
  return canvasWordOK(res);
}
function wordStrOK(w){ return WORDS.has(w) || verbizedStem(w)!==null; }   // Verbizer: word+ER / word+ING / word+ED counts
/* v0.51c Space Bar: two valid words, each checked on its own, played as one. */
function spaceHalves(res){
  const sp=res.spaceAt; if(!sp) return null;
  if(sp.length!==1) return false;
  const k=sp[0]; if(k<2 || res.length-k<2) return false;
  const s=res.map(r=>(r.letter||"").toLowerCase()).join("");
  return [s.slice(0,k), s.slice(k)];
}
function canvasWordOK(res){
  const h=spaceHalves(res);
  if(h===false) return false;
  if(h) return wordStrOK(h[0]) && wordStrOK(h[1]);
  return wordStrOK(res.map(r=>r.letter.toLowerCase()).join(""));
}''')
rep('''  const w=res.map(r=>r.letter.toLowerCase()).join("");
  if(WORDS.has(w)) return true;
  if(verbizedStem(w)!==null) return true;   // Verbizer: word+ER / word+ING / word+ED counts here too
  return false;
}''', '''  return canvasWordOK(res);   // v0.51c: handles the Space Bar too
}''')
# tile faces
rep('''  if(c.kind==="lucky7"){
    t.classList.add("lucky7");
    const g=document.createElement("span"); g.className="glyph"; g.textContent="🍀"; t.appendChild(g);
    const s=document.createElement("span"); s.className="glyph-sub"; s.textContent="LUCKY 7 · "+(typeof c.charges==="number"?c.charges:3)+"/3"; t.appendChild(s);
    t.addEventListener("click"''', '''  if(c.kind==="space"){   // v0.51c Space Bar: plays like a tile, joins two words
    t.classList.add("spacebar");
    const g=document.createElement("span"); g.className="glyph"; g.textContent="␣"; t.appendChild(g);
    const s=document.createElement("span"); s.className="glyph-sub"; s.textContent="SPACE"; t.appendChild(s);
    attachTileHandlers(t,c,where); return t;
  }
  if(c.kind==="lucky7"){
    t.classList.add("lucky7");
    const g=document.createElement("span"); g.className="glyph"; g.textContent="🍀"; t.appendChild(g);
    const s=document.createElement("span"); s.className="glyph-sub"; s.textContent="LUCKY 7 · "+(typeof c.charges==="number"?c.charges:3)+"/3"; t.appendChild(s);
    t.addEventListener("click"''')
rep('''  if(c.kind==="dealer"){
    t.classList.add("dealer");
    const g=document.createElement("span"); g.className="glyph"; g.textContent="🎴"; t.appendChild(g);
    const s=document.createElement("span"); s.className="glyph-sub"; s.textContent="DEALER"; t.appendChild(s);
    return t;
  }''', '''  if(c.kind==="dealer"){
    t.classList.add("dealer");
    const g=document.createElement("span"); g.className="glyph"; g.textContent="🎴"; t.appendChild(g);
    const s=document.createElement("span"); s.className="glyph-sub"; s.textContent="DEALER"; t.appendChild(s);
    return t;
  }
  if(c.kind==="space"){
    t.classList.add("spacebar");
    const g=document.createElement("span"); g.className="glyph"; g.textContent="␣"; t.appendChild(g);
    const s=document.createElement("span"); s.className="glyph-sub"; s.textContent="SPACE"; t.appendChild(s);
    return t;
  }''')
rep('''  if(c.kind==="lucky7") return "Lucky 7";
  return "the tile";''', '''  if(c.kind==="lucky7") return "Lucky 7";
  if(c.kind==="space") return "the Space Bar";
  return "the tile";''')
# no upgrades on the Space Bar; Root Word lets affix tiles carry a fourth
rep('function hasUpgradeRoom(c){ return upgradeCount(c) < MAX_TILE_UPGRADES; }',
    '''function tileUpgradeCap(c){ return (c && c.kind==="combo" && G.perks && G.perks.rootWord) ? MAX_TILE_UPGRADES+1 : MAX_TILE_UPGRADES; }
function hasUpgradeRoom(c){ return !!c && c.kind!=="space" && upgradeCount(c) < tileUpgradeCap(c); }''')
rep('''function gildCapFor(c){
  if(!c) return GILD_CAP;''', '''function gildCapFor(c){
  if(!c) return GILD_CAP;
  if(c.kind==="space") return 0;''')
rep('''  if(kind==="encore"){ if(c.kind==="lucky7"||c.kind==="dealer") return; }''',
    '''  if(kind==="encore"){ if(c.kind==="lucky7"||c.kind==="dealer"||c.kind==="space") return; }''')

# ---------------------------------------------------------------- scoring
rep('''  let m=lenMult(effLen);
  m=Math.round(m*100)/100;''', '''  let m=lenMult(effLen);
  if(charDef().longBoost && effLen>=5) m+=charDef().longBoost*(effLen-4);   // v0.51c Scholar: steeper length bonus
  if(G.perks.sesquipedalian && effLen>6) m+=effLen-6;                        // v0.51c Sesquipedalian
  m=Math.round(m*100)/100;''')
rep('''  if(G.perks.rapidFire && effLen<=4 && (G._rfStreak||0)>0) total*=1+0.15*G._rfStreak;            // v0.51b Rapid Fire''',
    '''  if(G.perks.rapidFire && effLen<=4 && (G._rfStreak||0)>0) total*=1+0.15*G._rfStreak;            // v0.51b Rapid Fire
  if(G.perks.runOn && effLen>=6 && (G._roStreak||0)>0) total*=1+0.25*G._roStreak;               // v0.51c Run-On Sentence
  if(G.perks.epigraph && effLen>=6 && G.levelStats && (G.levelStats.words||0)===0) total*=2;    // v0.51c Epigraph''')
rep('''  let inkPts=0;
  if(G.perks.indiaInk && (G.inkPtsPending||0)>0){ inkPts=G.inkPtsPending; total+=inkPts; }''',
    '''  let inkPts=0;
  if(G.perks.indiaInk && (G.inkPtsPending||0)>0){ inkPts=G.inkPtsPending; total+=inkPts; }
  if(G.perks.appendix && effLen>=6) total+=3*((G.hand||[]).length);   // v0.51c Appendix
  if(charDef().shortFlat && effLen<charDef().shortFlat) total=sum;      // v0.51c Scholar: short words score face value''')

# ---------------------------------------------------------------- after a word is set
rep('''    if(G.perks.smallPress && L===2){ G.scoreMult=Math.round(((G.scoreMult||1)+0.01)*1000)/1000; }
  }''', '''    if(G.perks.smallPress && L===2){ G.scoreMult=Math.round(((G.scoreMult||1)+0.01)*1000)/1000; }
    G._roStreak = L>=6 ? (G._roStreak||0)+1 : 0;                                   // v0.51c Run-On Sentence
    if(G.perks.unabridged && L>=8){ G.discardsLeft++; toast("Unabridged: a discard back"); }   // v0.51c
    if(!G._longest || L>G._longest.len || (L===G._longest.len && sc.total>G._longest.score)) G._longest={len:L, score:sc.total, word:w.toUpperCase()};   // v0.51c Magnum Opus
  }''')
# Magnum Opus: out of words short of the target, the longest word scores again (once per round)
rep('''    if(G.score>=G.target){ levelCleared(); return; }
    if(G.handsLeft<=0){ levelFailed(); return; }''', '''    if(G.score>=G.target){ levelCleared(); return; }
    if(G.handsLeft<=0 && G.perks.magnumOpus && !G._moUsed && G._longest && !G.overtime){
      G._moUsed=true; G.score+=G._longest.score; animateScore(G.score-G._longest.score, G.score);
      toast("Magnum Opus: "+G._longest.word+" scores again, +"+G._longest.score);
      TL.g("magnum_opus",{ round:G.level, word:G._longest.word, score:G._longest.score });
      if(G.score>=G.target){ levelCleared(); return; }
    }
    if(G.handsLeft<=0){ levelFailed(); return; }''')
rep('''  G._rfStreak=0; G._tgN=0;          // v0.51b Rapid Fire streak and Telegram count, per round''',
    '''  G._rfStreak=0; G._tgN=0;          // v0.51b Rapid Fire streak and Telegram count, per round
  G._roStreak=0; G._longest=null; G._moUsed=false;   // v0.51c Run-On Sentence, Magnum Opus''')
rep('''      rfStreak:G._rfStreak||0, tgN:G._tgN||0, qsRound:(G._qsRound==null?null:G._qsRound),''',
    '''      rfStreak:G._rfStreak||0, tgN:G._tgN||0, qsRound:(G._qsRound==null?null:G._qsRound),
      roStreak:G._roStreak||0, longest:(G._longest||null), moUsed:!!G._moUsed,''')
rep('''  G._rfStreak=+d.rfStreak||0; G._tgN=+d.tgN||0; G._qsRound=(d.qsRound==null?null:d.qsRound);''',
    '''  G._rfStreak=+d.rfStreak||0; G._tgN=+d.tgN||0; G._qsRound=(d.qsRound==null?null:d.qsRound);
  G._roStreak=+d.roStreak||0; G._longest=d.longest||null; G._moUsed=!!d.moUsed;''')
# Bookmark: one tile left on the canvas between words does not count toward the hand
rep('''function heldTileCount(){
  return G.hand.length + (G.canvas||[]).filter(c=>!formeLocked(c)).length;
}''', '''function heldTileCount(){
  const onCanvas=(G.canvas||[]).filter(c=>!formeLocked(c)).length;
  return G.hand.length + Math.max(0, onCanvas - ((G.perks && G.perks.bookmark && onCanvas>0) ? 1 : 0));   // v0.51c Bookmark
}''')
# definitions: both halves, in play order; telemetry carries the halves
rep('''  showDefinition(w);
  if(sc.total>G.levelStats.bestScore)''', '''  { const h=spaceHalves(res);   // v0.51c: a Space Bar play shows each word's definition in turn
    if(h){ showDefinition(h[0]); setTimeout(()=>{ try{ showDefinition(h[1]); }catch(e){} }, 2600); }
    else showDefinition(w); }
  if(sc.total>G.levelStats.bestScore)''')
rep('''      mystery_hit:!!sc.mysteryHit, mystery_mult:(sc.mysteryHit?sc.mysteryMult:null), gilded_tiles:gil, fused_tiles:fus }); }''',
    '''      mystery_hit:!!sc.mysteryHit, mystery_mult:(sc.mysteryHit?sc.mysteryMult:null), gilded_tiles:gil, fused_tiles:fus,
      space:(spaceHalves(res)||null) }); }''')

# ---------------------------------------------------------------- 8 Scholar perks
PERKS = [
  ("bookmark", "Bookmark", "rare", 8, "🔖", "One tile you leave on the canvas between words doesn't count toward your hand."),
  ("runOn", "Run-On Sentence", "rare", 9, "➰", "Each 6+ letter word in a row scores +25% more than the last. A shorter word resets it."),
  ("magnumOpus", "Magnum Opus", "epic", 13, "🏛️", "Run out of words short of the target and your longest word this round scores again. Once per round."),
  ("unabridged", "Unabridged", "common", 6, "📚", "Every word of 8 or more letters gives you a discard back."),
  ("epigraph", "Epigraph", "common", 5, "🪶", "Your first word each round scores double if it has 6 or more letters."),
  ("appendix", "Appendix", "common", 5, "📎", "A word of 6 or more letters gains +3 for every tile left in your hand."),
  ("sesquipedalian", "Sesquipedalian", "epic", 12, "🦉", "+1 to the length multiplier for every letter past 6. The word means given to using long words."),
  ("rootWord", "Root Word", "common", 5, "🌱", "Affix tiles can carry 4 upgrades instead of 3."),
]
WEIGHT = {"common": 1.6, "rare": 1.2, "epic": 0.75}
offer_fns = "\n".join('function sc_%sOffer(){ return {kind:"Perk",rarity:"%s",name:"%s",desc:"%s",price:px(%d),art:"%s",d:{type:"%s"}}; }' % (t, r, n, d, p, a, t) for t, n, r, p, a, d in PERKS)
block = "\n".join('    if(!G.perks.%s) e.push({make:()=>sc_%sOffer(), weight:%s, char:"scholar"});' % (t, t, WEIGHT[r]) for t, n, r, p, a, d in PERKS)
rep('''  if(G.character==="shortking"){''', '''  if(G.character==="scholar"){
%s
  }
  if(G.character==="shortking"){''' % block)
rep('function cutAboveOffer(){', offer_fns + '\nfunction cutAboveOffer(){')
pool = "\n".join('  {name:"%s", art:"%s", char:"scholar", desc:"%s", d:{type:"%s"}},' % (n, a, d, t) for t, n, r, p, a, d in PERKS)
rep('''  {name:"Cut Above",     art:"✂️", char:"editor",''', pool + '''\n  {name:"Cut Above",     art:"✂️", char:"editor",''')
rep('''    case "killFee":      G.perks.killFee=true; break;''',
    '''    case "killFee":      G.perks.killFee=true; break;
''' + "\n".join('    case "%s":' % t for t, *_ in PERKS) + ''' G.perks[d.type]=true; break;   // v0.51c Scholar perks''')
rep('''  const entries=perkPool(rng).filter(e=>!e.char || e.char==="shortking");''',
    '''  const entries=perkPool(rng).filter(e=>!e.char || e.char==="shortking" || e.char==="scholar");''')
rep('''  if(G.perks.killFee)      out.push("Kill Fee · $1 per letter cut");''',
    '''  if(G.perks.killFee)      out.push("Kill Fee · $1 per letter cut");
''' + "\n".join('  if(G.perks.%s) out.push("%s · %s");' % (t, n, d.rstrip(".")) for t, n, r, p, a, d in PERKS))
rep('''  if(P.killFee)    push("💵","Kill Fee","Every letter you cut pays $1.");''',
    '''  if(P.killFee)    push("💵","Kill Fee","Every letter you cut pays $1.");
''' + "\n".join('  if(P.%s) push("%s","%s","%s");' % (t, a, n, d) for t, n, r, p, a, d in PERKS))
# Shorty does nothing for him (short words score face value): keep it out of his shop
rep('''  if(!G.perks.shortKing && wordCap()>=99)         e.push''', '''  if(!G.perks.shortKing && wordCap()>=99 && !charDef().shortFlat)         e.push''')
rep('''function forChar(list){ return list.filter(x=>(!x.char || x.char===G.character) && !(wordCap()<6 && x.d && SK_DEAD.has(x.d.type))); }''',
    '''function forChar(list){ return list.filter(x=>(!x.char || x.char===G.character) && !(wordCap()<6 && x.d && SK_DEAD.has(x.d.type)) && !(charDef().shortFlat && x.d && x.d.type==="shortKing")); }''')

# Space Bar tile look
rep('''.tile.lucky7 .glyph{font-size:1.25em}''', '''.tile.lucky7 .glyph{font-size:1.25em}
.tile.spacebar{background:linear-gradient(180deg,#F3EEF9,#E2D9F2);border-color:#B9A9DB}
.tile.spacebar .glyph{font-size:1.05em;transform:translateY(-3px)}
.tile.spacebar .glyph-sub{position:absolute;left:0;right:0;bottom:3px;text-align:center;font-family:var(--ui);font-size:.36em;font-weight:800;letter-spacing:.06em;color:#6A55A0}
:root[data-theme="dark"] .tile.spacebar{background:linear-gradient(180deg,#3A3350,#2C2640);border-color:#6A5C93}
:root[data-theme="dark"] .tile.spacebar .glyph-sub{color:#C9B8F2}''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
