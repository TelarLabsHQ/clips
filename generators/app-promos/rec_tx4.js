// Tixward promo footage for conferences, workshops and trainings.
const {clip,launch}=require('./rec.js');const fs=require('fs');
const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
let ipn=10;const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.0.0.'+(ipn++),...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(120);await loc.click();};
const at=(d,h,m=0)=>Date.parse(`${d}T${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:00+08:00`);
(async()=>{
  const cf=await post('events',{title:'Future of Learning Summit 2027',organizer:'Bayview Educators Network',contact:'0775 555 0100',currency:'USD',tz:'Asia/Manila',starts_at:at('2027-02-20',9),
    venues:[{name:'Bayview Convention Center',address:'1 Harbor Drive, Bayview'}],cover:rd('conf'),pay_hours:48,
    description:'Two days of talks and hands-on sessions on teaching, technology and wellbeing. Includes lunch, snacks and a certificate of attendance.',
    types:[{name:'Early bird',price:25,qty:60,max_per:5},{name:'Regular',price:40,qty:300,max_per:5},{name:'Student',price:15,qty:80,max_per:2}],
    questions:[{label:'School or organization',type:'choice',required:true,options:['Riverside High School','Bayview Academy','Lakeside College','Oak Park School']}]});
  if(!cf.code) console.log('create failed:',cf);
  const K={'x-org-key':cf.org_key};await post(`org/${cf.code}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Bayview Educators Network',qr:rd('qr'),mine:true},K);
  const CE=await get('events/'+cf.code);const [eb,rg,stu]=CE.types;const m=CE.methods[0];const QQ=CE.questions[0];
  const names=['Olivia Bennett','Noah Patel','Ava Thompson','Liam Garcia','Sophia Nguyen','Ethan Brooks','Mia Rodriguez','Lucas Kim','Isabella Chen','Mason Rivera','Amelia Walker','Logan Foster','Harper Reyes','Elijah Scott','Chloe Tan','James Carter','Grace Lim','Daniel Cruz'];
  for(const [i,n] of names.entries()){const t=[eb,rg,rg,stu][i%4];const o=await post(`events/${cf.code}/order`,{name:n,contact:n.split(' ')[0].toLowerCase()+'@example.com',items:[{t:t.id,q:1}],method:m.id,answers:{[QQ.id]:QQ.options[i%4]}});if(o.error)console.log(o.error)}
  const org=await get('org/'+cf.code,K);for(const o of org.orders) await post(`org/${cf.code}/orders/${o.id}/approve`,{},K);
  const tks=(await get('org/'+cf.code,K)).tickets;
  for(const t of tks.slice(0,7)) await post(`door/${cf.code}/check`,{code:`TXW:${cf.code}:${t.code}`},{'x-door-key':org.event.door_key});
  const scanCode=tks[10].code;
  // workshop sessions
  const ws=await post('events',{title:'Design Thinking for Teams: Hands-on Workshop',organizer:'Bayview Educators Network',contact:'0775 555 0100',currency:'USD',tz:'Asia/Manila',mode:'shows',cover:rd('workshop'),
    venues:[{id:'rooma',name:'Room A'},{id:'roomb',name:'Room B'}],show_close_min:30,
    shows:[[ '2027-02-20',13,'rooma',30],['2027-02-20',13,'roomb',30],['2027-02-21',9,'rooma',30],['2027-02-21',13,'roomb',30]].map(([d,h,v,s])=>({starts_at:at(d,h),venue:v,seats:s})),
    types:[{name:'Workshop seat',price:20},{name:'Student seat',price:10}]});
  await post(`org/${ws.code}/methods`,{kind:'cash'},{'x-org-key':ws.org_key});
  console.log('seeded',cf.code,ws.code);
  const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
  await clip(b,'cf_event',{...phone,url:B+'/e/'+cf.code,setup:async p=>{await p.waitForTimeout(1000)},act:async p=>{
    await p.waitForTimeout(1200);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-70);await smooth(p,y);await p.waitForTimeout(900);
    await tap(p,p.locator('button[aria-label="More Early bird"]'));await p.waitForTimeout(350);await tap(p,p.locator('button[aria-label="More Early bird"]'));await p.waitForTimeout(400);
    await tap(p,p.locator('button[aria-label="More Student"]'));await p.waitForTimeout(1300)},tail:500});
  await clip(b,'cf_q',{...phone,url:B+'/e/'+cf.code,setup:async p=>{await p.waitForTimeout(1000);await p.click('button[aria-label="More Early bird"]');await p.click('button[aria-label="More Early bird"]');await p.waitForTimeout(300);
      await p.evaluate(()=>document.querySelector('#bName').scrollIntoView({block:'start'}));await p.evaluate(()=>scrollBy(0,-90))},act:async p=>{
    await p.waitForTimeout(600);await tap(p,p.locator('#bName'));await p.keyboard.type('Grace Lim',{delay:55});await tap(p,p.locator('#bContact'));await p.keyboard.type('grace@example.com',{delay:40});
    await p.evaluate(()=>document.querySelector('select.bAns').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(500);
    await tap(p,p.locator('select.bAns'));await p.waitForTimeout(400);await p.selectOption('select.bAns','Bayview Academy');await p.waitForTimeout(1300)},tail:500});
  await clip(b,'cf_sessions',{...phone,url:B+'/e/'+ws.code,setup:async p=>{await p.waitForTimeout(1000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-60);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(900);await tap(p,p.locator('.chip.pf',{hasText:'Room B'}));await p.waitForTimeout(900);await tap(p,p.locator('.chip:not(.pf)').filter({visible:true}).first());await p.waitForTimeout(600);
    await tap(p,p.locator('button[aria-label="More Workshop seat"]'));await p.waitForTimeout(1300)},tail:500});
  await clip(b,'cf_list',{w:1280,h:760,url:`${B}/o/#${cf.code}.${cf.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),cf.code);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=att]');await p.waitForTimeout(700);await p.evaluate(()=>scrollTo(0,280))},act:async p=>{
    await p.mouse.move(640,420);await p.waitForTimeout(800);await p.evaluate(()=>scrollTo({top:520,behavior:'smooth'}));await p.waitForTimeout(1100);await p.evaluate(()=>scrollTo({top:280,behavior:'smooth'}));await p.waitForTimeout(900);
    await tap(p,p.locator('#csv'));await p.waitForTimeout(1300)},tail:500});
  await clip(b,'cf_sheet',{w:1280,h:760,url:`${B}/o/#${cf.code}.${cf.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),cf.code);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=att]');await p.waitForTimeout(600);await p.evaluate(()=>scrollTo(0,250))},act:async p=>{
    await p.mouse.move(700,300);await p.waitForTimeout(600);await tap(p,p.locator('#sheetB'));await p.waitForTimeout(1300);await p.evaluate(()=>document.querySelector('#sheetOv').scrollTo({top:260,behavior:'smooth'}));await p.waitForTimeout(1300);
    await p.mouse.move(1150,30,{steps:12});await p.waitForTimeout(900)},tail:500});
  await clip(b,'cf_desk',{...phone,url:`${B}/door/#${cf.code}.${org.event.door_key}`,setup:async p=>{await p.waitForTimeout(1200)},act:async p=>{
    await p.waitForTimeout(600);await tap(p,p.locator('#code'));await p.keyboard.type(scanCode,{delay:65});await p.waitForTimeout(200);await tap(p,p.locator('#man button'));await p.waitForTimeout(2200)},tail:400});
  await b.close();
})();
