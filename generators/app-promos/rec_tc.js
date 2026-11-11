const {clip,chromium}=require('./rec');
const U='http://localhost:8890';
const noDl=async p=>p.context().route(/media\.telarlabs\.net/,r=>r.fulfill({status:204,body:''}));
(async()=>{const b=await chromium.launch();
 await clip(b,'tc_home',{w:720,h:1150,url:U+'/',cursor:'none',setup:async p=>{await p.waitForTimeout(1500)},
   act:async p=>{for(let i=0;i<12;i++){await p.mouse.wheel(0,55);await p.waitForTimeout(110)}await p.waitForTimeout(900);}});
 await clip(b,'tc_pick',{w:720,h:1150,url:U+'/category/celebrations-events/',cursor:'none',setup:async p=>{await p.waitForTimeout(1500);
     await p.evaluate(()=>{const a=document.querySelector('a[href*="birthday-balloons-rising-loop"]');a&&a.scrollIntoView({block:'center'})});await p.waitForTimeout(800)},
   act:async p=>{const a=p.locator('a[href*="birthday-balloons-rising-loop"]').first();const bb=await a.boundingBox();await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:10});await p.waitForTimeout(500);
     await p.mouse.down();await p.waitForTimeout(150);await p.mouse.up();await a.click();await p.waitForTimeout(2600);}});
 await clip(b,'tc_dl',{w:720,h:1150,url:U+'/clip/birthday-balloons-rising-loop/',cursor:'none',setup:async p=>{await noDl(p);await p.waitForTimeout(1800)},
   act:async p=>{const d=p.locator('a:has-text("Download")').first();await d.scrollIntoViewIfNeeded();await p.waitForTimeout(700);const bb=await d.boundingBox();
     await p.mouse.move(bb.x+bb.width/2,bb.y+bb.height/2,{steps:10});await p.mouse.down();await p.waitForTimeout(150);await p.mouse.up();
     await d.evaluate(a=>{a.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))}).catch(()=>{});await p.waitForTimeout(2200);}});
 await b.close();})();
