"""Generate talking sprites per pose: mouth openings m0..m4 (+ round 'o') and blink variants."""
import json, sys
from PIL import Image, ImageDraw, ImageFilter
D='/home/claude/wakil-content/mascot/'
C=json.load(open(D+'face_coords.json'))
EYES={'wave':[(229,174),(300,159)],'point':[(198,186),(277,168)],'think':[(183,177),(252,154)],'wink':[(305,160)],'shrug':[(209,182),(279,157)]}
SS=4  # supersample for smooth edges
def mouth_layer(size, cx, cy, w, h, round_=False):
    W,H=size; L=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); d=ImageDraw.Draw(L)
    cx,cy,w,h=cx*SS,cy*SS,w*SS,h*SS
    if round_: w=w*0.62
    # lips (darker rim)
    d.ellipse((cx-w/2-3*SS,cy-h/2-3*SS,cx+w/2+3*SS,cy+h/2+3*SS),fill=(150,72,58,255))
    # interior
    d.ellipse((cx-w/2,cy-h/2,cx+w/2,cy+h/2),fill=(58,18,16,255))
    # tongue
    if h>8*SS: d.ellipse((cx-w*0.32,cy+h*0.05,cx+w*0.32,cy+h/2+2*SS),fill=(196,92,92,255))
    # upper teeth
    if h>5*SS and not round_: d.chord((cx-w*0.42,cy-h/2+1*SS,cx+w*0.42,cy-h/2+max(5*SS,h*0.55)),0,180,fill=(250,246,240,255))
    # re-clip to mouth ellipse
    M=Image.new('L',L.size,0); ImageDraw.Draw(M).ellipse((cx-w/2-3*SS,cy-h/2-3*SS,cx+w/2+3*SS,cy+h/2+3*SS),fill=255)
    L.putalpha(Image.composite(L.getchannel('A'),Image.new('L',L.size,0),M))
    return L.resize((W,H),Image.LANCZOS)
cl01=lambda v:max(0,min(1,v))
def blink_layer(im, eyes):
    W,H=im.size; out=Image.new('RGBA',(W,H),(0,0,0,0))
    for (x,y) in eyes:
        px=[im.getpixel((x+dx,y+30))[:3] for dx in (-8,0,8)]
        sk=tuple(sum(c[i] for c in px)//3 for i in range(3))
        rx,ry=23,17
        L=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); d=ImageDraw.Draw(L)
        X,Y=x*SS,y*SS
        for i in range(-ry*SS-40,ry*SS+40):  # vertical gradient lid, darker on top
            t=cl01((i+ry*SS)/(ry*2*SS)); f=0.8+0.2*t
            col=tuple(int(v*f) for v in sk)+(255,)
            d.line((X-rx*SS-40,Y+i,X+rx*SS+40,Y+i),fill=col)
        M=Image.new('L',L.size,0); ImageDraw.Draw(M).ellipse((X-rx*SS,Y-ry*SS,X+rx*SS,Y+ry*SS),fill=255)
        M=M.filter(ImageFilter.GaussianBlur(3*SS)); L.putalpha(M)
        ImageDraw.Draw(L).arc((X-rx*SS*0.95,Y-ry*SS*0.9,X+rx*SS*0.95,Y+ry*SS*0.55),15,165,fill=(35,18,14,255),width=3*SS)
        out.alpha_composite(L.resize((W,H),Image.LANCZOS))
    return out
for n,c in C.items():
    im=Image.open(D+f'pose_{n}.png').convert('RGBA'); mx,my=c['mouth']; my+=11
    frames={'m0':im}
    for k,(w,h) in enumerate([(30,5),(34,10),(36,15),(38,20)],1):
        f=im.copy(); f.alpha_composite(mouth_layer(im.size,mx,my,w,h)); frames[f'm{k}']=f
    f=im.copy(); f.alpha_composite(mouth_layer(im.size,mx,my,30,16,True)); frames['mo']=f
    for k,f in frames.items():
        f.save(D+f'talk/{n}_{k}.png')
        b=f.copy(); b.alpha_composite(blink_layer(im,EYES[n])); b.save(D+f'talk/{n}_{k}_b.png')
print('ok')
