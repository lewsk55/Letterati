#!/usr/bin/env python3
"""0.51f -> 0.51g: desk unlocks. New players start with the Writer only. Each first
win (A0 or higher) with a desk you have not won with yet opens the next desk, in
order: Detective, Short King, Scholar, Editor. Writer loses the empty boon/bane lines.
usage: patch_051g.py in.html out.html"""
import sys, re
SRC, OUT = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit("expected %d, got %d: %s" % (n, c, a[:140]))
    s = s.replace(a, b)

rep('gameVersion:"0.51f"', 'gameVersion:"0.51g"')
m = re.findall(r'const VERSION *= *"0\.51f"', s); assert len(m)==1
s = s.replace(m[0], m[0].replace("0.51f","0.51g"))

# roster order = unlock order; unlock rule
rep('''const CHAR_ORDER = ["writer","detective","editor","shortking","scholar"];''',
'''const CHAR_ORDER = ["writer","detective","shortking","scholar","editor"];   // v0.51g: roster order is unlock order
/* v0.51g: desk unlocks. The Writer is always open. The Nth desk after her opens once
   you have won a run (any ascension, A0 included) with N different desks. */
const CHAR_UNLOCK_ORDER = ["detective","shortking","scholar","editor"];
function clearedDeskCount(){ return CHAR_ORDER.filter(id=>bestAsc(id)>=0).length; }
CHAR_UNLOCK_ORDER.forEach((id,k)=>{ if(CHARACTERS[id]) CHARACTERS[id].unlock=()=>clearedDeskCount()>=k+1; });
function nextLockedDesk(){ return CHAR_UNLOCK_ORDER.find(id=>CHARACTERS[id] && !CHARACTERS[id].unlock()); }''')

# writer: no boon/bane lines
rep('''    boon:"Nothing gained", bane:"Nothing lost",''', '''    boon:"", bane:"",   // v0.51g: no lines for the house hand''')
rep('''      <span class="dc-line"><span class="dc-plus">+</span><span>${escHtml(c.boon)}</span></span>
      <span class="dc-line"><span class="dc-minus">−</span><span>${escHtml(c.bane)}</span></span>''',
'''      ${c.boon?`<span class="dc-line"><span class="dc-plus">+</span><span>${escHtml(c.boon)}</span></span>`:""}
      ${c.bane?`<span class="dc-line"><span class="dc-minus">−</span><span>${escHtml(c.bane)}</span></span>`:""}''')
rep('''      <div class="csf-lines"><div class="csf-line"><span class="p">+</span><span>${escHtml(c.boon)}</span></div>
        <div class="csf-line"><span class="m">\\u2212</span><span>${escHtml(c.bane)}</span></div></div>`;''',
'''      <div class="csf-lines">${c.boon?`<div class="csf-line"><span class="p">+</span><span>${escHtml(c.boon)}</span></div>`:""}
        ${c.bane?`<div class="csf-line"><span class="m">\\u2212</span><span>${escHtml(c.bane)}</span></div>`:""}</div>`;''')

# locked panel copy: the next desk gets a concrete hint
rep('''      <div class="csf-soon">${c&&c.unlockHint ? escHtml(c.unlockHint) : "A new desk is on its way to the press. Check back after future updates."}</div>`;''',
'''      <div class="csf-soon">${escHtml(lockedDeskHint(slot.id))}</div>`;''')
rep('''let _csLastShown=null;''', '''function lockedDeskHint(id){
  if(!id) return "A new desk is on its way to the press. Check back after future updates.";
  const c=CHARACTERS[id]; if(c.unlockHint) return c.unlockHint;
  const k=CHAR_UNLOCK_ORDER.indexOf(id), need=(k+1)-clearedDeskCount();
  if(id!==nextLockedDesk()) return "Locked. Keep winning with new desks to open it.";
  return need<=1 ? "Win a run with a desk you have not won with yet to unlock this one. Any ascension counts, A0 included."
                 : "Win runs with "+need+" desks you have not won with yet to unlock this one.";
}
let _csLastShown=null;''')

# opening the screen never lands on a locked desk
rep('''  _csSlot = null; _csLastShown = null;   // v0.51f''', '''  if(!charUnlocked(_selChar)){ _selChar="writer"; _selAsc=0; }   // v0.51g
  _csSlot = null; _csLastShown = null;   // v0.51f''')

# win screen: announce a newly opened desk
rep('''  const newRung = recordAscWin(G.character||"writer", ascLevel());   // unlocks the next rung for this desk''',
'''  const _openBefore = CHAR_ORDER.filter(id=>charUnlocked(id));
  const newRung = recordAscWin(G.character||"writer", ascLevel());   // unlocks the next rung for this desk
  const _newDesks = devMode() ? [] : CHAR_ORDER.filter(id=>charUnlocked(id) && !_openBefore.includes(id));''')
rep('''  const unlock = (newRung && ascLevel()<MAX_ASC) ? `<div class="win-unlock">Ascension ${ascLevel()+1} unlocked for ${escHtml(charDef().name)}</div>` : "";''',
'''  const unlock = ((newRung && ascLevel()<MAX_ASC) ? `<div class="win-unlock">Ascension ${ascLevel()+1} unlocked for ${escHtml(charDef().name)}</div>` : "")
    + _newDesks.map(id=>`<div class="win-unlock" style="background:var(--brass-deep)">New desk unlocked: ${CHARACTERS[id].art} ${escHtml(CHARACTERS[id].name)}</div>`).join("");''')

open(OUT, "w", encoding="utf-8").write(s)
print("ok", len(s))
