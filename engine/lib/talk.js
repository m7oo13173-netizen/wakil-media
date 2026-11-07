// Talking-mascot engine: lip-sync from the voice envelope (C.env / C.zc at 30fps),
// automatic blinks, breathing, talk-driven body motion, and pose switching.
// Needs sprites from lib/make_visemes.py in mascot/talk/<pose>_<m0..m4|mo>[_b].png
const TK_VIS = ['m0','m1','m2','m3','m4','mo'];
function injectTalker(hostId, poses, widthPx=760){
  const host=$(hostId);
  for(const p of poses){
    const w=document.createElement('div'); w.className='tkp'; w.id='tk_'+p;
    w.style.cssText=`position:absolute;left:0;top:0;width:${widthPx}px;opacity:0;transform-origin:50% 90%`;
    for(const v of TK_VIS) for(const b of ['','_b']){
      const im=document.createElement('img'); im.src=`../mascot/talk/${p}_${v}${b}.png`;
      im.dataset.k=v+b; im.style.cssText='position:absolute;left:0;top:0;width:100%;visibility:hidden';
      w.appendChild(im);
    }
    w.firstChild.style.position='relative';
    host.appendChild(w);
  }
}
function tkLevel(T){
  const env=C.env||[], zc=C.zc||[], f=Math.floor(T*30);
  const e=Math.max(env[f]||0, 0.6*(env[f-1]||0)), z=zc[f]||0;
  let lv=e<.12?0:e<.3?1:e<.5?2:e<.72?3:4;
  if(lv>=2 && lv<=3 && z>0 && z<0.03) return {k:'mo',e};
  return {k:'m'+lv,e};
}
function tkBlink(T,a){
  // deterministic pseudo-random blinks every ~2.6–4.4s, plus one right after a pose change
  if(T-a>0.05 && T-a<0.17) return true;
  let t=0.9, i=0; while(t<T+1){ const d=0.12; if(T>=t&&T<t+d) return true; i++; t+=2.6+((i*7919)%180)/100; }
  return false;
}
// show pose p between a and b; opts: x,y (px), sc
function talker(T,p,a,b,opts={}){
  const w=$('tk_'+p); if(!w) return;
  if(T<a||T>=b){ w.style.opacity=0; return; }
  const {k,e}=tkLevel(T), bl=tkBlink(T,a)?'_b':'';
  for(const im of w.children) im.style.visibility=(im.dataset.k===k+bl)?'visible':'hidden';
  const pop=lin(T,a,a+.18), sq=1+0.05*(1-pop)*Math.sin(pop*Math.PI);
  const breath=Math.sin(T*2.1)*5, sway=Math.sin(T*1.3+a)*1.4 + Math.sin(T*3.1)*e*1.6;
  const nod=-e*12, sc=(opts.sc||1)*(1+Math.sin(T*2.1)*0.006);
  w.style.opacity=1;
  w.style.transform=`translate(${(opts.x||0)+Math.sin(T*.7)*6}px,${(opts.y||0)+breath+nod}px) rotate(${sway}deg) scale(${sc*sq},${sc/sq})`;
}
// camera: list of shots [{t, s, fx, fy}] — cut on t with a fast ease, slow drift within a shot
function camera(T,shots,el='cam',layers=[]){
  let i=0; while(i+1<shots.length && T>=shots[i+1].t) i++;
  const cur=shots[i], prev=shots[Math.max(0,i-1)], k=outCubic(lin(T,cur.t,cur.t+.22));
  const s=prev.s+(cur.s-prev.s)*k, fx=prev.fx+(cur.fx-prev.fx)*k, fy=prev.fy+(cur.fy-prev.fy)*k;
  const drift=1+0.035*lin(T,cur.t,(shots[i+1]||{t:cur.t+6}).t);
  const S=s*drift, dx=Math.sin(T*.45)*14, dy=Math.cos(T*.37)*8;
  $(el).style.transformOrigin='0 0';
  $(el).style.transform=`translate(${540-fx*S+dx}px,${960-fy*S+dy}px) scale(${S})`;
  for(const [id,f] of layers){ $(id).style.transform=`translate(${-dx*(f-1)*2}px,${-dy*(f-1)*2}px)`; }
  return {S,i};
}
