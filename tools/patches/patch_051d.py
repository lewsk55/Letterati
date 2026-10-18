#!/usr/bin/env python3
"""0.51d on top of 0.51c. See the spec in the thread (items 1-9).
usage: patch_051d.py in.html out.html '{"extra":1.10,"steep":2.0,"ban":4,"margins":2,"minLen":6,"smudge":2}'"""
import sys, json
SRC, OUT = sys.argv[1], sys.argv[2]
P = dict({"extra": 1.10, "steep": 2.0, "ban": 4, "margins": 2, "minLen": 6, "smudge": 2}, **(json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}))
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:160]))
    s = s.replace(a, b)

rep('const VERSION = "0.51c";', 'const VERSION = "0.51d";')
rep('gameVersion:"0.51c"', 'gameVersion:"0.51d"')

# ================================================================ 1. Second Edition retired
rep('''  if(!G.perks.secondEdition)     e.push({make:()=>secondEditionOffer(), weight:0.15});''',
    '''  // v0.51d: Second Edition retired''')
import re
m = re.search(r'\n  \{name:"Second Edition",[^\n]*\n', s)
assert m, "second edition pool entry"
s = s[:m.start()] + "\n" + s[m.end():]
rep('''  if(typeof G.perks.gildedAge!=="number") G.perks.gildedAge=0;''',
    '''  if(typeof G.perks.gildedAge!=="number") G.perks.gildedAge=0;
  G.perks.secondEdition=false;   // v0.51d: retired; a saved run simply loses it''')

# ================================================================ 2. one editor for every multi-letter tile (pairs, trios, combos)
rep('''function comboSeq(c){ return COMBO_DEFS[c.combo].seq; }
function comboLabel(c){ return COMBO_DEFS[c.combo].label; }
function comboEntries(c){ const u=c.upLevel||0; return comboSeq(c).map(L=>({letter:L, value:1*Math.pow(2,u)})); }''',
'''/* v0.51d: combo tiles take the same editor as fused tiles: letters can be turned
   off and reordered. c.order / c.active work as on trios; untouched tiles read as before. */
function comboBase(c){ return COMBO_DEFS[c.combo].seq; }
function comboOrder(c){ const n=comboBase(c).length; return Array.isArray(c.order)&&c.order.length===n ? c.order : comboBase(c).map((_,i)=>i); }
function comboActive(c){ const n=comboBase(c).length; return Array.isArray(c.active)&&c.active.length===n ? c.active : comboBase(c).map(()=>true); }
function comboEdited(c){ const o=comboOrder(c), a=comboActive(c); return o.some((x,i)=>x!==i) || a.some(x=>x===false); }
function comboSeq(c){ const b=comboBase(c), a=comboActive(c); return comboOrder(c).filter(i=>a[i]!==false).map(i=>b[i]); }
function comboLabel(c){ return comboEdited(c) ? comboSeq(c).join("") : COMBO_DEFS[c.combo].label; }
function comboLabelHtml(c){
  if(!comboEdited(c)) return COMBO_DEFS[c.combo].label;
  const b=comboBase(c), a=comboActive(c), o=comboOrder(c);
  return o.filter(i=>a[i]!==false).map(i=>b[i]).join("") + o.filter(i=>a[i]===false).map(i=>'<sub class="cm-off">'+b[i]+'</sub>').join("");
}
function comboEntries(c){ const u=c.upLevel||0; return comboSeq(c).map(L=>({letter:L, value:1*Math.pow(2,u)})); }''')
rep('''    const g=document.createElement("span"); g.className="combo-label"; g.textContent=comboLabel(c); t.appendChild(g);
    const v=document.createElement("span"); v.className="val"; v.textContent=comboValue(c); t.appendChild(v);
    const cm=document.createElement("span"); cm.className="clone-mark"; cm.textContent="✚"; t.appendChild(cm);
    tileBadges(t,c);
    attachTileHandlers(t,c,where); return t;''', '''    const g=document.createElement("span"); g.className="combo-label"; g.innerHTML=comboLabelHtml(c); t.appendChild(g);
    const v=document.createElement("span"); v.className="val"; v.textContent=comboValue(c); t.appendChild(v);
    const cm=document.createElement("span"); cm.className="clone-mark"; cm.textContent="✚"; t.appendChild(cm);
    tileBadges(t,c);
    attachTileHandlers(t,c,where); return t;''')
