#!/usr/bin/env python3
"""0.51n -> 0.51o: no layout judder while placing tiles (fixed row heights, top-anchored
play area, synchronous one-way screen fit); portrait only (orientation lock where the
browser allows it, a turn-upright screen where it does not). usage: patch_051o.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51n"', 'gameVersion:"0.51o"')
m = re.findall(r'const VERSION *= *"0\.51n"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51n","0.51o"))

# ---- stable geometry
rep('''body.fit-play main{min-height:0}''', '''body.fit-play main{min-height:0}
/* v0.51o: nothing above the word bank moves while tiles come and go. The play
   area is anchored to the top, the canvas row keeps one height for the round,
   and the score line under it always has room for two lines. */
body.fit-play .hand{align-items:flex-start;align-content:flex-start}   /* a one-row bank sits right under the toolbar */
/* the definition box keeps its full mystery-word height, so the mystery loading in
   (or a short definition replacing a long one) never shifts the board */
body.fit-play .def-strip{min-height:146px;box-sizing:border-box}
body.fit-play.cmp1 .def-strip{min-height:135px}
body.fit-play.cmp2 .def-strip{min-height:112px}
body.fit-play.cmp3 .def-strip{min-height:90px}
body.fit-play .canvas{min-height:var(--canvas-row-h,68px)}
body.fit-play .canvas-foot{min-height:44px;align-items:flex-start}
body.fit-play .hand{min-height:var(--hand-h,78px)}''')

# ---- synchronous, one-way fit
rep('''function fitScreen(){
  const playing=!$("play").classList.contains("hidden");
  document.body.classList.toggle("fit-play", playing);
  if(!playing){ document.body.classList.remove("cmp1","cmp2","cmp3"); return; }
  document.body.classList.remove("cmp1","cmp2","cmp3"); _fitCap={hand:52, canvas:54};
  fitHand(); fitCanvas();
  const steps=[()=>document.body.classList.add("cmp1"), ()=>document.body.classList.add("cmp2"),
    ()=>{ document.body.classList.add("cmp3"); _fitCap={hand:46, canvas:48}; },
    ()=>{ _fitCap={hand:42, canvas:44}; }, ()=>{ _fitCap={hand:38, canvas:40}; }, ()=>{ _fitCap={hand:34, canvas:36}; }];
  for(const st of steps){ if(playOverflow()<=1) break; st(); fitHand(); fitCanvas(); }
  markClamped();
}''', '''/* v0.51o: the fit only ever tightens within a round, and runs in the same frame as
   the change that caused it, so the screen never shows an in-between layout. It
   starts fresh on a new round, a new hand size or a resize. */
const FIT_LEVELS=[{c:[],hand:52,canvas:54},{c:["cmp1"],hand:52,canvas:54},{c:["cmp1","cmp2"],hand:52,canvas:54},
  {c:["cmp1","cmp2","cmp3"],hand:46,canvas:48},{c:["cmp1","cmp2","cmp3"],hand:42,canvas:44},
  {c:["cmp1","cmp2","cmp3"],hand:38,canvas:40},{c:["cmp1","cmp2","cmp3"],hand:34,canvas:36}];
let _fitLevel=0, _fitKey="";
function applyFitLevel(i){
  const L=FIT_LEVELS[i]; ["cmp1","cmp2","cmp3"].forEach(c=>{ const on=L.c.includes(c); if(document.body.classList.contains(c)!==on) document.body.classList.toggle(c,on); });
  _fitCap={hand:L.hand, canvas:L.canvas};
  const app=$("app"); app.style.setProperty("--canvas-row-h", (Math.round(L.canvas*1.24)+4)+"px");
  app.style.setProperty("--hand-h", (Math.round(Math.min(L.hand, 52)*1.24)*2+8)+"px");
}
function fitScreen(force){
  const playing=!$("play").classList.contains("hidden");
  if(document.body.classList.contains("fit-play")!==playing) document.body.classList.toggle("fit-play", playing);
  if(!playing){ ["cmp1","cmp2","cmp3"].forEach(c=>document.body.classList.remove(c)); return; }
  const key=(G.level||0)+":"+(G.attempt||0)+":"+(G.handSize||0)+":"+window.innerWidth+"x"+window.innerHeight;
  if(force || key!==_fitKey){ _fitKey=key; _fitLevel = window.innerHeight<720 ? 1 : 0; }   // short screens start tight, so the round never has to tighten mid-play
  applyFitLevel(_fitLevel); fitHand(); fitCanvas();
  while(playOverflow()>1 && _fitLevel<FIT_LEVELS.length-1){ _fitLevel++; applyFitLevel(_fitLevel); fitHand(); fitCanvas(); }
  markClamped();
}''')
# run the fit in the same frame as hand / canvas renders
rep('''  G.hand.forEach(c=>{ el.appendChild(buildTile(c,"hand")); });
  fitHand();''', '''  G.hand.forEach(c=>{ el.appendChild(buildTile(c,"hand")); });
  fitHand(); if(document.body.classList.contains("fit-play")) fitScreen();   // v0.51o: same frame, no in-between layout''')
rep('''  fitCanvas();
  updateLive();''', '''  fitCanvas();
  updateLive();
  if(document.body.classList.contains("fit-play")) fitScreen();   // v0.51o''')
rep('''  ["hand","canvas"].forEach(id=>{ const n=$(id); if(n) mo.observe(n,{childList:true}); });   // the fit itself only touches styles and classes here''',
    '''  // v0.51o: hand and canvas fit synchronously in their render functions''')
rep('''window.addEventListener("resize",()=>{ if(!$("play").classList.contains("hidden")){ fitHand(); fitCanvas(); scheduleFitScreen(); } });''',
    '''window.addEventListener("resize",()=>{ if(!$("play").classList.contains("hidden")){ fitScreen(true); } });''')

# ---- portrait only
rep('''<!-- ===== Title ===== -->''', '''<div id="rotateNote" aria-live="polite"><div class="rn-ico">📱</div><div class="rn-t">Turn your phone upright</div><div class="rn-s">Letterati plays in portrait.</div></div>
<!-- ===== Title ===== -->''')
rep('''body.fit-play{overflow:hidden}''', '''body.fit-play{overflow:hidden}
/* v0.51o: portrait only. Browsers that allow it get an orientation lock; on the
   rest (iPhone Safari among them) a phone held sideways sees this instead. */
#rotateNote{display:none}
@media (orientation:landscape) and (max-height:540px) and (pointer:coarse){
  #rotateNote{display:flex;position:fixed;inset:0;z-index:9999;flex-direction:column;align-items:center;justify-content:center;gap:8px;
    background:var(--page);color:var(--ink);text-align:center;padding:20px}
  #rotateNote .rn-ico{font-size:2.6rem;transform:rotate(-90deg)}
  #rotateNote .rn-t{font-family:var(--serif);font-weight:800;font-size:1.4rem}
  #rotateNote .rn-s{font-size:.9rem;color:var(--ink-soft)}
  #app,.overlay{visibility:hidden}
}''')
rep('''$("dpClose").addEventListener("click",()=>$("defPop").classList.add("hidden"));''',
'''$("dpClose").addEventListener("click",()=>$("defPop").classList.add("hidden"));
// v0.51o: ask for a portrait lock where the browser supports it (installed apps on Android); iPhone Safari declines quietly
function lockPortrait(){ try{ if(screen.orientation && screen.orientation.lock){ const p=screen.orientation.lock("portrait"); if(p&&p.catch) p.catch(()=>{}); } }catch(e){} }
lockPortrait(); document.addEventListener("pointerdown",lockPortrait,{once:true,passive:true});''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
