const {clip,launch}=require('./rec');const fs=require('fs'),path=require('path');
const B='http://quizpolice.telarlabs.net', DTR='/home/claude/drafttrail/public';
const serveDT=async ctx=>ctx.route(/^https:\/\/drafttrail\.telarlabs\.net\//,r=>{let u=new URL(r.request().url()).pathname;if(u.endsWith('/'))u+='index.html';
  const f=path.join(DTR,u); if(!fs.existsSync(f)) return r.fulfill({status:404,body:''});
  const ct=f.endsWith('.html')?'text/html':f.endsWith('.css')?'text/css':f.endsWith('.js')?'text/javascript':f.endsWith('.woff2')?'font/woff2':f.endsWith('.svg')?'image/svg+xml':'application/octet-stream';
  r.fulfill({status:200,body:fs.readFileSync(f),headers:{'content-type':ct}})});
const api=async(p,o={})=>{const r=await fetch('http://localhost:8882/api/'+p,{...o,headers:{'content-type':'application/json',...(o.headers||{})}});return r.json()};
const TASK='Short answer: Why do leaves change color?';
const mk=lim=>api('sessions',{method:'POST',body:JSON.stringify({title:TASK,quiz_url:'https://drafttrail.telarlabs.net/write/?task='+encodeURIComponent(TASK),embed_url:'https://drafttrail.telarlabs.net/write/?task='+encodeURIComponent(TASK),timing:'any',limit_min:lim,strict:true,max_exits:3})});
const TXT=['Leaves change color in autumn because the days get shorter and colder. ','The tree stops making chlorophyll, so the green fades away. ','Then the yellow and orange colors that were hiding in the leaf can show. '];
const PASTE='Chlorophyll degradation during senescence unmasks carotenoid pigments, while anthocyanin synthesis produces the vivid red hues observed in deciduous foliage. ';
async function joinStu(b,code,name,{rec=false}={}){const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});await serveDT(ctx);const p=await ctx.newPage();
  await p.goto(`${B}/join/?c=${code}`);await p.press('#code','Enter');await p.waitForSelector('#name',{state:'visible'});await p.fill('#name',name);await p.press('#name','Enter');await p.waitForTimeout(2500);return p;}
const typeIn=async(p,t,delay=8)=>{const f=p.frameLocator('#frame');await f.locator('#essay').click();await f.locator('#essay').pressSequentially(t,{delay});};
const leave=p=>p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))});
const back=p=>p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))});
(async()=>{const b=await launch();
 const q=await mk(15);
 // background class
 const kids={};for(const n of ['Noah Miller','Olivia Smith','Liam Brown','Ava Davis']){kids[n]=await joinStu(b,q.code,n);await typeIn(kids[n],TXT[0],2);}
 // 1 teacher set-up page
 await clip(b,'dt3_setup',{w:720,h:1000,cursor:'none',setup:async p=>{await serveDT(p.context());await p.goto('https://drafttrail.telarlabs.net/set-up/');await p.waitForTimeout(600);await p.evaluate(()=>scrollTo(0,140));},
   act:async p=>{await p.type('#suTask',TASK,{delay:35});await p.waitForTimeout(300);await p.check('input[name=mode][value=live]');await p.waitForTimeout(1600);}});
 // 2 student writes on a phone
 await clip(b,'dt3_student',{w:390,h:844,mobile:true,cursor:'none',setup:async p=>{await serveDT(p.context());await p.goto(`${B}/join/?c=${q.code}`);await p.press('#code','Enter');await p.waitForSelector('#name',{state:'visible'});await p.fill('#name','Emma Johnson');await p.press('#name','Enter');await p.waitForTimeout(2500);},
   act:async p=>{await typeIn(p,TXT[0]+TXT[1],30);await p.waitForTimeout(600);}});
 // 3 dashboard live
 const tctx=await b.newContext();const tp=await tctx.newPage();await tp.goto(B+'/teacher/');const store=JSON.stringify([{code:q.code,key:q.teacher_key,title:TASK,created:Date.now()}]);
 await tp.close();
 for(const n of Object.keys(kids)) await typeIn(kids[n],TXT[1],2);
 await clip(b,'dt3_dash',{w:720,h:1200,cursor:'none',setup:async p=>{await p.goto(B+'/teacher/');await p.evaluate(s=>localStorage.setItem('quizpolice.teacher.v1',s),store);await p.goto(`${B}/teacher/#${q.code}`);await p.waitForTimeout(3000);
     await p.evaluate(()=>{const t=document.querySelector('.grid2');if(t)window.scrollTo(0,t.getBoundingClientRect().top+scrollY-380);});await p.waitForTimeout(500);},
   act:async p=>{const k=kids['Liam Brown'];await k.frameLocator('#frame').locator('#essay').click();await k.keyboard.insertText(PASTE);await p.waitForTimeout(3200);
     await leave(kids['Ava Davis']);await p.waitForTimeout(3200);await back(kids['Ava Davis']);await p.waitForTimeout(3000);}});
 // 4 time's up: auto hand-in on a 1-minute task
 const q2=await mk(1);
 await clip(b,'dt3_timeup',{w:390,h:844,mobile:true,cursor:'none',setup:async p=>{await serveDT(p.context());await p.goto(`${B}/join/?c=${q2.code}`);await p.press('#code','Enter');await p.waitForSelector('#name',{state:'visible'});await p.fill('#name','Emma Johnson');await p.press('#name','Enter');await p.waitForTimeout(2500);
     await typeIn(p,TXT.join(''),15);await p.waitForFunction(()=>/0:0[3-5] left/.test(document.getElementById('sTime').textContent),null,{timeout:90000});},
   act:async p=>{await p.waitForFunction(()=>!document.getElementById('timeOv').hidden,null,{timeout:20000});await p.waitForTimeout(2500);}});
 // 5 review the class
 for(const n of Object.keys(kids)){const k=kids[n];await k.evaluate(()=>{});}
 for(const n of Object.keys(kids)){ if(await kids[n].isVisible('#warnOv')) await kids[n].click('#wOk'); await typeIn(kids[n],TXT[2],2);}
 for(const n of Object.keys(kids)){const f=kids[n].frameLocator('#frame');await f.locator('#subBtn').click();await f.locator('#subYes').click();await kids[n].waitForTimeout(800);}
 const bun=await api(`sessions/${q.code}/essays`,{headers:{'x-teacher-key':q.teacher_key}});fs.writeFileSync('/home/claude/promo-apps/files/class.drafttrail',JSON.stringify(bun));console.log('essays',bun.essays.length);
 await clip(b,'dt3_review',{w:720,h:1000,cursor:'none',setup:async p=>{await serveDT(p.context());await p.goto('https://drafttrail.telarlabs.net/review/');await p.waitForTimeout(500);},
   act:async p=>{await p.setInputFiles('input[type=file]','/home/claude/promo-apps/files/class.drafttrail');await p.waitForTimeout(1500);
     const n=p.locator('.sub:has-text("Liam Brown")');if(await n.count()){await n.first().click();}await p.waitForTimeout(2500);}});
 await b.close();})();
