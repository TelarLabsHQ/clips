// Extra Tixward promo footage: currencies, screenings, custom slots, blocking, front desk.
const {clip,launch}=require('./rec.js');const fs=require('fs');
const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json',...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(120);await loc.click();};
const day=n=>Date.parse(new Date(Date.now()+n*864e5).toISOString().slice(0,10)+'T00:00:00+08:00');
(async()=>{
  // ---------- events in several currencies ----------
  const cur=[];
  for(const [t,o,c,pr,img,v] of [['Harbor Lights Concert','Harbor Arts Society','USD',15,'cover','Harbor Hall'],['Sunset Strings on the Steps','Aegean Music Circle','EUR',12,'santorini','Old Town Steps'],
      ['Jakarta Indie Night','Kota Sound Collective','IDR',150000,'alley','Lantern Lane Hall'],['Lantern Festival Show','Golden Lantern Arts','CNY',80,'lantern','Riverside Pavilion'],['Spring Choir Concert','Blossom Choir Society','PHP',500,'sakura','Garden Chapel']]){
    const e=await post('events',{title:t,organizer:o,currency:c,tz:'Asia/Manila',starts_at:day(30)+19*36e5,venues:[{name:v}],cover:rd(img),types:[{name:'General',price:pr,qty:300}]});
    await post(`org/${e.code}/methods`,{kind:'cash'},{'x-org-key':e.org_key});cur.push(e.code);
  }
  // ---------- a film showing with several screenings in two places ----------
  const f=await post('events',{title:'Lakeview Film Week: "The Long Way Home"',organizer:'Lakeview Film Club',currency:'USD',tz:'Asia/Manila',mode:'shows',cover:rd('film'),
    venues:[{id:'hall1',name:'Lakeview Cinema, Hall 1'},{id:'libr1',name:'Oak Park Library'}],show_close_min:15,
    shows:[[1,14,'hall1',120],[1,17,'hall1',120],[1,19.5,'libr1',40],[2,14,'hall1',120],[2,19.5,'libr1',40]].map(([d,h,v,s])=>({starts_at:day(d)+h*36e5,venue:v,seats:s})),
    types:[{name:'Regular',price:8},{name:'Student',price:5}]});
  await post(`org/${f.code}/methods`,{kind:'cash'},{'x-org-key':f.org_key});
  // ---------- custom time slots ----------
  const ten=await post('events',{mode:'book',title:'Lakeside Tennis Club',organizer:'Lakeside Tennis Club',currency:'USD',venues:[{id:'v1',name:'Lakeside Park'}],
    book:{tz:'Asia/Manila',style:'custom',slot:60,max_slots:2,max_per:3,ahead:30,notice:60,hours:[],extra:[],off:[],
      sets:[{days:[1,2,3,4,5,6],slots:[[480,540],[540,600],[600,720],[720,780],[780,900],[900,1020],[1020,1140],[1140,1260]]},{days:[0],slots:[[420,540],[540,660],[660,780]]}],
      res:[{name:'Court A',price:10},{name:'Court B',price:10}],pay_now:false,pay_site:true}});
  // ---------- courts: blocking and front desk ----------
  const bk=await post('events',{mode:'book',title:'Riverside Badminton Courts',organizer:'Riverside Sports Club',currency:'USD',venues:[{id:'v1',name:'Riverside Sports Center'}],
    book:{tz:'Asia/Manila',style:'equal',slot:60,max_slots:3,max_per:3,ahead:30,notice:60,hours:Array(7).fill([480,1320]),extra:[],off:[],
      res:[{name:'Court 1',price:12},{name:'Court 2',price:12},{name:'Court 3 (indoor)',price:15}],pay_now:false,pay_site:true}});
  const BK={'x-org-key':bk.org_key};const BE=await get('events/'+bk.code);const R=BE.book.res;const today=BE.book.today;const tom=new Date(Date.parse(today+'T00:00:00Z')+864e5).toISOString().slice(0,10);
  for(const [r,s,n,who,paid] of [[0,540,2,'Ava Brooks',true],[1,900,1,'Ethan Park',false],[2,1080,2,'Lucas Kim',false],[0,1200,1,'Mia Torres',true]]) await post(`org/${bk.code}/book`,{res:R[r].id,date:today,start:s,slots:n,name:who,contact:'x',paid},BK);
  for(const [r,s,n,who] of [[0,1080,2,'Ava Brooks'],[1,1020,1,'Ethan Park'],[0,600,2,'Olivia Reyes'],[2,1140,2,'Lucas Kim'],[1,720,1,'Grace Lee']]) await post(`org/${bk.code}/book`,{res:R[r].id,date:tom,start:s,slots:n,name:who,contact:'x',paid:false},BK);
  const door=(await get('org/'+bk.code,BK)).event.door_key;
  console.log('seeded');
  const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
  await clip(b,'tx_cur',{...phone,url:B+'/e/'+cur[0],setup:async p=>{await p.waitForTimeout(1000)},act:async p=>{
    for(const c of cur.slice(1)){await p.waitForTimeout(1250);await p.goto(B+'/e/'+c);await p.waitForSelector('.from');await p.waitForTimeout(150);} await p.waitForTimeout(1300)},tail:300});
  await clip(b,'tx_shows',{...phone,url:B+'/e/'+f.code,setup:async p=>{await p.waitForTimeout(1000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-60);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(900);await tap(p,p.locator('.chip.pf',{hasText:'Oak Park Library'}));await p.waitForTimeout(800);await tap(p,p.locator('.chip.pf',{hasText:'All places'}));await p.waitForTimeout(500);
    await tap(p,p.locator('.chip:not(.pf)').nth(1));await p.waitForTimeout(700);await tap(p,p.locator('button[aria-label="More Regular"]'));await p.waitForTimeout(300);await tap(p,p.locator('button[aria-label="More Student"]'));await p.waitForTimeout(1200)},tail:500});
  await clip(b,'bk_custom',{...phone,url:B+'/b/'+ten.code,setup:async p=>{await p.waitForTimeout(900);const d=p.locator('.day:not([disabled])');let k=1;for(;k<8;k++){if(!/SUN/i.test(await d.nth(k).textContent()))break}await d.nth(k).click();await p.waitForTimeout(300);await p.evaluate(()=>document.querySelector('.slots').scrollIntoView({block:'start'}));await p.evaluate(()=>scrollBy(0,-80))},act:async p=>{
    await p.waitForTimeout(900);await tap(p,p.locator('.slot',{hasText:/^9:00 AM/}));await p.waitForTimeout(700);await tap(p,p.locator('.len').nth(1));await p.waitForTimeout(600);
    await p.evaluate(()=>document.querySelector('.sum').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(1400)},tail:500});
  await clip(b,'bk_block',{w:1280,h:760,url:`${B}/o/#${bk.code}.${bk.org_key}`,setup:async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),bk.code);await p.reload();await p.waitForTimeout(1200);await p.fill('#bDate',tom);await p.dispatchEvent('#bDate','change');await p.waitForTimeout(400);await p.evaluate(()=>document.querySelector('.sched').scrollIntoView({block:'start'}));await p.evaluate(()=>scrollBy(0,-120))},act:async p=>{
    await p.mouse.move(640,300);await p.waitForTimeout(700);await tap(p,p.locator('#bBlock'));await p.waitForTimeout(500);await p.selectOption('#aR',{index:2});await p.waitForTimeout(250);await p.selectOption('#aS','480');await p.waitForTimeout(200);await p.selectOption('#aN','3');await p.waitForTimeout(300);
    await tap(p,p.locator('#aName'));await p.keyboard.type('Maintenance',{delay:60});await p.waitForTimeout(300);await tap(p,p.locator('#aGo'));await p.waitForTimeout(1400);await p.evaluate(()=>{document.querySelector('.sched').scrollIntoView({block:'start'});scrollBy(0,-120)});await p.waitForTimeout(1300)},tail:500});
  await clip(b,'bk_desk',{...phone,url:`${B}/door/#${bk.code}.${door}`,setup:async p=>{await p.waitForTimeout(1200);const y=await p.$eval('#main .panel:nth-child(3)',e=>e.getBoundingClientRect().top+scrollY-20).catch(()=>300);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(1200);await tap(p,p.locator('[data-o]',{hasText:'Collect'}).first());await p.waitForTimeout(1100);await tap(p,p.locator('#paid'));await p.waitForTimeout(1800)},tail:400});
  await b.close();
})();
