const {clip,launch}=require('./rec.js');const B='http://localhost:8895',A={'x-admin-key':'test-admin-key'};
(async()=>{const evs=(await (await fetch(B+'/api/admin',{headers:A})).json()).events;
  const order=['Harbor Lights Concert','Sunset Strings on the Steps','Jakarta Indie Night','Lantern Festival Show','Spring Choir Concert'].map(t=>evs.find(e=>e.title===t).code);
  const b=await launch();
  await clip(b,'tx_cur',{w:390,h:844,mobile:true,cursor:'tap',url:B+'/e/'+order[0],setup:async p=>{await p.waitForTimeout(1000);
      // preload the other events so switching is instant
      await p.evaluate(async cs=>{window.__ev=[];for(const c of cs) window.__ev.push(await api('events/'+c))},order.slice(1))},act:async p=>{
    for(let i=0;i<order.length-1;i++){await p.waitForTimeout(1250);await p.evaluate(i=>{E=window.__ev[i];CUR=E.currency;TZ=E.tz||undefined;render();scrollTo(0,0)},i)} await p.waitForTimeout(1300)},tail:300});
  await b.close()})();
