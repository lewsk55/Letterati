// Headless runner for sim_v2.html (needs Playwright and a local web server on :8765 in the game folder).
// usage: node tools/sim/runner_char.js <runs> <regular|casual> <asc|mix> <gameFile> <seed> <parallel>
const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{
  const [n,profile,asc,game,seed,par]=[+(process.argv[2]||5),process.argv[3]||'regular',process.argv[4]==null||process.argv[4]==='mix'?null:+process.argv[4],process.argv[5]||'index.html',+(process.argv[6]||1),+(process.argv[7]||1)];
  const override=process.env.OVERRIDE?JSON.parse(process.env.OVERRIDE):{};
  const browser=await chromium.launch();
  const per=Math.ceil(n/par);
  const jobs=[...Array(par)].map(async(_,k)=>{
    const page=await browser.newPage({viewport:{width:390,height:844}});
    page.on('pageerror',e=>console.error('PAGEERR',e.message));
    await page.goto('http://localhost:8765/'+(process.env.SIM||'sim%20v2.html')); await page.waitForFunction(()=>window.__ready);
    return await page.evaluate(o=>window.runTest(o).then(r=>({version:r.version,ms:r.ms,runs:r.runs})),{n:per,profile,asc,game,seed:seed*100+k,override,char:process.env.CHAR||'mix'});
  });
  const res=await Promise.all(jobs);
  const runs=res.flatMap(r=>r.runs);
  fs.writeFileSync(process.env.OUT||'sim2_out.json', JSON.stringify(runs));
  console.log(JSON.stringify({version:res[0].version, n:runs.length, secs:(Math.max(...res.map(r=>r.ms))/1000).toFixed(0),
    ended:runs.reduce((m,r)=>(m[r._sim.ended||r.result]=(m[r._sim.ended||r.result]||0)+1,m),{}),
    errors:runs.flatMap(r=>r._sim.errors).slice(0,3)}));
  await browser.close();
})();