rep('''    const g=document.createElement("span"); g.className="combo-label"; g.textContent=comboLabel(c); t.appendChild(g);
    const v=document.createElement("span"); v.className="val"; v.textContent=comboValue(c); t.appendChild(v);
    const cm=document.createElement("span"); cm.className="clone-mark"; cm.textContent="✚"; t.appendChild(cm);
    tileBadges(t,c);
    return t;''', '''    const g=document.createElement("span"); g.className="combo-label"; g.innerHTML=comboLabelHtml(c); t.appendChild(g);
    const v=document.createElement("span"); v.className="val"; v.textContent=comboValue(c); t.appendChild(v);
    const cm=document.createElement("span"); cm.className="clone-mark"; cm.textContent="✚"; t.appendChild(cm);
    tileBadges(t,c);
    return t;''')
# editor reads and writes combos too
rep('''  const ord=Array.isArray(c.order)?c.order.slice():[0,1,2];
  return {letters:c.letters.map(x=>({L:x, v:trioSideValue(c,x)})), order:ord, active:trioActive(c).map(a=>a!==false)};''',
'''  if(c.kind==="combo"){ const u=c.upLevel||0;
    return {letters:comboBase(c).map(x=>({L:x, v:Math.pow(2,u)})), order:comboOrder(c).slice(), active:comboActive(c).map(a=>a!==false)}; }
  const ord=Array.isArray(c.order)?c.order.slice():[0,1,2];
  return {letters:c.letters.map(x=>({L:x, v:trioSideValue(c,x)})), order:ord, active:trioActive(c).map(a=>a!==false)};''')
rep('''  if(!c || (c.kind!=="fused" && c.kind!=="trio")) return;''', '''  if(!c || (c.kind!=="fused" && c.kind!=="trio" && c.kind!=="combo")) return;''')
rep('''  if(card && (card.kind==="fused" || card.kind==="trio")){   // v0.51c: hold to open the fuse editor''',
    '''  if(card && (card.kind==="fused" || card.kind==="trio" || card.kind==="combo")){   // v0.51c: hold to open the fuse editor (v0.51d: combos too)''')
rep('''.tile.fused,.tile.trio{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}''',
'''.tile.fused,.tile.trio,.tile.combo{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}
.combo-label .cm-off{font-size:1em;opacity:.35;vertical-align:baseline;margin-left:0}
#canvas .combo-label .cm-off{font-size:.5em;opacity:.55;margin-left:1px}
/* v0.51d: on the canvas a turned-off letter shrinks to a subscript, so the letters
   that spell the word take about 80% of the tile. The bank keeps the dimmed look. */
#canvas .tile.domino .dom-cell.dim{flex:0 0 13px;justify-content:flex-end;padding-bottom:6px;opacity:.45}
#canvas .tile.domino.on1.off1{width:calc(var(--tw,40px)*1.08 + 15px)}
#canvas .tile.domino.on1.off2{width:calc(var(--tw,40px)*1.08 + 30px)}
#canvas .tile.domino.on2.off1{width:calc(var(--tw,40px)*1.9 + 17px)}
.tile.domino .dom-div{display:none}
.tile.trio .clone-mark{position:absolute;right:3px;top:2px;font-size:.5em;color:#3C7E6E;z-index:3}
#canvas .tile.domino .dom-cell.dim .dom-letter{font-size:calc(var(--tfs,1.5rem)*.42)}
#canvas .tile.domino .dom-cell.dim .dom-val{display:none}
#canvas .tile.domino .dom-cell:not(.dim){flex:1 1 0}
@keyframes fePop{0%{transform:scale(1.22,.8)}45%{transform:scale(.92,1.1)}75%{transform:scale(1.04,.97)}100%{transform:scale(1,1)}}
.fe-chip.pop{animation:fePop .38s cubic-bezier(.3,1.6,.5,1)}
@media (prefers-reduced-motion: reduce){ .fe-chip.pop{animation:none} }''')
# squash and stretch in the editor: pop on tap, stretch while dragged, FLIP the others into place
rep('''function feRender(){
  const row=$("fuseChips"); row.innerHTML="";''', '''function feRender(popIdx){
  const row=$("fuseChips");
  const before=new Map(); [...row.children].forEach(n=>before.set(n.dataset.idx, n.getBoundingClientRect().left));
  row.innerHTML="";''')
rep('''  const word=FE.order.filter(i=>FE.active[i]).map(i=>FE.letters[i].L).join("");''',
'''  if(!reduceMotion()) [...row.children].forEach(n=>{   // others slide to their new seats, then settle
    const was=before.get(n.dataset.idx); if(was==null) return;
    const dx=was-n.getBoundingClientRect().left; if(Math.abs(dx)<1) return;
    n.style.transition="none"; n.style.transform="translateX("+dx+"px)";
    requestAnimationFrame(()=>{ n.style.transition="transform .32s cubic-bezier(.3,1.5,.5,1)"; n.style.transform=""; });
  });
  if(popIdx!=null && !reduceMotion()){ const n=[...row.children].find(x=>x.dataset.idx==popIdx); if(n){ void n.offsetWidth; n.classList.add("pop"); } }
  const word=FE.order.filter(i=>FE.active[i]).map(i=>FE.letters[i].L).join("");''')
