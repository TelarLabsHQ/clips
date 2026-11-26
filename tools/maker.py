"""Greeting video maker (/make/greeting-video/): a Telar Clips background + your message -> MP4, made in the browser.
Backgrounds are 1080p copies with a keyframe every half second in public/media/maker/ (same site, so the page can draw them)."""

BGS = [  # id, short title, occasions it suits, has a native 9:16 copy
 ('snowy-christmas-tree-forest-night-loop', 'Snowy Christmas forest', 'xmas pasko', True),
 ('snow-globe-swirling-snow-loop', 'Snow globe', 'xmas pasko', True),
 ('christmas-red-green-bokeh-loop', 'Christmas bokeh', 'xmas pasko', False),
 ('twinkling-christmas-string-lights-loop', 'String lights', 'xmas pasko ny', False),
 ('gold-stars-falling-christmas-loop', 'Falling gold stars', 'xmas pasko congrats', False),
 ('parol-light-sequence-loop', 'Parol lights', 'pasko xmas', False),
 ('falling-snow-night-loop', 'Falling snow', 'xmas', False),
 ('northern-lights-snowy-mountains-loop', 'Northern lights', 'xmas ny', True),
 ('new-year-fireworks-city-loop', 'City fireworks', 'ny congrats', False),
 ('champagne-gold-bubbles-rising-loop', 'Champagne bubbles', 'ny congrats bday', False),
 ('gold-silver-new-year-confetti-loop', 'New Year confetti', 'ny congrats', False),
 ('birthday-balloons-rising-loop', 'Birthday balloons', 'bday', False),
 ('celebration-confetti-loop', 'Confetti', 'bday congrats', False),
 ('floating-hearts-loop', 'Floating hearts', 'love thanks bday', False),
 ('golden-bokeh-lights-loop', 'Golden bokeh', 'thanks congrats ny bday love xmas', False),
 ('golden-sunset-clouds-loop', 'Golden sunset', 'thanks love', False),
]

LANGS = [('en', 'English'), ('fil', 'Filipino'), ('es', 'Español'), ('fr', 'Français'), ('de', 'Deutsch')]
OCC = [  # key, chip, [(language, greeting, message)]; the first is the default
 ('xmas', '🎄 Christmas', [
   ('en', 'Merry Christmas!', 'Wishing you peace, joy and love this season and all year long.'),
   ('fil', 'Maligayang Pasko!', 'At Manigong Bagong Taon sa inyong lahat!'),
   ('es', '¡Feliz Navidad!', 'Les deseamos paz, alegría y amor en estas fiestas y todo el año.'),
   ('fr', 'Joyeux Noël !', 'Paix, joie et amour pour les fêtes et toute l’année.'),
   ('de', 'Frohe Weihnachten!', 'Frieden, Freude und Liebe für die Feiertage und das ganze Jahr.')]),
 ('ny', '🎆 New Year', [
   ('en', 'Happy New Year 2027!', 'Cheers to new beginnings, good health and many happy moments.'),
   ('fil', 'Manigong Bagong Taon!', 'Nawa’y puno ng biyaya at saya ang 2027.'),
   ('es', '¡Feliz Año Nuevo 2027!', 'Que el nuevo año traiga salud, amor y alegría.'),
   ('fr', 'Bonne année 2027 !', 'Santé, bonheur et réussite pour la nouvelle année.'),
   ('de', 'Frohes neues Jahr 2027!', 'Gesundheit, Glück und Erfolg im neuen Jahr.')]),
 ('bday', '🎂 Birthday', [('en', 'Happy Birthday!', 'Wishing you a wonderful year ahead, full of laughter and love.')]),
 ('thanks', '🙏 Thank you', [('en', 'Thank You!', 'We’re so grateful for your kindness and support.')]),
 ('congrats', '🎉 Congratulations', [('en', 'Congratulations!', 'So proud of you. Here’s to your next adventure!')]),
 ('love', '💗 Love', [('en', 'With Love', 'You make every day brighter.')]),
]

