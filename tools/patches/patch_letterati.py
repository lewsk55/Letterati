#!/usr/bin/env python3
"""Build letterati_v0.51a.html from letterati_v0.5h.html.
Every edit is an exact-match replacement that must hit exactly once."""
import sys, re
SRC, OUT, MOD = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(SRC, encoding="utf-8").read()
module = open(MOD, encoding="utf-8").read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit("expected %d hit(s), got %d for:\n%s" % (n, c, a[:200]))
    s = s.replace(a, b)

# ---------------------------------------------------------------- version
rep('const VERSION = "0.5h";', 'const VERSION = "0.51a";')

# ---------------------------------------------------------------- module, inlined before the game script
rep('<script src="letterati-common.js"></script>\n<script>',
    '<script src="letterati-common.js"></script>\n'
    '<script>window.PBS_TELEMETRY_CONFIG={gameId:"letterati",gameVersion:"0.51a",inferQuitOnPagehide:false};</script>\n'
    '<script>\n' + module + '\n</script>\n<script>')

# ---------------------------------------------------------------- helper
rep('const WIN_LEVEL = 6;',
'''/* v0.51a analytics: PGames event stream (PBS Games Analytics Approach v1).
   Each call is one push onto the telemetry queue inside try/catch. The network
   runs on the module's own timer, so nothing here can slow scoring or throw into
   play. Tier A events use the shared names; game detail goes out as letterati:*. */
const TL={
  ev(name,p){ try{ if(window.PBSTelemetry) window.PBSTelemetry.track(name,p||{}); }catch(e){} },
  g(id,p){ try{ const T=window.PBSTelemetry; if(!T) return;
    // a late async event (a mystery clue landing after Quit to title) still belongs to the parked run
    if(!T.runOpen() && G.stats && G.stats.runId && !G.stats.result){ T.setRun(G.stats.runId); T.game("letterati:"+id,p||{}); T.closeRun(); }
    else T.game("letterati:"+id,p||{}); }catch(e){} },
  run(id){ try{ if(window.PBSTelemetry && id) window.PBSTelemetry.setRun(id); }catch(e){} },
  close(){ try{ if(window.PBSTelemetry) window.PBSTelemetry.closeRun(); }catch(e){} },
  done(){ try{ if(window.PBSTelemetry){ window.PBSTelemetry.markRunDone(); window.PBSTelemetry.closeRun(); } }catch(e){} }
};
function tlPerks(){   // owned perks as a short list of names, for run summaries
  try{
    const out=[], P=G.perks||{};
    Object.keys(P).forEach(k=>{
      const v=P[k];
      if(k==="firstUp"||k==="lastUp"){ const ls=Object.keys(v||{}).filter(L=>v[L]); if(ls.length) out.push(k+":"+ls.join("")); return; }
      if(v===true || (typeof v==="number" && v>0) || (v && typeof v==="object") || (typeof v==="string" && v)) out.push(k);
    });
    return out;
  }catch(e){ return []; }
}
const WIN_LEVEL = 6;''')

# ---------------------------------------------------------------- run start
rep('''  G.deck=rollStartingDeck();
  statInit(G.seed);''',
'''  G.deck=rollStartingDeck();
  statInit(G.seed);
  G._discardsUsed=0; G._otCount=0;
  TL.run(G.stats.runId);
  TL.ev("game_start",{ mode:G.mode, puzzle_type:G.mode, daily_id:G.dailyDate||null, seed:G.seed,
    character:G.character, ascension:G.ascension, asc_ladder:2, hearts:G.hearts, hand_size:G.handSize, dev:!!G.dev });''')

# abandoned saved run that a new run replaces
rep('''    enqueueTelemetry(s);
    if(s.mode==="daily" && s.dailyDate){''',
'''    enqueueTelemetry(s);
    if(s.runId){ TL.run(s.runId);
      TL.ev("game_quit",{ quit_type:"inferred", trigger:"replaced_by_new_run", round:d.level|0, hearts:d.hearts|0, coins:d.coins|0,
        run_score:d.runScore|0, run_ms:s.runMs|0, mode:s.mode, daily_id:s.dailyDate||null, character:s.character, ascension:s.ascension, quick_exit:!!s.quickExit });
      TL.done(); }
    if(s.mode==="daily" && s.dailyDate){''')