rep('''    if(moved) chip.style.transform="translateX("+dx+"px) scale(1.06)";''',
    '''    if(moved){ const st=Math.min(0.12, Math.abs(dx)/600); chip.style.transform="translateX("+dx+"px) rotate("+(dx>0?3:-3)+"deg) scale("+(1.06+st)+","+(1-st)+")"; }''')
rep('''    feApply(); feRender();
  };''', '''    feApply(); feRender(idx);
    try{ if(!reduceMotion() && FE && FE.card) Spring.pop(String(FE.card.id),(Math.random()*2-1)*6); }catch(_){}   // the tile itself squashes too
  };''')

# ================================================================ 4. definitions: nooner, and a rule for sexual definitions
rep('''const DEF_BLOCKLIST=new Set([''', '''const DEF_BLOCKLIST=new Set([
  "nooner","nooners",   // v0.51d''')
rep('''const EXPLICIT_DEF_RE=new RegExp(''', '''const EXPLICIT_DEF_RE=new RegExp(
  // v0.51d: anything describing sexual activity hides the card (the word stays playable)
  "sexual (?:intercourse|activity|activities|act|acts|encounter|encounters|relations|relationship|partner|partners|desire|pleasure|excitement|arousal|behaviou?r|contact|favou?rs?|conduct|attraction|appetite|union|congress|gratification|stimulation|innuendo)|"+
  "\\\\bhav(?:e|ing|ed) sex\\\\b|\\\\bsex (?:act|acts|toy|toys|worker|workers|work|object|appeal|drive|life|scene|partner|tourism)\\\\b|"+
  "sexually (?:explicit|active|aroused|attractive|suggestive|charged|provocative|promiscuous)|\\\\berotic\\\\w*|lovemaking|\\\\bmake love\\\\b|\\\\bmaking love\\\\b|"+
  "one-night stand|\\\\blustful\\\\w*|\\\\blecher\\\\w*|\\\\bpromiscu\\\\w*|\\\\bseduc\\\\w*|\\\\bquickie\\\\b|\\\\bbooty call\\\\b|\\\\bhook-? ?up\\\\b(?= with| for sex)|"+''')

# ================================================================ 5. mystery perks for everyone
rep('''    if(!G.perks.caseClosed)    e.push({make:()=>caseClosedOffer(),    weight:1.2, char:"detective"});\n''', '')
rep('''  {name:"Case Closed",   art:"🗃️", char:"detective", desc:"Solving a mystery word gives you a discard back.", d:{type:"caseClosed"}},''',
'''  {name:"Case Closed",   art:"🗃️", desc:"Solving a mystery word gives you a discard back.", d:{type:"caseClosed"}},
  {name:"Second Wind",   art:"🌬️", desc:"Your first mystery word each round doesn't use up a word.", d:{type:"secondWind"}},
  {name:"Gold Leaf",     art:"🍂", desc:"Solving a mystery word gilds the highest-value letter you used in it.", d:{type:"goldLeaf"}},
  {name:"Reward Poster", art:"📜", desc:"Every mystery word pays $3, plus $1 for each letter past 4.", d:{type:"rewardPoster"}},
  {name:"Paper Trail",   art:"🧾", desc:"After you solve a mystery word, your next word this round scores ×1.5.", d:{type:"paperTrail"}},''')
rep('''function caseClosedOffer(){''', '''function secondWindOffer(){ return {kind:"Perk",rarity:"rare",name:"Second Wind",desc:"Your first mystery word each round doesn't use up a word.",price:px(9),art:"🌬️",d:{type:"secondWind"}}; }
function goldLeafOffer(){ return {kind:"Perk",rarity:"rare",name:"Gold Leaf",desc:"Solving a mystery word gilds the highest-value letter you used in it.",price:px(9),art:"🍂",d:{type:"goldLeaf"}}; }
function rewardPosterOffer(){ return {kind:"Perk",rarity:"common",name:"Reward Poster",desc:"Every mystery word pays $3, plus $1 for each letter past 4.",price:px(5),art:"📜",d:{type:"rewardPoster"}}; }
function paperTrailOffer(){ return {kind:"Perk",rarity:"common",name:"Paper Trail",desc:"After you solve a mystery word, your next word this round scores ×1.5.",price:px(6),art:"🧾",d:{type:"paperTrail"}}; }
function caseClosedOffer(){''')
rep('''  if(!G.perks.fireSale)          e.push({make:()=>fireSaleOffer(),    weight:1.4});''',
'''  if(!G.perks.fireSale)          e.push({make:()=>fireSaleOffer(),    weight:1.4});
  // v0.51d: mystery-word perks, open to every character
  if(!G.perks.caseClosed)        e.push({make:()=>caseClosedOffer(),  weight:1.1});
  if(!G.perks.secondWind)        e.push({make:()=>secondWindOffer(),  weight:1.0});
  if(!G.perks.goldLeaf)          e.push({make:()=>goldLeafOffer(),    weight:1.0});
  if(!G.perks.rewardPoster)      e.push({make:()=>rewardPosterOffer(),weight:1.2});
  if(!G.perks.paperTrail)        e.push({make:()=>paperTrailOffer(),  weight:1.2});''')
