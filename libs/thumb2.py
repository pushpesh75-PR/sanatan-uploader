import sys, random, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
S='/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad'
sys.path.insert(0,S+'/work')
from gold import gold3d
T=S+'/thumb/'; W,H=1920,1080
logo=Image.open(S+'/brand/logo.png').convert('RGBA')
def fit(im,maxw):
  return im.resize((maxw,int(im.height*maxw/im.width)),Image.LANCZOS) if im.width>maxw else im
def ornament(w,col=(255,205,90)):
  im=Image.new('RGBA',(w,60),(0,0,0,0)); d=ImageDraw.Draw(im); cy=30
  for side in (-1,1):
    x0=w//2+side*40; x1=w//2+side*(w//2-30)
    for k in range(3):
      d.line([(x0,cy+(k-1)*0),(x1,cy)],fill=col+(255,),width=4 if k==1 else 2)
    d.ellipse((x1-9,cy-9,x1+9,cy+9),outline=col+(255,),width=3)
    d.arc((x1-side*30-12,cy-26,x1-side*30+12,cy-2),0,360,fill=col+(255,),width=2)
  d.polygon([(w//2,cy-22),(w//2+22,cy),(w//2,cy+22),(w//2-22,cy)],fill=col+(255,),outline=(110,30,0,255))
  d.polygon([(w//2,cy-10),(w//2+10,cy),(w//2,cy+10),(w//2-10,cy)],fill=(170,20,20,255))
  sh=im.filter(ImageFilter.GaussianBlur(3)); out=Image.new('RGBA',im.size,(0,0,0,0))
  blk=Image.new('RGBA',im.size,(0,0,0,0)); blk.putalpha(sh.getchannel('A')); out.alpha_composite(blk,(0,0)); out.alpha_composite(im)
  return out
def plaque(textimg,fill_top=(215,25,25),fill_bot=(120,0,0)):
  pw,ph=textimg.width+150,textimg.height+46
  im=Image.new('RGBA',(pw+80,ph+80),(0,0,0,0))
  sh=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((48,52,48+pw,52+ph),radius=26,fill=(0,0,0,190)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
  g=np.linspace(0,1,ph)[:,None]; col=(np.array(fill_top)*(1-g)+np.array(fill_bot)*g)
  grad=Image.fromarray(np.repeat(col[:,None,:],pw,1).astype(np.uint8).reshape(ph,pw,3),'RGB').convert('RGBA')
  m=Image.new('L',(pw,ph)); ImageDraw.Draw(m).rounded_rectangle((0,0,pw-1,ph-1),radius=26,fill=255); grad.putalpha(m)
  im.alpha_composite(grad,(40,40)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((40,40,40+pw,40+ph),radius=26,outline=(255,215,110,255),width=7)
  d.rounded_rectangle((54,54,26+pw,26+ph),radius=18,outline=(255,230,160,200),width=2)
  for x in (40,40+pw):
    cy=40+ph//2; d.polygon([(x,cy-30),(x+30,cy),(x,cy+30),(x-30,cy)],fill=(255,205,90,255),outline=(110,30,0,255))
  im.alpha_composite(textimg,(40+(pw-textimg.width)//2,40+(ph-textimg.height)//2-4))
  return im
def rays(cx,cy,r,alpha=110):
  im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
  for k in range(36):
    a=k*math.pi*2/36; a2=a+0.06
    d.polygon([(cx,cy),(cx+r*math.cos(a),cy+r*math.sin(a)),(cx+r*math.cos(a2),cy+r*math.sin(a2))],fill=(255,190,80,alpha if k%2==0 else alpha//2))
  im=im.filter(ImageFilter.GaussianBlur(18))
  yy,xx=np.mgrid[:H,:W]; fall=np.clip(1-np.sqrt((xx-cx)**2+(yy-cy)**2)/r,0,1)
  a=(np.asarray(im.getchannel('A'),np.float32)*fall).astype(np.uint8); im.putalpha(Image.fromarray(a))
  glow=Image.new('RGBA',(W,H),(255,170,60,0)); glow.putalpha(Image.fromarray((fall**2*120).astype(np.uint8))); im.alpha_composite(glow)
  return im
def sparkles(c,n=90,seed=1,xmax=W):
  r=random.Random(seed); d=ImageDraw.Draw(c)
  for _ in range(n):
    x=r.uniform(0,xmax); y=r.uniform(0,H); s=r.uniform(1.5,5); a=int(r.uniform(120,255))
    d.ellipse((x-s,y-s,x+s,y+s),fill=(255,225,140,a))
    if s>4: d.line([(x-14,y),(x+14,y)],fill=(255,240,190,a),width=2); d.line([(x,y-14),(x,y+14)],fill=(255,240,190,a),width=2)
def build(name,bgsrc,deity,hero_font,hero,top,ban,deity_crop,deity_x):
  bg=Image.open(T+bgsrc).convert('RGB').resize((W,H))
  bg=ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(2))).enhance(0.55).convert('RGBA')
  c=bg
  # left dark gradient for clean text area
  g=np.clip((np.linspace(1,0,W)-0.15)*1.6,0,0.85); a=(np.tile(g,(H,1))*255).astype(np.uint8)
  dk=Image.new('RGBA',(W,H),(25,5,8,0)); dk.putalpha(Image.fromarray(a)); c.alpha_composite(dk)
  c.alpha_composite(rays(505,470,950,95))
  # deity
  f=Image.open(T+deity).convert('RGBA'); x0,y0,x1,y1=deity_crop; part=f.crop((x0,y0,x1,y1))
  sc=H/part.height; part=part.resize((int(part.width*sc),H),Image.LANCZOS)
  al=np.ones((part.height,part.width),np.float32); fe=200
  al*=np.clip(np.arange(part.width)/fe,0,1)[None,:]**1.4
  part.putalpha(Image.fromarray((al*255).astype(np.uint8))); c.alpha_composite(part,(W-part.width,0))
  sparkles(c,110,3)
  # text block
  cx=505; y=80
  t1=fit(gold3d(top,'eczar',112,style='white',depth=3),860); c.alpha_composite(t1,(cx-t1.width//2,y)); y+=t1.height-8
  o=ornament(800); c.alpha_composite(o,(cx-o.width//2,y)); y+=o.height-4
  h=fit(gold3d(hero,hero_font,300),1000); c.alpha_composite(h,(cx-h.width//2,y)); y+=h.height+4
  o2=ornament(640); c.alpha_composite(o2,(cx-o2.width//2,y)); y+=o2.height-6
  bt=fit(gold3d(ban,'eczar',96,style='white',depth=3),700); p=plaque(bt); c.alpha_composite(p,(cx-p.width//2,y))
  # logo
  lg=logo.resize((150,150),Image.LANCZOS); c.alpha_composite(lg,(28,H-178))
  # vignette
  yy,xx=np.mgrid[:H,:W]; d=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)
  v=Image.new('RGBA',(W,H),(0,0,0,0)); v.putalpha(Image.fromarray((np.clip(d-0.75,0,1)*0.8*255).astype(np.uint8))); c.alpha_composite(v)
  c.convert('RGB').resize((1280,720),Image.LANCZOS).save(T+name,quality=93)
# A: classy serif, Lakshmi close-up on lotus
build('thumb_A.jpg','f_109269.png','f_109265.png','eczar','जय लक्ष्मी माँ','आई दीवाली','DJ धमाका 2026',(540,0,1420,900),930)
# B: bold DJ font, Lakshmi in sky with crowd
build('thumb_B.jpg','f_109271.png','f_109267.png','modak','जय लक्ष्मी माँ','दीवाली का जयकारा','DJ धमाका 2026',(520,0,1400,1080),900)
print('ok')