# ---------------------------------------------------------------- draft
rep('''  if(G.stats) G.stats.draft={offered:G.draft.offers.map(x=>x.name), picked:o.name, type:o.d&&o.d.type};''',
'''  if(G.stats) G.stats.draft={offered:G.draft.offers.map(x=>x.name), picked:o.name, type:o.d&&o.d.type};
  TL.g("draft",{ offered:G.draft.offers.map(x=>x.name), picked:o.name, type:(o.d&&o.d.type)||null, rarity:o.rarity||null });''')

# ---------------------------------------------------------------- boss start
rep('''      if(G.stats && !G.stats[bkey]) G.stats[bkey]={round:G.level, stage:stage, type:bt, heartsBefore:G.hearts, heartsAfter:null, cleared:null, words:0};''',
'''      if(G.stats && !G.stats[bkey]){ G.stats[bkey]={round:G.level, stage:stage, type:bt, heartsBefore:G.hearts, heartsAfter:null, cleared:null, words:0};
        TL.g("boss",{ phase:"start", round:G.level, stage:stage, type:bt, target:G.target, hearts:G.hearts }); }''')

# ---------------------------------------------------------------- level start (per-round counters + event)
rep('''  G._rescues=0; G._deadRescues=0;   // v0.5h: house discards handed out this round''',
'''  G._rescues=0; G._deadRescues=0;   // v0.5h: house discards handed out this round
  G._discardsUsed=0; G._otCount=0;  // v0.51a: discards actually spent, and overtime words, this round''')
rep('''  tickFlush(); G._roundStartMs=G.runMs||0;   // v0.5a telemetry: per-round duration
  clearUndo();
  showGame();''',
'''  tickFlush(); G._roundStartMs=G.runMs||0;   // v0.5a telemetry: per-round duration
  TL.ev("level_start",{ round:G.level, eq_level:eqLevel(G.level), target:G.target, words:G.handsLeft, discards:G.discardsLeft,
    hand_size:G.handSize, hearts:G.hearts, coins:G.coins, press_mult:G.scoreMult, endless:!!G.infinite,
    challenge:(challengeActive()?{type:G.challenge.type, reward:G.challenge.reward}:null),
    boss:(bossActive()?{type:G.boss.type, stage:G.boss.stage||0}:null),
    side_job:(G.sideJob?G.sideJob.key:null) });
  clearUndo();
  showGame();''')

# ---------------------------------------------------------------- ghost boss heart loss
rep('''        toast(BT.taunt+" "+sc.total+" against its "+quota+". A heart is gone.");''',
'''        toast(BT.taunt+" "+sc.total+" against its "+quota+". A heart is gone.");
        TL.g("heart",{ cause:"ghost", round:G.level, hearts_left:G.hearts, score:sc.total, quota:quota });''')

# ---------------------------------------------------------------- word
rep('''  if(G.perks.indiaInk && cash>0) G.inkPtsPending=(G.inkPtsPending||0)+cash;   // every dollar is a point on the next word
  renderHud();''',
'''  if(G.perks.indiaInk && cash>0) G.inkPtsPending=(G.inkPtsPending||0)+cash;   // every dollar is a point on the next word
  { let gil=0, fus=0; res.forEach(r=>{ const c=r.card; if(!c) return; if((c.upLevel||0)>0) gil++; if(c._fusedParent||c.kind==="fused"||c.kind==="trio") fus++; });
    TL.g("word",{ round:G.level, word:w.toUpperCase(), len:res.length, score:sc.total, cash:cash, n:G.levelStats.words,
      overtime:!!G.overtime, score_before:G.score, target:G.target, press_mult:G.scoreMult,
      mystery_hit:!!sc.mysteryHit, mystery_mult:(sc.mysteryHit?sc.mysteryMult:null), gilded_tiles:gil, fused_tiles:fus }); }
  renderHud();''')

