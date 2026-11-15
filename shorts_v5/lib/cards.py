from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
FD="/home/claude/work/v5/tk/fonts/"
TIRO=FD+"tiro-devanagari-hindi.ttf"; YATRA=FD+"tiro-devanagari-hindi.ttf"
W,H=1080,1920
def font(p,s): return ImageFont.truetype(p,s,layout_engine=ImageFont.Layout.RAQM)
def wrap(d,text,f,maxw):
    words=text.split(" "); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=f)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines
def caption_png(text,path,size=72,maxw=960,ybot=1560):
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); f=font(YATRA,size)
    lines=wrap(d,text,f,maxw); lh=int(size*1.55); th=lh*len(lines)
    top=ybot-th; pad=26
    band=Image.new("RGBA",(W,H),(0,0,0,0)); bd=ImageDraw.Draw(band)
    bd.rounded_rectangle((40,top-pad,W-40,ybot+pad-8),radius=34,fill=(0,0,0,150))
    im=Image.alpha_composite(im,band); d=ImageDraw.Draw(im)
    for i,l in enumerate(lines):
        w=d.textlength(l,font=f); x=(W-w)/2; y=top+i*lh
        d.text((x,y),l,font=f,fill=(255,255,255,255),stroke_width=4,stroke_fill=(0,0,0,255))
    im.save(path)
def card_on_bg(bg_path,blocks,out,dim=0.45):
    """blocks: list of (text,size,color,gap_after,fontpath). centered stack, vertically centered in 330..1300"""
    bg=Image.open(bg_path).convert("RGB").resize((W,H))
    ov=Image.new("RGB",(W,H),(0,0,0)); bg=Image.blend(bg,ov,dim); im=bg.convert("RGBA"); d=ImageDraw.Draw(im)
    rows=[]
    for t,s,c,g,fp in blocks:
        f=font(fp or YATRA,s); 
        for l in wrap(d,t,f,920): rows.append((l,f,c,int(s*1.45)))
        rows[-1]=rows[-1][:3]+(rows[-1][3]+g,)
    tot=sum(r[3] for r in rows); y=(330+1300)//2-tot//2
    for l,f,c,h in rows:
        w=d.textlength(l,font=f); d.text(((W-w)/2,y),l,font=f,fill=c,stroke_width=4,stroke_fill=(20,10,0,255)); y+=h
    im.convert("RGB").save(out,quality=95)
