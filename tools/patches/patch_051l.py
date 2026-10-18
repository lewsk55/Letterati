#!/usr/bin/env python3
"""0.51k -> 0.51l: triple fusion can build on 2-letter Scholar tiles (RE-, -ER, -ED);
every multi-letter tile (pair, trio, Scholar tile) uses the split chain-mark look in
one purple. usage: patch_051l.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51k"', 'gameVersion:"0.51l"')
m = re.findall(r'const VERSION *= *"0\.51k"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51k","0.51l"))

# ---------------------------------------------------------------- one purple for every fused tile
rep(''':root[data-theme="dark"] .tile.fused,
:root[data-theme="dark"] .clone-choice.fused-duo{
  background:linear-gradient(180deg,#28443C,#1E352E);border-color:#4C7A6C;
}''', ''':root[data-theme="dark"] .tile.fused,:root[data-theme="dark"] .tile.trio,
:root[data-theme="dark"] .clone-choice.fused-duo{
  background:linear-gradient(180deg,#3B3054,#2E2542);border-color:#6A5793;   /* v0.51l: purple, was green */
}''')
rep('''.tile.fused,.tile.trio{background:linear-gradient(180deg,#EAF3F0,#D3E7E0);border-color:#9FC4B8}''',
    '''.tile.fused,.tile.trio{background:linear-gradient(180deg,#F3EEFB,#E4DAF4);border-color:#C3B2E0}   /* v0.51l: purple, was green */''')
rep('''.tile.fused .clone-mark{position:absolute;right:3px;top:2px;font-size:.5em;color:#3C7E6E;z-index:3}''',
    '''.tile.fused .clone-mark{position:absolute;right:3px;top:2px;font-size:.5em;color:#7A5CA6;z-index:3}''')
rep('''.tile.trio .clone-mark{position:absolute;right:3px;top:2px;font-size:.5em;color:#3C7E6E;z-index:3}''',
    '''.tile.trio .clone-mark{position:absolute;right:3px;top:2px;font-size:.5em;color:#7A5CA6;z-index:3}
/* v0.51l: Scholar tiles draw as split tiles too, sized like a pair or a trio */
.tile.combo.domino.c2{width:calc(var(--tw,40px)*2 + var(--tgap,7px))}
.tile.combo.domino.c3{width:calc(var(--tw,40px)*2.6 + var(--tgap,7px)*2)}
.tile.combo.domino.c3 .dom-letter{font-size:.82em}
.tile.combo.domino.c3 .dom-val{font-size:.5em}''')
rep('''.clone-choice.fused-duo{background:linear-gradient(180deg,#EAF3F0,#D3E7E0);border-color:#9FC4B8;width:64px}''',
    '''.clone-choice.fused-duo{background:linear-gradient(180deg,#F3EEFB,#E4DAF4);border-color:#C3B2E0;width:64px}''')
s = s.replace('background:linear-gradient(180deg,#EAF3EF,#D8E8E0);border-color:#A9CcBD', 'background:linear-gradient(180deg,#F3EEFB,#E4DAF4);border-color:#C3B2E0')

# ---------------------------------------------------------------- Scholar tiles render as split tiles
rep('''function comboEntries(c){''', '''function comboDomino(t,c,banLock){   // v0.51l: one cell per letter, chain mark, like fused pairs and trios
  const b=comboBase(c), o=comboOrder(c), a=comboActive(c), u=c.upLevel||0;
  t.classList.add("combo","domino", b.length>=3?"c3":"c2");
  o.forEach(i=>{
    const cd=document.createElement("span"); cd.className="dom-cell"+(a[i]!==false?"":" dim")+(banLock&&banLock.has(b[i])?" locked":"");
    const g=document.createElement("span"); g.className="dom-letter"; g.textContent=b[i]; cd.appendChild(g);
    const v=document.createElement("span"); v.className="dom-val"; v.textContent=1*Math.pow(2,u); cd.appendChild(v);
    t.appendChild(cd);
  });
  const fm=document.createElement("span"); fm.className="clone-mark"; fm.textContent="⛓"; t.appendChild(fm);
}
function comboEntries(c){''')
rep('''  if(c.kind==="combo"){
    t.classList.add("combo");
    const banLock=bannedLetterSet();
    if(banLock && comboSeq(c).some(L=>banLock.has(L))) t.classList.add("locked-letter");
    const g=document.createElement("span"); g.className="combo-label"; g.innerHTML=comboLabelHtml(c); t.appendChild(g);
    const v=document.createElement("span"); v.className="val"; v.textContent=comboValue(c); t.appendChild(v);
    const cm=document.createElement("span"); cm.className="clone-mark"; cm.textContent="✚"; t.appendChild(cm);
    tileBadges(t,c);
    attachTileHandlers(t,c,where); return t;
  }''', '''  if(c.kind==="combo"){
    comboDomino(t,c,bannedLetterSet());   // v0.51l
    if(where==="canvas") domFit(t);
    tileBadges(t,c);
    attachTileHandlers(t,c,where); return t;
  }''')
rep('''  if(c.kind==="combo"){
    t.classList.add("combo");
    const g=document.createElement("span"); g.className="combo-label"; g.innerHTML=comboLabelHtml(c); t.appendChild(g);
    const v=document.createElement("span"); v.className="val"; v.textContent=comboValue(c); t.appendChild(v);
    const cm=document.createElement("span"); cm.className="clone-mark"; cm.textContent="✚"; t.appendChild(cm);
    tileBadges(t,c);
    return t;
  }''', '''  if(c.kind==="combo"){
    comboDomino(t,c,null);   // v0.51l
    tileBadges(t,c);
    return t;
  }''')

# ---------------------------------------------------------------- triple fusion on any two-letter fused tile
rep('''function tapTrioFuse(id){''', '''/* v0.51l: a triple fusion can build on any two-letter fused tile: a fused pair or a
   two-letter Scholar tile (RE-, -ER, -ED). Three-letter Scholar tiles are already full. */
function trioBaseOk(c){ return !!c && (c.kind==="fused" || (c.kind==="combo" && comboBase(c).length===2)); }
function trioBaseLetters(c){ return c.kind==="fused" ? [c.sides[0].letter, c.sides[1].letter] : comboOrder(c).map(i=>comboBase(c)[i]); }
function trioBaseLabel(c){ return c.kind==="fused" ? fusedLabel(c) : trioBaseLetters(c).join(""); }
function trioBaseValue(c){ return c.kind==="fused" ? fusedValue(c) : comboBase(c).length*Math.pow(2,c.upLevel||0); }   // every letter, muted or not
function tapTrioFuse(id){''')
rep('''    if(c.kind!=="fused") return;
    G.trioPairPending=id;
    $("selectHint").textContent="Now pick the letter to add to "+fusedLabel(c)+".";''',
'''    if(!trioBaseOk(c)) return;
    G.trioPairPending=id;
    $("selectHint").textContent="Now pick the letter to add to "+trioBaseLabel(c)+".";''')
rep('''  $("fuseMsg").innerHTML=`<b>${fusedLabel(pair)}</b> ${fusedValue(pair)} pts &nbsp;+&nbsp; <b>${letter.letter}</b>''',
    '''  $("fuseMsg").innerHTML=`<b>${trioBaseLabel(pair)}</b> ${trioBaseValue(pair)} pts &nbsp;+&nbsp; <b>${letter.letter}</b>''')
rep('''  const trio=makeTrioCard([pair.sides[0].letter, pair.sides[1].letter, letter.letter], up, mult);''',
    '''  const trio=makeTrioCard([...trioBaseLetters(pair), letter.letter], up, mult);   // v0.51l: pair or two-letter Scholar tile''')
rep('''    if(G.trioPairPending==null && c.kind==="fused"){ wrap.classList.add("selectable","gild"); wrap.addEventListener("click",()=>tapTrioFuse(c.id)); }''',
    '''    if(G.trioPairPending==null && trioBaseOk(c)){ wrap.classList.add("selectable","gild"); wrap.addEventListener("click",()=>tapTrioFuse(c.id)); }''')
rep('''  else if(mode==="triofuse"){ hint.textContent="Tap the fused pair to build on.";''',
    '''  else if(mode==="triofuse"){ hint.textContent="Tap a two-letter fused tile to build on.";''')
rep('''    $("selectHint").textContent="Tap the fused pair to build on.";''', '''    $("selectHint").textContent="Tap a two-letter fused tile to build on.";''')
# the shop only offers the upgrade when there is something to build on
rep('''    ...(G.deck.some(c=>c.kind==="fused") && G.deck.some(c=>c.kind==="letter")''',
    '''    ...(G.deck.some(c=>trioBaseOk(c)) && G.deck.some(c=>c.kind==="letter")''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