# ---------------------------------------------------------------- discards (fix the spent count)
rep('''  G.discardsLeft--;
  renderSideJob();   // v0.5a: Clean Sweep counts down''',
'''  G.discardsLeft--;
  G._discardsUsed=(G._discardsUsed||0)+1;   // v0.51a: the real count (the old formula missed character, ascension and house discards)
  TL.g("discard",{ round:G.level, tiles:bin.length, discards_left:G.discardsLeft });
  renderSideJob();   // v0.5a: Clean Sweep counts down''')
rep('''        G._deadRescues=(G._deadRescues||0)+1;
        G.discardsLeft++;''',
'''        G._deadRescues=(G._deadRescues||0)+1;
        G.discardsLeft++;
        TL.g("house_discard",{ round:G.level, n:G._deadRescues });''')
rep('''      heartsLeft:G.hearts, discardsLeft:G.discardsLeft, discardsSpent:discardsForLevel()-G.discardsLeft,''',
'''      heartsLeft:G.hearts, discardsLeft:G.discardsLeft, discardsSpent:(G._discardsUsed||0), houseDiscards:(G._deadRescues||0),''')
rep('''      heartsLeft:G.hearts, discardsLeft:G.discardsLeft, discardsSpent:(DISCARDS_PER_LEVEL+(G.extraDiscards||0))-G.discardsLeft,''',
'''      heartsLeft:G.hearts, discardsLeft:G.discardsLeft, discardsSpent:(G._discardsUsed||0), houseDiscards:(G._deadRescues||0),''')

# ---------------------------------------------------------------- level clear
rep('''    if(_bl && _bl.round===G.level && _bl.cleared==null){
      _bl.cleared=true; _bl.heartsAfter=G.hearts; _bl.words=(G.levelStats&&G.levelStats.words)||0; } }''',
'''    if(_bl && _bl.round===G.level && _bl.cleared==null){
      _bl.cleared=true; _bl.heartsAfter=G.hearts; _bl.words=(G.levelStats&&G.levelStats.words)||0;
      TL.g("boss",{ phase:"cleared", round:G.level, stage:_bl.stage||0, type:_bl.type, words:_bl.words, hearts_before:_bl.heartsBefore, hearts_after:G.hearts, target_final:G.target }); } }''')
rep('''  G.best=Math.max(G.best,G.level);
  const info={ score:G.score, target:G.target,''',
'''  { const ch=challengeActive()?G.challenge:null;
    if(ch) TL.g("challenge",{ phase:"cleared", round:G.level, type:ch.type, reward:ch.reward, epic:(ch.epic&&ch.epic.name)||null, hearts_after:G.hearts });
    if(rw.sideJob) TL.g("side_job",{ round:G.level, key:rw.sideJob.key, paid:rw.sideJob.paid });
    TL.ev("level_complete",{ round:G.level, eq_level:eqLevel(G.level), target:G.target, score:G.score, margin:G.score-G.target,
      hearts_left:G.hearts, words_used:G.levelStats.words, words_left:G.handsLeft, overtime_words:(G._otCount||0),
      discards_spent:(G._discardsUsed||0), discards_left:G.discardsLeft, house_discards:(G._deadRescues||0),
      payout:rw.total, coins_before:G.coins, purse:{ core:rw.core, words:rw.turnsBonus, discards:rw.discardAmt, clear:rw.clearBonus, marginalia:rw.marginalia, challenge:(rw.bonus||0), side_job:(rw.sideJob?rw.sideJob.paid:0), doubled:!!rw.doubled },
      round_ms:Math.max(0,(G.runMs||0)-(G._roundStartMs||0)), challenge:(ch?ch.type:null), boss:(bossActive()?G.boss.type:null), best_word:G.levelStats.bestWord, best_score:G.levelStats.bestScore }); }
  G.best=Math.max(G.best,G.level);
  const info={ score:G.score, target:G.target,''')

