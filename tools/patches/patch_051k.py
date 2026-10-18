#!/usr/bin/env python3
"""0.51j -> 0.51k: no No Reprints challenge for Short King; letters worth 5+ hold two
upgrades; no iOS text selection when holding a tile. usage: patch_051k.py in out"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)
rep('gameVersion:"0.51j"', 'gameVersion:"0.51k"')
m = re.findall(r'const VERSION *= *"0\.51j"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51j","0.51k"))

# 1. Short King never gets No Reprints (four legal lengths, five words: the rule eats the round)
rep('''function liveChallengeTypeFor(level){
  const t=challengeTypeFor(level);
  if(t!=="longform" || !wordCap() || wordCap()>=99) return t;
  const rng=makeRng("challenge-sk:"+level);
  const pool=CHALLENGE_ORDER.filter(x=>x!=="longform" && !(CHALLENGE_EARLY_ONLY.has(x) && level>4));''',
'''function liveChallengeTypeFor(level){
  const t=challengeTypeFor(level);
  const capped = wordCap() && wordCap()<99;   // Short King
  if(!capped || (t!=="longform" && t!=="reprints")) return t;   // v0.51k: reprints out for him too
  const rng=makeRng("challenge-sk:"+level);
  const pool=CHALLENGE_ORDER.filter(x=>x!=="longform" && x!=="reprints" && !(CHALLENGE_EARLY_ONLY.has(x) && level>4));''')

# 2. high-value letters (5+ points: K, J, X, Q, Z) hold two upgrades in total, not three
rep('''function tileUpgradeCap(c){ return (c && c.kind==="combo" && G.perks && G.perks.rootWord) ? MAX_TILE_UPGRADES+1 : MAX_TILE_UPGRADES; }''',
'''const HIGH_VALUE_UPGRADES = 2;   // v0.51k: K, J, X, Q and Z run hot too fast with three
function tileIsHighValue(c){
  if(!c) return false;
  const hv=v=>(+v||0)>=GILD_HIGH_VALUE;
  if(c.kind==="letter") return hv(c.base!=null?c.base:LETTER_VALUES[c.letter]);
  if(c.kind==="fused" && Array.isArray(c.sides)) return c.sides.some(sd=>hv(sd.base!=null?sd.base:LETTER_VALUES[sd.letter]));
  if(c.kind==="trio" && Array.isArray(c.letters)) return c.letters.some(L=>hv(LETTER_VALUES[L]));
  return false;
}
function tileUpgradeCap(c){
  if(c && c.kind==="combo" && G.perks && G.perks.rootWord) return MAX_TILE_UPGRADES+1;
  return tileIsHighValue(c) ? HIGH_VALUE_UPGRADES : MAX_TILE_UPGRADES;
}''')
rep('''  const slots = Math.min(gildCapFor(c)-u, MAX_TILE_UPGRADES-upgradeCount(c));''',
    '''  const slots = Math.min(gildCapFor(c)-u, tileUpgradeCap(c)-upgradeCount(c));''')
rep('''    toast("No tile can take that. Each tile holds "+MAX_TILE_UPGRADES+" upgrades at most."); haptic(20); return;''',
    '''    toast("No tile can take that. Each tile holds "+MAX_TILE_UPGRADES+" upgrades at most (letters worth 5 or more hold "+HIGH_VALUE_UPGRADES+")."); haptic(20); return;''')
rep('''  else { const n=upgradeCount(c); extra=`<small>${n+1} of ${MAX_TILE_UPGRADES} upgrade slots used after this</small>`; }''',
    '''  else { const n=upgradeCount(c); extra=`<small>${n+1} of ${tileUpgradeCap(c)} upgrade slots used after this</small>`; }''')
rep('''  if(upgradeCount(c)>=MAX_TILE_UPGRADES){ const m=document.createElement("span");''',
    '''  if(upgradeCount(c)>=tileUpgradeCap(c)){ const m=document.createElement("span");''')
rep('''  if(!hasUpgradeRoom(c)){ toast("That tile already carries "+MAX_TILE_UPGRADES+" upgrades"); return; }''',
    '''  if(!hasUpgradeRoom(c)){ toast("That tile already carries "+tileUpgradeCap(c)+" upgrades"); return; }''')

# 3. no text selection or callout on iOS while holding tiles or using the editor
rep('''.tile.fused,.tile.trio,.tile.combo{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}''',
'''.tile.fused,.tile.trio,.tile.combo{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}
/* v0.51k: a game screen, not a document. Long-presses must never start a text
   selection or the iOS callout menu (it grabbed the fuse editor's Done button). */
body{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
input,textarea,[contenteditable="true"]{-webkit-user-select:text;user-select:text;-webkit-touch-callout:default}''')
rep('''function openFuseEditor(c){''', '''function clearSelection(){ try{ const sel=window.getSelection&&window.getSelection(); if(sel&&sel.removeAllRanges) sel.removeAllRanges(); }catch(e){} }
document.addEventListener("selectstart",e=>{ let t=e.target; if(t && t.nodeType===3) t=t.parentElement; if(!t || !t.closest || !t.closest("input,textarea,[contenteditable=true]")) e.preventDefault(); });
function openFuseEditor(c){''')
rep('''  feRender();
  $("fuseEdit").classList.remove("hidden");''', '''  feRender(); clearSelection();
  $("fuseEdit").classList.remove("hidden");''')
open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
