// Daily seed guard. The daily press must never drift: for 30 fixed dates, the game's
// dailySeedFor / predictSeed / predRoll output has to match seed_baseline.json
// (recorded from v0.5h, the pinned predictor; every build since matches it).
// usage (from the repo root, with a local server on :8765 serving the repo):
//   node tools/checks/seeds_check.js index.html           -> compare
//   node tools/checks/seeds_check.js index.html --write   -> re-record baseline (only on purpose!)
const { chromium } = require('playwright');
const fs=require('fs'), path=require('path');
const BASE=path.join(__dirname,'seed_baseline.json');
(async()=>{
  const file=process.argv[2]||'index.html', write=process.argv.includes('--write');
  const b=await chromium.launch(); const p=await b.newPage();
  await p.goto('http://localhost:8765/'+file+'?dev=1'); await p.waitForTimeout(1500);
  const got=await p.evaluate(()=>{ const r=[]; const d0=new Date(2026,9,10);
    for(let i=0;i<30;i++){ const d=new Date(d0); d.setDate(d0.getDate()+i);
      const k=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
      const s=dailySeedFor(k); r.push([k,s,JSON.stringify(predictSeed(s)),JSON.stringify(predRoll(s))]); }
    return r; });
  await b.close();
  if(write){ fs.writeFileSync(BASE, JSON.stringify(got)); console.log('baseline written', got.length); return; }
  const want=JSON.parse(fs.readFileSync(BASE,'utf8')); let same=0;
  want.forEach((x,i)=>{ if(JSON.stringify(x)===JSON.stringify(got[i])) same++; else console.log('MISMATCH', x[0]); });
  console.log(`${file}: ${same}/${want.length} dates identical`); process.exit(same===want.length?0:1);
})();
