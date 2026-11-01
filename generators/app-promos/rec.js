// Shared recorder: each clip is its own browser context with video recording; logs the time actions start.
const {chromium}=require('playwright');const fs=require('fs');const {execSync}=require('child_process');
const OUT='/home/claude/promo-apps/raw/'; fs.mkdirSync(OUT,{recursive:true});
const CURSOR=`(()=>{const c=document.createElement('div');c.id='fakecur';c.style.cssText='position:fixed;z-index:2147483647;pointer-events:none;width:30px;height:30px;left:-50px;top:-50px;transform:translate(-4px,-26px);transition:none';
 c.innerHTML='<svg viewBox="0 0 24 24" width="30" height="30"><path d="M4 20l4.5-1L19.5 8a2.1 2.1 0 00-3-3L5.5 16z" fill="#fff" stroke="#222" stroke-width="1.6"/></svg>';
 const t=document.createElement('div');t.id='fakeptr';t.style.cssText='position:fixed;z-index:2147483647;pointer-events:none;width:26px;height:26px;border-radius:50%;background:rgba(255,200,60,.45);border:2px solid rgba(255,170,0,.9);left:-50px;top:-50px;transform:translate(-13px,-13px);display:none';
 addEventListener('DOMContentLoaded',()=>{document.body.append(c,t)});
 addEventListener('mousemove',e=>{for(const el of [c,t]){el.style.left=e.clientX+'px';el.style.top=e.clientY+'px'}},true);
 addEventListener('mousedown',()=>{t.style.display='block'},true);addEventListener('mouseup',()=>{setTimeout(()=>t.style.display='none',180)},true);
 window.__cur=k=>{c.style.display=k==='pen'?'block':'none';};})()`;
async function clip(b,name,{w=1280,h=720,url,setup,act,mobile=false,tail=800,cursor='pen'}){
  const ctx=await b.newContext({viewport:{width:w,height:h},recordVideo:{dir:OUT+'tmp-'+name,size:{width:w,height:h}},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});
  await ctx.addInitScript(CURSOR);
  const t0=Date.now(); const p=await ctx.newPage();
  if(url) await p.goto(url); if(setup) await setup(p);
  await p.evaluate(k=>window.__cur&&window.__cur(k),cursor);
  await p.waitForTimeout(300); const start=(Date.now()-t0)/1000;
  await act(p); await p.waitForTimeout(tail); const end=(Date.now()-t0)/1000;
  const v=p.video(); await ctx.close(); const src=await v.path();
  execSync(`ffmpeg -y -loglevel error -ss ${start} -to ${end} -i "${src}" -vf fps=30,format=yuv420p -c:v libx264 -crf 16 -preset fast "${OUT}${name}.mp4"`);
  fs.rmSync(OUT+'tmp-'+name,{recursive:true,force:true}); console.log('clip',name,(end-start).toFixed(1)+'s');
}
async function write(p,strokes,{pace=14,gap=60}={}){
  for(const st of strokes){await p.mouse.move(st[0][0],st[0][1]);await p.mouse.down();
    for(const pt of st.slice(1)){await p.mouse.move(pt[0],pt[1],{steps:2});await p.waitForTimeout(pace);} await p.mouse.up();await p.waitForTimeout(gap);}
}
function hand(spec){return JSON.parse(execSync(`python3 /home/claude/promo-apps/hand.py '${JSON.stringify(spec)}'`).toString());}
async function glide(p,pts,steps=12){for(const [x,y] of pts){await p.mouse.move(x,y,{steps});}}
const launch=()=>chromium.launch({args:['--host-resolver-rules=MAP quizpolice.telarlabs.net:80 127.0.0.1:8882']});
module.exports={clip,write,hand,glide,chromium,launch};
