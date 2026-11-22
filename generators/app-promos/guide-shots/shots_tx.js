// Screenshots of Tixward for the telarlabs.net guides (sample data only).
const {chromium}=require('playwright');const fs=require('fs');
const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/',OUT='/home/claude/shots/guides/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
let ipn=10;const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.7.'+Math.floor(ipn/200)+'.'+(ipn++%200),...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const FIRST=['Olivia','Noah','Ava','Liam','Sophia','Ethan','Mia','Lucas','Isabella','Mason','Amelia','Logan','Harper','Elijah','Chloe','James','Zoe','Henry','Ella','Jack','Lily','Ryan','Emma','Owen','Nora','Leo','Ruby','Max'];
const LAST=['Bennett','Patel','Thompson','Garcia','Nguyen','Brooks','Turner','Kim','Chen','Rivera','Walker','Foster','Reyes','Scott','Tan','Carter','Lee','Adams','Wright','Miller','Lim','Reed','Wang','Hughes','Price'];
const nm=i=>FIRST[i%FIRST.length]+' '+LAST[(i*7)%LAST.length];
const at=(d,h,m=0)=>Date.parse(`${d}T${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:00+08:00`);
const clean=p=>p.evaluate(()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode())if(n.nodeValue.includes('localhost'))n.nodeValue=n.nodeValue.replace(/(https?:\/\/)?localhost:8895/g,'tixward.telarlabs.net');
  document.querySelectorAll('input').forEach(i=>{if(i.value.includes('localhost'))i.value=i.value.replace(/https?:\/\/localhost:8895/g,'https://tixward.telarlabs.net')});});
