#!/usr/bin/env python3
"""0.51c add-on: press-and-hold editor for fused pairs and trios.
Replaces the old pick-on-drop and tap-on-canvas selectors.
usage: patch_fuse.py in.html out.html"""
import sys
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)

# ---------------------------------------------------------------- overlay markup
rep('''<div class="overlay hidden" id="fusedPick">''', '''<div class="overlay hidden" id="fuseEdit">
  <div class="clone-sheet">
    <div class="clone-title">Arrange the letters</div>
    <div class="clone-sub">Tap a letter to turn it off or on. Drag a letter to move it.</div>
    <div class="fe-row" id="fuseChips"></div>
    <div class="fe-read" id="fuseRead"></div>
    <div class="post-actions">
      <button class="menu-btn" id="fuseDone" style="max-width:160px">Done</button>
    </div>
  </div>
</div>
<div class="overlay hidden" id="fusedPick">''')
# ---------------------------------------------------------------- styles
rep('''.tile.lucky7 .glyph{font-size:1.25em}''', '''.tile.lucky7 .glyph{font-size:1.25em}
.tile.fused,.tile.trio{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}
.tile.fe-holding{transform:scale(1.08);transition:transform .35s ease}
.fe-row{display:flex;justify-content:center;gap:10px;margin:14px 0 6px;touch-action:none;min-height:78px}
.fe-chip{position:relative;width:58px;height:70px;border-radius:10px;border:1px solid var(--tile-edge);background:linear-gradient(180deg,#FCF8EE,var(--tile));
  display:flex;align-items:center;justify-content:center;font-family:var(--display,Georgia,serif);font-size:1.9rem;font-weight:700;color:var(--ink);
  box-shadow:0 3px 0 var(--tile-edge);cursor:grab;touch-action:none;-webkit-user-select:none;user-select:none;transition:opacity .15s ease,transform .15s ease}
.fe-chip .fe-v{position:absolute;right:6px;bottom:4px;font-family:var(--ui);font-size:.7rem;font-weight:700;color:var(--ink-soft,#7a6f5a)}
.fe-chip.off{opacity:.38;box-shadow:none;text-decoration:line-through}
.fe-chip.dragging{z-index:5;transition:none;box-shadow:0 10px 18px rgba(0,0,0,.25);cursor:grabbing}
.fe-read{text-align:center;font-family:var(--ui);font-size:.85rem;color:var(--ink-soft,#7a6f5a);min-height:20px}''')

# ---------------------------------------------------------------- the editor
rep('''function closeFusedSelector(){ fusedSelCard=null; $("fusedPick").classList.add("hidden"); }''',
'''function closeFusedSelector(){ fusedSelCard=null; $("fusedPick").classList.add("hidden"); }
/* v0.51c fuse editor: press and hold a fused pair or trio, in the word bank or on
   the canvas. Tap a letter to turn it off or on (one always stays on); drag a
   letter to move it. Every change lands on the tile at once. */
let FE=null;   // {card, letters:[{L,v}], order:[idx], active:[bool]}
function feFromCard(c){
  if(c.kind==="fused"){
    const m=fusedMode(c), L=c.sides.map(sd=>({L:sd.letter, v:fusedSideValue(sd)}));
    if(m===0) return {letters:L, order:[0,1], active:[true,false]};
    if(m===1) return {letters:L, order:[0,1], active:[false,true]};
    if(m===3) return {letters:L, order:[1,0], active:[true,true]};
    return {letters:L, order:[0,1], active:[true,true]};
  }
  const ord=Array.isArray(c.order)?c.order.slice():[0,1,2];
  return {letters:c.letters.map(x=>({L:x, v:trioSideValue(c,x)})), order:ord, active:trioActive(c).map(a=>a!==false)};
}
function feApply(){
  const c=FE.card, on=FE.order.filter(i=>FE.active[i]);
  if(c.kind==="fused"){ c.mode = on.length===2 ? (on[0]===0?2:3) : on[0]; }
  else { c.order=[...on, ...FE.order.filter(i=>!FE.active[i])]; c.active=FE.active.slice(); delete c.flipped; }
  renderHand(); renderCanvas(); save();
}
function feRender(){
  const row=$("fuseChips"); row.innerHTML="";
  FE.order.forEach((idx,pos)=>{
    const x=FE.letters[idx], b=document.createElement("div");
    b.className="fe-chip"+(FE.active[idx]?"":" off"); b.dataset.idx=idx;
    b.innerHTML=x.L+'<span class="fe-v">'+x.v+'</span>';
    b.addEventListener("pointerdown",e=>feDown(e,b,idx));
    row.appendChild(b);
  });
  const word=FE.order.filter(i=>FE.active[i]).map(i=>FE.letters[i].L).join("");
  const pts=FE.order.filter(i=>FE.active[i]).reduce((sm,i)=>sm+FE.letters[i].v,0);
  $("fuseRead").textContent="Plays as "+word+" · "+pts+" pts";
}
function feDown(e,chip,idx){
  e.preventDefault();
  const row=$("fuseChips"), x0=e.clientX; let moved=false;
  try{ chip.setPointerCapture(e.pointerId); }catch(_){}
  const move=ev=>{
    const dx=ev.clientX-x0;
    if(!moved && Math.abs(dx)>6){ moved=true; chip.classList.add("dragging"); }
    if(moved) chip.style.transform="translateX("+dx+"px) scale(1.06)";
  };
  const up=ev=>{
    chip.removeEventListener("pointermove",move); chip.removeEventListener("pointerup",up); chip.removeEventListener("pointercancel",up);
    if(!moved){
      const onCount=FE.active.filter(Boolean).length;
      if(FE.active[idx] && onCount<=1){ toast("At least one letter stays on"); return; }
      FE.active[idx]=!FE.active[idx]; haptic(8);
    } else {
      const others=[...row.children].filter(n=>n!==chip);
      let to=0; others.forEach(n=>{ const r=n.getBoundingClientRect(); if(ev.clientX>r.left+r.width/2) to++; });
      const from=FE.order.indexOf(idx); FE.order.splice(from,1); FE.order.splice(to,0,idx); haptic(10);
    }
    feApply(); feRender();
  };
  chip.addEventListener("pointermove",move); chip.addEventListener("pointerup",up); chip.addEventListener("pointercancel",up);
}
function openFuseEditor(c){
  if(!c || (c.kind!=="fused" && c.kind!=="trio")) return;
  FE=Object.assign({card:c}, feFromCard(c));
  feRender();
  $("fuseEdit").classList.remove("hidden");
  haptic([10,30,10]);
}
function closeFuseEditor(){ FE=null; $("fuseEdit").classList.add("hidden"); }
const FUSE_HOLD_MS=420;''')
rep('''$("fusedPickCancel").addEventListener("click",closeFusedSelector);''',
    '''$("fusedPickCancel").addEventListener("click",closeFusedSelector);
$("fuseDone").addEventListener("click",closeFuseEditor);
$("fuseEdit").addEventListener("click",e=>{ if(e.target.id==="fuseEdit") closeFuseEditor(); });''')

