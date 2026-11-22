const {chromium}=require('playwright');const OUT='/home/claude/shots/guides/';
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:1200,height:860},deviceScaleFactor:1.5});const p=await c.newPage();
 await p.goto('http://localhost:8962/review/');await p.waitForTimeout(800);
 await p.setInputFiles('input[type=file]',['/home/claude/promo-apps/files/alex.drafttrail','/home/claude/promo-apps/files/sam.drafttrail']);await p.waitForTimeout(2000);
 await p.screenshot({path:OUT+'dt-review-list.png'});
 await p.locator('text=Alex Rivera').first().click();await p.waitForTimeout(1500);await p.screenshot({path:OUT+'dt-review-flagged.png'});
 await p.locator('text=Sam Lee').first().click();await p.waitForTimeout(1500);await p.screenshot({path:OUT+'dt-review-clean.png'});
 await b.close()})();