HEAD = ('<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Great+Vibes&family=Poppins:wght@600;800&family=Baloo+2:wght@800&display=swap" rel="stylesheet">'
        '<script src="/assets/mp4-muxer.js" defer></script>')

def body(V):
    import json
    bgs = json.dumps([dict(id=i, t=t, o=o.split(), v=v) for i, t, o, v in BGS])
    occ = json.dumps([dict(k=k, l=l, v=[dict(c=c, h=h, m=m) for c, h, m in vs]) for k, l, vs in OCC], ensure_ascii=False)
    langs = json.dumps(dict(LANGS), ensure_ascii=False)
    return f'''
<section class="wrap mk">
  <p class="crumb"><a href="/">Telar Clips</a> › Greeting video maker</p>
  <h1>Greeting video maker</h1>
  <p class="lead">Put your message on a moving Christmas, New Year, birthday or thank-you background and download it as an MP4. Free, no sign-up, made right on your device.</p>
  <div class="mk-grid">
    <div class="mk-stage"><div class="mk-frame" id="frame"><canvas id="cv" width="1920" height="1080"></canvas></div>
      <div class="mk-row"><button class="btn btn-sm" id="play" type="button">❚❚ Pause</button><span class="muted" id="info"></span></div></div>
    <div class="mk-panel">
      <div class="mk-step"><h2>1. Occasion</h2><div class="chips" id="occ"></div><div class="chips mk-lang" id="lang"></div></div>
      <div class="mk-step"><h2>2. Background</h2><div class="mk-bgs" id="bgs"></div></div>
      <div class="mk-step"><h2>3. Your message</h2>
        <label>Greeting<input id="tH" maxlength="40"></label>
        <label>Message<textarea id="tM" maxlength="160" rows="3"></textarea></label>
        <label>From <span class="muted">(optional)</span><input id="tF" maxlength="50" placeholder="e.g. The Lee Family"></label></div>
      <div class="mk-step"><h2>4. Style</h2>
        <div class="mk-two"><label>Font<select id="sF"><option value="serif">Elegant</option><option value="script">Script</option><option value="sans">Modern</option><option value="fun">Playful</option></select></label>
        <label>Position<select id="sP"><option value="mid">Middle</option><option value="up">Top</option><option value="low">Bottom</option></select></label></div>
        <div class="mk-cols" id="cols"></div></div>
      <div class="mk-step"><h2>5. Size and length</h2>
        <div class="mk-two"><label>Shape<select id="sS"><option value="h">Landscape 16:9 (YouTube, TV)</option><option value="v">Portrait 9:16 (Stories, TikTok, Reels)</option><option value="sq">Square 1:1 (Facebook, Instagram)</option></select></label>
        <label>Length<select id="sL"><option value="8">8 seconds</option><option value="15" selected>15 seconds</option><option value="30">30 seconds</option></select></label></div>
        <label class="mk-chk"><input type="checkbox" id="sB" checked> Add a small “Made with Telar Clips” note</label></div>
      <button class="btn mk-go" id="go" type="button">⬇ Download MP4</button>
      <div class="mk-prog" id="prog" hidden><div><i id="bar"></i></div><span id="pt">Making your video…</span></div>
      <p class="muted small" id="done"></p>
    </div>
  </div>
</section>
<video id="vid" muted playsinline loop preload="auto" crossorigin="anonymous" style="display:none"></video>
<style>
.mk h1{{margin:6px 0 8px}}.mk .lead{{max-width:760px}}
.mk-grid{{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:24px;align-items:start;margin-top:18px}}@media(max-width:900px){{.mk-grid{{grid-template-columns:1fr}}}}
.mk-stage{{position:sticky;top:76px;display:flex;flex-direction:column;gap:10px}}@media(max-width:900px){{.mk-stage{{position:static}}}}
.mk-frame{{display:flex;justify-content:center;background:#0b0a0e;border:1px solid var(--line);border-radius:14px;padding:10px}}.mk-frame canvas{{max-width:100%;max-height:68vh;border-radius:8px;display:block;height:auto}}
.mk-row{{display:flex;gap:12px;align-items:center}}
.mk-panel{{display:flex;flex-direction:column;gap:14px}}.mk-step{{background:var(--bg2);border:1px solid var(--line);border-radius:14px;padding:14px;display:flex;flex-direction:column;gap:10px}}.mk-step h2{{font-size:17px;margin:0}}
.mk label{{display:flex;flex-direction:column;gap:5px;font-weight:600;font-size:14px}}.mk input,.mk textarea,.mk select{{font:inherit;font-size:16px;padding:9px 10px;border-radius:10px;border:1px solid var(--line);background:#16131c;color:var(--text);min-width:0;width:100%}}
.mk-two{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}}
.mk .chips{{display:flex;flex-wrap:wrap;gap:8px}}.mk [hidden]{{display:none!important}}.mk .mk-lang{{margin-top:2px}}.mk .mk-lang button{{padding:5px 11px;font-size:13px}}.mk .chips button{{border:1px solid var(--line);background:#16131c;color:var(--text);border-radius:99px;padding:7px 12px;font:inherit;font-size:14px;cursor:pointer}}.mk .chips button[aria-pressed=true]{{border-color:var(--accent);background:var(--accent);color:#1b1206;font-weight:700}}
.mk-bgs{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}}@media(max-width:480px){{.mk-bgs{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}
.mk-bgs button{{padding:0;border:2px solid transparent;border-radius:9px;overflow:hidden;background:#000;cursor:pointer;position:relative;aspect-ratio:16/9}}.mk-bgs button[aria-pressed=true]{{border-color:var(--accent)}}.mk-bgs img{{width:100%;height:100%;object-fit:cover;display:block}}
.mk-bgs span{{position:absolute;left:0;right:0;bottom:0;font-size:10px;line-height:1.2;padding:3px 4px;background:linear-gradient(transparent,rgba(0,0,0,.8));color:#fff;text-align:left}}
.mk-cols{{display:flex;gap:8px;flex-wrap:wrap}}.mk-cols button{{width:34px;height:34px;border-radius:50%;border:2px solid var(--line);cursor:pointer}}.mk-cols button[aria-pressed=true]{{outline:3px solid var(--accent);outline-offset:2px}}
.mk-chk{{flex-direction:row!important;align-items:center;font-weight:400!important}}.mk-chk input{{width:20px;height:20px}}
.mk-go{{font-size:18px;padding:14px}}.mk-prog div{{height:10px;border-radius:99px;background:#16131c;border:1px solid var(--line);overflow:hidden}}.mk-prog i{{display:block;height:100%;width:0;background:var(--accent);transition:width .2s}}.mk-prog span{{font-size:14px;color:var(--muted)}}
</style>
<script>
(function(){{
var BGS={bgs},OCC={occ},LANG={langs},V={json.dumps(V)};
var $=function(s){{return document.querySelector(s)}},$$=function(s){{return [].slice.call(document.querySelectorAll(s))}};
var FONTS={{serif:['700','Playfair Display',1],script:['400','Great Vibes',1.25],sans:['800','Poppins',.95],fun:['800','Baloo 2',1.05]}};
var COLS=[['#ffffff','White'],['#ffe3a3','Gold'],['#fff4dc','Cream'],['#ff6b6b','Red'],['#9ee6b5','Mint'],['#1d1b24','Dark']];
var q=new URLSearchParams(location.search),S={{occ:'xmas',lang:'en',bg:null,font:'serif',pos:'mid',col:'#ffe3a3',shape:'h',len:15,badge:true,edited:false}};
// first visit: start on the occasion of the season (Nov 1–Dec 26 Christmas, Dec 27–Jan 15 New Year, Feb 1–14 Love, otherwise Birthday)
function seasonal(d){{d=d||new Date();var m=d.getMonth()+1,x=d.getDate();if(m===11||(m===12&&x<=26))return 'xmas';if((m===12&&x>=27)||(m===1&&x<=15))return 'ny';if(m===2&&x<=14)return 'love';return 'bday'}}
var sv=null;try{{sv=JSON.parse(localStorage.getItem('tcMaker')||'null');if(sv)for(var k in sv)S[k]=sv[k]}}catch(e){{}}
if(!sv){{var qd=q.get('date');S.occ=seasonal(qd?new Date(qd+'T12:00:00'):null)}}
if(q.get('bg')&&BGS.some(function(b){{return b.id===q.get('bg')}}))S.bg=q.get('bg');
if(q.get('occ')==='pasko'){{S.occ='xmas';S.lang='fil';S.edited=false}}else if(q.get('occ')&&OCC.some(function(o){{return o.k===q.get('occ')}})){{S.occ=q.get('occ');S.edited=false}}
if(S.occ==='pasko'){{S.occ='xmas';S.lang='fil'}}if(!S.lang)S.lang='en';
var cv=$('#cv'),cx=cv.getContext('2d'),vid=$('#vid'),playing=true,t0=performance.now(),busy=false;
function save(){{try{{localStorage.setItem('tcMaker',JSON.stringify(S))}}catch(e){{}}}}
function occO(){{return OCC.filter(function(o){{return o.k===S.occ}})[0]||OCC[0]}}
function occ(){{var o=occO(),v=o.v.filter(function(x){{return x.c===S.lang}})[0]||o.v[0];var d=new Date(),y=String(d.getMonth()>=10?d.getFullYear()+1:d.getFullYear());return {{k:o.k,l:o.l,h:v.h.replace('2027',y),m:v.m.replace('2027',y)}}}}
function setText(){{if(!S.edited||confirmReplace()){{var o=occ();$('#tH').value=o.h;$('#tM').value=o.m;S.edited=false}}}}
function dims(){{return S.shape==='v'?[1080,1920]:S.shape==='sq'?[1080,1080]:[1920,1080]}}
function srcOf(id){{var b=BGS.filter(function(x){{return x.id===id}})[0];return '/media/maker/'+id+(S.shape==='v'&&b&&b.v?'-9x16':'')+'.mp4?v='+V}}
function setBg(){{var u=srcOf(S.bg);if(vid.getAttribute('src')!==u){{vid.src=u;vid.load();if(playing&&!busy)vid.play().catch(function(){{}})}}}}
function drawChips(){{drawLang();$('#occ').innerHTML=OCC.map(function(o){{return '<button type="button" data-o="'+o.k+'" aria-pressed="'+(o.k===S.occ)+'">'+o.l+'</button>'}}).join('');
 $$('#occ button').forEach(function(b){{b.onclick=function(){{S.occ=b.dataset.o;setText();var l=sorted();if(!l.slice(0,6).some(function(x){{return x.id===S.bg}}))S.bg=l[0].id;drawChips();drawBgs();setBg();save()}}}})}}
function drawLang(){{var o=occO(),el=$('#lang');el.hidden=o.v.length<2;el.innerHTML=o.v.length<2?'':'<span class="muted small" style="align-self:center">Language:</span>'+o.v.map(function(v){{return '<button type="button" data-l="'+v.c+'" aria-pressed="'+(v.c===(o.v.some(function(x){{return x.c===S.lang}})?S.lang:o.v[0].c))+'">'+LANG[v.c]+'</button>'}}).join('');
 $$('#lang button').forEach(function(b){{b.onclick=function(){{S.lang=b.dataset.l;setText();drawLang();save()}}}})}}
function confirmReplace(){{return window.confirm('Replace your message with the '+occ().l.replace(/^\\S+ /,'')+' greeting?')}}
var PREF={{xmas:'snowy-christmas-tree-forest-night-loop',ny:'new-year-fireworks-city-loop',bday:'birthday-balloons-rising-loop',thanks:'golden-sunset-clouds-loop',congrats:'celebration-confetti-loop',love:'floating-hearts-loop'}};
function sorted(){{var p=PREF[S.occ];return BGS.slice().sort(function(a,b){{return ((b.o.indexOf(S.occ)>=0)-(a.o.indexOf(S.occ)>=0))||((b.id===p)-(a.id===p))}})}}
function drawBgs(){{$('#bgs').innerHTML=sorted().map(function(b){{return '<button type="button" data-b="'+b.id+'" aria-pressed="'+(b.id===S.bg)+'" title="'+b.t+'"><img src="/media/poster/'+b.id+'.webp" alt="" loading="lazy"><span>'+b.t+'</span></button>'}}).join('');
 $$('#bgs button').forEach(function(b){{b.onclick=function(){{S.bg=b.dataset.b;drawBgs();setBg();save()}}}})}}
function drawCols(){{$('#cols').innerHTML=COLS.map(function(c){{return '<button type="button" data-c="'+c[0]+'" aria-pressed="'+(c[0]===S.col)+'" title="'+c[1]+'" aria-label="'+c[1]+' text" style="background:'+c[0]+'"></button>'}}).join('');
 $$('#cols button').forEach(function(b){{b.onclick=function(){{S.col=b.dataset.c;drawCols();save()}}}})}}
function wrap(ctx,text,maxW,bal){{var words=String(text).split(/\\s+/),lines=[],cur='';words.forEach(function(w){{var t=cur?cur+' '+w:w;if(ctx.measureText(t).width>maxW&&cur){{lines.push(cur);cur=w}}else cur=t}});if(cur)lines.push(cur);if(lines.length>1&&!bal){{var w=ctx.measureText(String(text)).width/lines.length*1.12;var l2=wrap(ctx,text,Math.min(maxW,w),1);if(l2.length===lines.length)return l2}}return lines}}
function ease(x){{x=Math.max(0,Math.min(1,x));return 1-Math.pow(1-x,3)}}
function frame(ctx,W,H,t,total){{
 ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);
 if(vid.readyState>=2){{var vw=vid.videoWidth,vh=vid.videoHeight,k=Math.max(W/vw,H/vh),sw=W/k,sh=H/k;ctx.drawImage(vid,(vw-sw)/2,(vh-sh)/2,sw,sh,0,0,W,H)}}
 var m=Math.min(W,H),f=FONTS[S.font],dark=S.col==='#1d1b24',hS=Math.round(m*.115*f[2]),mS=Math.round(m*.047),fS=Math.round(m*.04),maxW=W*.84;
 ctx.textAlign='center';ctx.textBaseline='alphabetic';
 ctx.font=f[0]+' '+hS+'px "'+f[1]+'"';var hl=wrap(ctx,$('#tH').value,maxW);
 ctx.font='500 '+mS+'px Inter, sans-serif';var ml=wrap(ctx,$('#tM').value,maxW*.92);
 var fr=$('#tF').value.trim(),gap=m*.035,hLH=hS*1.12,mLH=mS*1.35;
 var blockH=hl.length*hLH+(ml.length?gap+ml.length*mLH:0)+(fr?gap+fS*1.3:0);
 var top=S.pos==='up'?H*.12:S.pos==='low'?H*(S.shape==='v'?.76:.86)-blockH:(H-blockH)/2;
 // soft shade behind the text so it reads on any background
 var g=ctx.createRadialGradient(W/2,top+blockH/2,0,W/2,top+blockH/2,Math.max(W,blockH)*.62);g.addColorStop(0,dark?'rgba(255,255,255,.45)':'rgba(0,0,0,.42)');g.addColorStop(1,'rgba(0,0,0,0)');
 ctx.globalAlpha=ease(t/1.2);ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 var shadow=dark?'rgba(255,255,255,.65)':'rgba(0,0,0,.6)';
 function line(txt,y,font,size,start,col){{var a=ease((t-start)/.9);if(a<=0)return;ctx.globalAlpha=a;ctx.font=font;ctx.fillStyle=col;ctx.shadowColor=shadow;ctx.shadowBlur=size*.25;ctx.shadowOffsetY=size*.04;ctx.fillText(txt,W/2,y+(1-a)*size*.5);ctx.shadowBlur=0;ctx.shadowOffsetY=0}}
 var y=top;hl.forEach(function(l,i){{y+=hLH;line(l,y-hLH*.18,f[0]+' '+hS+'px "'+f[1]+'"',hS,.3+i*.15,S.col)}});
 if(ml.length){{y+=gap;ml.forEach(function(l,i){{y+=mLH;line(l,y-mLH*.25,'500 '+mS+'px Inter, sans-serif',mS,1.1+i*.12,dark?'#1d1b24':'#ffffff')}})}}
 if(fr){{y+=gap+fS*1.3;line(fr,y-fS*.3,'italic 600 '+fS+'px Inter, sans-serif',fS,1.8,S.col)}}
 if(S.badge){{ctx.globalAlpha=.78;var bs=Math.round(m*.022);ctx.font='600 '+bs+'px Inter, sans-serif';ctx.textAlign='right';ctx.fillStyle='#fff';ctx.shadowColor='rgba(0,0,0,.7)';ctx.shadowBlur=bs*.4;
  ctx.fillText('Made with Telar Clips · clips.telarlabs.net',W-m*.03,H-m*.03-(S.shape==='v'?H*.06:0));ctx.shadowBlur=0}}
 // a gentle fade in from black, and out at the very end
 var fo=Math.min(1,t/.5,(total-t)/.5);if(fo<1){{ctx.globalAlpha=1-Math.max(0,fo);ctx.fillStyle='#000';ctx.fillRect(0,0,W,H)}}
 ctx.globalAlpha=1}}
function size(){{var d=dims();if(cv.width!==d[0]||cv.height!==d[1]){{cv.width=d[0];cv.height=d[1]}}$('#info').textContent=d[0]+'×'+d[1]+' · '+S.len+' s'}}
function loop(){{if(!busy){{size();var total=S.len,t=((performance.now()-t0)/1000)%total;frame(cx,cv.width,cv.height,t,total)}}requestAnimationFrame(loop)}}
$('#play').onclick=function(){{playing=!playing;if(playing){{vid.play().catch(function(){{}});this.textContent='❚❚ Pause'}}else{{vid.pause();this.textContent='▶ Play'}}}};
['tH','tM','tF'].forEach(function(id){{$('#'+id).oninput=function(){{S.edited=true;S[id]=this.value;save()}}}});
$('#sF').onchange=function(){{S.font=this.value;save()}};$('#sP').onchange=function(){{S.pos=this.value;save()}};
$('#sS').onchange=function(){{S.shape=this.value;setBg();t0=performance.now();save()}};$('#sL').onchange=function(){{S.len=+this.value;t0=performance.now();save()}};$('#sB').onchange=function(){{S.badge=this.checked;save()}};
var o=occ();$('#tH').value=S.edited&&S.tH!=null?S.tH:o.h;$('#tM').value=S.edited&&S.tM!=null?S.tM:o.m;$('#tF').value=S.tF||'';
$('#sF').value=S.font;$('#sP').value=S.pos;$('#sS').value=S.shape;$('#sL').value=String(S.len);$('#sB').checked=S.badge;
if(!S.bg)S.bg=sorted()[0].id;drawChips();drawBgs();drawCols();setBg();
var fontsReady=document.fonts?Promise.all(Object.keys(FONTS).map(function(k){{return document.fonts.load(FONTS[k][0]+' 40px "'+FONTS[k][1]+'"')}}).concat([document.fonts.load('500 20px Inter'),document.fonts.load('italic 600 20px Inter')])):Promise.resolve();
fontsReady.then(function(){{}},function(){{}});vid.oncanplay=function(){{if(playing&&!busy)vid.play().catch(function(){{}})}};requestAnimationFrame(loop);

// ---- export: draw every frame at its exact time, encode it (WebCodecs + MP4 muxer); fall back to recording in real time
function seek(tt){{return new Promise(function(res){{if(Math.abs(vid.currentTime-tt)<.001&&vid.readyState>=2)return res();var done=false,fin=function(){{if(done)return;done=true;res()}};
 vid.addEventListener('seeked',function h(){{vid.removeEventListener('seeked',h);if(vid.requestVideoFrameCallback){{vid.requestVideoFrameCallback(function(){{fin()}});setTimeout(fin,120)}}else fin()}});vid.currentTime=tt;setTimeout(fin,1500)}})}}
function prog(p,txt){{$('#prog').hidden=false;$('#bar').style.width=Math.round(p*100)+'%';if(txt)$('#pt').textContent=txt}}
function fname(ext){{return 'greeting-'+(($('#tH').value||'video').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'video')+'.'+ext}}
function deliver(blob,ext){{var name=fname(ext),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();
 var mb=(blob.size/1048576).toFixed(1),sh='';var file=null;try{{file=new File([blob],name,{{type:blob.type}})}}catch(e){{}}
 $('#done').innerHTML='✓ Your video is ready ('+mb+' MB). If it didn’t download, <a href="'+url+'" download="'+name+'">tap here</a>.'+(file&&navigator.canShare&&navigator.canShare({{files:[file]}})?' <button class="btn btn-sm" id="shr" type="button">Share</button>':'');
 if($('#shr'))$('#shr').onclick=function(){{navigator.share({{files:[file],title:$('#tH').value}}).catch(function(){{}})}}}}
async function encodeMP4(W,H,total){{
 if(!('VideoEncoder' in window)||!window.Mp4Muxer)return null;
 var ways=['avc1.640028','avc1.4d4028','avc1.42e028','avc1.640033'],way=null,cfg;
 for(var i=0;i<ways.length&&!way;i++){{cfg={{codec:ways[i],width:W,height:H,bitrate:W*H>2e6?10e6:7e6,framerate:30}};try{{if((await VideoEncoder.isConfigSupported(cfg)).supported)way=ways[i]}}catch(e){{}}}}
 if(!way)return null;
 var target=new Mp4Muxer.ArrayBufferTarget(),mux=new Mp4Muxer.Muxer({{target:target,video:{{codec:'avc',width:W,height:H,frameRate:30}},fastStart:'in-memory'}}),out=0,err=null;
 var enc=new VideoEncoder({{output:function(c,m){{out++;mux.addVideoChunk(c,m)}},error:function(e){{err=e}}}});enc.configure(cfg);
 var oc=document.createElement('canvas');oc.width=W;oc.height=H;var octx=oc.getContext('2d'),N=Math.round(total*30),len=vid.duration||8;
 vid.pause();
 for(var f=0;f<N;f++){{if(err)throw err;var tt=f/30;await seek((tt%len)+.001);frame(octx,W,H,tt,total);
  var vf=new VideoFrame(oc,{{timestamp:Math.round(f*1e6/30),duration:Math.round(1e6/30)}});enc.encode(vf,{{keyFrame:f%60===0}});vf.close();
  while(enc.encodeQueueSize>8)await new Promise(function(r){{setTimeout(r,5)}});if(f%5===0)prog(f/N,'Making your video… '+Math.round(f/N*100)+'%')}}
 try{{await enc.flush()}}catch(e){{if(out<N*.98)throw e}}if(out<N*.98)throw err||new Error('The video could not be finished.');
 mux.finalize();return new Blob([target.buffer],{{type:'video/mp4'}})}}
async function record(W,H,total){{var st=cv.captureStream(30),types=['video/mp4;codecs=avc1','video/mp4','video/webm;codecs=vp9','video/webm'],type=types.filter(function(t){{return window.MediaRecorder&&MediaRecorder.isTypeSupported(t)}})[0];
 if(!type)throw new Error('This browser can’t make videos. Please try Chrome, Edge or Safari.');
 var rec=new MediaRecorder(st,{{mimeType:type,videoBitsPerSecond:8e6}}),parts=[];rec.ondataavailable=function(e){{if(e.data.size)parts.push(e.data)}};
 busy=false;t0=performance.now();vid.currentTime=0;vid.play();rec.start(250);
 await new Promise(function(r){{var iv=setInterval(function(){{var p=(performance.now()-t0)/1000/total;prog(Math.min(1,p),'Recording… '+Math.round(Math.min(1,p)*100)+'%');if(p>=1){{clearInterval(iv);r()}}}},200)}});
 await new Promise(function(r){{rec.onstop=r;rec.stop()}});return {{blob:new Blob(parts,{{type:type.split(';')[0]}}),ext:type.indexOf('mp4')>=0?'mp4':'webm'}}}}
$('#go').onclick=async function(){{if(busy)return;var d=dims(),total=S.len,b=this;b.disabled=true;$('#done').textContent='';
 try{{await fontsReady.catch(function(){{}});busy=true;prog(0,'Getting ready…');var blob=null;
  try{{blob=await encodeMP4(d[0],d[1],total)}}catch(e){{console.warn(e);blob=null}}
  if(blob){{deliver(blob,'mp4')}}else{{busy=false;var r=await record(d[0],d[1],total);deliver(r.blob,r.ext)}}
  prog(1,'Done!');try{{if(window.gtag)gtag('event','greeting_video')}}catch(e){{}}}}
 catch(e){{$('#done').textContent='Sorry, the video couldn’t be made: '+(e.message||e)+'. Try a shorter length, or another browser.'}}
 finally{{busy=false;b.disabled=false;t0=performance.now();if(playing)vid.play().catch(function(){{}});setTimeout(function(){{$('#prog').hidden=true}},2500)}}}};
}})();
</script>'''

