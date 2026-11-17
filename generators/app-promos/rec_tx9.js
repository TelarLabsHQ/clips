// Tixward promo footage: a small event gets a proper page (Book Club Holiday Dinner, 24 seats).
const R0=require('./rec.js'),launch=R0.launch,ONLY=process.env.ONLY;const clip=(b,n,o)=>!ONLY||ONLY.split(',').includes(n)?R0.clip(b,n,o):null;
const fs=require('fs');const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
let ipn=10;const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.3.'+Math.floor(ipn/200)+'.'+(ipn++%200),...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(120);await loc.click();};
const NAMES=['Olivia Bennett','Noah Patel','Ava Thompson','Liam Garcia','Sophia Nguyen','Ethan Brooks','Mia Turner','Lucas Kim','Isabella Chen','Mason Rivera','Amelia Walker','Logan Foster','Harper Reyes','Elijah Scott','Chloe Tan','James Carter','Zoe Lee','Henry Adams'];
const MEALS=['Chicken','Fish','Vegetarian'];
(async()=>{
  const ev=await post('events',{title:'Book Club Holiday Dinner',organizer:'Bayview Book Club',contact:'ellen@bayviewbooks.example',currency:'USD',tz:'Asia/Manila',starts_at:Date.parse('2026-12-12T11:00:00Z'),agree:true,
    venues:[{name:'Olive Tree Bistro, 2nd floor',address:'14 Harbor Road, Bayview'}],cover:rd('dinner'),pay_hours:48,
    description:'Our year-end dinner for members and guests: a three-course meal, a book swap, and a few surprises. Dinner and drinks are included. Seats are limited to 24.',
    types:[{name:'Dinner seat',price:25,qty:24,max_per:4}],questions:[{label:'Meal choice',type:'choice',required:true,options:MEALS}]});
  if(!ev.code){console.log(ev);process.exit(1)}
  const K={'x-org-key':ev.org_key},C=ev.code;await post(`org/${C}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Bayview Book Club',qr:rd('qr'),mine:true},K);
  const E=await get('events/'+C);const t=E.types[0],m=E.methods[0],q=E.questions[0];
  const ml=[0,1,0,2,0,1,0,0,2,1,0,1,0,2,0,1,0,0];
  for(let i=0;i<18;i++){const o=await post(`events/${C}/order`,{name:NAMES[i],contact:NAMES[i].split(' ')[0].toLowerCase()+'@example.com',items:[{t:t.id,q:1}],method:m.id,answers:{[q.id]:MEALS[ml[i]]}});if(o.error)console.log(o.error)}
  const org=await get('org/'+C,K);for(const o of org.orders) await post(`org/${C}/orders/${o.id}/approve`,{},K);
  console.log('seeded',C);
  const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
  await clip(b,'sp_chat',{...phone,url:'http://localhost:8933/chat2.html',setup:async p=>{await p.waitForTimeout(600)},act:async p=>{await p.evaluate(()=>window.play());await p.waitForTimeout(3300)},tail:400});
  await clip(b,'sp_page',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(1200)},act:async p=>{
    await p.waitForTimeout(1800);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-110);await smooth(p,y);await p.waitForTimeout(2600)},tail:400});
  await clip(b,'sp_share',{...phone,url:`${B}/o/#${C}.${ev.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),C);await p.reload();await p.waitForTimeout(1300);await p.evaluate(c=>{const l=document.querySelector('#lEvent');if(l)l.textContent='tixward.telarlabs.net/e/'+c},C)},act:async p=>{
    await p.waitForTimeout(900);await tap(p,p.locator('#qEvent'));await p.waitForTimeout(2800)},tail:400});
  await clip(b,'sp_rsvp',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(1000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-110);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(400);await tap(p,p.locator('button[aria-label="More Dinner seat"]'));await p.waitForTimeout(250);await tap(p,p.locator('button[aria-label="More Dinner seat"]'));await p.waitForTimeout(350);
    await p.evaluate(()=>document.querySelector('#bName').scrollIntoView({block:'start',behavior:'smooth'}));await p.evaluate(()=>scrollBy(0,-70));await p.waitForTimeout(500);
    await tap(p,p.locator('#bName'));await p.keyboard.type('Grace Lim',{delay:40});await tap(p,p.locator('#bContact'));await p.keyboard.type('grace@example.com',{delay:28});
    await tap(p,p.locator('select.bAns'));await p.waitForTimeout(250);await p.selectOption('select.bAns','Fish');await p.waitForTimeout(300);
    await p.evaluate(()=>document.querySelector('.pName').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(500);
    await tap(p,p.locator('.pName'));await p.keyboard.type('Daniel Reed',{delay:40});await tap(p,p.locator('select.pAns'));await p.waitForTimeout(250);await p.selectOption('select.pAns','Vegetarian');await p.waitForTimeout(1100)},tail:400});
  await clip(b,'sp_list',{w:960,h:760,url:`${B}/o/#${C}.${ev.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),C);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=att]');await p.waitForTimeout(700);
      const y=await p.$eval('.ansc',e=>e.getBoundingClientRect().top+scrollY-150);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.mouse.move(400,300);await p.waitForTimeout(1000);await tap(p,p.locator('.ansc',{hasText:'Vegetarian'}).first());await p.waitForTimeout(2200)},tail:400});
  await b.close();
})();
