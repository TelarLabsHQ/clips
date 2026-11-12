const {clip,launch,glide}=require('./rec');const fs=require('fs'),path=require('path');
const DTR='/home/claude/drafttrail/public', D='https://drafttrail.telarlabs.net';
const serveDT=async ctx=>ctx.route(/^https:\/\/drafttrail\.telarlabs\.net\//,r=>{let u=new URL(r.request().url()).pathname;if(u.endsWith('/'))u+='index.html';
  const f=path.join(DTR,u); if(!fs.existsSync(f)) return r.fulfill({status:404,body:''});
  const ct=f.endsWith('.html')?'text/html':f.endsWith('.css')?'text/css':f.endsWith('.js')?'text/javascript':f.endsWith('.woff2')?'font/woff2':f.endsWith('.svg')?'image/svg+xml':'application/octet-stream';
  r.fulfill({status:200,body:fs.readFileSync(f),headers:{'content-type':ct}})});
const W=720,H=1100;
const URL_='/write/?task='+encodeURIComponent('Case study: The River Towns')+'&style=cmos-nb&words=3000&sections='+encodeURIComponent('Background|Problem|Analysis|Recommendation');
async function prep(p,{withCite=false}={}){
  await serveDT(p.context());await p.goto(D+URL_);await p.waitForTimeout(500);
  await p.fill('#sName','Ava Wilson');
  await p.evaluate(()=>{const t=document.querySelector('#essay');t.focus();t.setSelectionRange(13,13)});
  await p.keyboard.type('Before 1850, most river towns were small landings. Steamboats changed that, and trade grew quickly',{delay:0});
  await p.click('.tabs button[data-t=sources]');await p.click('#addSrc');
  await p.selectOption('#fType','book');await p.fill('[data-f=authors]','Smith, Jane');await p.fill('[data-f=title]','The River Towns: Trade and Settlement');await p.fill('[data-f=publisher]','Lakeview Press');await p.fill('[data-f=place]','Chicago');await p.fill('[data-f=year]','2019');await p.click('#srcSave');
  await p.click('#addSrc');await p.selectOption('#fType','journal');await p.fill('[data-f=authors]','Lee, Ann B.; Garcia, Mark');await p.fill('[data-f=title]','Markets on the Water');await p.fill('[data-f=container]','Journal of Economic History');await p.fill('[data-f=volume]','45');await p.fill('[data-f=issue]','2');await p.fill('[data-f=year]','2021');await p.fill('[data-f=pages]','101-130');await p.click('#srcSave');
  await p.click('.tabs button[data-t=outline]');
  const end=await p.evaluate(()=>document.querySelector('#essay').value.indexOf('quickly')+7);
  await p.evaluate(e=>{const t=document.querySelector('#essay');t.focus();t.setSelectionRange(e,e)},end);
  if(withCite){ await p.click('#citeBtn');await p.click('#citeList label:nth-child(1)');await p.fill('#citePg','45');await p.click('#citeGo');await p.keyboard.type('.',{delay:0}); }
  await p.evaluate(()=>scrollTo(0,0));
}
const box=async(p,sel)=>{const b=await p.locator(sel).boundingBox();return [b.x+b.width/2,b.y+b.height/2]};
const clickG=async(p,sel)=>{const [x,y]=await box(p,sel);await glide(p,[[x,y]],14);await p.waitForTimeout(150);await p.mouse.click(x,y);};
(async()=>{const b=await launch();
 // 1 set-up: citation style, word goal, sections
 if(!process.argv[2]||process.argv.includes('dt4_setup')) await clip(b,'dt4_setup',{w:W,h:H,setup:async p=>{await serveDT(p.context());await p.goto(D+'/set-up/');await p.waitForTimeout(500);await p.fill('#suTask','Case study: The River Towns');await p.evaluate(()=>scrollTo(0,330));await p.mouse.move(300,200);},
   act:async p=>{await clickG(p,'#suStyle');await p.selectOption('#suStyle','cmos-nb');await p.waitForTimeout(500);
     await clickG(p,'#suWords');await p.keyboard.type('3000',{delay:90});await p.waitForTimeout(300);
     await clickG(p,'#suSecT');await p.selectOption('#suSecT',{index:2});await p.waitForTimeout(900);}});
 // 2 cite with one click
 if(!process.argv[2]||process.argv.includes('dt4_cite')) await clip(b,'dt4_cite',{w:W,h:H,setup:async p=>{await prep(p);await p.mouse.move(400,600);},
   act:async p=>{await clickG(p,'#citeBtn');await p.waitForTimeout(500);await clickG(p,'#citeList label:nth-child(1)');await p.waitForTimeout(300);
     await clickG(p,'#citePg');await p.keyboard.type('45',{delay:120});await p.waitForTimeout(250);await clickG(p,'#citeGo');await p.keyboard.type('.',{delay:0});await p.waitForTimeout(900);}});
 // 3 pasted quote becomes a cited quote
 if(!process.argv[2]||process.argv.includes('dt4_quote')) await clip(b,'dt4_quote',{w:W,h:H,setup:async p=>{await prep(p,{withCite:true});await p.keyboard.type(' As Smith writes, ',{delay:0});await p.mouse.move(400,600);},
   act:async p=>{await p.waitForTimeout(400);
     await p.evaluate(()=>{const t=document.querySelector('#essay');const s=t.selectionStart;t.dispatchEvent(new InputEvent('beforeinput',{inputType:'insertFromPaste',bubbles:true,cancelable:true}));t.setRangeText('trade, not farming, built these towns',s,s,'end');t.dispatchEvent(new InputEvent('input',{inputType:'insertFromPaste',bubbles:true}))});
     await p.waitForTimeout(1300);await clickG(p,'#qPg');await p.keyboard.type('52',{delay:120});await p.waitForTimeout(300);await clickG(p,'#qYes');await p.waitForTimeout(1500);}});
 // 4 preview with footnotes, then Word
 if(!process.argv[2]||process.argv.includes('dt4_preview')) await clip(b,'dt4_preview',{w:W,h:H,setup:async p=>{await prep(p,{withCite:true});await p.keyboard.type(' By 1870, shipping had tripled.',{delay:0});
     await p.click('#citeBtn');await p.click('#citeList label:nth-child(2)');await p.fill('#citePg','110');await p.click('#citeGo');await p.keyboard.type(' Trade, not farming, built these towns.',{delay:0});
     await p.click('#citeBtn');await p.click('#citeList label:nth-child(1)');await p.fill('#citePg','60');await p.click('#citeGo');await p.mouse.move(400,500);},
   act:async p=>{await clickG(p,'#prevBtn');await p.waitForTimeout(400);await p.fill('#pTitle','Trade and the River Towns');await p.waitForTimeout(900);
     await p.evaluate(async()=>{const d=document.querySelector('#prevOv .dlg');for(let i=0;i<40;i++){d.scrollTop+=12;await new Promise(r=>setTimeout(r,30))}});await p.waitForTimeout(700);
     const [x,y]=await box(p,'#prevWord');await glide(p,[[x,y]],16);await p.waitForTimeout(900);}});
 // 5 review: writing sessions and sources
 if(!process.argv[2]||process.argv.includes('dt4_review')) await clip(b,'dt4_review',{w:W,h:H,setup:async p=>{await serveDT(p.context());await p.goto(D+'/review/');await p.click('#sampleBtn');await p.waitForTimeout(400);await p.click('.sub:has-text("Ava Wilson (sample)")');await p.waitForTimeout(400);
     const y=await p.evaluate(()=>{const e=[...document.querySelectorAll('.lbl')].find(x=>/Writing sessions/.test(x.textContent));return e.getBoundingClientRect().top+scrollY-120});await p.evaluate(y=>scrollTo(0,y),y);await p.mouse.move(360,300);},
   act:async p=>{await p.waitForTimeout(1200);await p.evaluate(async()=>{for(let i=0;i<45;i++){scrollBy(0,9);await new Promise(r=>setTimeout(r,30))}});await p.waitForTimeout(1200);}});
 await b.close();})();
