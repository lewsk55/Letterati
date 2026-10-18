#!/usr/bin/env python3
"""0.51m -> 0.51n: layout pass. Tiles sized in letter units (fused tiles slimmer),
canvas always one line, word bank at most two lines, compact HUD, definitions clamp
to two lines with a tap-for-full popup, and the play screen fits without scrolling.
usage: patch_051n.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51m"', 'gameVersion:"0.51n"')
m = re.findall(r'const VERSION *= *"0\.51m"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51m","0.51n"))

# ---------------------------------------------------------------- tile fitting in letter units
rep('''function slotCount(arr){ return arr.reduce((n,c)=>n+(c.kind==="fused"?2:(c.kind==="trio"?3:1)),0); }   // fused dominoes are double-width, trios triple (v492e)
function fitHand(){
  const eff=slotCount(G.hand), el=$("hand");
  const two = eff>10;                     // past 10 slots, spill into a second row below
  el.classList.toggle("tworow", two);
  const perRow = two ? Math.ceil(eff/2) : eff;
  fitRow(el, perRow, {min:30,max:50,ratio:1.24,fsDiv:29,gap:6});
}
function fitCanvas(){ fitRow($("canvas"),slotCount(G.canvas),{min:24,max:54,ratio:1.24,fsDiv:29,gap:7}); }''',
'''function slotCount(arr){ return arr.reduce((n,c)=>n+(c.kind==="fused"?2:(c.kind==="trio"?3:1)),0); }   // fused dominoes are double-width, trios triple (v492e)
/* v0.51n: every tile is sized in letter units. A two-letter tile is 1.7 letters
   wide, a three-letter tile 2.3 (tighter than before). On the canvas a tile with
   letters switched off narrows further, since off letters shrink to a subscript. */
const TU={pair:1.7, trio:2.3, offStrip:0.32};
function tileUnits(c, where){
  if(!c) return 1;
  let n=0, on=0;
  if(c.kind==="fused"){ n=2; const m=fusedMode(c); on=(m===0||m===1)?1:2; }
  else if(c.kind==="trio"){ n=3; on=trioActive(c).filter(a=>a!==false).length; }
  else if(c.kind==="combo"){ n=comboBase(c).length; on=comboActive(c).filter(a=>a!==false).length; }
  else return 1;
  if(where==="canvas" && on<n) return (on===1?1.08:1.75) + (n-on)*TU.offStrip;
  return n>=3 ? TU.trio : TU.pair;
}
// Largest tile width that packs the units into maxRows greedy rows (browser flex-wrap packs the same way).
function packWidth(units, avail, maxRows, o){
  for(let w=o.max; w>=o.min; w--){
    for(const gap of [o.gap, Math.max(3,o.gap-3)]){
      let rows=1, x=0;
      for(const u of units){ const tw=Math.ceil(u*w); const need=(x?gap:0)+tw;
        if(x && x+need>avail){ rows++; x=tw; } else x+=need; if(tw>avail){ rows=99; break; } }
      if(rows<=maxRows) return {w,gap,rows};
    }
  }
  return null;
}
function fitUnits(el, arr, where, maxRows, o){
  const tiles=[...el.children].filter(t=>t.classList.contains("tile"));
  if(!tiles.length){ el.style.removeProperty("--tw"); el.style.removeProperty("--th"); el.style.removeProperty("--tfs"); el.style.setProperty("--tgap",o.gap+"px"); el.classList.remove("tworow"); return; }
  const byId=new Map(arr.map(c=>[String(c.id),c]));
  const units=tiles.map(t=>tileUnits(byId.get(t.dataset.id), where));
  const cs=getComputedStyle(el);
  const avail=el.clientWidth-(parseFloat(cs.paddingLeft)||0)-(parseFloat(cs.paddingRight)||0)-6;
  if(avail<=0) return;
  let fit=null;
  for(let r=1;r<=maxRows && !fit;r++){
    const f=packWidth(units, avail, r, o);
    if(f && (r===maxRows || f.w>=o.oneRowMin)) fit=f;   // stay on one row while tiles stay a comfortable size
  }
  if(!fit) fit=packWidth(units, avail, maxRows, Object.assign({},o,{min:12})) || {w:12,gap:2,rows:maxRows};
  const w=fit.w, h=Math.round(w*o.ratio);
  el.style.setProperty("--tw",w+"px"); el.style.setProperty("--th",h+"px");
  el.style.setProperty("--tfs",(w/o.fsDiv).toFixed(2)+"rem"); el.style.setProperty("--tgap",fit.gap+"px");
  el.classList.toggle("tworow", fit.rows>1);
  tiles.forEach((t,i)=>{ if(units[i]!==1) t.style.width=Math.ceil(units[i]*w)+"px"; else t.style.removeProperty("width"); });
}
const HAND_FIT={min:30,max:52,oneRowMin:34,ratio:1.24,fsDiv:29,gap:6};
const CANVAS_FIT={min:22,max:54,oneRowMin:0,ratio:1.24,fsDiv:29,gap:7};
function fitHand(){ fitUnits($("hand"), G.hand, "hand", 2, Object.assign({},HAND_FIT,{max:Math.min(HAND_FIT.max, _fitCap.hand)})); }
function fitCanvas(){ fitUnits($("canvas"), G.canvas, "canvas", 1, Object.assign({},CANVAS_FIT,{max:Math.min(CANVAS_FIT.max, _fitCap.canvas)})); }
let _fitCap={hand:52, canvas:54};''')

# ---------------------------------------------------------------- CSS: compact HUD, clamp, compaction levels
rep('''.hud-center{display:flex;flex-direction:column;align-items:center;gap:3px;justify-self:center}''',
    '''.hud-center{display:flex;flex-direction:row;align-items:baseline;gap:12px;justify-self:center}   /* v0.51n: round and coins on one line */''')
rep('''.progress-wrap{margin-top:9px}''', '''.progress-wrap{margin-top:5px}
.progress-meta{padding-left:50px}   /* v0.51n: clear the menu button now that the score sits higher */''')
rep('''.progress-meta .target{color:var(--ink-soft);font-weight:800;display:flex;flex-direction:column;align-items:flex-end;line-height:1.15;text-align:right}''',
    '''.progress-meta .target{color:var(--ink-soft);font-weight:800;display:flex;flex-direction:row;align-items:baseline;gap:6px;line-height:1.15;text-align:right}   /* v0.51n: one line */''')
rep('''.progress-meta .target .to-go{font-size:.6rem;font-weight:800;letter-spacing:.02em;color:var(--ink-soft);text-transform:uppercase;margin-top:1px}''',
    '''.progress-meta .target .to-go{font-size:.6rem;font-weight:800;letter-spacing:.02em;color:var(--ink-soft);text-transform:uppercase;margin-top:1px}
.progress-meta .target .to-go::before{content:"· ";opacity:.6}''')
rep('''.def-strip .dd{display:block;font-size:.82rem;color:var(--ink-soft);margin-top:3px;line-height:1.4}''',
    '''.def-strip .dd{display:block;font-size:.82rem;color:var(--ink-soft);margin-top:3px;line-height:1.4}
/* v0.51n: long definitions stop at two lines; a tap opens the full text */
.def-strip .dd{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden}
.def-strip .dd.clamped{cursor:pointer}
.def-strip .dd-more{display:inline-block;margin-top:2px;font-size:.62rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--brass-deep);cursor:pointer}
#defPop .sheet{max-width:420px}
#defPop .dp-word{font-family:var(--serif);font-weight:800;font-size:1.3rem;text-transform:uppercase;letter-spacing:.06em;color:var(--ink);text-align:center}
#defPop .dp-pos{font-family:var(--serif);font-style:italic;color:var(--brass-deep);text-align:center;margin-top:2px}
#defPop .dp-def{font-size:.95rem;line-height:1.5;color:var(--ink);margin:12px 0 4px;text-align:left}
/* v0.51n: the play screen fits the viewport; levels tighten spacing when it would not */
body.fit-play{overflow:hidden}
body.fit-play #app{height:100vh;height:100dvh;min-height:0}
body.fit-play main{min-height:0}
body.cmp1 main{padding-top:8px;gap:6px}
body.cmp1 .play-center{gap:6px}
body.cmp1 .eyebrow{display:none}
body.cmp1 .canvas-wrap{padding:9px 10px 8px}
body.cmp1 .canvas-foot{margin-top:6px}
body.cmp1 .def-strip{padding:6px 11px}
body.cmp1 #hud{padding-bottom:6px}
body.cmp1 .hand-wrap{padding-top:4px}
body.cmp2 .def-strip .dd{-webkit-line-clamp:1}
body.cmp2 .def-strip .dmy{margin-top:3px}
body.cmp2 #chalBanner .cb-desc{font-size:.6rem}
body.cmp2 #sideJob{margin-top:3px}
body.cmp2 .actions .btn{padding-top:9px;padding-bottom:9px}
body.cmp3 .def-strip .dmy{display:none}
body.cmp3 .hand-meta .icon-btn{padding-top:5px;padding-bottom:5px}''')
# kill fixed widths that would fight the inline unit widths
rep('''.tile.combo.domino.c2{width:calc(var(--tw,40px)*2 + var(--tgap,7px))}''', '''.tile.combo.domino.c2{width:calc(var(--tw,40px)*1.7)}''')
rep('''.tile.combo.domino.c3{width:calc(var(--tw,40px)*2.6 + var(--tgap,7px)*2)}''', '''.tile.combo.domino.c3{width:calc(var(--tw,40px)*2.3)}''')
rep('''.tile.fused.domino{width:calc(var(--tw,40px)*2 + var(--tgap,7px))}''', '''.tile.fused.domino{width:calc(var(--tw,40px)*1.7)}   /* v0.51n: tighter; inline width from fitUnits wins */''')
rep('''.tile.trio.domino{width:calc(var(--tw,40px)*2.6 + var(--tgap,7px)*2)}''', '''.tile.trio.domino{width:calc(var(--tw,40px)*2.3)}''')

# ---------------------------------------------------------------- definition popup markup
rep('''<!-- ===== Title ===== -->''', '''<div class="overlay hidden" id="defPop">
  <div class="sheet sheet-center">
    <div class="dp-word" id="dpWord"></div>
    <div class="dp-pos" id="dpPos"></div>
    <div class="dp-def" id="dpDef"></div>
    <div class="post-actions"><button class="menu-btn" id="dpClose" style="max-width:160px">Close</button></div>
  </div>
</div>
<!-- ===== Title ===== -->''')

# ---------------------------------------------------------------- screen fit + clamp detection
rep('''window.addEventListener("resize",()=>{ if(!$("play").classList.contains("hidden")){ fitHand(); fitCanvas(); } });''',
'''window.addEventListener("resize",()=>{ if(!$("play").classList.contains("hidden")){ fitHand(); fitCanvas(); scheduleFitScreen(); } });
/* v0.51n: keep the play screen on one screen. Tighten in steps until nothing
   overflows: spacing, then shorter definition, then smaller tiles. */
let _fitQueued=false;
function scheduleFitScreen(){ if(_fitQueued) return; _fitQueued=true; requestAnimationFrame(()=>{ _fitQueued=false; fitScreen(); }); }
function playOverflow(){
  const se=document.scrollingElement||document.documentElement, app=$("app"), pc=document.querySelector(".play-center"), mn=$("play");
  const handBottom=$("hand").getBoundingClientRect().bottom + 6;
  return Math.max(0, app.scrollHeight - app.clientHeight, se.scrollHeight - window.innerHeight,
    handBottom - window.innerHeight, pc ? pc.scrollHeight - pc.clientHeight : 0, mn ? mn.scrollHeight - mn.clientHeight : 0); }
function fitScreen(){
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
}
function markClamped(){
  const dd=document.querySelector("#defStrip .dd"); if(!dd) return;
  const strip=$("defStrip"); const old=strip.querySelector(".dd-more");
  const cut = dd.scrollHeight > dd.clientHeight + 2;
  if(dd.classList.contains("clamped")!==cut) dd.classList.toggle("clamped", cut);
  if(cut && !old){ const mo=document.createElement("span"); mo.className="dd-more"; mo.textContent="Tap for the full definition"; dd.insertAdjacentElement("afterend", mo); }
  if(!cut && old) old.remove();
}
function openDefPop(){
  const strip=$("defStrip"); const dd=strip.querySelector(".dd"); if(!dd) return;
  const w=strip.querySelector(".dw"), p=strip.querySelector(".dpos");
  $("dpWord").textContent = w ? w.textContent : "";
  $("dpPos").textContent = p ? p.textContent : "";
  $("dpDef").textContent = dd.textContent;
  $("defPop").classList.remove("hidden"); haptic(8);
}
$("defStrip").addEventListener("click",e=>{
  const t=e.target; if(!t || !t.closest) return;
  if(t.closest(".dd-more") || (t.closest(".dd") && t.closest(".dd").classList.contains("clamped"))){ e.stopPropagation(); e.preventDefault(); openDefPop(); }
}, true);
$("dpClose").addEventListener("click",()=>$("defPop").classList.add("hidden"));
$("defPop").addEventListener("click",e=>{ if(e.target.id==="defPop") $("defPop").classList.add("hidden"); });
{ const mo=new MutationObserver(()=>scheduleFitScreen());
  ["hand","canvas"].forEach(id=>{ const n=$(id); if(n) mo.observe(n,{childList:true}); });   // the fit itself only touches styles and classes here
  ["chalBanner","sideJob","postActions","proofRow","wordTally","play","hud"].forEach(id=>{ const n=$(id); if(n) mo.observe(n,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:["class"]}); });
  const ds=$("defStrip"); if(ds) new MutationObserver(recs=>{ if(recs.some(r=>!(r.target.classList&&(r.target.classList.contains("dd")||r.target.classList.contains("dd-more"))) && ![...r.addedNodes,...r.removedNodes].every(n=>n.classList&&n.classList.contains("dd-more")))) scheduleFitScreen(); })
    .observe(ds,{childList:true,subtree:true,attributes:true,attributeFilter:["class"]}); }''')
rep('''@media (max-width:380px){
  .tile{width:44px;height:56px;font-size:1.5rem}''', '''@media (max-width:380px){   /* v0.51n: tile size comes from fitUnits on every width */''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
