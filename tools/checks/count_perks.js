const { chromium } = require('playwright');
(async()=>{ const b=await chromium.launch(); const p=await b.newPage();
  await p.goto('http://localhost:8765/'+(process.argv[2]||'index.html')+'?dev=1'); await p.waitForTimeout(1500);
  const r=await p.evaluate(()=>{
    const out={};
    const collect=(charId)=>{ newRun('CNT','writer',0,'free'); G.character=charId; G.perks={...G.perks};
      G.deck.push(makeFusedCard(makeLetterCard('E'),makeLetterCard('R')));
      const m=new Map();
      for(let i=0;i<40;i++){ perkPool(makeRng('c'+i)).forEach(e=>{ try{ const o=e.make(); m.set(o.d&&o.d.type||o.name,{name:o.name,kind:o.kind,rarity:o.rarity,char:e.char||null}); }catch(x){} }); }
      return m; };
    const w=collect('writer');
    const all=new Map(w);
    ['detective','shortking','scholar','editor'].forEach(c=>collect(c).forEach((v,k)=>all.set(k,v)));
    const ep=new Map(); CHALLENGE_EPIC_POOL.forEach(e=>ep.set(e.d.type,{name:e.name,char:e.char||null}));
    // perks also offered via charOffers (character-only shop items)?
    const perks=[...all.values()].filter(v=>v.kind==='Perk');
    const general=perks.filter(v=>!v.char), byChar={}; perks.filter(v=>v.char).forEach(v=>(byChar[v.char]=byChar[v.char]||[]).push(v.name));
    const epicGeneral=[...ep.values()].filter(v=>!v.char).map(v=>v.name).filter(n=>!general.some(g=>g.name===n));
    const kinds={}; [...all.values()].filter(v=>!v.char).forEach(v=>kinds[v.kind]=(kinds[v.kind]||0)+1);
    const rar={}; general.forEach(v=>rar[v.rarity]=(rar[v.rarity]||0)+1);
    return {general:general.length, generalNames:general.map(v=>v.name).sort(), rar, byChar, epicOnlyGeneral:epicGeneral, otherShopKinds:kinds};
  });
  console.log(JSON.stringify(r,null,1)); await b.close(); })();
