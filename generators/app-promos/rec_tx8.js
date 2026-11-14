// Tixward promo footage: an alternative to big ticketing sites.
const R0=require('./rec.js'),launch=R0.launch,ONLY=process.env.ONLY;const clip=(b,n,o)=>!ONLY||ONLY.split(',').includes(n)?R0.clip(b,n,o):null;
const B='http://localhost:8895';const smooth=(p,y)=>p.evaluate(y=>scrollTo({top:y,behavior:'smooth'}),y);
(async()=>{
  const b=await launch();const phone={w:390,h:844,mobile:true,cursor:'tap'};
  await clip(b,'cmp_fee',{...phone,url:'http://localhost:8933/fees.html',setup:async p=>{await p.waitForTimeout(600)},act:async p=>{await p.evaluate(()=>window.play());await p.waitForTimeout(3800)},tail:400});
  await clip(b,'cmp_wallets',{...phone,url:B+'/payments/',setup:async p=>{await p.waitForTimeout(800);const y=await p.evaluate(()=>{const h=[...document.querySelectorAll('h2')].find(x=>x.textContent.includes('E-wallets'));return h.getBoundingClientRect().top+scrollY-20});await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(1400);await smooth(p,await p.evaluate(()=>scrollY+420));await p.waitForTimeout(1300);await smooth(p,await p.evaluate(()=>scrollY+420));await p.waitForTimeout(1100)},tail:300});
  await clip(b,'cmp_price',{...phone,url:B+'/pricing/',setup:async p=>{await p.waitForTimeout(800);const y=await p.$eval('table.tbl',e=>e.getBoundingClientRect().top+scrollY-170);await p.evaluate(y=>scrollTo(0,y),y)},act:async p=>{
    await p.waitForTimeout(800);await smooth(p,await p.evaluate(()=>scrollY+60));await p.waitForTimeout(4400)},tail:300});
  await b.close();
})();