# ---------------------------------------------------------------- level fail (an overtime word: costs a heart unless a perk covers it)
rep('''      wordsLeft:G.handsLeft, payout:0}); }
  if(!heartFree){''',
'''      wordsLeft:G.handsLeft, payout:0}); }
  G._otCount=(G._otCount||0)+1;
  TL.ev("level_fail",{ round:G.level, eq_level:eqLevel(G.level), target:G.target, score:G.score, margin:G.score-G.target,
    hearts_left:G.hearts, heart_free:(deadlineFree?"deadline_ext":(midnightFree?"midnight_press":null)), overtime_n:G._otCount,
    words_used:G.levelStats.words, discards_spent:(G._discardsUsed||0), house_discards:(G._deadRescues||0),
    boss:(bossActive()?G.boss.type:null), challenge:(challengeActive()?G.challenge.type:null) });
  if(!heartFree){''')
rep('''        G.reprintUsed=true; G.hearts=1; renderHud();''',
'''        G.reprintUsed=true; G.hearts=1; renderHud();
        TL.g("heart",{ cause:"reprint_save", round:G.level, hearts_left:1 });''')

# ---------------------------------------------------------------- challenges
rep('''    G.stats.challenges.push({round:lvl, type, rewardsOffered:(G.challengePending.trio||[]).slice(), taken:false, reward:null, cleared:null, heartsBefore:G.hearts, heartsAfter:null}); }''',
'''    G.stats.challenges.push({round:lvl, type, rewardsOffered:(G.challengePending.trio||[]).slice(), taken:false, reward:null, cleared:null, heartsBefore:G.hearts, heartsAfter:null}); }
  TL.g("challenge",{ phase:"offered", round:lvl, type:type, rewards_offered:(G.challengePending.trio||[]).slice(), required:!!challengeMandatory(lvl), epic:(G.challengePending.epic&&G.challengePending.epic.name)||null });''')
rep('''    if(ch && ch.round===G.level){ ch.taken=true; ch.reward=p.reward; } }
  G.challengePending=null;''',
'''    if(ch && ch.round===G.level){ ch.taken=true; ch.reward=p.reward; } }
  TL.g("challenge",{ phase:"taken", round:G.level, type:p.type, reward:p.reward, hearts:G.hearts });
  G.challengePending=null;''')
rep('''  if(challengeMandatory(G.level)) return;   // A1 Challenger: the round 5 challenge cannot be skipped
  G.challenge=null; G.challengePending=null;''',
'''  if(challengeMandatory(G.level)) return;   // A1 Challenger: the round 5 challenge cannot be skipped
  TL.g("challenge",{ phase:"skipped", round:G.level, type:(G.challengePending&&G.challengePending.type)||null });
  G.challenge=null; G.challengePending=null;''')

# ---------------------------------------------------------------- shop
rep('''    bought:[], rerolls:0 };
  G.stats.shops.push(G._curShop);
}''',
'''    bought:[], rerolls:0 };
  G.stats.shops.push(G._curShop);
  TL.g("shop_open",{ round:G.level, coins:G.coins, offered:(offers||[]).map(o=>({name:o.name, kind:o.kind, price:o.price, type:(o.d&&o.d.type)||null})) });
}''')
rep('''function statShopBuy(name, price, type){ if(G._curShop) G._curShop.bought.push({name,price,type:type||null}); }
function statShopReroll(){ if(G._curShop) G._curShop.rerolls++; }
function statShopClose(){ if(G._curShop){ G._curShop.coinsOut=G.coins;
  G._curShop.passed=G._curShop.offered.filter(o=>!G._curShop.bought.some(b=>b.name===o.name)).map(o=>o.name); }
  G._curShop=null; }''',
'''function statShopBuy(name, price, type){ if(G._curShop) G._curShop.bought.push({name,price,type:type||null});
  TL.g("shop_buy",{ round:G.level, name:name, price:price, type:type||null, coins_after:G.coins }); }
function statShopReroll(){ if(G._curShop) G._curShop.rerolls++;
  TL.g("shop_reroll",{ round:G.level, coins_after:G.coins }); }
function statShopClose(partial){ if(G._curShop){ G._curShop.coinsOut=G.coins;
  G._curShop.passed=G._curShop.offered.filter(o=>!G._curShop.bought.some(b=>b.name===o.name)).map(o=>o.name);
  TL.g("shop_close",{ round:G._curShop.round, coins_in:G._curShop.coinsIn, coins_out:G.coins, bought:G._curShop.bought,
    rerolls:G._curShop.rerolls, passed:G._curShop.passed, partial:!!partial }); }
  G._curShop=null; }''')