rep('''    case "caseClosed":   G.perks.caseClosed=true; break;''',
    '''    case "caseClosed":   G.perks.caseClosed=true; break;
    case "secondWind": case "goldLeaf": case "rewardPoster": case "paperTrail": G.perks[d.type]=true; break;   // v0.51d''')
rep('''    if(G.perks.caseClosed){ G.discardsLeft++; toast("Case Closed: discard returned"); }''',
'''    if(G.perks.caseClosed){ G.discardsLeft++; toast("Case Closed: discard returned"); }
    if(G.perks.secondWind && !G.overtime && G._swRound!==G.level){ G._swRound=G.level; G.handsLeft++; toast("Second Wind: that word was free"); }
    if(G.perks.rewardPoster){ const pay=3+Math.max(0,res.length-4); G.coins=Math.min(999,(G.coins||0)+pay); toast("Reward Poster: $"+pay); }
    if(G.perks.goldLeaf){ let best=null;
      res.forEach(r=>{ const c=r.card&&(r.card._fusedParent||r.card); if(c && c.kind==="letter" && canGild(c) && (!best || cardValue(c)>cardValue(best))) best=c; });
      if(best){ best.upLevel=(best.upLevel||0)+1; toast("Gold Leaf: "+best.letter+" gilded"); } }
    if(G.perks.paperTrail) G._ptNext=true;''')
rep('''  const sc=scoreOf(res);
  const w=w0;''', '''  const sc=scoreOf(res);
  G._ptNext=false;   // v0.51d Paper Trail: consumed by this word (a solve below arms it again)
  const w=w0;''')
rep('''  if(G.perks.rapidFire && effLen<=4 && (G._rfStreak||0)>0) total*=1+0.15*G._rfStreak;            // v0.51b Rapid Fire''',
    '''  if(G.perks.rapidFire && effLen<=4 && (G._rfStreak||0)>0) total*=1+0.15*G._rfStreak;            // v0.51b Rapid Fire
  if(G.perks.paperTrail && G._ptNext) total*=1.5;                                                // v0.51d Paper Trail''')
rep('''  G._roStreak=0; G._longest=null; G._moUsed=false;   // v0.51c Run-On Sentence, Magnum Opus''',
    '''  G._roStreak=0; G._longest=null; G._moUsed=false;   // v0.51c Run-On Sentence, Magnum Opus
  G._ptNext=false;                                   // v0.51d Paper Trail''')
rep('''      roStreak:G._roStreak||0, longest:(G._longest||null), moUsed:!!G._moUsed,''',
    '''      roStreak:G._roStreak||0, longest:(G._longest||null), moUsed:!!G._moUsed,
      swRound:(G._swRound==null?null:G._swRound), ptNext:!!G._ptNext, pendingRewards:(G.pendingRewards||[]),''')
rep('''  G._roStreak=+d.roStreak||0; G._longest=d.longest||null; G._moUsed=!!d.moUsed;''',
    '''  G._roStreak=+d.roStreak||0; G._longest=d.longest||null; G._moUsed=!!d.moUsed;
  G._swRound=(d.swRound==null?null:d.swRound); G._ptNext=!!d.ptNext; G.pendingRewards=Array.isArray(d.pendingRewards)?d.pendingRewards:[];''')
rep('''  G.letterPlays={}; G._dealerCardId=null; G._qsRound=null; G._rfStreak=0; G._tgN=0;''',
    '''  G.letterPlays={}; G._dealerCardId=null; G._qsRound=null; G._rfStreak=0; G._tgN=0; G._swRound=null; G._ptNext=false; G.pendingRewards=[];''')
# deck lists
PERKS = [("secondWind","Second Wind","🌬️","Your first mystery word each round doesn't use up a word."),
         ("goldLeaf","Gold Leaf","🍂","Solving a mystery word gilds the highest-value letter you used in it."),
         ("rewardPoster","Reward Poster","📜","Every mystery word pays $3, plus $1 for each letter past 4."),
         ("paperTrail","Paper Trail","🧾","After you solve a mystery word, your next word this round scores ×1.5.")]