TEXT = '''
<section class="wrap prose" style="margin-top:34px">
<h2>How to make a greeting video</h2>
<ol><li><b>Pick the occasion.</b> Christmas, New Year, birthday, thank you, congratulations or love. It fills in a greeting you can change. Christmas and New Year greetings also come in Filipino, Spanish, French and German.</li>
<li><b>Choose a background.</b> Moving snow, lights, fireworks, balloons, hearts and more, from the Telar Clips library.</li>
<li><b>Type your message</b> and who it’s from.</li>
<li><b>Style it:</b> font, color and where the text sits.</li>
<li><b>Pick a shape and length,</b> then tap <b>Download MP4</b>. The video is made on your phone or computer in a few seconds, and nothing is uploaded.</li></ol>
__AD__
<h2>Which shape should I choose?</h2>
<ul><li><b>Portrait 9:16</b> for Facebook and Instagram Stories, TikTok, Reels, YouTube Shorts and WhatsApp Status.</li>
<li><b>Square 1:1</b> for Facebook and Instagram posts and group chats.</li>
<li><b>Landscape 16:9</b> for YouTube, a TV or projector at a party, or a church or school screen.</li></ul>
<p>More on sizes in our guide to <a href="https://telarlabs.net/guides/video-sizes-tiktok-reels-shorts-youtube/">video sizes for TikTok, Reels, Shorts and YouTube</a>.</p>
<h2>Tips</h2>
<ul><li><b>Keep it short.</b> A greeting of 3 to 8 words, and one sentence of message, reads best on a phone.</li>
<li><b>Add music</b> in TikTok, Instagram or CapCut after downloading, using their licensed music.</li>
<li><b>Making many?</b> Your last design is remembered on this device, so you only change the name and download again.</li>
<li><b>Want your own text style?</b> Download the background itself from its clip page and use any video editor. See <a href="/guides/holiday-greeting-video/">how to make a holiday greeting video</a>.</li></ul>
<h2>Questions</h2>
<h3>Is it free?</h3><p>Yes, with no sign-up and no watermark you can’t remove. The small “Made with Telar Clips” note is optional.</p>
<h3>Can I use it for my business or church?</h3><p>Yes. The backgrounds are free for personal and commercial use under the <a href="/license/">Telar Clips license</a>.</p>
<h3>It doesn’t work on my phone.</h3><p>Video making needs a recent browser. Chrome, Edge and Safari work best. If a long video fails, try 8 or 15 seconds.</p>
</section>'''
