#!/usr/bin/env python3
"""0.51d -> 0.51e: free play picker after a run, audio wake after backgrounding,
Gold Leaf epic, softer endless walls, reset options in settings.
usage: patch_051e.py in.html out.html"""
import sys
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)

# version
rep('gameVersion:"0.51d"', 'gameVersion:"0.51e"')
import re
m = re.findall(r'const VERSION *= *"0\.51d"', s); assert len(m)==1, m
s = s.replace(m[0], m[0].replace("0.51d","0.51e"))

# 1. New free play run from the game over screen goes through the character + ascension picker
rep('''$("overNewBtn").addEventListener("click",()=>{ if(!freePlayUnlocked()){ goToTitle(); return; } newRun(generateValidatedSeed(), G.character, G.ascension, "free"); });''',
'''$("overNewBtn").addEventListener("click",()=>{   // v0.51e: pick the desk and the rung again, starting from the last run's
  if(!freePlayUnlocked()){ goToTitle(); return; }
  if(CHARACTERS[G.character]) _selChar=G.character;
  _selAsc=+G.ascension||0;
  goToTitle(); startFreeFlow(null); });''')

# 2. Audio: iOS parks the context as "interrupted" (not "suspended") after the app is
#    backgrounded, so the old check never resumed it. Resume on any non-running
#    state, wake on return to the page, and rebuild the context if it will not come back.
rep('''function audio(){
  try{
    if(!audioCtx){ const AC=window.AudioContext||window.webkitAudioContext; if(AC) audioCtx=new AC(); }
    if(audioCtx && audioCtx.state==="suspended") audioCtx.resume();
  }catch(e){}
  return audioCtx;
}''', '''function audio(){
  try{
    if(!audioCtx || audioCtx.state==="closed"){ const AC=window.AudioContext||window.webkitAudioContext; if(AC) audioCtx=new AC(); }
    if(audioCtx && audioCtx.state!=="running"){ const p=audioCtx.resume(); if(p&&p.catch) p.catch(()=>{}); }
  }catch(e){}
  return audioCtx;
}
// v0.51e: called from a tap. If the context is still stuck after a resume, build a fresh one.
function audioWake(){
  try{
    if(!audioCtx){ audio(); return; }
    if(audioCtx.state==="running") return;
    const ctx=audioCtx, p=ctx.resume();
    const check=()=>{ if(ctx===audioCtx && ctx.state!=="running"){ try{ ctx.close(); }catch(e){} audioCtx=null; audio(); } };
    if(p&&p.then) p.then(()=>setTimeout(check,60),()=>check()); else setTimeout(check,60);
  }catch(e){ audioCtx=null; }
}''')
rep('''document.addEventListener("pointerdown",()=>audio(),{passive:true});''',
'''document.addEventListener("pointerdown",()=>audioWake(),{passive:true});
document.addEventListener("touchend",()=>audioWake(),{passive:true});   // iOS only unlocks audio on touchend/click
document.addEventListener("visibilitychange",()=>{ if(!document.hidden && audioCtx && audioCtx.state!=="running"){ try{ const p=audioCtx.resume(); if(p&&p.catch) p.catch(()=>{}); }catch(e){} } });''')

# 3. Gold Leaf is epic
rep('''function goldLeafOffer(){ return {kind:"Perk",rarity:"rare",name:"Gold Leaf",desc:"Solving a mystery word gilds the highest-value letter you used in it.",price:px(9),art:"🍂",d:{type:"goldLeaf"}}; }''',
'''function goldLeafOffer(){ return {kind:"Perk",rarity:"epic",name:"Gold Leaf",desc:"Solving a mystery word gilds the highest-value letter you used in it.",price:px(13),art:"🍂",d:{type:"goldLeaf"}}; }''')
rep('''  if(!G.perks.goldLeaf)          e.push({make:()=>goldLeafOffer(),    weight:1.0});''',
    '''  if(!G.perks.goldLeaf)          e.push({make:()=>goldLeafOffer(),    weight:0.75});   // v0.51e: epic''')

