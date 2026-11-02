const {chromium}=require('playwright');const fs=require('fs');const {execSync}=require('child_process');
const U='http://localhost:8875/stories-demo/', OUT='/home/claude/promo-apps/raw/';
const KJS=fs.readFileSync('/home/claude/telarlabs-home/public/stories-demo/assets/kokoro.web.js','utf8').split('https://huggingface.co/').join('http://localhost:8871/');
(async()=>{const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:720,height:1150},hasTouch:true,recordVideo:{dir:OUT+'tmp-ts',size:{width:720,height:1150}}});
 await ctx.route(/kokoro\.web\.js$/,r=>r.fulfill({status:200,body:KJS,headers:{'content-type':'text/javascript'}}));
 await ctx.addInitScript(()=>{try{localStorage.setItem('ts-help','1')}catch(e){};addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='.badge{display:none!important}';document.head.append(s)})});
 const T0=Date.now();const p=await ctx.newPage();const M={};const mark=k=>{M[k]=(Date.now()-T0)/1000;console.log(k,M[k]);};
 await p.goto(U);await p.waitForTimeout(1500);
 // new blank scene after scene 10
 await p.click('#strip .scene:nth-child(10)');await p.waitForTimeout(300);await p.click('#strip .add');await p.waitForTimeout(400);
 await p.click('.tabs button[data-t=bg]');await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(600);
 mark('bg');
 const bgs=await p.$$('#bgGrid button');
 for(const i of [2,4,3]){await bgs[i].evaluate(e=>e.click());await p.waitForTimeout(900);}
 await p.click('.tabs button[data-t=chars]');await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(400);
 mark('chars');
 const ch=await p.$$('#charGrid button');
 await ch[0].evaluate(e=>e.click());await p.waitForTimeout(800);
 const box=await p.locator('#cv').boundingBox();const sx=box.width/1280, sy=box.height/720;
 // drag Mira to the left
 await p.mouse.move(box.x+640*sx,box.y+520*sy);await p.mouse.down();await p.mouse.move(box.x+420*sx,box.y+530*sy,{steps:18});await p.mouse.up();await p.waitForTimeout(500);
 await ch[ch.length-1].evaluate(e=>e.click());await p.waitForTimeout(700);
 await p.mouse.move(box.x+640*sx,box.y+600*sy);await p.mouse.down();await p.mouse.move(box.x+760*sx,box.y+620*sy,{steps:15});await p.mouse.up();await p.waitForTimeout(400);
 await p.click('#selFlip');await p.waitForTimeout(700);await p.click('#selDone');await p.waitForTimeout(600);
 mark('type');
 await p.click('.tabs button[data-t=words]');await p.locator('#caption').scrollIntoViewIfNeeded();await p.evaluate(()=>scrollBy(0,-260));await p.waitForTimeout(300);
 await p.click('#caption');await p.keyboard.type('Mira and Mochi made a new friend at the park.',{delay:45});await p.waitForTimeout(500);
 await p.click('#aiOne');mark('ai');
 await p.waitForFunction(()=>/Done|could not/.test(document.getElementById('aiInfo').textContent),null,{timeout:120000});mark('aidone');
 await p.waitForTimeout(1200);await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(400);
 mark('play');await p.click('#playScene');await p.waitForTimeout(5000);
 mark('export');await p.click('#exportBtn');await p.waitForTimeout(6000);mark('end');
 const v=p.video();await ctx.close();const src=await v.path();
 execSync(`ffmpeg -y -loglevel error -i "${src}" -vf fps=30,format=yuv420p -c:v libx264 -crf 16 -preset fast "${OUT}ts_all.mp4"`);
 fs.writeFileSync(OUT+'ts_marks.json',JSON.stringify(M));fs.rmSync(OUT+'tmp-ts',{recursive:true,force:true});await b.close();})();
