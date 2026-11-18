// Tixward promo footage: Zumba in the Park, Saturday sessions with 25 slots each.
const R0=require('./rec.js'),launch=R0.launch,ONLY=process.env.ONLY;const clip=(b,n,o)=>!ONLY||ONLY.split(',').includes(n)?R0.clip(b,n,o):null;
const fs=require('fs');const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
let ipn=10;const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.5.'+Math.floor(ipn/200)+'.'+(ipn++%200),...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(110);await loc.click();};
const FIRST=['Olivia','Noah','Ava','Liam','Sophia','Ethan','Mia','Lucas','Isabella','Mason','Amelia','Logan','Harper','Elijah','Chloe','James','Zoe','Henry','Ella','Jack','Lily','Ryan','Emma','Owen','Nora','Leo','Ruby','Max'];
const LAST=['Bennett','Patel','Thompson','Garcia','Nguyen','Brooks','Turner','Kim','Chen','Rivera','Walker','Foster','Reyes','Scott','Tan','Carter','Lee','Adams','Wright','Miller','Lim','Reed','Wang','Hughes','Price'];
const nm=i=>FIRST[i%FIRST.length]+' '+LAST[(i*7)%LAST.length];
const at=(d,h,m=0)=>Date.parse(`${d}T${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:00+08:00`);
const QA=['Yes, first time!','I’ve joined before'];
(async()=>{
  const ev=await post('events',{title:'Zumba in the Park: Saturday Sessions',organizer:'Coach Mia Turner',contact:'coachmia@example.com',currency:'USD',tz:'Asia/Manila',mode:'shows',show_word:'session',agree:true,cover:rd('zumba'),pay_hours:12,show_close_min:30,
    venues:[{id:'lawn',name:'Lakeside Park, Main Lawn',address:'Lakeside Drive, Bayview'}],
    description:'A one-hour Zumba class in the park with a licensed instructor. All levels welcome, so bring a friend! Wear comfy shoes and bring water and a towel.',
    shows:[['2026-11-28',6,30],['2026-11-28',17,0],['2026-12-05',6,30],['2026-12-05',17,0]].map(([d,h,m])=>({starts_at:at(d,h,m),venue:'lawn',seats:25})),
    types:[{name:'Drop-in',price:5,qty:0,max_per:4},{name:'Student',price:3,qty:0,max_per:4}],
    questions:[{label:'First time doing Zumba?',type:'choice',required:true,options:QA}]});
  if(!ev.code){console.log(ev);process.exit(1)}
  const K={'x-org-key':ev.org_key},C=ev.code;await post(`org/${C}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Mia Turner',qr:rd('qr'),mine:true},K);
  const E=await get('events/'+C);const [drop,stu]=E.types,m=E.methods[0],q=E.questions[0];const S=E.shows;
  const fill=[25,18,9,4];let n=0;
  for(const [si,cnt] of fill.entries()) for(let i=0;i<cnt;i++,n++){const o=await post(`events/${C}/order`,{name:nm(n),contact:nm(n).split(' ')[0].toLowerCase()+n+'@example.com',show:S[si].id,items:[{t:(n%4===3?stu:drop).id,q:1}],method:m.id,answers:{[q.id]:QA[n%3===0?0:1]}});if(o.error)console.log(o.error)}
  const org=await get('org/'+C,K);for(const o of org.orders) await post(`org/${C}/orders/${o.id}/approve`,{},K);
  const O2=await get('org/'+C,K);const shOf={};for(const o of O2.orders)shOf[o.id]=o.show_id;const tk=O2.tickets.filter(t=>shOf[t.order_id]===S[0].id);const door=org.event.door_key;for(const t of tk.slice(0,20)) await post(`door/${C}/check`,{code:`TXW:${C}:${t.code}`},{'x-door-key':door});
  const scan=tk[22].code;console.log('seeded',C,tk.length);
  const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
  await clip(b,'zb_page',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(1200)},act:async p=>{
    await p.waitForTimeout(2000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-60);await smooth(p,y);await p.waitForTimeout(2600)},tail:400});
  await clip(b,'zb_pick',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(1000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-60);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(600);await tap(p,p.locator('.chip:not(.pf)').nth(1));await p.waitForTimeout(600);
    await tap(p,p.locator('button[aria-label="More Drop-in"]'));await p.waitForTimeout(250);await tap(p,p.locator('button[aria-label="More Student"]'));await p.waitForTimeout(350);
    await p.evaluate(()=>document.querySelector('#bName').scrollIntoView({block:'start',behavior:'smooth'}));await p.evaluate(()=>scrollBy(0,-70));await p.waitForTimeout(450);
    await tap(p,p.locator('#bName'));await p.keyboard.type('Grace Lim',{delay:38});await tap(p,p.locator('#bContact'));await p.keyboard.type('0775 555 0142',{delay:30});
    await tap(p,p.locator('select.bAns'));await p.waitForTimeout(200);await p.selectOption('select.bAns',QA[1]);await p.waitForTimeout(250);
    await p.evaluate(()=>document.querySelector('.pName').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(450);
    await tap(p,p.locator('.pName'));await p.keyboard.type('Chloe Tan',{delay:38});await tap(p,p.locator('select.pAns'));await p.waitForTimeout(200);await p.selectOption('select.pAns',QA[0]);await p.waitForTimeout(1000)},tail:400});
  await clip(b,'zb_list',{w:960,h:760,url:`${B}/o/#${C}.${ev.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),C);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=att]');await p.waitForTimeout(700);
      const y=await p.$eval('.ansc',e=>e.getBoundingClientRect().top+scrollY-150);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.mouse.move(400,300);await p.waitForTimeout(1000);await tap(p,p.locator('.ansc',{hasText:'first time'}).first());await p.waitForTimeout(2200)},tail:400});
  await clip(b,'zb_door',{...phone,url:`${B}/door/#${C}.${door}`,setup:async p=>{await p.waitForTimeout(1300)},act:async p=>{
    await p.waitForTimeout(800);await tap(p,p.locator('#code'));await p.keyboard.type(scan,{delay:55});await p.waitForTimeout(150);await tap(p,p.locator('#man button'));await p.waitForTimeout(2300)},tail:400});
  await b.close();
})();
