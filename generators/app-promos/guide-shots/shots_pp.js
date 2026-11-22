// PizarraPad boards for the guides: a blackboard lesson and a sorting activity.
const {chromium}=require('playwright');const OUT='/home/claude/shots/guides/';
let n=0;const id=()=>'g'+(n++);
const T=(x,y,s,z=34,c='ink',b=false)=>({id:id(),t:'t',x,y,s,z,b,c});
const Sh=(k,a,b,c='ink',w=4)=>({id:id(),t:'s',k,c,w,a,b});
const P=(pts,c='ink',w=4,hl=false)=>({id:id(),t:'p',c,w,hl,pen:!hl,pts:pts.map(p=>[p[0],p[1],p[2]??.6])});
const curve=(f,a,b,step=.05)=>{const o=[];for(let t=a;t<=b+1e-9;t+=step)o.push(f(t));return o};
// lesson board
const L=[T(60,40,'Photosynthesis: how plants make food',40,'ink',true),
  P(curve(t=>[60+t*690,98+Math.sin(t*9)*3,.3+.5*Math.sin(t*3)],0,1,.02),'yellow',4),
  // sun
  Sh('circle',[90,150],[190,250],'yellow',5),
  ...[0,1,2,3,4,5,6,7].map(k=>{const a=k*Math.PI/4;return Sh('line',[140+70*Math.cos(a),200+70*Math.sin(a)],[140+100*Math.cos(a),200+100*Math.sin(a)],'yellow',4)}),
  // plant
  P(curve(t=>[520+Math.sin(t*3)*6,560-t*260],0,1),'green',6),
  P(curve(t=>{const a=t*Math.PI;return [520+t*120,420-Math.sin(a)*40]},0,1),'green',4),P(curve(t=>{const a=t*Math.PI;return [520+t*120,420+Math.sin(a)*10]},0,1),'green',4),
  P(curve(t=>{const a=t*Math.PI;return [520-t*110,470-Math.sin(a)*38]},0,1),'green',4),P(curve(t=>{const a=t*Math.PI;return [520-t*110,470+Math.sin(a)*10]},0,1),'green',4),
  P(curve(t=>[380+t*300,565+Math.sin(t*20)*3],0,1,.02),'orange',4),
  // arrows and labels
  Sh('arrow',[225,275],[430,370],'yellow',4),T(300,222,'sunlight',28,'yellow'),
  Sh('arrow',[340,650],[500,578],'blue',4),T(60,640,'water from the roots',26,'blue'),
  Sh('arrow',[820,330],[660,400],'ink',4),T(830,300,'carbon dioxide (CO₂)',26,'ink'),
  Sh('arrow',[640,470],[830,520],'green',4),T(840,505,'oxygen (O₂) out',26,'green'),
  Sh('rect',[880,90],[1220,230],'orange',4),T(900,110,'Word equation',24,'orange',true),
  T(900,150,'water + CO₂',30,'ink'),T(900,190,'→ sugar + oxygen',30,'ink',true),
  P([[905,212],[1150,212]],'yellow',5,true)];
// activity board
const items=[['a goldfish',0],['a rock',1],['a mango tree',0],['a bicycle',1],['a mushroom',0],['a cloud',1]];
const A=[T(60,40,'Sort it out: living or non-living?',40,'ink',true),
  Sh('rect',[60,120],[600,520],'yellow',5),T(90,140,'LIVING',34,'yellow',true),
  Sh('rect',[680,120],[1220,520],'blue',5),T(710,140,'NON-LIVING',34,'blue',true),
  ...items.map(([s,k],i)=>{const r=Math.floor(i/2);return T(k?720:100,220+r*95,'• '+s,32,'ink')}),
  Sh('circle',[78,398],[330,460],'orange',4),T(345,414,'← Why? It grows!',26,'orange'),
  T(60,560,'Your turn: explain one choice in a full sentence.',30,'green'),
  P(curve(t=>[60+t*720,600+Math.sin(t*14)*2,.4],0,1,.02),'green',3)];
(async()=>{const b=await chromium.launch();
  for(const [name,objs,board] of [['pp-lesson',L,'black'],['pp-activity',A,'green']]){
    const c=await b.newContext({viewport:{width:1280,height:760},deviceScaleFactor:1.5});const p=await c.newPage();
    await p.addInitScript(([objs,board])=>{try{localStorage.setItem('pizarrapad.v1',JSON.stringify({pages:[{objs}],page:0,board,tpl:'plain',penOnly:false,lang:'en',tool:'pen',color:'ink',size:1,tsize:1,bold:false,shape:'rect'}))}catch(e){}},[objs,board]);
    await p.goto('http://localhost:8963/board/');await p.waitForTimeout(1500);await p.screenshot({path:OUT+name+'.png'});console.log('shot',name);await c.close()}
  await b.close()})();
