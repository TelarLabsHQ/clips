// Tixward promo footage: small events (paid workshop with 40 seats, free seminar with 60 seats).
const R0=require('./rec.js'),launch=R0.launch,ONLY=process.env.ONLY;const clip=(b,n,o)=>!ONLY||ONLY.split(',').includes(n)?R0.clip(b,n,o):null;
const fs=require('fs');const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
let ipn=10;const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.1.'+Math.floor(ipn/200)+'.'+(ipn++%200),...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(120);await loc.click();};
const NAMES=['Olivia Bennett','Noah Patel','Ava Thompson','Liam Garcia','Sophia Nguyen','Ethan Brooks','Mia Turner','Lucas Kim','Isabella Chen','Mason Rivera','Amelia Walker','Logan Foster','Harper Reyes','Elijah Scott','Chloe Tan','James Carter','Zoe Lee','Henry Adams','Ella Wright','Jack Miller'];
(async()=>{
  // ---------- paid workshop, 40 seats ----------
  const ws=await post('events',{title:'Watercolor Workshop for Beginners',organizer:'Harbor Arts Society',contact:'hello@harborarts.example',currency:'USD',tz:'Asia/Manila',starts_at:Date.parse('2026-12-05T02:00:00Z'),agree:true,
    venues:[{name:'Harbor Hall, Room 2',address:'12 Bay Road, Harbor City'}],cover:rd('workshop'),pay_hours:24,
    description:'A relaxed two-hour class for beginners. All paints and paper included.',types:[{name:'Workshop seat',price:15,qty:40,max_per:4}]});
  const WK={'x-org-key':ws.org_key};await post(`org/${ws.code}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Harbor Arts Society',qr:rd('qr'),mine:true},WK);
  const WE=await get('events/'+ws.code);const seat=WE.types[0],wm=WE.methods[0];
  let n=0;for(let i=0;i<9;i++){const q=i<8?4:3;const o=await post(`events/${ws.code}/order`,{name:NAMES[i],contact:`p${i}@example.com`,items:[{t:seat.id,q}],method:wm.id});if(o.error)console.log(o.error);n+=q}
  let org=await get('org/'+ws.code,WK);for(const o of org.orders) await post(`org/${ws.code}/orders/${o.id}/approve`,{},WK);
  const em=await post(`events/${ws.code}/order`,{name:'Emma Johnson',contact:'emma@example.com',items:[{t:seat.id,q:2}],method:wm.id});await post(`orders/${em.token}/proof`,{ref:'1012 345 678901',shot:rd('receipt')});
  // now 35 + 2 = 37 taken → 3 left
  // ---------- free seminar, 60 seats ----------
  const sm=await post('events',{title:'Free Parenting Seminar',organizer:'Bayview Parents Association',contact:'parents@bayview.example',currency:'USD',tz:'Asia/Manila',starts_at:Date.parse('2026-12-06T01:00:00Z'),agree:true,
    venues:[{name:'Bayview Library, Hall B',address:'8 Elm Street, Bayview'}],cover:rd('seminar'),
    description:'A free morning seminar on helping kids with screen time and study habits. Seats are limited to the size of the hall.',types:[{name:'Free seat',price:0,qty:60,max_per:4}]});
  const SK={'x-org-key':sm.org_key};const SE=await get('events/'+sm.code);const fseat=SE.types[0];
  for(let i=0;i<14;i++){const o=await post(`events/${sm.code}/order`,{name:NAMES[(i+3)%NAMES.length],contact:`s${i}@example.com`,items:[{t:fseat.id,q:4}]});if(o.error)console.log(o.error)}
  const o57=await post(`events/${sm.code}/order`,{name:'Henry Adams',contact:'henry@example.com',items:[{t:fseat.id,q:2}]});
  // 58 taken → 2 left
  const sorg=await get('org/'+sm.code,SK);const door=sorg.event.door_key;
  console.log('seeded',ws.code,sm.code);
  const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
  await clip(b,'sm_chat',{...phone,url:'http://localhost:8933/chat.html',setup:async p=>{await p.waitForTimeout(600)},act:async p=>{await p.evaluate(()=>window.play());await p.waitForTimeout(3600)},tail:400});
  await clip(b,'sm_left',{...phone,url:B+'/e/'+ws.code,setup:async p=>{await p.waitForTimeout(1000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-120);await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(300)},act:async p=>{
    await p.waitForTimeout(1300);
    for(let i=0;i<3;i++){const o=await post(`events/${ws.code}/order`,{name:NAMES[10+i],contact:`x${i}@example.com`,items:[{t:seat.id,q:1}],method:wm.id});if(o.error)console.log(o.error)}
    await p.evaluate(()=>load());await p.waitForTimeout(1700)},tail:400});
  await clip(b,'sm_approve',{...phone,url:`${B}/o/#${ws.code}.${ws.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),ws.code);await p.reload();await p.waitForTimeout(1300);
      await p.click('#tabs button[data-t=pay]');await p.waitForTimeout(700);await p.evaluate(()=>{const t=document.querySelector('#tabs');scrollTo(0,t.getBoundingClientRect().top+scrollY-10)})},act:async p=>{
    await p.waitForTimeout(900);const ap=p.locator('button',{hasText:'Approve'}).filter({hasText:/^Approve$/}).first();await tap(p,ap);await p.waitForTimeout(1800)},tail:400});
  await clip(b,'sm_free',{...phone,url:B+'/e/'+sm.code,setup:async p=>{await p.waitForTimeout(1000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-120);await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(300)},act:async p=>{
    await p.waitForTimeout(700);await tap(p,p.locator('button[aria-label="More Free seat"]'));await p.waitForTimeout(250);await tap(p,p.locator('button[aria-label="More Free seat"]'));await p.waitForTimeout(400);
    await p.evaluate(()=>document.querySelector('#bName').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(500);
    await tap(p,p.locator('#bName'));await p.keyboard.type('Grace Lim',{delay:45});await tap(p,p.locator('#bContact'));await p.keyboard.type('grace@example.com',{delay:30});await p.waitForTimeout(200);
    const go=p.locator('#buy button[type=submit], #buy button.pri').last();await go.scrollIntoViewIfNeeded();await tap(p,go);await p.waitForTimeout(2600)},tail:500});
  // door: check in 41 of 60, then scan one more
  const sorg2=await get('org/'+sm.code,SK);const tk=sorg2.tickets;console.log('tickets',tk.length);
  for(const t of tk.slice(0,41)) await post(`door/${sm.code}/check`,{code:`TXW:${sm.code}:${t.code}`},{'x-door-key':door});
  const scan=tk[45].code;
  await clip(b,'sm_door',{...phone,url:`${B}/door/#${sm.code}.${door}`,setup:async p=>{await p.waitForTimeout(1300)},act:async p=>{
    await p.waitForTimeout(800);await tap(p,p.locator('#code'));await p.keyboard.type(scan,{delay:55});await p.waitForTimeout(150);await tap(p,p.locator('#man button'));await p.waitForTimeout(1500);
    const nx=p.locator('button',{hasText:'Next'}).first();if(await nx.count()){await tap(p,nx);}await p.waitForTimeout(1500)},tail:400});
  await b.close();
})();
