#!/usr/bin/env python3
"""0.51b: Short King character + 12 character perks, Shorty rename.
Applied on top of patch_sk.py output (character, cap, rules, curve).
usage: patch_051b.py in.html out.html"""
import sys
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)

# ---------------------------------------------------------------- version
rep('const VERSION = "0.51a";', 'const VERSION = "0.51b";')
rep('gameVersion:"0.51a"', 'gameVersion:"0.51b"')

# ---------------------------------------------------------------- the old perk becomes Shorty
rep('''  {name:"Short King",       art:"👑", desc:"Short words score big: 2 letters ×3, 3 letters ×2.5, 4 letters ×1.75.", d:{type:"shortKing"}},''',
    '''  {name:"Shorty",           art:"🤏", desc:"Short words score big: 2 letters ×3, 3 letters ×2.5, 4 letters ×1.75.", d:{type:"shortKing"}},''')
rep('''  return {kind:"Perk",rarity:"rare",name:"Short King",desc:''', '''  return {kind:"Perk",rarity:"rare",name:"Shorty",desc:''')
rep('''  if(G.perks.shortKing)  out.push("Short King · ×3/×2.5/×1.75 for 2 to 4 letters");''',
    '''  if(G.perks.shortKing)  out.push("Shorty · ×3/×2.5/×1.75 for 2 to 4 letters");''')
rep('''  if(P.shortKing)  push("👑","Short King","Short words score big''', '''  if(P.shortKing)  push("🤏","Shorty","Short words score big''')
s = s.replace('price:px(8), art:"👑", d:{type:"shortKing"}};', 'price:px(8), art:"🤏", d:{type:"shortKing"}};')

# ---------------------------------------------------------------- character copy
rep('''  blurb:"Small words, big numbers. Two to four letters hit hard, and he works fast.",
  boon:"2, 3 and 4 letter words score x3.5, x3 and x2. ",
  bane:"No word longer than 5 letters.",''',
'''  blurb:"Small words, big numbers. Two to four letters hit hard, and he gets an extra word every round.",
  boon:"2, 3 and 4 letter words score ×3.5, ×3 and ×2. Five words a round.",
  bane:"No word longer than 5 letters. Targets run 30 percent higher in rounds 1 to 4, 25 percent in round 5 and 15 percent in round 6.",''')

# ---------------------------------------------------------------- the 12 perks: definitions
PERKS = [
  # type, name, rarity, price, art, desc
  ("quickStudy", "Quick Study", "common", 5, "⚡", "Your first 2-letter word each round doesn't use up a word."),
  ("shortFuse", "Short Fuse", "common", 5, "🧨", "One extra discard every round."),
  ("telegram", "Telegram", "rare", 8, "📠", "Every third word of 2 or 3 letters in a round doesn't use up a word."),
  ("rapidFire", "Rapid Fire", "common", 6, "💥", "Each word of 4 letters or fewer in a row scores +15% more than the last. A 5-letter word resets it."),
  ("oneTwo", "One-Two Punch", "rare", 8, "👊", "A 3-letter word set right after a 2-letter word scores ×2."),
  ("daisyChain", "Daisy Chain", "rare", 8, "🌼", "A word that starts with the last letter of your previous word scores ×1.4."),
  ("twoBit", "Two-Bit", "common", 5, "✌️", "2-letter words count their tile values twice."),
  ("bigType", "Big Type", "rare", 9, "🅰️", "Tiles worth 5 or more points score double in words of 3 letters or fewer."),
  ("giltEdge", "Gilt Edge", "epic", 13, "📒", "Gilds count double in 2 and 3-letter words."),
  ("smallPress", "Small Press", "epic", 14, "🗞️", "Every 2-letter word raises your score multiplier by 1% for the rest of the run."),
  ("pennyPress", "Penny Press", "common", 5, "💲", "Earn $1 for every word of 3 letters or fewer."),
  ("classifieds", "Classifieds", "rare", 8, "📰", "Letter tiles in the shop cost $1 less, and you earn $2 for every word left unused when you clear a round."),
]
WEIGHT = {"common":1.6, "rare":1.2, "epic":0.75}
offer_fns = "\n".join(
  'function sk_%sOffer(){ return {kind:"Perk",rarity:"%s",name:"%s",desc:"%s",price:px(%d),art:"%s",d:{type:"%s"}}; }' % (t, r, n, d, p, a, t)
  for t, n, r, p, a, d in PERKS)