rep('''  if(G.perks.caseClosed)   out.push("Case Closed · a solve returns a discard");''',
    '''  if(G.perks.caseClosed)   out.push("Case Closed · a solve returns a discard");
''' + "\n".join('  if(G.perks.%s) out.push("%s · %s");' % (t, n, d.rstrip(".")) for t, n, a, d in PERKS))
rep('''  if(P.killFee)    push("💵","Kill Fee","Every letter you cut pays $1.");''',
    '''  if(P.killFee)    push("💵","Kill Fee","Every letter you cut pays $1.");
''' + "\n".join('  if(P.%s) push("%s","%s","%s");' % (t, a, n, d) for t, n, a, d in PERKS))

# ================================================================ 6. Detective targets +10%
rep('''    targetMult:1, hearts:3, unlimitedMystery:true''', '''    targetMult:1.10, hearts:3, unlimitedMystery:true''')

# ================================================================ 7. foiled shop letters arrive at 4+ points
rep('''  const L=weightedLetter(rng,pool), v=LETTER_VALUES[L];
  return {kind:"Letter",rarity:"uncommon",name:"Foiled "+L,
    desc:"A new "+v+"-point "+L+" with a Foil Stamp: it scores double the first time you play it each round."+heldNote(L),
    price:px((4+Math.ceil(v/2))*LETTER_PRICE_SCALE),
    art:`<span class="mini-tile" style="background:linear-gradient(180deg,#EEF2F6,#D7DEE8);border-color:#9DAABB">${L}<span class="mv">${v}</span></span>`,
    d:{type:"letter",L,foil:true}};''',
'''  const L=weightedLetter(rng,pool), v0=LETTER_VALUES[L];
  let g=0; while(v0*Math.pow(2,g)<4 && g<GILD_CAP) g++;   // v0.51d: foiled letters arrive gilded to 4+ points (no extra draw from the seed)
  const v=v0*Math.pow(2,g);
  return {kind:"Letter",rarity:(g>=2?"rare":"uncommon"),name:"Foiled "+L,
    desc:"A new "+v+"-point "+L+(g?" (gilded)":"")+" with a Foil Stamp: it scores double the first time you play it each round."+heldNote(L),
    price:letterAcquireCost(L,g)+2,
    art:`<span class="mini-tile${g?" upgraded":""}" style="background:linear-gradient(180deg,#EEF2F6,#D7DEE8);border-color:#9DAABB">${L}<span class="mv">${v}</span></span>`,
    d:{type:"letter",L,foil:true,gild:g}};''')

# ================================================================ 8. challenge upgrade reward: gild, golden, stamp or fusion
rep('''function challengeUpgradeLetterFor(level){''', '''/* v0.51d: the "upgrade" reward rolls a variant per round (its own seed key, so
   nothing else moves): a free gild, a golden multiplier on a letter you pick
   (×1.25 / ×1.5 / ×1.75 / ×2 at 55 / 30 / 12 / 3 percent), a stamp you place,
   or a free fusion. */
const UPGRADE_VARIANTS=[["gild",35],["golden",30],["stamp",20],["fuse",15]];
const GOLDEN_TIERS=[[1.25,55,"common"],[1.5,30,"rare"],[1.75,12,"epic"],[2,3,"legendary"]];
const STAMP_NAMES={foil:"Foil Stamp",boldface:"Bold Face",dropcap:"Drop Cap",serif:"Serif Stamp",ditto:"Ditto Mark",inkwell:"Ink Well",encore:"Encore",watermark:"Watermark"};
function rollUpgradeVariant(level){
  const rng=makeRng("chupv:"+level);
  const pick=list=>{ let t=0; list.forEach(x=>t+=x[1]); let r=rng()*t; for(const x of list){ r-=x[1]; if(r<=0) return x; } return list[0]; };
  const v=pick(UPGRADE_VARIANTS)[0];
  if(v==="golden"){ const t=pick(GOLDEN_TIERS); return {kind:"golden", mult:t[0], tier:t[2]}; }
  if(v==="stamp"){ const ks=Object.keys(STAMP_NAMES); return {kind:"stamp", stamp:ks[Math.floor(rng()*ks.length)]}; }
  return {kind:v};
}
function upgradeRewardText(u){
  if(!u || u.kind==="gild") return {badge:"FREE GILD", name:"Your pick of gild", desc:"Gild any tile you own, free, at the next shop."};
  if(u.kind==="golden") return {badge:"GOLDEN ×"+u.mult, name:"Golden ×"+u.mult+" letter", desc:"Make any letter you own golden: every word with it scores ×"+u.mult+". "+u.tier[0].toUpperCase()+u.tier.slice(1)+" roll."};
  if(u.kind==="stamp") return {badge:"FREE STAMP", name:"Free "+STAMP_NAMES[u.stamp], desc:"Place a "+STAMP_NAMES[u.stamp]+" on any tile you own, free, at the next shop."};
  return {badge:"FREE FUSION", name:"Free letter fusion", desc:"Fuse any two letters you own into one tile, free, at the next shop."};
}
function challengeUpgradeLetterFor(level){''')
rep('''  G.challengePending={ type, banned, houseLetter, epic:challengeEpicFor(lvl), reward:null, trio:rewardTrioFor(lvl,type) };''',
    '''  G.challengePending={ type, banned, houseLetter, epic:challengeEpicFor(lvl), reward:null, trio:rewardTrioFor(lvl,type), up:rollUpgradeVariant(lvl) };''')
