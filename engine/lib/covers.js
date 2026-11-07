const {chromium}=require('playwright');const path=require('path');
const S=JSON.parse(process.argv[2]);
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const s of S){const q=new URLSearchParams(s.q).toString();await p.goto('file://'+path.resolve(__dirname,'cover.html')+'?'+q);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);await p.screenshot({path:s.o,type:'jpeg',quality:90});}
await b.close();})();
