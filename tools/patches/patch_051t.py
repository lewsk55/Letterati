#!/usr/bin/env python3
"""0.51s -> 0.51t: every desk plays to the same targets. The old target premiums
(Detective +10%, Editor +20%, Scholar +100%, Short King's 1.15 / 1.1 / 1.0 curve) move
into each desk's letter values as a built-in scoring scale, so a score of 400 means the
same on any desk and the tally never shows a separate cut. Ascension still raises
targets. Runs saved before 0.51t are rescaled on load so a round in progress stays fair.
Live only: the pinned predictor works at the A0 Writer baseline and is untouched.
usage: patch_051t.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51s"', 'gameVersion:"0.51t"')
m = re.findall(r'const VERSION *= *"0\.51s"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51s","0.51t"))

# ---------- character data: targets to 1, premium becomes a scoring scale ----------
rep('''    targetMult:1.10, hearts:3, unlimitedMystery:true''',
    '''    targetMult:1, scoreScale:1/1.10, hearts:3, unlimitedMystery:true   // v0.51t: was targetMult 1.10''')
rep('''    bane:"Targets are 20 percent higher and you have one fewer discard. No word may be set twice running.",
    targetMult:1.20, hearts:3,''',
    '''    bane:"One fewer discard. No word may be set twice running.",
    /* v0.51t: was targetMult 1.20 */ targetMult:1, scoreScale:1/1.20, hearts:3,''')
rep('''  bane:"No word longer than 5 letters. Higher targets. A 2-letter word played again this run scores ×0.6, then ×0.3.",''',
    '''  bane:"No word longer than 5 letters. A 2-letter word played again this run scores ×0.6, then ×0.3.",''')
rep('''  targetCurve:[1.15,  1.15,  1.15,  1.15,  1.1,  1.0],   // v0.51i (was 1.3 x4, 1.25, 1.15)''',
    '''  scoreCurve:[1/1.15, 1/1.15, 1/1.15, 1/1.15, 1/1.1, 1],   // v0.51t: was targetCurve 1.15 x4, 1.1, 1.0 (v0.51i)''')
rep('''  bane:"Three words a round and higher targets. Words under 5 letters score face value, with no multipliers.",
  targetMult:2.0, hearts:3,''',
    '''  bane:"Three words a round. Words under 5 letters score face value, with no multipliers.",
  /* v0.51t: was targetMult 2.0 */ targetMult:1, scoreScale:0.5, hearts:3,''')

# the scale itself, next to runTargetMult
rep('''function runTargetMult(){''',
'''/* v0.51t: each desk's built-in scoring scale. It used to be a target premium; carrying
   it in the letter values instead keeps every desk's scores and targets on one scale. */
function charScoreScale(){
  const d=charDef(); let k=(typeof d.scoreScale==="number") ? d.scoreScale : 1;
  const c=d.scoreCurve; if(c) k*=(c[Math.min(G.level||1, c.length)-1]||1);
  return k;
}
function runTargetMult(){''')

# bake it into each letter's base value
rep('''    let v=r.value;
''', '''    let v=r.value*charScoreScale();   // v0.51t: the desk's scoring scale, built into letter values
''')

# a run saved before 0.51t: bring its target and scores onto the new scale
rep('''  G.score=d.score||0; G.handsLeft=d.handsLeft||0; G.discardsLeft=d.discardsLeft||0;''',
'''  G.score=d.score||0; G.handsLeft=d.handsLeft||0; G.discardsLeft=d.discardsLeft||0;
  if(!d.scoreScaleV){   // v0.51t: older saves carry the old target premium
    const k=charScoreScale();
    if(k!==1){ G.target=Math.round(G.target*k); G.score=Math.round(G.score*k); G.runScore=Math.round((G.runScore||0)*k); }
  }''')
rep('''attempt:G.attempt, target:G.target, score:G.score,''',
    '''attempt:G.attempt, target:G.target, score:G.score, scoreScaleV:1,''')


# ---------- Options: clear the local leaderboard ----------
rep('''      <button class="menu-btn alt opt-danger" id="optResetRunsBtn">Reset run data</button>''',
'''      <button class="menu-btn alt opt-danger" id="optClearLbBtn">Clear leaderboard</button>
      <div class="opt-note">Empties "Your best runs". Run history and progress are kept.</div>
      <button class="menu-btn alt opt-danger" id="optResetRunsBtn">Reset run data</button>''')
rep('''const OPT_RESET_LABEL={optResetProgBtn:"Reset progress", optResetRunsBtn:"Reset run data"};''',
'''const OPT_RESET_LABEL={optResetProgBtn:"Reset progress", optResetRunsBtn:"Reset run data", optClearLbBtn:"Clear leaderboard"};
/* v0.51t: clearing the board keeps the run history (for export and balance) and only
   hides runs that started before the clear. */
const LB_CLEAR_KEY="letterati_lb_cleared";
function lbClearedAt(){ try{ return localStorage.getItem(LB_CLEAR_KEY)||""; }catch(e){ return ""; } }
function clearLeaderboard(){
  try{ localStorage.setItem(LB_CLEAR_KEY, new Date().toISOString()); }catch(e){}
  renderLeaderboard(); toast("Leaderboard cleared"); haptic([10,30,10]);
}''')
rep('''  const top=runs.filter(r=>(r&&r.runScore||0)>0)''',
'''  const cut=lbClearedAt();   // v0.51t: runs from before a clear stay off the board
  const top=runs.filter(r=>(r&&r.runScore||0)>0 && (!cut || (r.startedAt||"")>cut))''')
rep('''$("optResetRunsBtn").addEventListener("click",()=>optResetTap("optResetRunsBtn",resetRunData));''',
'''$("optResetRunsBtn").addEventListener("click",()=>optResetTap("optResetRunsBtn",resetRunData));
$("optClearLbBtn").addEventListener("click",()=>optResetTap("optClearLbBtn",clearLeaderboard));   // v0.51t''')

open(OUT, "w", encoding="utf-8").write(s)
print("wrote", OUT)
