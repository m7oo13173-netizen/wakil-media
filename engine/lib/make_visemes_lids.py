from PIL import Image, ImageDraw, ImageFilter
SS=4
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