char_block = "\n".join('    if(!G.perks.%s) e.push({make:()=>sk_%sOffer(), weight:%s, char:"shortking"});' % (t, t, WEIGHT[r]) for t, n, r, p, a, d in PERKS)
rep('''  if(G.character==="editor"){
    if(!G.perks.cutAbove)''', '''  if(G.character==="shortking"){
%s
  }
  if(G.character==="editor"){
    if(!G.perks.cutAbove)''' % char_block)
rep('function cutAboveOffer(){', offer_fns + '\nfunction cutAboveOffer(){')
# challenge reward pool (char-gated, like the Detective's and the Editor's)
pool = "\n".join('  {name:"%s", art:"%s", char:"shortking", desc:"%s", d:{type:"%s"}},' % (n, a, d, t) for t, n, r, p, a, d in PERKS)
rep('''  {name:"Cut Above",     art:"✂️", char:"editor",''', pool + '''\n  {name:"Cut Above",     art:"✂️", char:"editor",''')
# granting
rep('''    case "killFee":      G.perks.killFee=true; break;''',
    '''    case "killFee":      G.perks.killFee=true; break;
''' + "\n".join('    case "%s":' % t for t, *_ in PERKS) + ''' G.perks[d.type]=true; break;   // v0.51b Short King perks''')
# his perks may open a run: the draft takes char perks for Short King only
rep('''  const entries=perkPool(rng).filter(e=>!e.char);''', '''  const entries=perkPool(rng).filter(e=>!e.char || e.char==="shortking");''')
# deck screen lists
rep('''  if(G.perks.killFee)      out.push("Kill Fee · $1 per letter cut");''',
    '''  if(G.perks.killFee)      out.push("Kill Fee · $1 per letter cut");
''' + "\n".join('  if(G.perks.%s) out.push("%s · %s");' % (t, n, d.rstrip(".")) for t, n, r, p, a, d in PERKS))
rep('''  if(P.killFee)    push("💵","Kill Fee","Every letter you cut pays $1.");''',
    '''  if(P.killFee)    push("💵","Kill Fee","Every letter you cut pays $1.");
''' + "\n".join('  if(P.%s) push("%s","%s","%s");' % (t, a, n, d) for t, n, r, p, a, d in PERKS))

# ---------------------------------------------------------------- effects
# Short Fuse
rep('''  return Math.max(0, DISCARDS_PER_LEVEL+(G.extraDiscards||0)+(charDef().discardsDelta||0)-(ascHas(3)?1:0));''',
    '''  return Math.max(0, DISCARDS_PER_LEVEL+(G.extraDiscards||0)+(charDef().discardsDelta||0)+(G.perks&&G.perks.shortFuse?1:0)-(ascHas(3)?1:0));''')
# per-letter: Gilt Edge, Big Type
rep('''    let v=r.value;
    if(G.perks.vowelPower && VOWELS.has(r.letter)) v+=(+G.perks.vowelPower||0);   // v42a: +1 per vowel per stack''',
'''    let v=r.value;
    if(G.perks.giltEdge && res.length<=3){ const up=(r.card&&r.card.upLevel)||0; if(up>0) v*=Math.pow(2,up); }   // v0.51b Gilt Edge: gilds count twice
    if(G.perks.bigType && res.length<=3 && r.value>=5) v*=2;                     // v0.51b Big Type
    if(G.perks.vowelPower && VOWELS.has(r.letter)) v+=(+G.perks.vowelPower||0);   // v42a: +1 per vowel per stack''')
# Two-Bit
rep('''  let m=lenMult(effLen);
  m=Math.round(m*100)/100;
  let total=sum*m;''', '''  let m=lenMult(effLen);
  m=Math.round(m*100)/100;
  if(G.perks.twoBit && res.length===2) sum*=2;                        // v0.51b Two-Bit
  let total=sum*m;''')
# Rapid Fire, One-Two Punch, Daisy Chain (read the previous word, which submitWord records after scoring)
rep('''  // Short King: tiered boost for short words (see SHORT_KING_MULT)
  let shortHit=false, shortMult=1;''', '''  if(G.perks.rapidFire && effLen<=4 && (G._rfStreak||0)>0) total*=1+0.15*G._rfStreak;            // v0.51b Rapid Fire
  if(G.perks.oneTwo && effLen===3 && G.lastWordLen===2) total*=2;                                 // v0.51b One-Two Punch
  if(G.perks.daisyChain && G.lastWordLast && res.length && res[0].letter===G.lastWordLast) total*=1.4;   // v0.51b Daisy Chain
  // Short King: tiered boost for short words (see SHORT_KING_MULT)
  let shortHit=false, shortMult=1;''')
