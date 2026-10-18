#!/usr/bin/env python3
"""0.51e -> 0.51f: fighting-game style character select. An 8-slot roster grid,
a feature panel with stat bars for the selected desk, '?' slots for desks not yet
unlocked or not yet built. usage: patch_051f.py in.html out.html"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)

rep('gameVersion:"0.51e"', 'gameVersion:"0.51f"')
m = re.findall(r'const VERSION *= *"0\.51e"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51e","0.51f"))

# ---------------------------------------------------------------- markup
rep('''    <div class="cs-eyebrow" id="csEyebrow">Who is at the desk</div>
    <div class="cs-grid" id="charGrid"></div>''',
'''    <div class="cs-eyebrow" id="csEyebrow">Who is at the desk</div>
    <div class="cs-feature" id="csFeature"></div>
    <div class="cs-roster" id="charGrid"></div>''')

# ---------------------------------------------------------------- styles
rep('''.cs-grid{display:flex;flex-direction:column;gap:10px}''',
'''.cs-grid{display:flex;flex-direction:column;gap:10px}
/* v0.51f: roster select. Feature panel on top, portrait grid below. */
.cs-feature{position:relative;background:var(--paper);border:2px solid var(--ink);border-radius:16px;padding:14px 14px 12px;
  box-shadow:0 4px 0 var(--ink);overflow:hidden;min-height:268px}
.cs-feature::before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(135deg,transparent 0 10px,rgba(185,138,46,.07) 10px 11px);pointer-events:none}
.csf-top{position:relative;display:flex;gap:13px;align-items:center}
.csf-portrait{flex:0 0 auto;width:86px;height:86px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:3.1rem;
  background:radial-gradient(circle at 50% 40%,#FFF8E6,var(--tile) 60%,var(--tile-edge));border:2px solid var(--brass);box-shadow:inset 0 -6px 0 rgba(138,100,24,.18)}
.csf-portrait.unknown{background:var(--ink);border-color:var(--ink);color:var(--page);font-family:var(--serif);font-weight:700}
.csf-id{min-width:0}
.csf-tag{font-size:.56rem;letter-spacing:.18em;text-transform:uppercase;font-weight:800;color:var(--brass-deep)}
.csf-name{font-family:var(--serif);font-weight:800;font-size:1.55rem;line-height:1.02;color:var(--ink);margin-top:2px}
.csf-best{display:inline-block;margin-top:6px;font-size:.56rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800;color:var(--paper);background:var(--moss);padding:3px 7px;border-radius:999px}
.csf-best.none{background:transparent;color:var(--ink-soft);border:1px solid var(--tile-edge)}
.csf-blurb{position:relative;font-size:.76rem;color:var(--ink-soft);line-height:1.38;margin:10px 0 8px}
.csf-stats{position:relative;display:grid;grid-template-columns:auto 1fr auto;gap:5px 9px;align-items:center}
.csf-sk{font-size:.58rem;letter-spacing:.14em;text-transform:uppercase;font-weight:800;color:var(--ink)}
.csf-bar{display:flex;gap:3px}
.csf-pip{flex:1;height:9px;border-radius:2px;background:var(--page-deep);transform-origin:left center}
.csf-pip.on{background:var(--brass)}
.csf-pip.on.hot{background:var(--oxblood)}
.csf-sv{font-size:.66rem;font-weight:800;color:var(--ink-soft);min-width:30px;text-align:right;font-variant-numeric:tabular-nums}
.csf-lines{position:relative;margin-top:9px}
.csf-line{font-size:.72rem;line-height:1.32;margin-top:4px;display:flex;gap:6px;align-items:baseline;color:var(--ink)}
.csf-line .p{color:var(--moss);font-weight:900;flex:0 0 auto}
.csf-line .m{color:var(--oxblood);font-weight:900;flex:0 0 auto}
.csf-soon{position:relative;font-size:.8rem;color:var(--ink-soft);line-height:1.45;margin-top:14px;text-align:center}
.cs-feature.enter .csf-portrait{animation:csfIn .34s cubic-bezier(.34,1.56,.64,1)}
.cs-feature.enter .csf-name,.cs-feature.enter .csf-tag{animation:csfSlide .28s ease-out}
.cs-feature.enter .csf-pip.on{animation:csfPip .32s ease-out both}
@keyframes csfIn{0%{transform:translateX(-26px) scale(.8);opacity:0}100%{transform:none;opacity:1}}
@keyframes csfSlide{0%{transform:translateX(18px);opacity:0}100%{transform:none;opacity:1}}
@keyframes csfPip{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}
.cs-roster{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px}
.cs-slot{position:relative;aspect-ratio:1/1;border-radius:12px;border:2px solid var(--tile-edge);background:var(--tile);
  display:flex;align-items:center;justify-content:center;font-size:1.9rem;cursor:pointer;padding:0;font-family:inherit;color:var(--ink);
  box-shadow:0 3px 0 var(--tile-edge);transition:transform .12s ease}
.cs-slot:active{transform:translateY(2px);box-shadow:0 1px 0 var(--tile-edge)}
.cs-slot .cs-sname{position:absolute;left:0;right:0;bottom:3px;font-size:.48rem;letter-spacing:.08em;text-transform:uppercase;font-weight:800;color:var(--ink-soft);text-align:center;white-space:nowrap;overflow:hidden}
.cs-slot.picked{border-color:var(--brass);background:#FFF6DC;box-shadow:0 0 0 3px rgba(185,138,46,.35),0 3px 0 var(--brass-deep)}
.cs-slot.picked::after{content:"P1";position:absolute;top:-8px;left:-6px;font-size:.52rem;font-weight:900;letter-spacing:.06em;color:var(--paper);background:var(--oxblood);padding:2px 5px;border-radius:5px}
.cs-slot.picked.flash{animation:csSlot .3s ease-out}
@keyframes csSlot{0%{transform:scale(1.12)}100%{transform:scale(1)}}
.cs-slot.unknown{background:var(--ink);border-color:var(--ink);box-shadow:0 3px 0 #000;color:var(--page);font-family:var(--serif);font-weight:800;font-size:1.7rem}
.cs-slot.unknown .cs-sname{color:rgba(231,220,196,.55)}
.cs-slot.unknown.picked{border-color:var(--brass);box-shadow:0 0 0 3px rgba(185,138,46,.35),0 3px 0 #000}
.cs-slot.cleared::before{content:"";position:absolute;top:5px;right:5px;width:7px;height:7px;border-radius:50%;background:var(--moss)}
#charStartBtn:disabled{opacity:.45}
:root[data-theme="dark"] .cs-slot.picked{background:#3A3324}
:root[data-theme="dark"] .cs-slot.unknown,:root[data-theme="dark"] .csf-portrait.unknown{background:#15131B;border-color:#0D0C12;color:#9A93A8;box-shadow:0 3px 0 #000}
:root[data-theme="dark"] .cs-slot.unknown .cs-sname{color:#6A6478}
:root[data-theme="dark"] .cs-slot.unknown.picked{border-color:var(--brass)}
#charScreen.cs-locked-view .cs-asc-head,#charScreen.cs-locked-view #ascRow,#charScreen.cs-locked-view #ascDesc{visibility:hidden}
:root[data-theme="dark"] .csf-portrait{background:radial-gradient(circle at 50% 40%,#4A4254,#34303F 70%)}''')

# ---------------------------------------------------------------- roster data + renderer
rep('''function renderCharSelect(){
  const grid=$("charGrid"); grid.innerHTML="";
  CHAR_ORDER.forEach(id=>{
    const c=CHARACTERS[id], best=bestAsc(id);
    const b=document.createElement("button");
    b.className="cs-card"+(id===_selChar?" picked":"");
    b.innerHTML=`<span class="cs-art">${c.art}</span>
      <span class="cs-body">
        <span class="cs-name">${escHtml(c.name)}</span>
        <span class="cs-blurb">${escHtml(c.blurb)}</span>
        <span class="cs-line"><span class="cs-plus">+</span><span>${escHtml(c.boon)}</span></span>
        <span class="cs-line"><span class="cs-minus">\\u2212</span><span>${escHtml(c.bane)}</span></span>
        <span class="cs-best">${best<0?"Not yet cleared":("Best clear \\u00B7 A"+best)}</span>
      </span>`;
    b.addEventListener("click",()=>{
      _selChar=id;
      _selAsc=Math.min(_selAsc, unlockedAsc(id));
      renderCharSelect(); haptic(10);
    });
    grid.appendChild(b);
  });''',
'''/* v0.51f: the roster. Eight slots; desks fill them in CHAR_ORDER and the rest show
   as "?". A desk can carry unlock:()=>bool to start locked (none do yet); a locked
   desk shows as "?" with its unlock hint. To add a desk: define it in CHARACTERS,
   append its id to CHAR_ORDER, and set its complexity (1 to 5). */
const ROSTER_SLOTS = 8;
const CHAR_COMPLEXITY = { writer:1, detective:3, editor:5, shortking:2, scholar:4 };
function charUnlocked(id){ const c=CHARACTERS[id]; return !!c && (devMode() || typeof c.unlock!=="function" || !!c.unlock()); }
function charStats(c){
  const words=HANDS_PER_LEVEL+(c.handsDelta||0), hand=START_HAND+(c.handSizeDelta||0), disc=DISCARDS_PER_LEVEL+(c.discardsDelta||0);
  const tm=Array.isArray(c.targetCurve) ? c.targetCurve.reduce((a,b)=>a+b,0)/c.targetCurve.length*(c.targetMult||1) : (c.targetMult||1);
  const clamp=v=>Math.max(1,Math.min(5,Math.round(v)));
  const cx=CHAR_COMPLEXITY[c.id]||3;
  return [
    {k:"Words",     v:words+"/rd",  p:clamp(words-1)},
    {k:"Hand",      v:hand+" tiles", p:clamp(3+(hand-START_HAND)*2/3)},
    {k:"Discards",  v:String(disc), p:clamp(disc)},
    {k:"Targets",   v:(tm===1?"Base":"+"+Math.round((tm-1)*100)+"%"), p:clamp(2+(tm-1)*3), hot:true},
    {k:"Complexity",v:["","Easy","Light","Medium","Tricky","Expert"][cx], p:cx, hot:true}
  ];
}
let _csLastShown=null;
function renderCharFeature(slot){
  const f=$("csFeature"); if(!f) return;
  let html;
  if(slot.id && charUnlocked(slot.id)){
    const c=CHARACTERS[slot.id], best=bestAsc(slot.id);
    const pips=st=>{ let h=""; for(let i=1;i<=5;i++) h+=`<span class="csf-pip${i<=st.p?" on":""}${st.hot&&i<=st.p&&st.p>=4?" hot":""}" style="animation-delay:${(i-1)*35}ms"></span>`; return h; };
    html=`<div class="csf-top"><div class="csf-portrait">${c.art}</div>
        <div class="csf-id"><div class="csf-tag">${escHtml(c.tag||"")}</div><div class="csf-name">${escHtml(c.name)}</div>
        <span class="csf-best${best<0?" none":""}">${best<0?"Not yet cleared":("Best clear \\u00B7 A"+best)}</span></div></div>
      <div class="csf-blurb">${escHtml(c.blurb)}</div>
      <div class="csf-stats">${charStats(c).map(st=>`<span class="csf-sk">${st.k}</span><span class="csf-bar">${pips(st)}</span><span class="csf-sv">${escHtml(st.v)}</span>`).join("")}</div>
      <div class="csf-lines"><div class="csf-line"><span class="p">+</span><span>${escHtml(c.boon)}</span></div>
        <div class="csf-line"><span class="m">\\u2212</span><span>${escHtml(c.bane)}</span></div></div>`;
  } else {
    const c=slot.id?CHARACTERS[slot.id]:null;
    html=`<div class="csf-top"><div class="csf-portrait unknown">?</div>
        <div class="csf-id"><div class="csf-tag">${c?"Locked":"Coming soon"}</div><div class="csf-name">???</div></div></div>
      <div class="csf-soon">${c&&c.unlockHint ? escHtml(c.unlockHint) : "A new desk is on its way to the press. Check back after future updates."}</div>`;
  }
  f.innerHTML=html;
  const key=slot.id||("empty"+slot.i);
  if(key!==_csLastShown){ f.classList.remove("enter"); void f.offsetWidth; f.classList.add("enter"); _csLastShown=key; }
}
let _csSlot=null;   // index of the slot being viewed (may be a "?" slot)
function renderCharSelect(){
  const grid=$("charGrid"); grid.innerHTML="";
  const slots=[]; for(let i=0;i<Math.max(ROSTER_SLOTS,CHAR_ORDER.length);i++) slots.push({i, id:CHAR_ORDER[i]||null});
  if(_csSlot==null || !slots[_csSlot]) _csSlot=Math.max(0,CHAR_ORDER.indexOf(_selChar));
  slots.forEach(sl=>{
    const open=sl.id && charUnlocked(sl.id), c=sl.id?CHARACTERS[sl.id]:null;
    const b=document.createElement("button");
    b.className="cs-slot"+(open?"":" unknown")+(sl.i===_csSlot?" picked":"")+(open&&bestAsc(sl.id)>=0?" cleared":"");
    b.setAttribute("aria-label", open ? c.name : "Locked desk");
    b.innerHTML=(open?c.art:"?")+`<span class="cs-sname">${open?escHtml(c.name.replace(/^The /,"")):"???"}</span>`;
    b.addEventListener("click",()=>{
      _csSlot=sl.i;
      if(open){ _selChar=sl.id; _selAsc=Math.min(_selAsc, unlockedAsc(sl.id)); }
      renderCharSelect(); haptic(10);
      const nb=$("charGrid").children[sl.i]; if(nb){ nb.classList.add("flash"); }
    });
    grid.appendChild(b);
  });
  const cur=slots[_csSlot];
  renderCharFeature(cur);
  const viewingOpen = cur.id && charUnlocked(cur.id);
  $("charScreen").classList.toggle("cs-locked-view", !viewingOpen);
  { const sb=$("charStartBtn"); if(sb){ sb.disabled=!viewingOpen; sb.textContent = viewingOpen ? ("Begin as "+CHARACTERS[_selChar].name.replace(/^The /,"")) : "Locked"; } }''')

# opening the screen resets the viewed slot to the chosen desk
rep('''  _selAsc = Math.min(_selAsc, unlockedAsc(_selChar));
  renderCharSelect();''', '''  _selAsc = Math.min(_selAsc, unlockedAsc(_selChar));
  _csSlot = null; _csLastShown = null;   // v0.51f
  renderCharSelect();''')

open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
