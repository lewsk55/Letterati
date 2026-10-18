#!/usr/bin/env python3
"""0.51q -> 0.51r:
(1) A solved mystery word is retired for the rest of the run, by word and by definition
    text, so the same clue cannot come back (the Detective gets a fresh clue every hand,
    which made repeats likely).
(2) Challenge upgrade rewards say what the upgrade does: gild doubles points, and each
    stamp carries its own effect text.
(3) Dealer's Choice shows the draw pile and the discard as two labeled groups (it could
    always pull from both, but the screen mixed them and said "draw pile"), and it still
    opens when the draw pile is empty but the discard is not.
(4) Short King never meets Perfect Type in the final proof, joining The Ghost Writer in
    the swap list. Live only: the pinned daily predictor (bossTypeFor) is untouched.
usage: patch_051r.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51q"', 'gameVersion:"0.51r"')
m = re.findall(r'const VERSION *= *"0\.51q"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51q","0.51r"))

# ---------- (1) retire solved mystery words for the run ----------
rep('''/* Commit a clue and tag its rarity. */
function setMystery(w, d){''',
'''/* v0.51r: once a mystery word is solved it is out of circulation for the run. Both the
   word and its definition text are retired, so a different word that happens to share
   the same definition cannot bring the clue back either. */
function mysteryDefKey(def){ return String(def||"").toLowerCase().replace(/\\s+/g," ").trim(); }
function mysteryDefRetired(def){ const k=mysteryDefKey(def); return !!k && (G.mysteryDoneDefs||[]).includes(k); }
function retireMystery(m){
  if(!m || !m.word) return;
  if(!G.mysteryDone) G.mysteryDone=[];
  if(!G.mysteryDoneDefs) G.mysteryDoneDefs=[];
  if(!G.mysteryDone.includes(m.word)) G.mysteryDone.push(m.word);
  const k=mysteryDefKey(m.def); if(k && !G.mysteryDoneDefs.includes(k)) G.mysteryDoneDefs.push(k);
}
/* Commit a clue and tag its rarity. */
function setMystery(w, d){''')

rep('''const cands=mysteryCandidates(8).filter(w=>!(G.mysterySkip||[]).includes(w));''',
'''const cands=mysteryCandidates(8).filter(w=>!(G.mysterySkip||[]).includes(w) && !(G.mysteryDone||[]).includes(w));   // v0.51r: solved words stay retired''')

rep('''d && d.def && !defRevealsWord(d.def,w)''',
    '''d && d.def && !defRevealsWord(d.def,w) && !mysteryDefRetired(d.def)''', 2)

rep('''  if(sc.mysteryHit){
    if(!charHas("unlimitedMystery")) G.mysterySolvedLevel=G.level;''',
'''  if(sc.mysteryHit){
    retireMystery(G.mystery);   // v0.51r: never offered again this run
    if(!charHas("unlimitedMystery")) G.mysterySolvedLevel=G.level;''')

# save, load, new run
rep('''mysterySkip:(G.mysterySkip||[]),''',
    '''mysterySkip:(G.mysterySkip||[]), mysteryDone:(G.mysteryDone||[]), mysteryDoneDefs:(G.mysteryDoneDefs||[]),''')
rep('''G.mysterySkip=d.mysterySkip||[];''',
    '''G.mysterySkip=d.mysterySkip||[]; G.mysteryDone=d.mysteryDone||[]; G.mysteryDoneDefs=d.mysteryDoneDefs||[];''')
rep('''G.mysteryLevel=null; G.mysterySkip=[];''',
    '''G.mysteryLevel=null; G.mysterySkip=[]; G.mysteryDone=[]; G.mysteryDoneDefs=[];''')

# ---------- (2) upgrade rewards explain themselves ----------
rep('''function upgradeRewardText(u){
  if(!u || u.kind==="gild") return {badge:"FREE GILD", name:"Your pick of gild", desc:"Gild any tile you own, free, at the next shop."};''',
'''/* v0.51r: what each stamp does, matching its shop card, so a challenge reward never
   names a stamp without explaining it. */
const STAMP_EFFECTS={
  foil:"Its value doubles the first time you play it each round.",
  boldface:"It counts as two letters toward word length.",
  dropcap:"It scores triple as the first letter of a word.",
  serif:"Its value doubles as the first or last letter of a word.",
  ditto:"It copies the highest value of the other tiles in the word.",
  inkwell:"You earn $1 every time you play it.",
  encore:"After you play it, it returns to the top of your pile.",
  watermark:"It is always in your opening hand each round."
};
function upgradeRewardText(u){
  if(!u || u.kind==="gild") return {badge:"FREE GILD", name:"Your pick of gild", desc:"Gild any tile you own, free, at the next shop. Gilding doubles that tile's points."};''')
rep('''desc:"Place a "+STAMP_NAMES[u.stamp]+" on any tile you own, free, at the next shop."};''',
    '''desc:"Place "+(/^[AEIOU]/.test(STAMP_NAMES[u.stamp])?"an ":"a ")+STAMP_NAMES[u.stamp]+" on any tile you own, free, at the next shop. "+(STAMP_EFFECTS[u.stamp]||"")};''')
rep('''return {badge:"FREE FUSION", name:"Free letter fusion", desc:"Fuse any two letters you own into one tile, free, at the next shop."};''',
    '''return {badge:"FREE FUSION", name:"Free letter fusion", desc:"Fuse any two letters you own into one tile, free, at the next shop. The tile plays both letters at once."};''')
rep('''desc:"Challenge reward. Tap any tile to gild it, free."''',
    '''desc:"Challenge reward. Tap any tile to gild it, free. Its points double."''')

# ---------- (3) Dealer's Choice: draw pile and discard, labeled ----------
rep('''function useDealersChoice(card){
  if(!G.drawPile || G.drawPile.length===0){ toast("Your draw pile is empty"); haptic(8); return; }''',
'''function useDealersChoice(card){
  // v0.51r: the discard counts too, so only refuse when both piles are empty
  if(!(G.drawPile||[]).length && !(G.played||[]).length){ toast("Your draw and discard piles are empty"); haptic(8); return; }''')
rep('''hint.textContent="Tap a tile in your draw pile to pull it into your hand.";''',
    '''hint.textContent="Tap a tile in your draw or discard pile to pull it into your hand.";''')
rep('''  if(G.selectMode==="dealer"){
    list.className="deck-list";
    [...G.drawPile, ...(G.played||[])].sort(sortFn).forEach(c=>list.appendChild(deckTileEl(c)));   // v495a: draw pile AND discard
  }''',
'''  if(G.selectMode==="dealer"){
    // v0.51r: the two piles were mixed into one sorted grid, so discards read as draw
    // pile tiles. They now sit in their own labeled groups.
    list.classList.remove("deck-list");
    [{label:"Draw pile", cards:G.drawPile.slice(), empty:"Empty."},
     {label:"Discard", cards:(G.played||[]).slice(), empty:"Nothing in your discard yet this round."}].forEach(g=>{
      const sec=document.createElement("div"); sec.className="deck-group";
      const head=document.createElement("div"); head.className="dg-head";
      head.innerHTML=`<span>${g.label}</span><span class="dg-count">${g.cards.length}</span>`;
      sec.appendChild(head);
      const row=document.createElement("div"); row.className="dg-row";
      if(g.cards.length){ g.cards.sort(sortFn).forEach(c=>row.appendChild(deckTileEl(c))); }
      else { const e=document.createElement("div"); e.className="dg-empty"; e.textContent=g.empty; row.appendChild(e); }
      sec.appendChild(row);
      list.appendChild(sec);
    });
  }''')
rep('''desc:"Tap it in your hand to pull any tile from your draw pile or discard. This card takes its place.",''',
    '''desc:"Tap it in your hand to pull any tile from your draw pile or your discard pile. This card takes its place.",''')

# ---------- (4) no Perfect Type for Short King ----------
rep('''function liveBossTypeFor(seed, stage){
  const t=bossTypeFor(seed, stage);
  if(t!=="ghost" || wordCap()>=99) return t;
  const pool=BOSS_ORDER.filter(x=>x!=="ghost" && x!==(stage?bossTypeFor(seed,0):null));
  const rng=makeRng("boss-sk:"+seed+":"+(stage||0));
  return pool[Math.floor(rng()*pool.length)];
}''',
'''/* v0.51r: a capped-length desk (Short King) also skips Perfect Type, whose five letter
   floor is out of reach with a five letter cap. The A5 second proof avoids whatever the
   first proof became after the swap, not just its pre-swap roll. */
const CAPPED_SKIP_BOSSES=new Set(["ghost","perfect"]);
function liveBossTypeFor(seed, stage){
  const t=bossTypeFor(seed, stage);
  if(wordCap()>=99) return t;
  const first=stage ? liveBossTypeFor(seed,0) : null;
  if(!CAPPED_SKIP_BOSSES.has(t) && t!==first) return t;
  const pool=BOSS_ORDER.filter(x=>!CAPPED_SKIP_BOSSES.has(x) && x!==first);
  const rng=makeRng("boss-sk:"+seed+":"+(stage||0));
  return pool[Math.floor(rng()*pool.length)];
}''')
rep('''  if(G.boss && G.boss.type && !BOSS_TYPES[G.boss.type]){
    G.boss.type=liveBossTypeFor(G.seed); G.boss.introSeen=false;
  }''',
'''  if(G.boss && G.boss.type && !BOSS_TYPES[G.boss.type]){
    G.boss.type=liveBossTypeFor(G.seed); G.boss.introSeen=false;
  }
  // v0.51r: a Short King run saved before this build may have Perfect Type waiting.
  // Swap it while the proof is still ahead; a proof already under way plays out.
  if(G.boss && G.boss.type && wordCap()<99 && CAPPED_SKIP_BOSSES.has(G.boss.type) && !(G.boss.active && G.level===WIN_LEVEL)){
    G.boss.type=liveBossTypeFor(G.seed, G.proofStage||0); G.boss.introSeen=false;
  }''')

open(OUT, "w", encoding="utf-8").write(s)
print("wrote", OUT)
