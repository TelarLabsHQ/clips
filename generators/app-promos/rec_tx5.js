// Tixward promo footage for fun runs.
const R0=require('./rec.js'),launch=R0.launch,ONLY=process.env.ONLY;const clip=(b,n,o)=>!ONLY||ONLY.split(',').includes(n)?R0.clip(b,n,o):null;const fs=require('fs');
const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
let ipn=10;const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.0.1.'+(ipn++),...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(120);await loc.click();};
const at=(d,h,m=0)=>Date.parse(`${d}T${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:00+08:00`);
(async()=>{
  const ev=await post('events',{title:'Run for Bayview Libraries 2027',organizer:'Bayview Runners Club',contact:'0775 555 0188',currency:'USD',tz:'Asia/Manila',starts_at:at('2027-03-07',5,30),
    venues:[{name:'Bayview Bay Walk',address:'Start and finish: Harbor Park, Bayview'}],cover:rd('run'),pay_hours:48,
    description:'A fun run for the whole family. Every race slot includes a race kit with shirt and bib, a finisher medal, and water stations along the route. All proceeds go to new books for Bayview public libraries.',
    types:[{name:'Kids 1K',price:8,qty:100,max_per:4},{name:'3K',price:15,qty:200,max_per:6},{name:'5K',price:20,qty:200,max_per:6},{name:'10K',price:25,qty:150,max_per:4}],
    questions:[{label:'Shirt size',type:'choice',required:true,options:['XS','S','M','L','XL']},{label:'Emergency contact',type:'text',required:true}]});
  if(!ev.code) {console.log('create failed:',ev);process.exit(1)}
  const K={'x-org-key':ev.org_key};await post(`org/${ev.code}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Bayview Runners Club',qr:rd('qr'),mine:true},K);
  const E=await get('events/'+ev.code);const [k1,r3,r5,r10]=E.types;const m=E.methods[0];const SQ=E.questions[0],EQ=E.questions[1];
  const names=['Olivia Bennett','Noah Patel','Ava Thompson','Liam Garcia','Sophia Nguyen','Ethan Brooks','Mia Rodriguez','Lucas Kim','Isabella Chen','Mason Rivera','Amelia Walker','Logan Foster','Harper Reyes','Elijah Scott','Chloe Tan','James Carter','Grace Lim','Daniel Cruz','Emily Wong','Jack Miller','Zoe Lee','Henry Adams'];
  const sizes=['M','L','S','M','XL','L','M','S','XS','M','L','M','S','L','M','XL','S','M','L','M','S','L'];
  for(const [i,n] of names.entries()){const t=[r5,r10,r3,r5,k1,r10][i%6];const o=await post(`events/${ev.code}/order`,{name:n,contact:n.split(' ')[0].toLowerCase()+'@example.com',items:[{t:t.id,q:1}],method:m.id,answers:{[SQ.id]:sizes[i],[EQ.id]:'0775 555 '+String(1100+i*7)}});if(o.error)console.log(o.error)}
  const org=await get('org/'+ev.code,K);for(const o of org.orders) await post(`org/${ev.code}/orders/${o.id}/approve`,{},K);
  const tks=(await get('org/'+ev.code,K)).tickets;
  for(const t of tks.slice(0,6)) await post(`door/${ev.code}/check`,{code:`TXW:${ev.code}:${t.code}`},{'x-door-key':org.event.door_key});
  const scanCode=tks[9].code;
  console.log('seeded',ev.code);
  const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
  await clip(b,'fr_event',{...phone,url:B+'/e/'+ev.code,setup:async p=>{await p.waitForTimeout(1000)},act:async p=>{
    await p.waitForTimeout(1300);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-70);await smooth(p,y);await p.waitForTimeout(900);
    await tap(p,p.locator('button[aria-label="More 5K"]'));await p.waitForTimeout(350);await tap(p,p.locator('button[aria-label="More 5K"]'));await p.waitForTimeout(400);
    await tap(p,p.locator('button[aria-label="More Kids 1K"]'));await p.waitForTimeout(1300)},tail:500});
  await clip(b,'fr_q',{...phone,url:B+'/e/'+ev.code,setup:async p=>{await p.waitForTimeout(1000);await p.click('button[aria-label="More 5K"]');await p.waitForTimeout(300);
      await p.evaluate(()=>document.querySelector('#bName').scrollIntoView({block:'start'}));await p.evaluate(()=>scrollBy(0,-90))},act:async p=>{
    await p.waitForTimeout(500);await tap(p,p.locator('#bName'));await p.keyboard.type('Grace Lim',{delay:50});await tap(p,p.locator('#bContact'));await p.keyboard.type('grace@example.com',{delay:35});
    await p.evaluate(()=>document.querySelector('select.bAns').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(500);
    await tap(p,p.locator('select.bAns'));await p.waitForTimeout(350);await p.selectOption('select.bAns','M');await p.waitForTimeout(450);
    await tap(p,p.locator('input.bAns'));await p.keyboard.type('Mom · 0775 555 0142',{delay:45});await p.waitForTimeout(1100)},tail:500});
  const orgSetup=async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),ev.code);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=att]');await p.waitForTimeout(700)};
  await clip(b,'fr_list',{w:960,h:760,url:`${B}/o/#${ev.code}.${ev.org_key}`,setup:async p=>{await orgSetup(p);const y=await p.$eval('.ansc',e=>e.getBoundingClientRect().top+scrollY-150);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(1000);await tap(p,p.locator('.ansc',{hasText:'M'}).first());await p.waitForTimeout(1500);await tap(p,p.locator('.ansc',{hasText:'L'}).first());await p.waitForTimeout(1400)},tail:500});
  await clip(b,'fr_sheet',{w:1280,h:760,url:`${B}/o/#${ev.code}.${ev.org_key}`,setup:async p=>{await orgSetup(p);await p.evaluate(()=>scrollTo(0,250))},act:async p=>{
    await p.mouse.move(700,300);await p.waitForTimeout(600);await tap(p,p.locator('#sheetB'));await p.waitForTimeout(1300);await p.evaluate(()=>{const o=document.querySelector('#sheetOv'),pg=o.querySelectorAll('.sp')[2]||o.querySelectorAll('.sp')[0];o.scrollTo({top:o.scrollTop+pg.getBoundingClientRect().top-90,behavior:'smooth'})});await p.waitForTimeout(1300);
    await p.mouse.move(1150,30,{steps:12});await p.waitForTimeout(900)},tail:500});
  await clip(b,'fr_desk',{...phone,url:`${B}/door/#${ev.code}.${org.event.door_key}`,setup:async p=>{await p.waitForTimeout(1200)},act:async p=>{
    await p.waitForTimeout(600);await tap(p,p.locator('#code'));await p.keyboard.type(scanCode,{delay:65});await p.waitForTimeout(200);await tap(p,p.locator('#man button'));await p.waitForTimeout(2200)},tail:400});
  await b.close();
})();
