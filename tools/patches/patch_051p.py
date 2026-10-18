#!/usr/bin/env python3
"""0.51o -> 0.51p: (1) the screen fit measured scroll and box sizes, which tile springs
and lifts inflate, so the first touch shrank tiles for the round; it now sums layout
heights. (2) Less empty space: board anchored to the top, no reserved height in the
definition box, the bank reserves only the rows this round's hand needs, and each
round starts from the largest tile size that fits. usage: patch_051p.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51o"', 'gameVersion:"0.51p"')
m = re.findall(r'const VERSION *= *"0\.51o"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51o","0.51p"))

# CSS: drop the definition reservation, anchor the board to the top
rep('''body.fit-play .def-strip{min-height:146px;box-sizing:border-box}
body.fit-play.cmp1 .def-strip{min-height:135px}
body.fit-play.cmp2 .def-strip{min-height:112px}
body.fit-play.cmp3 .def-strip{min-height:90px}''',
'''/* v0.51p: the board is anchored to the top, so the definition box can change size
   (a mystery word loading in, a short definition) without moving anything above it. */
body.fit-play .play-center{justify-content:flex-start}''')

# measurement + fit
rep('''function playOverflow(){
  const se=document.scrollingElement||document.documentElement, app=$("app"), pc=document.querySelector(".play-center"), mn=$("play");
  const handBottom=$("hand").getBoundingClientRect().bottom + 6;
  return Math.max(0, app.scrollHeight - app.clientHeight, se.scrollHeight - window.innerHeight,
    handBottom - window.innerHeight, pc ? pc.scrollHeight - pc.clientHeight : 0, mn ? mn.scrollHeight - mn.clientHeight : 0); }''',
'''/* v0.51p: sum layout heights (offsetHeight), which tile springs, lifts and the screen
   shake never change. The definition box counts at least its mystery-word height, so
   a mystery loading in after the deal cannot force a mid-round squeeze. */
const DEF_ASSUME=[150,150,140,118,96];
function playOverflow(){
  const app=$("app"), hud=$("hud"), mn=$("play"), pc=document.querySelector(".play-center"), hw=document.querySelector(".hand-wrap");
  if(!mn || !pc || !hw) return 0;
  const lvl=document.body.classList.contains("cmp3")?4:document.body.classList.contains("cmp2")?3:document.body.classList.contains("cmp1")?2:0;
  const vis=[...pc.children].filter(n=>n.id==="defStrip" || n.offsetParent!==null);
  const pcs=getComputedStyle(pc), ms=getComputedStyle(mn);
  const gapPc=parseFloat(pcs.rowGap)||0, gapM=parseFloat(ms.rowGap)||0;
  const pcNeed=vis.reduce((t,n)=>t+(n.id==="defStrip" ? Math.max(n.offsetParent!==null?n.offsetHeight:0, DEF_ASSUME[lvl]) : n.offsetHeight),0) + gapPc*Math.max(0,vis.length-1);
  const mainNeed=(parseFloat(ms.paddingTop)||0) + pcNeed + gapM + hw.offsetHeight + (parseFloat(ms.paddingBottom)||0);
  const total=(hud && !hud.classList.contains("hidden") ? hud.offsetHeight : 0) + mainNeed;
  return total + 4 - (app.clientHeight || window.innerHeight);
}''')
rep('''const FIT_LEVELS=[{c:[],hand:52,canvas:54},''', '''const FIT_LEVELS=[{c:[],hand:62,canvas:64},{c:[],hand:57,canvas:59},{c:[],hand:52,canvas:54},''')
rep('''  app.style.setProperty("--hand-h", (Math.round(Math.min(L.hand, 52)*1.24)*2+8)+"px");
}''', '''}
// the bank keeps room for the rows this round's full hand needs, measured once per round
function reserveHandRows(grow){
  const h=$("hand"), th=parseFloat(getComputedStyle(h).getPropertyValue("--th"))||62;
  const rows=h.classList.contains("tworow")?2:1, need=rows*th + (rows-1)*6 + 4;
  const cur=parseFloat($("app").style.getPropertyValue("--hand-h"))||0;
  if(!grow || need>cur) $("app").style.setProperty("--hand-h", need+"px");
}''')
rep('''  if(force || key!==_fitKey){ _fitKey=key; _fitLevel = window.innerHeight<720 ? 1 : 0; }   // short screens start tight, so the round never has to tighten mid-play
  applyFitLevel(_fitLevel); fitHand(); fitCanvas();
  while(playOverflow()>1 && _fitLevel<FIT_LEVELS.length-1){ _fitLevel++; applyFitLevel(_fitLevel); fitHand(); fitCanvas(); }
  markClamped();''', '''  const fresh = force || key!==_fitKey;
  if(fresh){ _fitKey=key; _fitLevel=0; $("app").style.removeProperty("--hand-h"); }   // each round starts from the largest size
  applyFitLevel(_fitLevel); fitHand(); fitCanvas();
  if(fresh) reserveHandRows(false);
  while(playOverflow()>0 && _fitLevel<FIT_LEVELS.length-1){ _fitLevel++; applyFitLevel(_fitLevel); fitHand(); fitCanvas(); reserveHandRows(false); }
  if(!fresh) reserveHandRows(true);
  markClamped();''')
rep('''body.fit-play .hand{min-height:var(--hand-h,78px)}''', '''body.fit-play .hand{min-height:var(--hand-h,60px)}''')
rep('''const HAND_FIT={min:30,max:52,''', '''const HAND_FIT={min:30,max:64,''')
rep('''const CANVAS_FIT={min:22,max:54,''', '''const CANVAS_FIT={min:22,max:66,''')
rep('''let _fitCap={hand:52, canvas:54};''', '''let _fitCap={hand:52, canvas:54};
// v0.51p: leftover height is shared out evenly between the board's sections once per round
function spreadSlack(){
  const app=$("app"); app.style.removeProperty("--pc-gap"); app.style.removeProperty("--pc-pad");
  const slack=-playOverflow(); if(slack<=8) return;
  const pc=document.querySelector(".play-center"); const n=[...pc.children].filter(x=>x.offsetParent!==null).length;
  const base=parseFloat(getComputedStyle(pc).rowGap)||10, use=slack*0.7, per=Math.min(28, use/(n+1));
  app.style.setProperty("--pc-gap", (base+per)+"px"); app.style.setProperty("--pc-pad", per+"px");
}''')
rep('''body.fit-play .play-center{justify-content:flex-start}''', '''body.fit-play .play-center{justify-content:flex-start;gap:var(--pc-gap,10px);padding-top:var(--pc-pad,0px)}''')
rep('''  if(!fresh) reserveHandRows(true);
  markClamped();''', '''  if(!fresh) reserveHandRows(true);
  if(fresh) spreadSlack();
  markClamped();''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
