// Launch footage for Telar Stories (current app, phone size): ready-made story, new scene, AI voice, play, make video, backup.
const {chromium}=require('playwright');const fs=require('fs');const {execSync}=require('child_process');
const U='http://localhost:8875/', OUT='/home/claude/promo-apps/raw/';
(async()=>{const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:720,height:1150},hasTouch:true,acceptDownloads:true,recordVideo:{dir:OUT+'tmp-ts4',size:{width:720,height:1150}}});
 await ctx.addInitScript(()=>{try{localStorage.setItem('ts-help','1')}catch(e){}});
 const T0=Date.now();const p=await ctx.newPage();const M={};const mark=k=>{M[k]=(Date.now()-T0)/1000;console.log(k,M[k]);};
 const tapEl=async sel=>{const el=await p.$(sel);await el.scrollIntoViewIfNeeded();await p.waitForTimeout(250);const bx=await el.boundingBox();await p.mouse.move(bx.x+bx.width/2,bx.y+bx.height/2,{steps:8});await p.waitForTimeout(120);await el.click();};
 await p.goto(U);await p.waitForTimeout(2500);
 // 1) ready-made stories
 await p.evaluate(()=>scrollTo(0,250));await p.waitForTimeout(700);mark('stories');
 await tapEl('.sb-chips button[data-s="sheep"]');await p.waitForTimeout(700);await tapEl('#sbYes');await p.waitForTimeout(2600);
 await tapEl('.sb-chips button[data-s="noah"]');await p.waitForTimeout(700);await tapEl('#sbYes');await p.waitForTimeout(2600);
 // 2) blank story: build a scene
 await tapEl('.sb-chips button[data-s="blank"]');await p.waitForTimeout(600);await tapEl('#sbYes');await p.waitForTimeout(1500);
 await p.click('.tabs button[data-t=bg]');await p.evaluate(()=>scrollTo(0,document.querySelector('.stage-box').getBoundingClientRect().top+scrollY-10));await p.waitForTimeout(500);
 mark('bg');
 for(const k of ['playground','village-park','garden-rainbow']){await p.$eval(`#bgGrid button:has(img[src*="bg/${k}-t"])`,e=>e.click());await p.waitForTimeout(900);}
 await p.click('.tabs button[data-t=chars]');await p.waitForTimeout(500);
 mark('chars');
 await p.$eval('#charGrid button:has(img[src*="ch/mira-wave-happy"])',e=>e.click());await p.waitForTimeout(800);
 const box=await p.locator('#cv').boundingBox();const sx=box.width/1280, sy=box.height/720;
 await p.mouse.move(box.x+640*sx,box.y+520*sy);await p.mouse.down();await p.mouse.move(box.x+430*sx,box.y+530*sy,{steps:18});await p.mouse.up();await p.waitForTimeout(500);
 await p.$eval('#charGrid button:has(img[src*="ch/mochi-sitting"])',e=>e.click());await p.waitForTimeout(700);
 await p.mouse.move(box.x+640*sx,box.y+600*sy);await p.mouse.down();await p.mouse.move(box.x+780*sx,box.y+620*sy,{steps:15});await p.mouse.up();await p.waitForTimeout(400);
 await p.click('#selFlip');await p.waitForTimeout(700);await p.click('#selDone');await p.waitForTimeout(600);
 // 3) words + AI voice
 mark('type');
 await p.click('.tabs button[data-t=words]');await p.locator('#caption').scrollIntoViewIfNeeded();await p.evaluate(()=>scrollBy(0,-330));await p.waitForTimeout(300);
 await p.click('#caption');await p.keyboard.type('Mira and Mochi found a rainbow after the rain.',{delay:45});await p.waitForTimeout(500);
 await p.click('#aiOne');mark('ai');
 await p.waitForFunction(()=>/Done|could not/.test(document.getElementById('aiInfo').textContent),null,{timeout:240000});mark('aidone');
 await p.waitForTimeout(1500);await p.evaluate(()=>scrollTo(0,document.querySelector('.stage-box').getBoundingClientRect().top+scrollY-10));await p.waitForTimeout(400);
 mark('play');await p.click('#playScene');await p.waitForTimeout(5200);
 // 4) make the video
 await p.waitForTimeout(800);mark('export');await p.click('#exportBtn');await p.waitForFunction(()=>/saved/i.test(document.getElementById('ovTitle').textContent),null,{timeout:240000});mark('saved');await p.waitForTimeout(3500);
 await p.click('#ovClose').catch(()=>{});await p.waitForTimeout(500);
 // 5) backup
 await p.locator('#bkSave').scrollIntoViewIfNeeded();await p.evaluate(()=>scrollBy(0,-200));await p.waitForTimeout(500);mark('backup');
 await tapEl('#bkSave');await p.waitForFunction(()=>/Saved/.test(document.getElementById('bkInfo').textContent),null,{timeout:60000});await p.waitForTimeout(3000);mark('end');
 const v=p.video();await ctx.close();const src=await v.path();
 execSync(`ffmpeg -y -loglevel error -i "${src}" -vf fps=30,format=yuv420p -c:v libx264 -crf 16 -preset fast "${OUT}ts4_all.mp4"`);
 fs.writeFileSync(OUT+'ts4_marks.json',JSON.stringify(M));fs.rmSync(OUT+'tmp-ts4',{recursive:true,force:true});await b.close();})();
