// Tixward promo footage: batch reunion (rn), family reunion (fm), Christmas party (xm).
const R0=require('./rec.js'),launch=R0.launch,ONLY=process.env.ONLY;const clip=(b,n,o)=>!ONLY||ONLY.split(',').some(x=>n.startsWith(x))?R0.clip(b,n,o):null;
const fs=require('fs');const B='http://localhost:8895',W='/home/claude/promo-apps/work/tx/';const rd=n=>fs.readFileSync(W+n+'.b64','utf8');
let ipn=10;const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.4.'+Math.floor(ipn/200)+'.'+(ipn++%200),...h},body:JSON.stringify(body)}).then(r=>r.json());
const get=(p,h={})=>fetch(B+'/api/'+p,{headers:h}).then(r=>r.json());
const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
const tap=async(p,loc)=>{const bb=await loc.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:8});await p.waitForTimeout(110);await loc.click();};
const FIRST=['Olivia','Noah','Ava','Liam','Sophia','Ethan','Mia','Lucas','Isabella','Mason','Amelia','Logan','Harper','Elijah','Chloe','James','Zoe','Henry','Ella','Jack','Grace','Daniel','Lily','Ryan','Emma','Owen','Nora','Leo','Ruby','Max'];
const LAST=['Bennett','Patel','Thompson','Garcia','Nguyen','Brooks','Turner','Kim','Chen','Rivera','Walker','Foster','Reyes','Scott','Tan','Carter','Lee','Adams','Wright','Miller','Lim','Reed','Wang','Hughes','Price'];
const nm=i=>FIRST[i%FIRST.length]+' '+LAST[(i*7)%LAST.length];
const V={
 rn:{cover:'reunion',ev:{title:'Class of 2016 Homecoming & 10th Reunion',organizer:'Bayview High Alumni Association',contact:'alumni@bayviewhigh.example',currency:'USD',starts_at:Date.parse('2026-12-19T10:00:00Z'),
     venues:[{name:'Bayview High School Gym',address:'45 Park Avenue, Bayview'}],pay_hours:24,
     description:'Ten years since graduation! Dinner, a slideshow, a campus tour and a homecoming shirt for every alumnus. Plus-ones are welcome.',
     types:[{name:'Alumni',price:40,qty:200,max_per:4},{name:'Plus-one',price:30,qty:100,max_per:3}],
     questions:[{label:'Section',type:'choice',required:true,options:['Section A','Section B','Section C','Section D','Guest']},{label:'Homecoming shirt size',type:'choice',required:true,options:['S','M','L','XL']}]},
   seed:i=>({t:i%6===5?1:0,a:[['Section A','Section B','Section C','Section D'][i%4],['S','M','L','XL','M','L'][i%6]],pay:i<44}), n:52,
   buy:[[0,1],[1,1]], me:['Grace Lim',['Section B','M']], others:[['Daniel Reed',['Guest','L']]], tap:'Section B'},
 fm:{cover:'family',ev:{title:'Bennett Family Reunion 2026',organizer:'The Bennett Family',contact:'emily.bennett@example.com',currency:'USD',starts_at:Date.parse('2026-12-27T02:00:00Z'),
     venues:[{name:'Lakeside Park, Pavilion 3',address:'Lakeside Drive, Bayview'}],
     description:'Lunch, games for the kids, the family photo and the new reunion shirts. Free for everyone, just sign up so we know how much food to prepare.',
     types:[{name:'Adult',price:0,qty:150,max_per:8},{name:'Kid (12 and under)',price:0,qty:80,max_per:8}],
     questions:[{label:'Family branch',type:'choice',required:true,options:["Robert's family","Susan's family","Michael's family","Anna's family"]},{label:'Reunion shirt size',type:'choice',required:true,options:['Kids S','Kids M','S','M','L','XL']}]},
   seed:i=>({t:i%3===2?1:0,a:[["Robert's family","Susan's family","Michael's family","Anna's family"][i%4],i%3===2?['Kids S','Kids M'][i%2]:['S','M','L','XL','M'][i%5]],pay:true}), n:44,
   buy:[[0,1],[1,1]], me:['Emily Bennett',["Susan's family",'M']], others:[['Lily Bennett',["Susan's family",'Kids M']]], tap:"Susan's family"},
 xm:{cover:'xmas',ev:{title:'Harbor Design Studio Christmas Party',organizer:'Harbor Design Studio',contact:'party@harbordesign.example',currency:'USD',starts_at:Date.parse('2026-12-18T11:00:00Z'),
     venues:[{name:'Rooftop Garden, Harbor Tower',address:'88 Harbor Road, Bayview'}],pay_hours:48,
     description:'Dinner, music and our gift exchange (a $20 gift if you join). Free for the team; plus-ones are $20 to cover their dinner.',
     types:[{name:'Team member',price:0,qty:40,max_per:1},{name:'Plus-one',price:20,qty:25,max_per:1}],
     questions:[{label:'Meal choice',type:'choice',required:true,options:['Chicken','Fish','Vegetarian']},{label:'Joining the gift exchange?',type:'choice',required:true,options:["Yes, I'm in","No, thanks"]}]},
   seed:i=>({t:0,a:[['Chicken','Fish','Chicken','Vegetarian','Fish'][i%5],["Yes, I'm in","Yes, I'm in","No, thanks"][i%3]],pay:true}), n:28,
   buy:[[0,1],[1,1]], me:['Ava Thompson',['Fish',"Yes, I'm in"]], others:[['Noah Kim',['Chicken','No, thanks']]], tap:'Vegetarian'},
};
(async()=>{
 const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
 for(const [k,c] of Object.entries(V)){ if(ONLY&&!ONLY.split(',').some(x=>x.startsWith(k)))continue;
  const ev=await post('events',{...c.ev,tz:'Asia/Manila',agree:true,cover:rd(c.cover)});if(!ev.code){console.log(k,ev);continue}
  const K={'x-org-key':ev.org_key},C=ev.code;
  if(c.ev.types.some(t=>t.price)) await post(`org/${C}/methods`,{kind:'wallet',label:'E-wallet',account_name:c.ev.organizer,qr:rd('qr'),mine:true},K);
  const E=await get('events/'+C);const Q=E.questions,m=(E.methods||[])[0];
  for(let i=0;i<c.n;i++){const s=c.seed(i),ty=E.types[s.t];const o=await post(`events/${C}/order`,{name:nm(i),contact:nm(i).split(' ')[0].toLowerCase()+i+'@example.com',items:[{t:ty.id,q:1}],method:ty.price?m.id:undefined,answers:{[Q[0].id]:s.a[0],[Q[1].id]:s.a[1]}});if(o.error)console.log(k,o.error);s.ok=s.pay}
  const org=await get('org/'+C,K);const payIdx=new Set([...Array(c.n).keys()].filter(i=>c.seed(i).pay));
  for(const o of org.orders) if(o.status!=='approved'){const i=+((o.contact.match(/(\d+)@/)||[])[1]);if(payIdx.has(i)) await post(`org/${C}/orders/${o.id}/approve`,{},K)}
  const tk=(await get('org/'+C,K)).tickets;const door=org.event.door_key;
  for(const t of tk.slice(0,Math.floor(tk.length*0.55))) await post(`door/${C}/check`,{code:`TXW:${C}:${t.code}`},{'x-door-key':door});
  const scan=tk[tk.length-2].code;console.log(k,'seeded',C,tk.length);
  await clip(b,k+'_page',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(1200)},act:async p=>{
    await p.waitForTimeout(2000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-110);await smooth(p,y);await p.waitForTimeout(2600)},tail:400});
  await clip(b,k+'_signup',{...phone,url:B+'/e/'+C,setup:async p=>{await p.waitForTimeout(1000);const y=await p.$eval('#tickets',e=>e.getBoundingClientRect().top+scrollY-110);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(300);for(const [ti,q] of c.buy) for(let j=0;j<q;j++){await tap(p,p.locator(`button[aria-label="More ${E.types[ti].name}"]`));await p.waitForTimeout(220)}
    await p.evaluate(()=>document.querySelector('#bName').scrollIntoView({block:'start',behavior:'smooth'}));await p.evaluate(()=>scrollBy(0,-70));await p.waitForTimeout(450);
    await tap(p,p.locator('#bName'));await p.keyboard.type(c.me[0],{delay:38});await tap(p,p.locator('#bContact'));await p.keyboard.type(c.me[0].split(' ')[0].toLowerCase()+'@example.com',{delay:26});
    const sel=p.locator('select.bAns');for(let j=0;j<2;j++){await tap(p,sel.nth(j));await p.waitForTimeout(180);await sel.nth(j).selectOption(c.me[1][j]);await p.waitForTimeout(200)}
    await p.evaluate(()=>document.querySelector('.pName').scrollIntoView({block:'center',behavior:'smooth'}));await p.waitForTimeout(450);
    await tap(p,p.locator('.pName').first());await p.keyboard.type(c.others[0][0],{delay:38});
    const ps=p.locator('select.pAns');for(let j=0;j<2;j++){await tap(p,ps.nth(j));await p.waitForTimeout(180);await ps.nth(j).selectOption(c.others[0][1][j]);await p.waitForTimeout(200)}
    await p.waitForTimeout(900)},tail:400});
  const orgSetup=async p=>{await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),C);await p.reload();await p.waitForTimeout(1200);await p.click('#tabs button[data-t=att]');await p.waitForTimeout(700)};
  await clip(b,k+'_list',{w:960,h:760,url:`${B}/o/#${C}.${ev.org_key}`,setup:async p=>{await orgSetup(p);const y=await p.$eval('.ansc',e=>e.getBoundingClientRect().top+scrollY-150);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.mouse.move(400,300);await p.waitForTimeout(1000);await tap(p,p.locator('.ansc',{hasText:c.tap}).first());await p.waitForTimeout(2200)},tail:400});
  await clip(b,k+'_sheet',{w:1280,h:760,url:`${B}/o/#${C}.${ev.org_key}`,setup:async p=>{await orgSetup(p);await p.evaluate(()=>scrollTo(0,250))},act:async p=>{
    await p.mouse.move(700,300);await p.waitForTimeout(500);await tap(p,p.locator('#sheetB'));await p.waitForTimeout(1300);
    await p.evaluate(()=>{const o=document.querySelector('#sheetOv'),pg=o.querySelector('.sp');o.scrollTo({top:o.scrollTop+pg.getBoundingClientRect().top-90,behavior:'smooth'})});await p.mouse.move(1180,420,{steps:12});await p.waitForTimeout(1600)},tail:500});
  await clip(b,k+'_door',{...phone,url:`${B}/door/#${C}.${door}`,setup:async p=>{await p.waitForTimeout(1300)},act:async p=>{
    await p.waitForTimeout(800);await tap(p,p.locator('#code'));await p.keyboard.type(scan,{delay:55});await p.waitForTimeout(150);await tap(p,p.locator('#man button'));await p.waitForTimeout(2300)},tail:400});
 }
 await b.close();
})();
