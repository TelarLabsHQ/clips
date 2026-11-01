const {clip,glide,chromium}=require('./rec');const fs=require('fs');
const W='http://localhost:8883/write/', R='http://localhost:8883/review/';
const OWN1="My dream job is to become a marine biologist. Every summer my family visits the beach, and I spend hours looking at crabs and small fish in the rock pools. ";
const OWN2="I want to understand how the ocean works and how we can protect it. ";
const PASTE="Marine biology is a fascinating field that encompasses the study of marine organisms, their behaviors, and their interactions with the environment. Pursuing a career in this discipline requires dedication, scientific rigor, and a profound commitment to conservation. ";
const HONEST="When I grow up I want to be a nurse like my aunt. She works nights at the city hospital and she always says the hardest part is not the work but saying goodbye to patients she likes. Last year when my grandfather was sick, she explained everything to us in a calm way. I think that is a kind of strength too. I want to learn to care for people when they are scared. ";
async function typeHuman(p,sel,text,{delay=45,typo=true}={}){const words=text.split(' ');let i=0;
 for(const w of words){ if(typo&&i%9===4&&w.length>3){await p.type(sel,w.slice(0,-1)+'x',{delay});await p.waitForTimeout(150);await p.keyboard.press('Backspace');await p.keyboard.type(w.slice(-1)+' ',{delay});}
  else await p.type(sel,w+' ',{delay}); i++; }}
(async()=>{const b=await chromium.launch();fs.mkdirSync('files',{recursive:true});
 // Background: make the honest file (not recorded)
 { const ctx=await b.newContext({acceptDownloads:true});const p=await ctx.newPage();await p.goto(W);
   await p.fill('#task','Essay: My Dream Job');await p.fill('#sName','Sam Lee');const half=HONEST.length>>1;await typeHuman(p,'#essay',HONEST.slice(0,half),{delay:190});await p.waitForTimeout(7000);await typeHuman(p,'#essay',HONEST.slice(half),{delay:190,typo:false});
   const [d]=await Promise.all([p.waitForEvent('download'),p.click('#dlBtn')]);await d.saveAs('files/sam.drafttrail');await ctx.close(); }
 // Recorded: student writes, then pastes
 let ctxKeep=null;
 await clip(b,'dt_a',{w:620,h:1000,url:W,cursor:'none',setup:async p=>{await p.fill('#task','Essay: My Dream Job');await p.fill('#sName','Alex Rivera');await p.click('#essay');},
   act:async p=>{await typeHuman(p,'#essay',OWN1,{delay:170});await p.waitForTimeout(500);await p.keyboard.insertText(PASTE);await p.waitForTimeout(700);await typeHuman(p,'#essay',OWN2,{delay:170,typo:false});
     const [d]=await Promise.all([p.waitForEvent('download'),p.click('#dlBtn')]);await d.saveAs('files/alex.drafttrail');await p.waitForTimeout(1200);}});
 // Recorded: teacher opens both files, sees flags
 await clip(b,'dt_b',{w:620,h:1000,url:R,cursor:'none',setup:async p=>{await p.waitForTimeout(400);},act:async p=>{
   await p.setInputFiles('input[type=file]',['files/alex.drafttrail','files/sam.drafttrail']);await p.waitForTimeout(1200);
   await p.evaluate(()=>{const e=[...document.querySelectorAll('*')].find(x=>x.children.length===0&&/ESSAY: MY DREAM JOB/i.test(x.textContent));if(e)window.scrollTo({top:e.getBoundingClientRect().top+scrollY-200,behavior:'smooth'});});await p.waitForTimeout(3500);}});
 // Recorded: replay with pasted text highlighted
 await clip(b,'dt_c',{w:620,h:1000,url:R,cursor:'none',setup:async p=>{await p.setInputFiles('input[type=file]',['files/alex.drafttrail','files/sam.drafttrail']);await p.waitForTimeout(800);
   await p.evaluate(()=>{const r=[...document.querySelectorAll('h2,h3,div')].find(e=>/^REPLAY$/i.test(e.textContent.trim()));(r||document.body).scrollIntoView({block:'start'});window.scrollBy(0,-20);});
   await p.selectOption('#speed',{index:0}).catch(()=>{});await p.waitForTimeout(400);},
   act:async p=>{await p.click('#pbtn');await p.waitForTimeout(9000);}});
 // Recorded: honest essay = no flags
 await clip(b,'dt_d',{w:620,h:1000,url:R,cursor:'none',setup:async p=>{await p.setInputFiles('input[type=file]',['files/alex.drafttrail','files/sam.drafttrail']);await p.waitForTimeout(800);},
   act:async p=>{await p.click('.sub:has-text("Sam Lee")');await p.waitForTimeout(600);await p.evaluate(()=>{const e=[...document.querySelectorAll('*')].find(x=>x.children.length===0&&/ESSAY: MY DREAM JOB/i.test(x.textContent));if(e)window.scrollTo({top:e.getBoundingClientRect().top+scrollY-200,behavior:'smooth'});});await p.waitForTimeout(2500);}});
 await b.close();})();
