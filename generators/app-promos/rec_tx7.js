// Tixward promo footage: a small language course with 20 slots.
const R0=require('./rec.js'),launch=R0.launch,ONLY=process.env.ONLY;const clip=(b,n,o)=>!ONLY||ONLY.split(',').includes(n)?R0.clip(b,n,o):null;
const fs=require('fs');const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
let ipn=10;const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.2.'+Math.floor(ipn/200)+'.'+(ipn++%200),...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(120);await loc.click();};
const NAMES=['Olivia Bennett','Noah Patel','Ava Thompson','Liam Garcia','Sophia Nguyen','Ethan Brooks','Mia Turner','Lucas Kim','Isabella Chen','Mason Rivera','Amelia Walker','Logan Foster','Harper Reyes','Elijah Scott','Chloe Tan','James Carter'];
const LV=['Total beginner','I know a few words','I can hold a short chat'];
(async()=>{
  const ev=await post('events',{title:'Beginner Mandarin: 8 Saturdays',organizer:'Bayview Language Center',contact:'hello@bayviewlang.example',currency:'USD',tz:'Asia/Manila',starts_at:Date.parse('2027-01-09T01:00:00Z'),agree:true,
    venues:[{name:'Bayview Language Center, Room 3',address:'21 Market Street, Bayview'}],cover:rd('course'),pay_hours:48,
    description:'Eight Saturday classes, January 9 to February 27, 9:00 to 11:00 AM, with Ms. Wang. A small class of 20, so everyone gets to speak. Book and materials included.',
    types:[{name:'Course enrollment',price:120,qty:20,max_per:2}],
    questions:[{label:'Your Mandarin level',type:'choice',required:true,options:LV},{label:'Preferred name in class',type:'text'}]});
  if(!ev.code){console.log(ev);process.exit(1)}
  const K={'x-org-key':ev.org_key},C=ev.code;await post(`org/${C}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Bayview Language Center',qr:rd('qr'),mine:true},K);
  const E=await get('events/'+C);const t=E.types[0],m=E.methods[0];const [q1,q2]=E.questions;
  const lv=[0,0,1,0,2,0,1,0,0,1,0,2,0,1,0,0];
  for(let i=0;i<16;i++){const o=await post(`events/${C}/order`,{name:NAMES[i],contact:NAMES[i].split(' ')[0].toLowerCase()+'@example.com',items:[{t:t.id,q:1}],method:m.id,answers:{[q1.id]:LV[lv[i]]}});if(o.error)console.log(o.error)}
  const org=await get('org/'+C,K);for(const o of org.orders) await post(`org/${C}/orders/${o.id}/approve`,{},K);
  console.log('seeded',C);
  const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
  await clip(b,'lc_event',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(1200)},act:async p=>{
    await p.waitForTimeout(2200);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-110);await smooth(p,y);await p.waitForTimeout(2600)},tail:400});
  await clip(b,'lc_enroll',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(1000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-110);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(500);await tap(p,p.locator('button[aria-label="More Course enrollment"]'));await p.waitForTimeout(400);
    await p.evaluate(()=>document.querySelector('#bName').scrollIntoView({block:'start',behavior:'smooth'}));await p.evaluate(()=>scrollBy(0,-80));await p.waitForTimeout(600);
    await tap(p,p.locator('#bName'));await p.keyboard.type('Daniel Reed',{delay:45});await tap(p,p.locator('#bContact'));await p.keyboard.type('daniel@example.com',{delay:30});
    await p.evaluate(()=>document.querySelector('select.bAns').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(500);
    await tap(p,p.locator('select.bAns'));await p.waitForTimeout(300);await p.selectOption('select.bAns','Total beginner');await p.waitForTimeout(500);
    await tap(p,p.locator('input.bAns'));await p.keyboard.type('Dan',{delay:70});await p.waitForTimeout(900)},tail:400});
  const orgSetup=async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),C);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=att]');await p.waitForTimeout(700)};
  await clip(b,'lc_list',{w:960,h:760,url:`${B}/o/#${C}.${ev.org_key}`,setup:async p=>{await orgSetup(p);const y=await p.$eval('.ansc',e=>e.getBoundingClientRect().top+scrollY-150);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.mouse.move(400,300);await p.waitForTimeout(900);await tap(p,p.locator('.ansc',{hasText:'Total beginner'}).first());await p.waitForTimeout(2200)},tail:400});
  await clip(b,'lc_sheet',{w:1280,h:760,url:`${B}/o/#${C}.${ev.org_key}`,setup:async p=>{await orgSetup(p);await p.evaluate(()=>scrollTo(0,250))},act:async p=>{
    await p.mouse.move(700,300);await p.waitForTimeout(500);await tap(p,p.locator('#sheetB'));await p.waitForTimeout(1300);
    await p.evaluate(()=>{const o=document.querySelector('#sheetOv'),pg=o.querySelector('.sp');o.scrollTo({top:o.scrollTop+pg.getBoundingClientRect().top-90,behavior:'smooth'})});await p.mouse.move(1180,420,{steps:12});await p.waitForTimeout(1600)},tail:500});
  await b.close();
})();