rep('''    if(key==="epic" && p.epic){ r={badge:"EPIC", name:p.epic.name, desc:p.epic.desc, art:p.epic.art}; }''',
    '''    if(key==="epic" && p.epic){ r={badge:"EPIC", name:p.epic.name, desc:p.epic.desc, art:p.epic.art}; }
    if(key==="upgrade"){ r=upgradeRewardText(p.up); }''')
rep('''  G.challenge={ type:p.type, reward:p.reward, banned:p.banned||[], houseLetter:p.houseLetter||null, epic:p.epic||null, active:true };''',
    '''  G.challenge={ type:p.type, reward:p.reward, banned:p.banned||[], houseLetter:p.houseLetter||null, epic:p.epic||null, up:p.up||null, active:true };''')
rep('''      G.pendingFreeGild=(G.pendingFreeGild||0)+1;
      rw.freeGild=true;''', '''      const u=G.challenge.up;
      if(!u || u.kind==="gild") G.pendingFreeGild=(G.pendingFreeGild||0)+1;
      else { if(!G.pendingRewards) G.pendingRewards=[]; G.pendingRewards.push(u); }
      rw.freeGild=true; rw.freeUpgrade=upgradeRewardText(u).name;''')
rep('''  if(rw.freeGild)   bits.push("free gild waiting in the shop");''',
    '''  if(rw.freeGild)   bits.push((rw.freeUpgrade||"free gild").toLowerCase().replace(/^your pick of gild$/,"free gild")+" waiting in the shop");''')
# the shop shelf carries one free offer per banked reward
rep('''function appendShopExtras(){
  const n=+G.pendingFreeGild||0;''', '''function appendShopExtras(){
  (G.pendingRewards||[]).forEach((u,i)=>{
    if((G.shopOffers||[]).some(o=>o.d && o.d.rewardIdx===i && !o.sold)) return;
    const tx=upgradeRewardText(u); let o;
    if(u.kind==="golden") o={kind:"Upgrade",rarity:u.tier,name:tx.name,desc:"Challenge reward. "+tx.desc,needsTarget:"freegolden",art:"🌟",d:{type:"freeGolden",mult:u.mult}};
    else if(u.kind==="stamp"){ const mk={foil:foilOffer,encore:encoreOffer,watermark:watermarkOffer,boldface:boldFaceOffer,dropcap:dropCapOffer,serif:serifStampOffer,ditto:dittoMarkOffer,inkwell:inkWellOffer}[u.stamp];
      o=mk?mk():null; if(o){ o=Object.assign({},o,{name:tx.name, desc:"Challenge reward. "+tx.desc}); } }
    else if(u.kind==="fuse"){ o=Object.assign({},fusionOffer(),{name:tx.name, desc:"Challenge reward. "+tx.desc}); }
    if(!o) return;
    o.price=0; o.pinned=true; o.sold=false; o.reward=true; o.d=Object.assign({},o.d,{rewardIdx:i});
    G.shopOffers.unshift(o);
  });
  const n=+G.pendingFreeGild||0;''')
rep('''    case "freeGild":     openDeck("freegild"); break;''', '''    case "freeGild":     openDeck("freegild"); break;
    case "freeGolden":   G._goldenMult=d.mult||1.25; G._rewardIdx=d.rewardIdx; openDeck("freegolden"); break;   // v0.51d''')
rep('''  if(G.selectMode==="freegild" && stampTargetOk(c,"freegild")){''',
    '''  if(G.selectMode==="freegolden" && c.kind==="letter" && (c.mult||1)<(G._goldenMult||1.25)){ wrap.classList.add("selectable","gild"); pickOn(wrap,c,()=>doFreeGolden(c.id)); }
  if(G.selectMode==="freegild" && stampTargetOk(c,"freegild")){''')
