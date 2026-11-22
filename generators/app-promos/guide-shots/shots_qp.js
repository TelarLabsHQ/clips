// Screenshots of QuizPolice for the telarlabs.net guides (sample data only).
const {chromium}=require('playwright');const fs=require('fs');
const B='http://localhost:8960',OUT='/home/claude/shots/guides/',MOCK=fs.readFileSync('/home/claude/promo-apps/mockquiz.html','utf8');
const post=(p,b,h={})=>fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json',...h},body:JSON.stringify(b)}).then(r=>r.json());
const clean=p=>p.evaluate(()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode())if(n.nodeValue.includes('localhost'))n.nodeValue=n.nodeValue.replace(/(https?:\/\/)?localhost:8960/g,'quizpolice.telarlabs.net')});
const names=['Olivia Bennett','Noah Patel','Ava Thompson','Liam Garcia','Sophia Nguyen','Ethan Brooks','Mia Rodriguez','Lucas Kim','Isabella Chen','Mason Rivera','Amelia Walker','Logan Foster','Harper Reyes','Chloe Tan'];
(async()=>{
  const s=await post('sessions',{title:'Science Quiz 3: Plants and Photosynthesis',quiz_url:'https://docs.google.com/forms/d/e/1FAIpQLSc-sample/viewform',max_exits:3,strict:true,sections:['Grade 8 – Acacia','Grade 8 – Molave']});
  const H={'x-student-token':''};const tok=[];
  for(const [i,n] of names.entries()){const j=await post('join',{code:s.code,name:n,section:i%2?'Grade 8 – Molave':'Grade 8 – Acacia'});tok.push(j.token)}
  const ev=(t,b)=>post('me/event',b,{'x-student-token':t});
  // a few realistic exits (ago_ms places them in the past)
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  await ev(tok[6],{kind:'leave',how:'switched tab or app'});await wait(4000);await ev(tok[6],{kind:'back'});
  await ev(tok[1],{kind:'leave',how:'switched tab or app'});await wait(6000);await ev(tok[1],{kind:'back'});
  await ev(tok[6],{kind:'leave',how:'switched tab or app'});await wait(5000);await ev(tok[6],{kind:'back'});
  await ev(tok[4],{kind:'leave',how:'clicked outside the quiz'});await wait(3000);await ev(tok[4],{kind:'back'});
  await ev(tok[6],{kind:'leave',how:'switched tab or app'});await wait(7000);await ev(tok[6],{kind:'back'});
  await ev(tok[9],{kind:'leave',how:'switched tab or app'});await wait(2000);
  await ev(tok[2],{kind:'done'});await ev(tok[11],{kind:'done'});
  for(const t of tok) await fetch(B+'/api/me',{headers:{'x-student-token':t}});
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1200,height:820},deviceScaleFactor:1.5});const p=await ctx.newPage();
  await p.goto(`${B}/teacher/#t=${s.code}.${s.teacher_key}`);await p.waitForTimeout(3500);await clean(p);
  await p.setViewportSize({width:1200,height:900});await p.evaluate(()=>{const e=[...document.querySelectorAll('*')].find(x=>x.textContent.trim()==='ANSWERING'||x.textContent.trim()==='Answering');const y=e.getBoundingClientRect().top+scrollY-70;scrollTo(0,y)});await p.waitForTimeout(400);
  await p.screenshot({path:OUT+'qp-dashboard.png'});console.log('shot qp-dashboard');
  // student join screen on a phone
  const ph=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});const q=await ph.newPage();
  await q.route(/docs\.google\.com/,r=>r.fulfill({status:200,contentType:'text/html',body:MOCK}));
  await q.goto(B+'/join/');await q.fill('#code',s.code);await q.press('#code','Enter');await q.waitForSelector('#name',{state:'visible'});
  await q.fill('#name','Grace Lim');await q.waitForTimeout(400);await clean(q);
  await q.screenshot({path:OUT+'qp-join.png'});console.log('shot qp-join');
  await b.close();
})();
