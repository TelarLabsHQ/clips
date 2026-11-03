const {clip,chromium}=require('./rec');
const U='http://localhost:8875/stories-demo/';
const CSS=`#cv{position:fixed!important;left:0;top:0;width:1280px!important;height:720px!important;z-index:2147483646;max-width:none!important}body{overflow:hidden}`;
async function scene(b,name,story,i,ms){
 await clip(b,name,{w:1280,h:720,url:U,cursor:'none',setup:async p=>{
   await p.evaluate(()=>{try{localStorage.setItem('ts-help','1')}catch(e){}});await p.reload();await p.waitForTimeout(1500);
   await p.evaluate(s=>{document.querySelector(`.sb-chips button[data-s=${s}]`).click();document.getElementById('sbYes').click();},story);
   await p.waitForTimeout(3500);
   await p.evaluate(i=>{document.querySelector(`#strip .scene:nth-child(${i})`).click();
     for(const id of ['caption','title']){const e=document.getElementById(id);e.value='';e.dispatchEvent(new Event('input'));}},i);
   await p.addStyleTag({content:CSS});await p.waitForTimeout(600);
   await p.evaluate(()=>document.getElementById('playScene').click());await p.waitForTimeout(150);
 },act:async p=>{await p.waitForTimeout(ms);},tail:0});
}
(async()=>{const b=await chromium.launch();
 await scene(b,'st2_star','xmas',10,4500);
 await scene(b,'st2_angel','xmas',2,4500);
 await scene(b,'st2_gift','gift',9,4500);
 await scene(b,'st2_cookies','gift',8,4000);
 await scene(b,'st2_sheep','sheep',9,4000);
 await scene(b,'st2_mira','mira',8,4000);
 await b.close();})();
