"""Lip-sync sprites that move the character's OWN mouth: the lower lip + jaw are warped
down (per-column inverse displacement) and the opened gap shows a soft dark mouth cavity.
Writes mascot/talk/<pose>_<m0..m4|mo>[_b].png (blink lids reused from make_visemes)."""
import json, numpy as np, cv2
from PIL import Image
D='/home/claude/wakil-content/mascot/'
C=json.load(open(D+'face_coords.json'))
EYES={'wave':[(229,174),(300,159)],'point':[(198,186),(277,168)],'think':[(183,177),(252,154)],'wink':[(305,160)],'shrug':[(209,182),(279,157)]}
def smooth(t): t=np.clip(t,0,1); return t*t*(3-2*t)
def open_mouth(im, mx, my, sp, h, half=34, chin=80):
    a=np.array(im).astype(np.float32); H,W=a.shape[:2]
    xs=np.arange(W); u=np.clip(np.abs(xs-mx)/half,0,1); fx=np.sqrt(1-u**2)*(1-smooth((u-0.7)/0.3)*0.3)   # elliptical opening
    y0=np.arange(H,dtype=np.float32)
    mapx=np.tile(xs.astype(np.float32),(H,1)); mapy=np.tile(y0[:,None],(1,W)).copy()
    gap=np.zeros((H,W),np.float32)
    for x in range(max(0,mx-half-2),min(W,mx+half+3)):
        hx=h*fx[x]; seam=my+np.polyval(sp,x-mx)
        if hx<0.3: continue
        d=hx*(1-smooth((y0-seam)/chin)); d[y0<seam]=0      # forward displacement of source rows
        yf=y0+d                                            # monotonic
        mapy[:,x]=np.interp(y0,yf,y0)
        g=(y0>=seam)&(y0<seam+hx); gap[g,x]=1
    out=cv2.remap(a,mapx,mapy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    # cavity: dark, slightly lighter (tongue) toward the bottom, soft edges
    seamc=my+np.polyval(sp,np.arange(W)-mx); yy=(np.arange(H)[:,None]-seamc[None,:])/max(h,1)
    cav=np.zeros_like(out); cav[...,0]=48+40*np.clip(yy,0,1); cav[...,1]=14+8*np.clip(yy,0,1); cav[...,2]=14+10*np.clip(yy,0,1); cav[...,3]=255
    g=cv2.GaussianBlur(gap,(0,0),0.8)[...,None]
    out=out*(1-g)+cav*g
    # soft shadow under upper lip
    sh=cv2.GaussianBlur(gap,(0,0),2.0)[...,None]*0.25; out[...,:3]*=(1-sh)
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8),'RGBA')
lids=json.load(open(D+'face_coords.json'))
from make_visemes_lids import blink_layer
for n,c in C.items():
    im=Image.open(D+f'pose_{n}.png').convert('RGBA'); mx,my=c['mouth']; sp=c['seam']
    fr={'m0':im}
    for k,h in enumerate([4,8,12,16],1): fr[f'm{k}']=open_mouth(im,mx,my,sp,h)
    fr['mo']=open_mouth(im,mx,my,sp,11,half=22)
    bl=blink_layer(im,EYES[n])
    for k,f in fr.items():
        f.save(D+f'talk/{n}_{k}.png'); b=f.copy(); b.alpha_composite(bl); b.save(D+f'talk/{n}_{k}_b.png')
print('ok')
