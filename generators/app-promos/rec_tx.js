// Tixward promo footage: seeds demo data on the local server, then records phone and desktop clips.
const {clip,launch}=require('./rec.js');const fs=require('fs');
const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json',...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(120);await loc.click();};
(async()=>{
  // ---------- seed: a concert ----------
  const ev=await post('events',{title:'Harbor Lights Concert',organizer:'Harbor Arts Society',contact:'hello@harborarts.example',currency:'USD',tz:'Asia/Manila',mode:'single',
    starts_at:Date.parse('2026-12-12T11:00:00Z'),venues:[{name:'Harbor Hall',address:'12 Bay Road, Harbor City'}],cover:rd('cover'),pay_hours:24,
    description:'An evening of acoustic music by the water, with local bands and a choir. Gates open at 6:30 PM.',
    types:[{name:'General',price:15,qty:300,max_per:10},{name:'Student',price:10,qty:100,max_per:10}]});
  const K={'x-org-key':ev.org_key};const C=ev.code;
  await post(`org/${C}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Harbor Arts Society',account_no:'09171234567',qr:rd('qr'),mine:true},K);
  await post(`org/${C}/methods`,{kind:'cash',note:'Pay at the gate from 6:30 PM.'},K);
  const E=await get('events/'+C);const [g,st]=E.types;const gc=E.methods.find(m=>m.kind==='wallet'),cash=E.methods.find(m=>m.kind==='cash');
  // pending payments to approve
  const mk=async(name,contact,items,m)=>post(`events/${C}/order`,{name,contact,items,method:m.id});
  const e1=await mk('Emma Johnson','emma@example.com',[{t:g.id,q:2}],gc);await post(`orders/${e1.token}/proof`,{ref:'1012 345 678901',shot:rd('receipt')});
  const e2=await mk('Liam Chen','0917 555 0182',[{t:st.id,q:1}],gc);await post(`orders/${e2.token}/proof`,{ref:'2045 118 330972',shot:rd('receipt')});
  // a reserved order for the "pay" clip, and an approved ticket for the door clip
  const r1=await mk('Mia Torres','0917 555 0123',[{t:g.id,q:2}],gc);
  const d1=await mk('Noah Davis','noah@example.com',[{t:g.id,q:1}],cash);const org=await get('org/'+C,K);const od=org.orders.find(o=>o.name==='Noah Davis');
  await post(`org/${C}/orders/${od.id}/approve`,{},K);const tk=(await get('orders/'+d1.token)).tickets[0].code;
  // ---------- seed: badminton courts ----------
  const bk=await post('events',{mode:'book',title:'Riverside Badminton Courts',organizer:'Riverside Sports Club',contact:'0917 555 0100',currency:'USD',
    venues:[{id:'v1',name:'Riverside Sports Center',address:'45 Park Avenue, Riverside'}],pay_hours:2,description:'Three air-conditioned courts. Rackets for rent at the front desk.',
    book:{tz:'Asia/Manila',style:'equal',slot:60,max_slots:3,max_per:3,ahead:30,notice:60,hours:[[480,1320],[480,1320],[480,1320],[480,1320],[480,1320],[480,1320],[480,1320]],extra:[],off:[],
      res:[{name:'Court 1',price:12},{name:'Court 2',price:12},{name:'Court 3 (indoor)',price:15}],pay_now:true,pay_site:true}});
  const BK={'x-org-key':bk.org_key};await post(`org/${bk.code}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Riverside Sports Club',qr:rd('qr'),mine:true},BK);
  const BE=await get('events/'+bk.code);const R=BE.book.res;const tom=new Date(Date.parse(BE.book.today+'T00:00:00Z')+864e5).toISOString().slice(0,10);
  for(const [r,s,n,who] of [[0,1080,2,'Ava Brooks'],[1,1020,1,'Ethan Park'],[0,600,2,'Olivia Reyes'],[2,1140,2,'Lucas Kim']]) await post(`events/${bk.code}/order`,{res:R[r].id,date:tom,start:s,slots:n,name:who,contact:who.split(' ')[0].toLowerCase()+'@example.com',pay:'site'});
  await post(`org/${bk.code}/book`,{res:R[1].id,date:tom,start:480,slots:2,name:'Club training',kind:'block'},BK);
  console.log('seeded',C,bk.code,tom);
  const b=await launch();
  const phone={w:390,h:844,mobile:true,cursor:'tap'};
  // 1. buyer picks tickets
  await clip(b,'tx_event',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(900)},act:async p=>{
    await p.waitForTimeout(900);await smooth(p,520);await p.waitForTimeout(900);
    const box=await p.$('#tickets');const y=await box.evaluate(e=>e.getBoundingClientRect().top+scrollY-70);await smooth(p,y);await p.waitForTimeout(700);
    await tap(p,p.locator('button[aria-label="More General"]'));await p.waitForTimeout(350);await tap(p,p.locator('button[aria-label="More General"]'));await p.waitForTimeout(500);
    await p.evaluate(()=>document.querySelector('#bName').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(600);
    await tap(p,p.locator('#bName'));await p.keyboard.type('Sofia Martin',{delay:55});await tap(p,p.locator('#bContact'));await p.keyboard.type('0917 555 0147',{delay:45});
    await p.evaluate(()=>document.querySelector('#go').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(600);await tap(p,p.locator('#go'));await p.waitForURL(/\/t\//);await p.waitForTimeout(1200)},tail:900});
  // 2. buyer pays and sends the screenshot
  await clip(b,'tx_pay',{...phone,url:B+'/t/?k='+r1.token,setup:async p=>{await p.waitForTimeout(800);const y=await p.$eval('.payqr',e=>e.getBoundingClientRect().top+scrollY-260);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(1300);await p.evaluate(()=>document.querySelector('#proof').scrollIntoView({block:'start',behavior:'smooth'}));await p.waitForTimeout(800);
    await tap(p,p.locator('#shot'));await p.setInputFiles('#shot',W+'receipt.jpg');await p.waitForTimeout(900);
    await tap(p,p.locator('#ref'));await p.keyboard.type('3301 772 104588',{delay:45});await p.evaluate(()=>document.querySelector('#pgo').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(500);
    await tap(p,p.locator('#pgo'));await p.waitForTimeout(1500);await smooth(p,0);await p.waitForTimeout(1200)},tail:700});
  // 3. organizer approves
  await clip(b,'tx_approve',{w:1280,h:760,url:`${B}/o/#${C}.${ev.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),C);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=pay]');await p.waitForTimeout(1200);await p.evaluate(()=>scrollTo(0,330))},act:async p=>{
    await p.mouse.move(640,400);await p.waitForTimeout(1200);const a=p.locator('.ap').first();await tap(p,a);await p.waitForTimeout(1600);await p.mouse.move(700,380,{steps:10});await p.waitForTimeout(800)},tail:600});
  // 5. the buyer's QR ticket
  await clip(b,'tx_ticket',{...phone,url:B+'/t/?k='+d1.token,setup:async p=>{await p.waitForTimeout(1000)},act:async p=>{await p.waitForTimeout(800);await smooth(p,380);await p.waitForTimeout(1800)},tail:500});
  // 4. door scanner
  const door=(await get('org/'+C,K)).event.door_key;
  await clip(b,'tx_door',{...phone,url:`${B}/door/#${C}.${door}`,setup:async p=>{await p.waitForTimeout(1200)},act:async p=>{
    await p.waitForTimeout(700);await tap(p,p.locator('#code'));await p.keyboard.type(tk,{delay:70});await p.waitForTimeout(250);await tap(p,p.locator('#man button'));await p.waitForTimeout(2300)},tail:500});
  // ---------- bookings ----------
  await clip(b,'bk_page',{...phone,url:B+'/b/'+bk.code,setup:async p=>{await p.waitForTimeout(1000)},act:async p=>{
    await p.waitForTimeout(800);await p.evaluate(()=>document.querySelector('#book').scrollIntoView({block:'start',behavior:'smooth'}));await p.waitForTimeout(900);
    await tap(p,p.locator('.rc',{hasText:'Court 1'}));await p.waitForTimeout(400);await tap(p,p.locator('.day').nth(1));await p.waitForTimeout(700);
    await p.evaluate(()=>document.querySelector('.slots').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(1200)},tail:500});
  await clip(b,'bk_pick',{...phone,url:B+'/b/'+bk.code,setup:async p=>{await p.waitForTimeout(900);await p.locator('.day').nth(1).click();await p.waitForTimeout(300);await p.evaluate(()=>document.querySelector('.slots').scrollIntoView({block:'start'}));await p.evaluate(()=>scrollBy(0,-90))},act:async p=>{
    await p.waitForTimeout(700);await tap(p,p.locator('.slot',{hasText:/^3:00 PM$/}));await p.waitForTimeout(600);await tap(p,p.locator('.len',{hasText:'2 hours'}));await p.waitForTimeout(500);
    await p.evaluate(()=>document.querySelector('.sum').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(1300)},tail:500});
  await clip(b,'bk_book',{...phone,url:B+'/b/'+bk.code,setup:async p=>{await p.waitForTimeout(900);await p.locator('.day').nth(1).click();await p.locator('.slot',{hasText:/^3:00 PM$/}).click();await p.locator('.len',{hasText:'2 hours'}).click();await p.waitForTimeout(300);await p.evaluate(()=>document.querySelector('.sum').scrollIntoView({block:'start'}))},act:async p=>{
    await p.waitForTimeout(600);await tap(p,p.locator('#bName'));await p.keyboard.type('Daniel Cruz',{delay:55});await tap(p,p.locator('#bContact'));await p.keyboard.type('0917 555 0166',{delay:45});
    await p.evaluate(()=>document.querySelector('input[name=pay][value=site]').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(500);
    await tap(p,p.locator('label.meth',{hasText:'Pay on-site'}));await p.waitForTimeout(500);await tap(p,p.locator('#bGo'));await p.waitForURL(/\/t\//);await p.waitForTimeout(1800)},tail:600});
  await clip(b,'bk_sched',{w:1280,h:760,url:`${B}/o/#${bk.code}.${bk.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),bk.code);await p.reload();await p.waitForTimeout(1200);await p.fill('#bDate',tom);await p.dispatchEvent('#bDate','change');await p.waitForTimeout(400);await p.evaluate(()=>document.querySelector('.sched').scrollIntoView({block:'start'}));await p.evaluate(()=>scrollBy(0,-120))},act:async p=>{
    await p.mouse.move(640,300);await p.waitForTimeout(900);await tap(p,p.locator('[data-ar]').nth(9));await p.waitForTimeout(700);await tap(p,p.locator('#aName'));await p.keyboard.type('Grace Lee',{delay:60});
    await p.waitForTimeout(300);await tap(p,p.locator('#aGo'));await p.waitForTimeout(1500);await p.evaluate(()=>{const s=document.querySelector('.sched');s&&s.scrollIntoView({block:'start'});scrollBy(0,-120)});await p.waitForTimeout(1300)},tail:600});
  await b.close();
})();
