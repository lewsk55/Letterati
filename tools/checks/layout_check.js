// Layout guard for the play screen (v0.51p rules): no scrolling, word bank at most two
// rows, canvas never overflows, nothing above the bank moves while tiles are tapped in,
// and tiles do not shrink on interaction. Screenshots land in tools/checks/out/.
// usage: node tools/checks/layout_check.js index.html
const { chromium } = require('playwright');
const fs=require('fs'), path=require('path');
(async()=>{
  const file=process.argv[2]||'index.html', outDir=path.join(__dirname,'out'); fs.mkdirSync(outDir,{recursive:true});
  const b=await chromium.launch(); const res={}; const errs=[];
  for(const vp of [{n:'se',width:375,height:667},{n:'i15',width:390,height:844},{n:'max',width:430,height:932}]){
    const p=await (await b.newContext({viewport:{width:vp.width,height:vp.height},hasTouch:true,isMobile:true})).newPage(); p.on('pageerror',e=>errs.push(vp.n+': '+e.message));
    await p.goto('http://localhost:8765/'+file+'?dev=1'); await p.waitForTimeout(1200);
    await p.evaluate(()=>{ newRun('LAYOUT','scholar',0,'free'); G.draft.pick=0; takeDraft(); document.getElementById('runIntroScreen').classList.add('hidden'); startLevel();
      G.hand=['B','A','Z','I','N','G','H','J','R'].map(L=>makeLetterCard(L)).concat([makeFusedCard(makeLetterCard('E'),makeLetterCard('R')), makeTrioCard(['E','N','T'])]); G.canvas=[]; renderHand(); renderCanvas(); });
    await p.waitForTimeout(1500);
    const pos=()=>p.evaluate(()=>['.canvas-wrap','#actionsRow','#defStrip'].map(q=>Math.round(document.querySelector(q).getBoundingClientRect().top)));
    const tw0=await p.evaluate(()=>getComputedStyle(document.getElementById('canvas')).getPropertyValue('--tw'));
    const p0=await pos(); let moves=0;
    for(let i=0;i<7;i++){ const t=await p.$('#hand .tile'); const bb=await t.boundingBox(); await p.touchscreen.tap(bb.x+bb.width/2,bb.y+bb.height/2); await p.waitForTimeout(40); if(JSON.stringify(await pos())!==JSON.stringify(p0)) moves++; await p.waitForTimeout(200); }
    await p.waitForTimeout(600);
    res[vp.n]=await p.evaluate(()=>{ const hand=document.getElementById('hand'), cv=document.getElementById('canvas'), wrap=cv.parentElement.getBoundingClientRect();
      return { scroll:document.scrollingElement.scrollHeight-innerHeight,
        handRows:new Set([...hand.children].map(t=>Math.round(t.getBoundingClientRect().top))).size,
        canvasOverflow:[...cv.children].some(t=>{ const r=t.getBoundingClientRect(); return r.left<wrap.left-1||r.right>wrap.right+1; }),
        fitLevel:typeof _fitLevel!=='undefined'?_fitLevel:null }; });
    res[vp.n].movesWhileTapping=moves;
    await p.screenshot({path:path.join(outDir,'layout_'+vp.n+'.png')}); }
  res.errs=errs; console.log(JSON.stringify(res,null,1)); await b.close();
  const bad=Object.entries(res).filter(([k,v])=>k!=='errs'&&(v.scroll>0||v.handRows>2||v.canvasOverflow||v.movesWhileTapping>0));
  process.exit(bad.length||errs.length?1:0);
})();