# Penny Press
rep('''  if(challengeDoublePay()) cash=Math.round(cash*1.5);   // v48g: payout challenge reward is +50%''',
    '''  if(G.perks.pennyPress && res.length<=3) cash+=1;                                        // v0.51b Penny Press
  if(challengeDoublePay()) cash=Math.round(cash*1.5);   // v48g: payout challenge reward is +50%''')
# word refunds, streak, Small Press: after the word is spent
rep('''  G.handsLeft--;
  // high-score cash bonus''', '''  G.handsLeft--;
  { const L=res.length;   // v0.51b Short King perks that act once the word is set
    if(!G.overtime && G.perks.quickStudy && L===2 && G._qsRound!==G.level){ G._qsRound=G.level; G.handsLeft++; toast("Quick Study: that word was free"); }
    if(L<=3){ G._tgN=(G._tgN||0)+1; if(!G.overtime && G.perks.telegram && G._tgN%3===0){ G.handsLeft++; toast("Telegram: that word was free"); } }
    G._rfStreak = L<=4 ? (G._rfStreak||0)+1 : 0;
    if(G.perks.smallPress && L===2){ G.scoreMult=Math.round(((G.scoreMult||1)+0.01)*1000)/1000; }
  }
  // high-score cash bonus''')
# Classifieds: cheaper letters (after the seeded rolls, so the shelf itself is unchanged) and pay for unused words
rep('''  rollSales(shelfOut,rng);
  G.shopSeen=''', '''  rollSales(shelfOut,rng);
  if(G.perks.classifieds) shelfOut.forEach(o=>{ if(o.kind==="Letter" && o.price>1) o.price-=1; });   // v0.51b Classifieds
  G.shopSeen=''')
rep('''  return {base,core,turnsBonus,wordsLeft:G.handsLeft,preBonus,discardCount,discardBonus,discardAmt,clearBonus:CLEAR_BONUS,interest,marginalia,total,doubled};''',
    '''  const classifieds = G.perks.classifieds ? 2*Math.max(0,G.handsLeft|0) : 0;   // v0.51b Classifieds
  total+=classifieds;
  return {base,core,turnsBonus,wordsLeft:G.handsLeft,preBonus,discardCount,discardBonus,discardAmt,clearBonus:CLEAR_BONUS,interest,marginalia,classifieds,total,doubled};''')
# per-round counters reset, saved and restored
rep('''  G._discardsUsed=0; G._otCount=0;  // v0.51a: discards actually spent, and overtime words, this round''',
    '''  G._discardsUsed=0; G._otCount=0;  // v0.51a: discards actually spent, and overtime words, this round
  G._rfStreak=0; G._tgN=0;          // v0.51b Rapid Fire streak and Telegram count, per round''')
rep('''      discardsUsed:G._discardsUsed||0, deadRescues:G._deadRescues||0, otCount:G._otCount||0,''',
    '''      discardsUsed:G._discardsUsed||0, deadRescues:G._deadRescues||0, otCount:G._otCount||0,
      rfStreak:G._rfStreak||0, tgN:G._tgN||0, qsRound:(G._qsRound==null?null:G._qsRound),''')
rep('''  G._discardsUsed=+d.discardsUsed||0; G._deadRescues=+d.deadRescues||0; G._otCount=+d.otCount||0;''',
    '''  G._discardsUsed=+d.discardsUsed||0; G._deadRescues=+d.deadRescues||0; G._otCount=+d.otCount||0;
  G._rfStreak=+d.rfStreak||0; G._tgN=+d.tgN||0; G._qsRound=(d.qsRound==null?null:d.qsRound);''')
rep('''  G.letterPlays={}; G._dealerCardId=null;''', '''  G.letterPlays={}; G._dealerCardId=null; G._qsRound=null; G._rfStreak=0; G._tgN=0;''')

# ---------------------------------------------------------------- the cap explains itself
rep('''  const gates = (challengeActive() && (challengeMinLen()>0 || !!bannedLetterSet() || ["house","reprints"].includes(G.challenge.type)))''',
    '''  const gates = wordCap()<99
             || (challengeActive() && (challengeMinLen()>0 || !!bannedLetterSet() || ["house","reprints"].includes(G.challenge.type)))''')
rep('''    if(minL && res.length<minL){''', '''    if(res.length>wordCap()){
      why = `a valid word, but ${escHtml(charDef().name)} sets ${wordCap()} letters at most`;
    } else if(minL && res.length<minL){''')

# the canvas label names the cap too
rep('''    if(minL && res.length>=2 && res.length<minL && res.every(r=>r.letter)) label="need "+minL+"+ letters";''',
    '''    if(res.length>wordCap()) label=wordCap()+" letters at most";
    else if(minL && res.length>=2 && res.length<minL && res.every(r=>r.letter)) label="need "+minL+"+ letters";''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