# shop undo: also roll back the stats record, so undone buys stop counting
rep('''    fuseOfferIdx:G.fuseOfferIdx, pendingFreeGild:+G.pendingFreeGild||0,''',
'''    fuseOfferIdx:G.fuseOfferIdx, pendingFreeGild:+G.pendingFreeGild||0,
    statBought:(G._curShop?G._curShop.bought.length:null), statRerolls:(G._curShop?G._curShop.rerolls:null),''')
rep('''  if(s.pendingFreeGild!=null) G.pendingFreeGild=s.pendingFreeGild;   // v0.5a: undoing a free gild gives it back''',
'''  if(s.pendingFreeGild!=null) G.pendingFreeGild=s.pendingFreeGild;   // v0.5a: undoing a free gild gives it back
  if(G._curShop && s.statBought!=null){   // v0.51a: an undone buy or reroll no longer counts in the run stats
    const gone=G._curShop.bought.splice(s.statBought);
    if(s.statRerolls!=null) G._curShop.rerolls=s.statRerolls;
    TL.g("shop_undo",{ round:G.level, undone:gone.map(b=>b.name) }); }''')

# a rerolled shelf is a new set of offers: log it so buy rates count every appearance
rep('''  statShopReroll();
  G.shopOffers=buildShopPool();
  appendShopExtras();''',
'''  statShopReroll();
  G.shopOffers=buildShopPool();
  appendShopExtras();
  TL.g("shop_shelf",{ round:G.level, offered:G.shopOffers.map(o=>({name:o.name, kind:o.kind, price:o.price, type:(o.d&&o.d.type)||null})) });''')

# ---------------------------------------------------------------- free gild from a challenge reward
rep('''  G.pendingFreeGild=Math.max(0,(+G.pendingFreeGild||0)-1);
  G._freeGildDone=true;''',
'''  G.pendingFreeGild=Math.max(0,(+G.pendingFreeGild||0)-1);
  G._freeGildDone=true;
  TL.g("gild",{ source:"challenge_reward", tile:tileShortName(c), level:c.upLevel });''')

# ---------------------------------------------------------------- mystery
rep('''    G.stats.mystery.push({round:G.level, answer:w, tier:tier.key, solved:false, mult:null, character:G.character||"writer"}); }''',
'''    G.stats.mystery.push({round:G.level, answer:w, tier:tier.key, solved:false, mult:null, character:G.character||"writer"}); }
  TL.g("mystery",{ phase:"shown", round:G.level, answer:w, tier:tier.key });''')

# ---------------------------------------------------------------- endless
rep('function winContinueEndless(){', 'function winContinueEndless(){\n  TL.g("endless",{ round:G.level });')