const shot=async(p,name,opt={})=>{await clean(p);await p.waitForTimeout(300);await p.screenshot({path:OUT+name+'.png',...opt});console.log('shot',name)};
const saved=async(p,C)=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),C)};
(async()=>{
  // ---------- Zumba sessions
  const QA=['Yes, first time!','I’ve joined before'];
  const ev=await post('events',{title:'Zumba in the Park: Saturday Sessions',organizer:'Coach Mia Turner',contact:'coachmia@example.com',currency:'USD',tz:'Asia/Manila',mode:'shows',show_word:'session',agree:true,cover:rd('zumba'),pay_hours:12,show_close_min:30,
    venues:[{id:'lawn',name:'Lakeside Park, Main Lawn',address:'Lakeside Drive, Bayview'}],
    description:'A one-hour Zumba class in the park with a licensed instructor. All levels welcome, so bring a friend!',
    shows:[['2026-12-05',6,30],['2026-12-05',17,0],['2026-12-12',6,30],['2026-12-12',17,0]].map(([d,h,m])=>({starts_at:at(d,h,m),venue:'lawn',seats:25})),
    types:[{name:'Drop-in',price:5,qty:0,max_per:4},{name:'Student',price:3,qty:0,max_per:4}],
    questions:[{label:'First time doing Zumba?',type:'choice',required:true,options:QA}]});
  const K={'x-org-key':ev.org_key},C=ev.code;await post(`org/${C}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Mia Turner',qr:rd('qr'),mine:true},K);
  let E=await get('events/'+C);const [drop,stu]=E.types,m=E.methods[0],q=E.questions[0],S=E.shows;
  let n=0;for(const [si,cnt] of [25,18,9,4].entries()) for(let i=0;i<cnt;i++,n++) await post(`events/${C}/order`,{name:nm(n),contact:'0775 555 0'+String(100+n),show:S[si].id,items:[{t:(n%4===3?stu:drop).id,q:1}],method:m.id,answers:{[q.id]:QA[n%3===0?0:1]}});
  let org=await get('org/'+C,K);for(const o of org.orders) await post(`org/${C}/orders/${o.id}/approve`,{},K);
  const O2=await get('org/'+C,K);const shOf={};for(const o of O2.orders)shOf[o.id]=o.show_id;const tk=O2.tickets.filter(t=>shOf[t.order_id]===S[0].id);const door=org.event.door_key;
  for(const t of tk.slice(0,20)) await post(`door/${C}/check`,{code:`TXW:${C}:${t.code}`},{'x-door-key':door});
  // ---------- Reunion with sections
  const SEC=['Section A','Section B','Section C'];
  const ru=await post('events',{title:'Homecoming & 10th Reunion',organizer:'Bayview High Class of 2016',contact:'0775 555 0116',currency:'USD',tz:'Asia/Manila',agree:true,cover:rd('reunion'),pay_hours:48,starts_at:at('2026-12-19',18),
    venues:[{name:'Bayview High School Gym',address:'1 School Road, Bayview'}],description:'Dinner, a slideshow of old photos and a tribute to our teachers. Partners are welcome.',
    types:[{name:'Alumni',price:35,qty:200,max_per:4},{name:'Plus-one',price:30,qty:80,max_per:2}],
    questions:[{label:'Section',type:'choice',required:true,options:SEC},{label:'Meal choice',type:'choice',options:['Chicken','Fish','Vegetarian']}]});
  const RK={'x-org-key':ru.org_key},RC=ru.code;await post(`org/${RC}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Bayview High Class of 2016',qr:rd('qr'),mine:true},RK);
  E=await get('events/'+RC);const [al,po]=E.types,rm=E.methods[0],q1=E.questions[0],q2=E.questions[1];
  const toApprove=[];
  for(let i=0;i<38;i++){const o=await post(`events/${RC}/order`,{name:nm(i+5),contact:'0775 555 0'+String(200+i),items:[{t:(i%5===4||(i>=28&&i<33)?po:al).id,q:1}],method:rm.id,answers:{[q1.id]:SEC[i%3===2?2:(i%2)],[q2.id]:['Chicken','Fish','Vegetarian'][i%3]}});
    if(i<28) toApprove.push(nm(i+5));
    if(i<33&&o.token&&i>=28) await post(`orders/${o.token}/proof`,{ref:'7015 '+String(331000+i*137),shot:rd('receipt')});
    if(i>=33&&o.token) globalThis.reserved=globalThis.reserved||o.token;}
  org=await get('org/'+RC,RK);for(const o of org.orders.filter(o=>toApprove.includes(o.name))) await post(`org/${RC}/orders/${o.id}/approve`,{},RK);
  // ---------- Fundraiser levels
  const fu=await post('events',{title:'Holiday Dinner for the Library',organizer:'Bayview Book Club',contact:'0775 555 0150',currency:'USD',tz:'Asia/Manila',agree:true,cover:rd('dinner'),pay_hours:48,starts_at:at('2026-12-12',19),
    venues:[{name:'Olive Tree Bistro',address:'Harbor Road, Bayview'}],description:'A three-course dinner and live music. Every ticket helps buy new books for the Bayview Library children’s room.',
    types:[{name:'Regular seat',price:25,qty:120,max_per:8},{name:'Supporter seat',price:50,qty:60,max_per:8},{name:'Table of 8',price:180,qty:10,max_per:2},{name:'Volunteer',price:0,qty:20,max_per:1}]});
  await post(`org/${fu.code}/methods`,{kind:'wallet',label:'E-wallet',account_name:'Bayview Book Club',qr:rd('qr'),mine:true},{'x-org-key':fu.org_key});
  await post(`org/${fu.code}/methods`,{kind:'cash'},{'x-org-key':fu.org_key});
  console.log('seeded',C,RC,fu.code);

  const b=await chromium.launch();
  const phone=async()=>{const c=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});return c.newPage()};
  const desk=async(w=1100,h=760)=>{const c=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:1.5});return c.newPage()};
  // 1 zumba: pick a session
  let p=await phone();await p.goto(B+'/e/'+C);await p.waitForTimeout(1200);
  await p.evaluate(()=>{const y=document.querySelector('#tickets').getBoundingClientRect().top+scrollY-20;scrollTo(0,y)});await p.locator('.chip:not(.pf)').nth(1).click();await p.waitForTimeout(400);
  await p.click('button[aria-label="More Drop-in"]');await p.click('button[aria-label="More Student"]');await p.waitForTimeout(300);
  await p.evaluate(()=>{const y=document.querySelector('#tickets').getBoundingClientRect().top+scrollY-20;scrollTo(0,y)});await shot(p,'tx-zumba-sessions');
  // 2 zumba attendees: first-timers
  p=await desk();await p.goto(`${B}/o/#${C}.${ev.org_key}`);await saved(p,C);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=att]');await p.waitForTimeout(800);
  await p.evaluate(()=>scrollTo(0,0));await shot(p,'tx-zumba-attendees',{fullPage:false});
  // 3 door: valid then used
  p=await phone();await p.goto(`${B}/door/#${C}.${door}`);await p.waitForTimeout(1500);
  await p.fill('#code',tk[22].code);await p.click('#man button');await p.waitForTimeout(900);await shot(p,'tx-door-valid');
  await p.waitForTimeout(2500);await p.fill('#code',tk[3].code);await p.click('#man button');await p.waitForTimeout(350);await shot(p,'tx-door-used');
  // 4 reunion attendees grouped by section
  p=await desk();await p.goto(`${B}/o/#${RC}.${ru.org_key}`);await saved(p,RC);await p.reload();await p.waitForTimeout(1200);await shot(p,'tx-reunion-overview');
  await p.click('#tabs button[data-t=pay]');await p.waitForTimeout(900);await shot(p,'tx-payments-to-check');
  await p.click('#tabs button[data-t=att]');await p.waitForTimeout(900);await shot(p,'tx-reunion-attendees');
  // 5 buyer: reserved order, send proof
  p=await phone();await p.goto(`${B}/t/?k=${globalThis.reserved}`);await p.waitForTimeout(1500);await shot(p,'tx-send-proof');
  // 6 buyer: approved ticket
  const anyApproved=(await get('org/'+RC,RK)).orders.find(o=>o.status==='approved');
  // 7 fundraiser levels + event page top
  p=await phone();await p.goto(B+'/e/'+fu.code);await p.waitForTimeout(1500);await shot(p,'tx-event-page');
  await p.evaluate(()=>{const y=document.querySelector('#tickets').getBoundingClientRect().top+scrollY-20;scrollTo(0,y)});await p.waitForTimeout(300);await shot(p,'tx-fundraiser-levels');
  await b.close();
})();
