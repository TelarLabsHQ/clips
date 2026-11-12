const {chromium}=require('playwright');(async()=>{const B='http://localhost:8895',S='/home/claude/shots/tx/';const errs=[];let ip=30;
const post=(p,body,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json','cf-connecting-ip':'10.2.0.'+(ip++),...h},body:JSON.stringify(body)}).then(r=>r.json());
const ev=await post('events',{title:'Film Viewing: "Hidden Figures"',organizer:'Riverside High School Science Club',contact:'0775 555 0100',currency:'USD',tz:'Asia/Manila',mode:'shows',venues:[{id:'aud',name:'School Auditorium'}],
  shows:[{starts_at:Date.parse('2026-12-03T09:00:00+08:00'),seats:300,venue:'aud'},{starts_at:Date.parse('2026-12-03T13:00:00+08:00'),seats:300,venue:'aud'}],types:[{name:'Student',price:3}],
  questions:[{label:'Teacher / adviser',type:'choice',options:['Ms. Johnson','Mr. Chen','Mrs. Miller'],required:true},{label:'Section',type:'text'}]});
const K={'x-org-key':ev.org_key};await post(`org/${ev.code}/methods`,{kind:'cash'},K);const E=await (await fetch(B+'/api/events/'+ev.code)).json();const [q1,q2]=E.questions;
const N=[['Ava Thompson','Ms. Johnson','Homeroom 10A'],['Liam Garcia','Ms. Johnson','Homeroom 10A'],['Sophia Nguyen','Ms. Johnson','Homeroom 10A'],['Ethan Brooks','Ms. Johnson','Homeroom 10A'],['Noah Patel','Mr. Chen','Homeroom 10B'],['Lucas Kim','Mr. Chen','Homeroom 10B'],
  ['Harper Reyes','Mr. Chen','Homeroom 10B'],['Mia Rodriguez','Mrs. Miller','Homeroom 10C'],['Chloe Tan','Mrs. Miller','Homeroom 10C'],['James Carter','Mrs. Miller','Homeroom 10C'],['Grace Lim','Mrs. Miller','Homeroom 10C'],['Daniel Cruz','Ms. Johnson','Homeroom 10A']];
for(const [n,t,s] of N) await post(`events/${ev.code}/order`,{name:n,contact:n.split(' ')[0].toLowerCase()+'@example.com',items:[{t:E.types[0].id,q:1}],show:E.shows[0].id,method:E.methods[0].id,answers:{[q1.id]:t,[q2.id]:s}});
const o=await (await fetch(B+'/api/org/'+ev.code,{headers:K})).json();for(const x of o.orders.slice(2)) await post(`org/${ev.code}/orders/${x.id}/approve`,{},K);
const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:900},timezoneId:'Asia/Manila'})).newPage();p.on('pageerror',e=>errs.push(e.message));
await p.goto(B+'/o/');await p.evaluate(c=>localStorage.setItem('tixward.saved.'+c,'true'),ev.code);await p.goto(`${B}/o/#${ev.code}.${ev.org_key}`);await p.waitForTimeout(1200);
await p.click('#tabs button[data-t=att]');await p.waitForTimeout(500);await p.click('#sheetB');await p.waitForTimeout(500);
console.log('pages:',await p.$$eval('.sp',x=>x.map(s=>s.querySelector('.sg')?.textContent+' rows '+s.querySelectorAll('tbody tr:not(.bl)').length).join(' | ')));
await p.screenshot({path:S+'sheet-preview.png'});
await p.emulateMedia({media:'print'});await p.pdf({path:S+'tixward-sample-sign-in-sheet.pdf',format:'A4',printBackground:true,preferCSSPageSize:true});await p.emulateMedia({media:'screen'});
await p.uncheck('#shG');await p.waitForTimeout(200);console.log('ungrouped pages:',await p.$$eval('.sp',x=>x.length),'cols:',await p.$$eval('.sp th',x=>x.map(t=>t.textContent).join('|')));
await p.check('#shU');await p.waitForTimeout(200);console.log('with unpaid rows:',await p.$$eval('.sp tbody tr:not(.bl)',x=>x.length));
await p.click('#shX');await p.waitForTimeout(200);console.log('closed:',await p.isHidden('#sheetOv'));
const m=await (await b.newContext({viewport:{width:390,height:844}})).newPage();await m.goto(`${B}/o/#${ev.code}.${ev.org_key}`);await m.waitForTimeout(1000);await m.click('#sDone').catch(()=>{});await m.click('#tabs button[data-t=att]');await m.waitForTimeout(400);await m.click('#sheetB');await m.waitForTimeout(400);await m.screenshot({path:S+'sheet-phone.png'});
console.log('errors',errs);await b.close()})();