rep('''function doFreeGild(id){''', '''function rewardConsumed(){   // v0.51d: a free reward offer was used; drop it from the bank
  const o=(G.shopOffers||[]).find(x=>x.reward && x.sold && x.d && x.d.rewardIdx!=null && !x._consumed);
  if(o){ o._consumed=true; const i=o.d.rewardIdx; if(G.pendingRewards && G.pendingRewards[i]) G.pendingRewards[i]=null; }
  G.pendingRewards=(G.pendingRewards||[]).filter(Boolean);
  (G.shopOffers||[]).forEach(x=>{ if(x.reward && !x._consumed && x.d) x.d.rewardIdx=null; });
  G.shopOffers=(G.shopOffers||[]).filter(x=>!(x.reward && !x.sold));   // re-seat the rest with fresh indexes
  appendShopExtras(); G._rewardDone=true;
}
function doFreeGolden(id){
  const c=G.deck.find(x=>x.id===id); if(!c || c.kind!=="letter") return;
  c.mult=Math.max(c.mult||1, G._goldenMult||1.25);
  toast(c.letter+" is golden: ×"+c.mult); haptic([12,30,12]);
  G.selectMode=null; rewardConsumed(); closeDeck(); renderShop(); save();
}
function doFreeGild(id){''')
# free fusion, free stamp: zero cost, and the reward is used up when the tile changes
rep('''  const cost=fusionCost(letterAcquireCost(a.letter,a.upLevel||0)+letterAcquireCost(b.letter,b.upLevel||0));   // v0.5g: 5..20''',
    '''  const freeFuse=(typeof G.fuseOfferIdx==="number" && G.shopOffers[G.fuseOfferIdx] && G.shopOffers[G.fuseOfferIdx].reward);
  const cost=freeFuse ? 0 : fusionCost(letterAcquireCost(a.letter,a.upLevel||0)+letterAcquireCost(b.letter,b.upLevel||0));   // v0.5g: 5..20 (v0.51d: free as a challenge reward)''')
rep('''  statShopBuy("Fuse "+a.letter+b.letter, cost, "fuse");''', '''  statShopBuy("Fuse "+a.letter+b.letter, cost, "fuse");
  if(typeof G.fuseOfferIdx==="number" && G.shopOffers[G.fuseOfferIdx] && G.shopOffers[G.fuseOfferIdx].reward) rewardConsumed();''')
rep('''  syncGemini(c);
  toast(label+" applied to "+tileShortName(c));''', '''  syncGemini(c);
  if((G.shopOffers||[]).some(x=>x.reward && x.sold && !x._consumed && x.needsTarget===kind)) rewardConsumed();   // v0.51d free stamp
  toast(label+" applied to "+tileShortName(c));''')
rep('''function closeDeck(){
  if(G.selectMode==="freegild" && !G._freeGildDone){''', '''function closeDeck(){
  if(!G._rewardDone){   // v0.51d: backing out of a free reward puts it back on the shelf
    (G.shopOffers||[]).forEach(x=>{ if(x.reward && x.sold && !x._consumed) x.sold=false; });
  }
  G._rewardDone=false;
  if(G.selectMode==="freegild" && !G._freeGildDone){''')
rep('''const STAMP_MODES = new Set(["encore","growth","foil","watermark","boldface","dropcap","serif","ditto","inkwell","freegild"]);''',
    '''const STAMP_MODES = new Set(["encore","growth","foil","watermark","boldface","dropcap","serif","ditto","inkwell","freegild"]);   // (freegolden is checked on its own)''')

# ================================================================ 9. stiffer challenges (live only; the predictor keeps its own constants)
rep('''const CHALLENGE_TARGET_MULT = 1.75;''', '''const CH_LIVE = { extra:%(extra)s, steep:%(steep)s, ban:%(ban)s, margins:%(margins)s, minLen:%(minLen)s, smudge:%(smudge)s };   // v0.51d live challenge rules (sim-tuned toward ~65%% cleared)
const CHALLENGE_TARGET_MULT = 1.75;''' % P)
rep('''  if(challengeActive() && G.challenge.type==="steep"){ G.target=Math.round(G.target*CHALLENGE_TARGET_MULT); }''',
    '''  if(challengeActive() && G.challenge.type==="steep"){ G.target=Math.round(G.target*CH_LIVE.steep); }
  if(challengeActive()){ G.target=Math.round(G.target*CH_LIVE.extra); }   // v0.51d: every challenge round also asks for more''')