# 4. Softer endless walls: was 1.5 + 0.25/round (R7 x1.75, R8 x2.0, R9 x2.25 ...),
#    now R7 x1.4, R8 x1.55, R9 x1.7 ... Five endless rounds in: about x14 instead of x54.
rep('''const ENDLESS_WALL_BASE = 1.5;''', '''const ENDLESS_WALL_BASE = 1.25;   // v0.51e: was 1.5''')
rep('''const ENDLESS_WALL_STEP = 0.25;''', '''const ENDLESS_WALL_STEP = 0.15;   // v0.51e: was 0.25''')

# 5. Settings: reset progress and reset run data, each with a tap-again confirm
rep('''    <button class="menu-btn" id="optExportBtn" style="margin-top:18px">Export last run's stats</button>
    <button class="menu-btn alt" id="optBackBtn">Back</button>''',
'''    <button class="menu-btn" id="optExportBtn" style="margin-top:18px">Export last run's stats</button>
    <div class="opt-reset">
      <button class="menu-btn alt opt-danger" id="optResetProgBtn">Reset progress</button>
      <div class="opt-note">Locks every character back to A0. Your saved run and today's press are kept.</div>
      <button class="menu-btn alt opt-danger" id="optResetRunsBtn">Reset run data</button>
      <div class="opt-note">Clears the run history stored on this device. Progress is kept.</div>
    </div>
    <button class="menu-btn alt" id="optBackBtn">Back</button>''')
rep('''.win-unlock{''', '''.opt-reset{margin-top:14px;padding-top:12px;border-top:1px solid var(--tile-edge,#d8cdb6)}
.opt-reset .menu-btn{margin-top:8px}
.opt-danger{color:var(--oxblood,#9E3B2E)}
.opt-danger.arm{background:var(--oxblood,#9E3B2E);color:#fff;border-color:var(--oxblood,#9E3B2E)}
.opt-note{color:var(--ink-soft);font-size:.75rem;margin:4px 0 2px;text-align:center}
.win-unlock{''')
rep('''function closeOptions(){ $("optionsScreen").classList.add("hidden"); }''',
'''function closeOptions(){ $("optionsScreen").classList.add("hidden"); optDisarm(); }
/* v0.51e: resets. First tap arms the button, a second tap within 4s does it. */
const OPT_RESET_LABEL={optResetProgBtn:"Reset progress", optResetRunsBtn:"Reset run data"};
let _optArm=null, _optArmT=null;
function optDisarm(){ if(_optArm){ const b=$(_optArm); if(b){ b.classList.remove("arm"); b.textContent=OPT_RESET_LABEL[_optArm]; } } _optArm=null; clearTimeout(_optArmT); }
function optResetTap(id, doIt){
  if(_optArm!==id){ optDisarm(); _optArm=id; const b=$(id); b.classList.add("arm"); b.textContent="Tap again to confirm"; haptic(10);
    _optArmT=setTimeout(optDisarm,4000); return; }
  optDisarm(); doIt();
}
function resetProgress(){
  saveProgress({});   // v2 key stays present, so the old v1 migration never re-runs
  try{ localStorage.setItem(ASC_LADDER_KEY,"2"); }catch(e){}
  _selAsc=0; toast("Progress reset. Every character is back to A0."); haptic([10,30,10]);
}
function resetRunData(){
  try{ localStorage.removeItem("letterati_runs"); localStorage.removeItem("letterati_laststats"); }catch(e){}
  toast("Run history cleared from this device."); haptic([10,30,10]); openOptions();
}''')
rep('''$("fuseDone").addEventListener("click",closeFuseEditor);''', '''$("fuseDone").addEventListener("click",closeFuseEditor);
$("optResetProgBtn").addEventListener("click",()=>optResetTap("optResetProgBtn",resetProgress));
$("optResetRunsBtn").addEventListener("click",()=>optResetTap("optResetRunsBtn",resetRunData));''')

open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