# ---------------------------------------------------------------- run end
rep('''  try{ localStorage.setItem("letterati_laststats", JSON.stringify(G.stats)); }catch(e){}
  try{ const arr=JSON.parse(localStorage.getItem("letterati_runs")||"[]"); arr.push(G.stats);''',
'''  try{ localStorage.setItem("letterati_laststats", JSON.stringify(G.stats)); }catch(e){}
  try{   // v0.51a: terminal event for the PGames stream
    const S=G.stats; TL.run(S.runId);
    if(G._curShop) statShopClose(true);
    { const ch=(S.challenges||[]).find(c=>c.taken&&c.cleared===false&&c.round===S.finalRound);
      if(ch) TL.g("challenge",{ phase:"failed", round:ch.round, type:ch.type, reward:ch.reward, hearts_after:G.hearts }); }
    [S.bossLog,S.bossLog2].forEach(b=>{ if(b && b.cleared===false){
      TL.g("boss",{ phase:"failed", round:b.round, stage:b.stage||0, type:b.type, words:b.words, hearts_before:b.heartsBefore, hearts_after:b.heartsAfter, target_final:G.target }); } });
    const won=!!S.wonRun || result==="win";
    const name= won ? "game_complete" : (S.ending==="gameover" ? "game_over" : "game_quit");
    const p={ result:result, ending:S.ending, exit_context:S.exitContext, won:won, endless:!!G.infinite,
      final_round:S.finalRound, rounds_cleared:(S.rounds||[]).filter(r=>r.cleared).length, run_score:S.runScore|0,
      duration_ms:S.runMs|0, best_word:S.bestWord||"", best_score:S.bestScore|0, words:(S.words||[]).length,
      character:S.character, ascension:S.ascension, mode:S.mode, daily_id:S.dailyDate||null, seed:S.seed,
      quick_exit:!!S.quickExit, hearts:G.hearts, coins:G.coins, deck_size:(G.deck||[]).length, press_mult:G.scoreMult,
      draft:(S.draft&&S.draft.picked)||null, perks:tlPerks() };
    if(name==="game_quit"){ p.quit_type="explicit"; p.trigger=S.exitContext; }
    TL.ev(name,p); TL.done();
  }catch(e){}
  try{ const arr=JSON.parse(localStorage.getItem("letterati_runs")||"[]"); arr.push(G.stats);''')

# ---------------------------------------------------------------- retire the GGW upload (project paused; PGames replaces it)
rep('''function telemetryEnabled(){ return !!(TELEMETRY_ENDPOINT && TELEMETRY_ANON_KEY); }''',
'''// v0.51a: retired. Runs and ratings now go out as events to the PGames project
// (see TL). The local run history and the JSON export are unchanged. Anything
// still waiting in letterati_pending_telemetry is left in place, unsent.
function telemetryEnabled(){ return false; }''')
rep('''function enqueueTelemetry(run){
  if(!run || !run.runId) return;''',
'''function enqueueTelemetry(run){
  if(!telemetryEnabled()) return;
  if(!run || !run.runId) return;''')
rep('''function submitSeedRating(vote, comment, isNote){
  try{''',
'''function submitSeedRating(vote, comment, isNote){
  TL.g("seed_rating",{ vote:vote, note:String(comment||"").slice(0,280), is_note:!!isNote, rated_run_id:(G.stats&&G.stats.runId)||null,
    seed:G.seed||null, round:G.level|0, won:!!G.wonRun, run_score:G.runScore|0, mode:G.mode||null, daily_id:G.dailyDate||null });
  if(!telemetryEnabled()) return;
  try{''')

# ---------------------------------------------------------------- park / resume
rep('''  G.paused=false;
  save();                         // capture current "play" phase before hiding screens''',
'''  G.paused=false;
  save();                         // capture current "play" phase before hiding screens
  TL.g("park",{ round:G.level, hearts:G.hearts, coins:G.coins }); TL.close();''')
rep('''  if(!G.stats) statInit(G.seed);   // legacy save with no stats → begin tracking now so the run isn't lost''',
'''  if(!G.stats) statInit(G.seed);   // legacy save with no stats → begin tracking now so the run isn't lost
  G._discardsUsed=+d.discardsUsed||0; G._deadRescues=+d.deadRescues||0; G._otCount=+d.otCount||0;
  TL.run(G.stats.runId); TL.g("resume",{ phase:d.phase||null, round:G.level, saved_version:G.stats.version||null });''')
rep('''      attempt:G.attempt, target:G.target, score:G.score, handsLeft:G.handsLeft, discardsLeft:G.discardsLeft,''',
'''      attempt:G.attempt, target:G.target, score:G.score, handsLeft:G.handsLeft, discardsLeft:G.discardsLeft,
      discardsUsed:G._discardsUsed||0, deadRescues:G._deadRescues||0, otCount:G._otCount||0,''')

# ---------------------------------------------------------------- session start at boot
rep('''loadDefStore();
try{ window.addEventListener("pagehide", flushDefStore);''',
'''loadDefStore();
try{ if(window.PBSTelemetry) window.PBSTelemetry.sessionStart(); }catch(e){}
try{ window.addEventListener("pagehide", flushDefStore);''')

open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