rep('''  const tgt = p.type==="steep" ? Math.round(base*CHALLENGE_TARGET_MULT) : base;''',
    '''  const tgt = Math.round((p.type==="steep" ? Math.round(base*CH_LIVE.steep) : base)*CH_LIVE.extra);''')
rep('''  $("chalTarget").innerHTML = p.type==="steep"''', '''  $("chalTarget").innerHTML = true''')
rep('''  const banned = type==="locked" ? deckTopLetters(CHALLENGE_BAN_COUNT) : [];''', '''  const banned = type==="locked" ? deckTopLetters(CH_LIVE.ban) : [];''')
rep('''  let m=(challengeActive() && G.challenge.type==="longform") ? CHALLENGE_MIN_LEN : 0;''', '''  let m=(challengeActive() && G.challenge.type==="longform") ? CH_LIVE.minLen : 0;''')
rep('''G.handSize=Math.max(3,G.handSize-MARGINS_TILES);''', '''G.handSize=Math.max(3,G.handSize-CH_LIVE.margins);''')
rep('''    G.hand[Math.floor(rngS()*G.hand.length)]._smudged=true;''',
    '''    const idx=[...G.hand.keys()]; for(let k=0;k<Math.min(CH_LIVE.smudge,G.hand.length);k++){ const j=Math.floor(rngS()*idx.length); G.hand[idx.splice(j,1)[0]]._smudged=true; }''')
# challenge copy follows the live numbers
rep('''  steep:  { name:"Steep Target", badge:"+75% target", diff:2,
            desc:"Clear a target that is 75 percent higher this round." },
  locked: { name:"Letters Locked", badge:"3 letters out", diff:2,
            desc:"Your three most-used letters are off the board this round." },
  longform:{ name:"Long Form", badge:"5+ letters only", diff:2,   /* v0.5a: 7/7 cleared, was 3 */
            desc:"Only words of five letters or more will count this round." },
  smudged:{ name:"Smudged Ink", badge:"1 tile smudged", diff:2,
            desc:"One tile in every hand is smudged and scores zero." },''', '''  steep:  { name:"Steep Target", badge:"+%(steepPct)s%% target", diff:2,
            desc:"Clear a target that is %(steepPct)s percent higher this round." },
  locked: { name:"Letters Locked", badge:"%(ban)s letters out", diff:2,
            desc:"Your %(banWord)s most-used letters are off the board this round." },
  longform:{ name:"Long Form", badge:"%(minLen)s+ letters only", diff:2,
            desc:"Only words of %(minWord)s letters or more will count this round." },
  smudged:{ name:"Smudged Ink", badge:"%(smudge)s tiles smudged", diff:2,
            desc:"%(smudgeWord)s tiles in every hand are smudged and score zero." },''' % dict(P, steepPct=round((P["steep"]-1)*100), banWord={3:"three",4:"four",5:"five",6:"six"}[P["ban"]], minWord={5:"five",6:"six",7:"seven",8:"eight"}[P["minLen"]], smudgeWord={1:"One",2:"Two",3:"Three",4:"Four"}[P["smudge"]]))
rep('''  margins:{ name:"Small Margins", badge:"smaller hand", diff:1,
            desc:"Your hand holds one fewer tile this round." },''', '''  margins:{ name:"Small Margins", badge:"smaller hand", diff:1,
            desc:"Your hand holds %(mWord)s fewer tile%(mS)s this round." },''' % dict(mWord={1:"one",2:"two",3:"three"}[P["margins"]], mS="" if P["margins"]==1 else "s"))

# every fused tile wears the chain mark, trios included
rep('''    t.classList.add("trio","domino");''', '''    t.classList.add("trio","domino");
    { const fm=document.createElement("span"); fm.className="clone-mark"; fm.textContent="⛓"; t.appendChild(fm); }''', 2)
# canvas: fused tiles with letters off shrink to fit the letters still on
rep('''    if(where==="canvas"){ tileBadges(t,c); attachTileHandlers(t,c,"canvas"); return t; }   // v0.51c: hold to edit the letters''',
    '''    if(where==="canvas"){ domFit(t); tileBadges(t,c); attachTileHandlers(t,c,"canvas"); return t; }   // v0.51c: hold to edit the letters''')
rep('''    if(where==="canvas"){ attachFusedCanvasHandlers(t,c); return t; }''',
    '''    if(where==="canvas"){ domFit(t); attachFusedCanvasHandlers(t,c); return t; }''')
rep('''function _feHintShown(){''', '''function domFit(t){   // v0.51d: tag a canvas domino with how many letters are on and off
  const off=t.querySelectorAll(".dom-cell.dim").length, on=t.querySelectorAll(".dom-cell").length-off;
  if(off){ t.classList.add("on"+on,"off"+off); }
}
function _feHintShown(){''')

open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