# ---------------------------------------------------------------- press and hold on the tile
rep('''function onTileDown(e,el,card,where){
  if(e.pointerType==="mouse"&&e.button!==0) return;
  haptic(8);
  drag={el,card,where,startX:e.clientX,startY:e.clientY,moved:false,clone:null,hover:null};''',
'''function onTileDown(e,el,card,where){
  if(e.pointerType==="mouse"&&e.button!==0) return;
  haptic(8);
  drag={el,card,where,startX:e.clientX,startY:e.clientY,moved:false,clone:null,hover:null};
  if(card && (card.kind==="fused" || card.kind==="trio")){   // v0.51c: hold to open the fuse editor
    el.classList.add("fe-holding");
    drag.hold=setTimeout(()=>{
      if(!drag || drag.card!==card || drag.moved) return;
      el.classList.remove("fe-holding");
      document.removeEventListener("pointermove",onTileMove);
      document.removeEventListener("pointerup",onTileUp);
      document.removeEventListener("pointercancel",onTileUp);
      drag=null; justDragged=true; setTimeout(()=>justDragged=false,350);   // swallow the click that follows the release
      openFuseEditor(card);
    }, FUSE_HOLD_MS);
  }''')
rep('''  if(!drag.moved && Math.hypot(dx,dy)>DRAG_THRESHOLD){
    drag.moved=true;''', '''  if(!drag.moved && Math.hypot(dx,dy)>DRAG_THRESHOLD){
    drag.moved=true;
    if(drag.hold){ clearTimeout(drag.hold); drag.hold=null; drag.el.classList.remove("fe-holding"); }''')
rep('''  const d=drag; drag=null;
  if(d.clone) d.clone.remove();''', '''  const d=drag; drag=null;
  if(d.hold){ clearTimeout(d.hold); d.el.classList.remove("fe-holding"); }
  if(d.clone) d.clone.remove();''')

# ---------------------------------------------------------------- retire the old pickers: fused tiles tap like any tile
rep('''  el.addEventListener("click",e=>{
    if(justDragged){ e.preventDefault(); return; }
    e.preventDefault();
    openFusedSelector(c);   // v493a: tap a placed fused tile to rearrange or remove it, same as trios
  });''', '''  el.addEventListener("click",e=>{
    if(justDragged){ e.preventDefault(); return; }
    e.preventDefault();
    if(tapToBin(c,"canvas")) return;
    removeFromCanvas(c.id);   // v0.51c: a tap sends it back like any tile; hold to edit the letters
  });''')
rep('''    if(where==="canvas"){
      t.addEventListener("pointerdown",e=>onTileDown(e,t,c,"canvas"));
      t.addEventListener("click",e=>{ if(justDragged){ e.preventDefault(); return; } e.preventDefault();
        openTrioSelector(c); });   // tap on the press to rearrange the letters
      tileBadges(t,c); return t;
    }''', '''    if(where==="canvas"){ tileBadges(t,c); attachTileHandlers(t,c,"canvas"); return t; }   // v0.51c: hold to edit the letters''')
rep('''  if(c.kind==="fused"){ openFusedSelector(c); }   // choose the letter config on drop
  if(c.kind==="trio"){ openTrioSelector(c); }     // arrange the trio on drop''',
'''  if((c.kind==="fused"||c.kind==="trio") && !_feHintShown()){   // v0.51c: teach the hold once
    toast("Press and hold a fused tile to turn letters off or move them"); _feHintMark(); }''')
rep('''function removeFromCanvas(id){''', '''function _feHintShown(){ try{ return localStorage.getItem("letterati_fe_hint")==="1"; }catch(e){ return true; } }
function _feHintMark(){ try{ localStorage.setItem("letterati_fe_hint","1"); }catch(e){} }
function removeFromCanvas(id){''')

open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
