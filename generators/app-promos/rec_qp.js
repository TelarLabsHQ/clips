const {clip,glide,chromium,launch}=require('./rec');const fs=require('fs');
const B='http://quizpolice.telarlabs.net', MOCK=fs.readFileSync('/home/claude/promo-apps/mockquiz.html','utf8');
const FORM='https://docs.google.com/forms/d/e/1FAIpQLSdemoScienceQuizGrade6/viewform';
const mock=async ctx=>ctx.route(/docs\.google\.com/,r=>r.fulfill({status:200,body:MOCK,headers:{'content-type':'text/html'}}));
const leave=async p=>{await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'hidden'});document.dispatchEvent(new Event('visibilitychange'));});};
const back=async p=>{await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'visible'});document.dispatchEvent(new Event('visibilitychange'));});};
async function student(b,code,name){const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});await mock(ctx);const p=await ctx.newPage();
  await p.goto(`${B}/join/?c=${code}`);await p.waitForTimeout(500);if(await p.isVisible('#code'))await p.fill('#code',code),await p.press('#code','Enter');
  await p.waitForSelector('#name',{state:'visible'});await p.fill('#name',name);if(await p.isVisible('#section'))await p.selectOption('#section',{index:1}).catch(()=>{});await p.press('#name','Enter');
  await p.waitForSelector('#quiz:not([hidden])',{timeout:10000});return p;}
(async()=>{const b=await launch();const TW=720,TH=1200;let code='';
 // a) teacher creates a quiz
 await clip(b,'qp_a',{w:TW,h:TH,url:B+'/teacher/',cursor:'none',setup:async p=>{await p.waitForTimeout(600);},act:async p=>{
   await p.click('#toNew');await p.waitForTimeout(500);await p.type('#fTitle','Science Quiz – Grade 6',{delay:35});
   await p.type('#fUrl',FORM,{delay:8});await p.waitForTimeout(400);await p.click('#newForm button.pri');await p.waitForTimeout(2500);
   code=(await p.evaluate(()=>location.hash)).slice(1);
   await p.evaluate(()=>localStorage.setItem('__keep',1));}});
 // need the teacher store for later dashboards: create again in a persistent context
 const tctx=await b.newContext({viewport:{width:TW,height:TH}});const tp=await tctx.newPage();await tp.goto(B+'/teacher/');await tp.click('#toNew');
 await tp.fill('#fTitle','Science Quiz – Grade 6');await tp.fill('#fUrl',FORM);await tp.click('#newForm button.pri');await tp.waitForTimeout(1500);
 code=(await tp.evaluate(()=>location.hash)).slice(1);const store=await tp.evaluate(()=>JSON.stringify(Object.fromEntries(Object.entries(localStorage))));console.log('code',code);
 // b) student joins on a phone
 await clip(b,'qp_b',{w:390,h:844,mobile:true,url:`${B}/join/?c=${code}`,cursor:'none',setup:async p=>{await mock(p.context());await p.waitForTimeout(500);},act:async p=>{
   if(await p.isVisible('#code')){await p.fill('#code','');await p.type('#code',code,{delay:120});await p.press('#code','Enter');}
   await p.waitForSelector('#name',{state:'visible'});await p.type('#name','Ana Reyes',{delay:90});await p.waitForTimeout(300);await p.press('#name','Enter');
   await p.waitForTimeout(2500);const f=p.frameLocator('#frame');await f.locator('label:has-text("Mercury")').click();await p.waitForTimeout(600);
   await f.locator('label:has-text("Carbon dioxide")').click();await p.waitForTimeout(900);}});
 // more students in the background
 const kids={};for(const n of ['Ben Cruz','Chloe Tan','David Okafor','Ella Novak','Farah Khan']) kids[n]=await student(b,code,n);
 // c) dashboard live while students leave
 const dashSetup=async p=>{await p.evaluate(s=>{for(const [k,v] of Object.entries(JSON.parse(s)))localStorage.setItem(k,v)},store);await p.goto(`${B}/teacher/#${code}`);await p.waitForTimeout(2500);};
 await clip(b,'qp_c',{w:TW,h:TH,url:B+'/teacher/',cursor:'none',setup:dashSetup,act:async p=>{
   await p.waitForTimeout(1500);await leave(kids['Ben Cruz']);await p.waitForTimeout(3500);await leave(kids['Farah Khan']);await p.waitForTimeout(3000);
   await back(kids['Ben Cruz']);await p.waitForTimeout(3000);}});
 // d) student phone: leaving shows a warning
 await clip(b,'qp_d',{w:390,h:844,mobile:true,cursor:'none',setup:async p=>{await mock(p.context());await p.goto(`${B}/join/?c=${code}`);await p.press('#code','Enter');
   await p.waitForSelector('#name',{state:'visible'});await p.fill('#name','Gabe Silva');await p.press('#name','Enter');await p.waitForSelector('#quiz:not([hidden])');await p.waitForTimeout(1500);},
   act:async p=>{await p.waitForTimeout(800);await leave(p);await p.waitForTimeout(2500);await back(p);await p.waitForTimeout(3000);}});
 // e) dashboard after: exits counted, lock + unlock
 await back(kids['Farah Khan']);for(let i=0;i<3;i++){await leave(kids['David Okafor']);await kids['David Okafor'].waitForTimeout(1200);await back(kids['David Okafor']);await kids['David Okafor'].waitForTimeout(800);}
 await clip(b,'qp_e',{w:TW,h:TH,url:B+'/teacher/',cursor:'none',setup:dashSetup,act:async p=>{await p.waitForTimeout(2500);
   const r=p.locator('#rows >> text=David Okafor');if(await r.count()){await r.first().click();await p.waitForTimeout(2000);if(await p.isVisible('#unlock')){await p.click('#unlock');await p.waitForTimeout(2000);}}}});
 await b.close();})();
