const {clip,write,hand,glide,chromium}=require('./rec');
const U='http://localhost:8881/board/';
const menu=async(p,label)=>{await p.click('#menuBtn');await p.waitForTimeout(250);await p.click(`#menu button:has-text("${label}")`);await p.waitForTimeout(250);await p.keyboard.press('Escape').catch(()=>{});await p.mouse.click(1240,400).catch(()=>{});};
const clear=async p=>{await p.click('#menuBtn');await p.waitForTimeout(200);await p.click('#clearBtn');await p.waitForTimeout(200);await p.click('#cYes');await p.waitForTimeout(200);};
const tool=async(p,t)=>{await p.click(`.tb[data-tool="${t}"]`);await p.waitForTimeout(150);};
const ellipse=(cx,cy,rx,ry,n=40)=>[Array.from({length:n+3},(_,i)=>[cx+rx*Math.cos(i/n*6.4-1.2),cy+ry*Math.sin(i/n*6.4-1.2)])];
(async()=>{const b=await chromium.launch();
 const H=hand({eq:{text:'3 + 4 = 7',x:300,y:330,h:110},hi:{text:'Hello, class!',x:250,y:330,h:110},
   fr:{text:'Today: Fractions',x:200,y:250,h:80},y2:{text:'y = 2x + 1',x:260,y:300,h:100},hw:{text:'Homework: page 25',x:150,y:330,h:66}});
 // a) sample page: laser + circle the answer
 await clip(b,'pp_a',{url:U,setup:async p=>{await p.waitForTimeout(800);await tool(p,'laser');await p.evaluate(()=>window.__cur('ptr'))},cursor:'none',act:async p=>{
   await glide(p,[[760,370],[880,350],[1000,370],[1090,360]],18); await p.waitForTimeout(200);
   await tool(p,'pen'); await p.evaluate(()=>window.__cur('pen')); await write(p,ellipse(1040,362,82,52),{pace:12});}});
 // b) clean whiteboard, write a sum
 await clip(b,'pp_b',{url:U,setup:async p=>{await p.waitForTimeout(800);await clear(p);await tool(p,'pen');},act:async p=>{await write(p,H.eq);
   await write(p,ellipse(915,275,70,80),{pace:10});}});
 // c) blackboard
 await clip(b,'pp_c',{url:U,setup:async p=>{await p.waitForTimeout(800);await clear(p);await menu(p,'Blackboard');await tool(p,'pen');},act:async p=>{await write(p,H.hi,{pace:12,gap:40});}});
 // d) greenboard + grid
 await clip(b,'pp_d',{url:U,setup:async p=>{await p.waitForTimeout(800);await clear(p);await menu(p,'Greenboard');await menu(p,'Grid');await tool(p,'pen');},act:async p=>{await write(p,H.y2,{pace:12,gap:40});}});
 // e) blackboard + lines, homework, then save image
 await clip(b,'pp_e',{url:U,setup:async p=>{await p.waitForTimeout(800);await clear(p);await menu(p,'Blackboard');await menu(p,'Lines');await tool(p,'pen');},act:async p=>{await write(p,H.hw,{pace:10,gap:35});await p.waitForTimeout(300);
   await p.click('#menuBtn');await p.waitForTimeout(900);}});
 // f) toolbar tour on sample page (tools visible)
 await clip(b,'pp_f',{url:U,setup:async p=>{await p.waitForTimeout(800);},cursor:'none',act:async p=>{await p.click('#menuBtn');await p.waitForTimeout(1500);await p.mouse.click(640,300);await p.waitForTimeout(400);}});
 await b.close();})();
