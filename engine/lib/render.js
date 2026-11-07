// usage: node render.js <reelDir> <cues.json|-> <audio.wav|-> <out.mp4|snap> [snap times...]
const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');const path=require('path');
const [dir,cuesF,audio,out,...snaps]=process.argv.slice(2);
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(dir,'reel.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
if(cuesF!=='-'){const c=JSON.parse(fs.readFileSync(cuesF));await p.evaluate(c=>{Object.assign(C,c)},c);}
const D=await p.evaluate(()=>C.D);
await p.evaluate(()=>{if(typeof injectHookFX==='function')injectHookFX();});
const F=T=>{setT(T);if(typeof hookFX==='function')hookFX(T,C.D);};
await p.exposeFunction('noop',()=>{});
if(out==='snap'){for(const T of snaps.map(Number)){await p.evaluate(T=>{setT(T);if(typeof hookFX==='function')hookFX(T,C.D);},T);await p.screenshot({path:path.join(dir,`snap_${T}.png`)});}await b.close();return;}
const args=['-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-'];
if(audio!=='-')args.push('-i',audio);
args.push('-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p');
if(audio!=='-')args.push('-c:a','aac','-b:a','192k','-shortest');
args.push('-movflags','+faststart',out);
const ff=spawn('ffmpeg',args,{stdio:['pipe','ignore','ignore']});
for(let i=0;i<Math.round(30*D);i++){await p.evaluate(T=>{setT(T);if(typeof hookFX==='function')hookFX(T,C.D);},i/30);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();})();
