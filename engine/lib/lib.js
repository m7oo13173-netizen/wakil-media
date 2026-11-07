// Shared animation helpers + signature "يلا!" sting for WakilSmart reels.
const $=id=>document.getElementById(id);
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const lin=(t,a,b)=>cl((t-a)/(b-a));
const outBack=x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const outCubic=x=>1-Math.pow(1-x,3);
function vis(t,a,b,fi=.25,fo=.18){ if(t<a||t>b) return 0; return Math.min(lin(t,a,a+fi),1-lin(t,b-fo,b)); }
function popEl(el,t,a,b,opts={}){
  if(typeof el==='string') el=$(el);
  const fi=opts.fi||.3; if(a<=0.1) a=-1;
  const v=vis(t,a,b,fi,opts.fo||.18);
  const s=t<a+fi?outBack(lin(t,a,a+fi)):1;
  el.style.opacity=v>0?Math.min(1,v*3):0;
  el.style.transform=(opts.base||'')+` scale(${0.4+0.6*s})`;
}
function pose(id,t,a,b,opts={}){
  const el=$('p_'+id);
  if(a<=0.05) a=-1;
  if(t<a||t>b){el.style.opacity=0;return;}
  const k=outBack(lin(t,a,a+.35)), out=lin(t,b-.15,b);
  const bob=Math.sin((t-a)*5.2)*(opts.bob??8), sq=1+Math.sin((t-a)*5.2+1)*0.012;
  const x=opts.x||0, sc=opts.sc||1, rot=opts.rot?Math.sin((t-a)*3)*opts.rot:0;
  el.style.opacity=1-out;
  el.style.transform=`translateX(calc(-50% + ${x}px)) translateY(${(1-k)*700+bob+out*120}px) scale(${sc*sq},${sc/sq}) rotate(${rot}deg)`;
}
// Signature ending — inject once, call yalla(T, A) every frame. A = start of the spoken "يلا".
function injectYalla(){
  const h=`<div class="bg" id="bgY" style="background:radial-gradient(circle at 50% 45%,#ffd23f 0%,#ff8a00 55%,#d9480f 100%);opacity:0"></div>
  <div class="abs" id="raysY" style="left:-420px;top:-60px;width:1920px;height:1920px;opacity:0;background:repeating-conic-gradient(from 0deg,rgba(255,255,255,.22) 0deg 10deg,transparent 10deg 20deg);border-radius:50%"></div>
  <img class="pose" id="p_yalla" src="../mascot/pose_celebrate.png" style="opacity:0">
  <div class="abs big" id="yallaT" style="top:180px;font-size:300px;color:#fff;text-shadow:0 14px 0 #b03a00,0 0 60px rgba(0,0,0,.25);opacity:0">يلا!</div>
  <div class="abs brand" id="yallaB" style="top:590px;font-size:76px;opacity:0">Wakil<span style="color:#1b1530">Smart</span>.ai</div>`;
  $('stage').insertAdjacentHTML('beforeend',h);
}
function yalla(T,A){
  const on=T>=A, k=on?lin(T,A,A+.18):0;
  $('bgY').style.opacity=k; $('raysY').style.opacity=k;
  $('raysY').style.transform=`rotate(${(T-A)*40}deg)`;
  const el=$('p_yalla');
  if(!on){el.style.opacity=0;$('yallaT').style.opacity=0;$('yallaB').style.opacity=0;return;}
  const pk=outBack(lin(T,A,A+.35)), bob=Math.sin((T-A)*9)*14;
  el.style.opacity=1;
  el.style.transform=`translateX(-50%) translateY(${(1-pk)*800+bob}px) scale(${1.05+0.04*Math.sin((T-A)*9)}) rotate(${Math.sin((T-A)*7)*3}deg)`;
  const y=$('yallaT'), yk=outBack(lin(T,A+.05,A+.4));
  y.style.opacity=lin(T,A+.05,A+.15);
  y.style.transform=`scale(${0.2+0.8*yk+0.06*Math.sin((T-A)*16)}) rotate(${Math.sin((T-A)*20)*3*Math.exp(-(T-A)*2)}deg)`;
  $('yallaB').style.opacity=lin(T,A+.5,A+.8);
}

// Hook FX: punch-in zoom + shake on the first 0.6s, flash, and a retention progress bar.
function injectHookFX(){
  $('stage').insertAdjacentHTML('beforeend','<div id="pbar" style="position:absolute;left:0;top:0;height:14px;width:0;background:#ffd23f;z-index:99;box-shadow:0 0 18px #ffd23f"></div><div id="hflash" style="position:absolute;inset:0;background:#fff;opacity:0;z-index:98;pointer-events:none"></div>');
}
function hookFX(T,D){
  const st=$('stage'), k=lin(T,0,.55);
  const z=1.1-0.1*outCubic(k), sh=T<.6?Math.sin(T*90)*14*(1-k):0;
  st.style.transformOrigin='50% 35%'; st.style.transform=`translate(${sh}px,${-sh*.6}px) scale(${z})`;
  $('hflash').style.opacity=(T>0.03&&T<0.25)?0.5*(1-lin(T,.05,.25)):0;
  $('pbar').style.width=(100*Math.min(1,T/D))+'%';
}
