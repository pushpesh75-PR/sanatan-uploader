import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
S='/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad'
sys.path.insert(0,S+'/work')
from txt import render
T=S+'/thumb/'
W,H=1920,1080
logo=Image.open(S+'/brand/logo.png').convert('RGBA')
def fitw(im,w): return im.resize((w,int(im.height*w/im.width)),Image.LANCZOS) if im.width>w else im
def banner(text,size=96,fill=(205,20,20)):
  t=render(text,'teko',size,glow=(90,0,0),grad=((255,255,255),(255,250,235),(255,225,200)))
  pw,ph=t.width+80,t.height+30
  im=Image.new('RGBA',(pw+60,ph+60),(0,0,0,0))
  sh=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(sh).polygon([(40,38),(pw+40,38),(pw+20,ph+38),(20,ph+38)],fill=(0,0,0,170)); sh=sh.filter(ImageFilter.GaussianBlur(10)); im.alpha_composite(sh)
  d=ImageDraw.Draw(im); d.polygon([(30,25),(pw+30,25),(pw+10,ph+25),(10,ph+25)],fill=fill+(255,),outline=(255,210,90,255))
  d.line([(30,25),(pw+30,25),(pw+10,ph+25),(10,ph+25),(30,25)],fill=(255,210,90,255),width=5)
  im.alpha_composite(t,(20+(pw-t.width)//2,25+(ph-t.height)//2))
  return im
def leftbg(src,dark=0.45,blur=6):
  b=Image.open(T+src).convert('RGB').resize((W,H)).filter(ImageFilter.GaussianBlur(blur))
  return ImageEnhance.Brightness(b).enhance(dark).convert('RGBA')
def place_right(canvas,src,cx_src,crop_w,dest_x,scale=1.0,feather=220):
  f=Image.open(T+src).convert('RGBA')
  x0=int(cx_src-crop_w/2); part=f.crop((x0,0,x0+crop_w,1080))
  if scale!=1.0: part=part.resize((int(part.width*scale),int(part.height*scale)),Image.LANCZOS)
  # feather left edge
  a=np.ones((part.height,part.width),np.float32)
  ramp=np.clip(np.arange(part.width)/feather,0,1)**1.5; a*=ramp[None,:]
  part.putalpha(Image.fromarray((a*255).astype(np.uint8)))
  canvas.alpha_composite(part,(dest_x,H-part.height))
def vignette(canvas,strength=0.55):
  yy,xx=np.mgrid[:H,:W]; d=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)
  a=(np.clip(d-0.6,0,1)*strength*255).astype(np.uint8)
  v=Image.new('RGBA',(W,H),(0,0,0,0)); v.putalpha(Image.fromarray(a)); canvas.alpha_composite(v)
def glowdots(canvas,seed=3,n=60):
  import random; r=random.Random(seed); d=ImageDraw.Draw(canvas)
  for _ in range(n):
    x=r.uniform(0,W*0.55); y=r.uniform(0,H); s=r.uniform(2,6)
    d.ellipse((x-s,y-s,x+s,y+s),fill=(255,215,120,int(r.uniform(90,220))))
def text_block(canvas,main,sub,ban,x_center=520,y0=150,msize=250):
  m=fitw(render(main,'teko',msize),980); canvas.alpha_composite(m,(int(x_center-m.width/2),y0))
  s=fitw(render(sub,'teko',150,grad=((255,255,255),(255,240,200),(255,200,90))),900); y1=y0+m.height-40
  canvas.alpha_composite(s,(int(x_center-s.width/2),y1))
  b=fitw(banner(ban),900); y2=y1+s.height-10
  canvas.alpha_composite(b,(int(x_center-b.width/2),y2))
def logo_corner(canvas,size=170,pos=(30,30)):
  canvas.alpha_composite(logo.resize((size,size),Image.LANCZOS),pos)
def save(canvas,name):
  canvas.convert('RGB').resize((1280,720),Image.LANCZOS).save(T+name,quality=92)
# A: Lakshmi on lotus right, ghat/fireworks left
c=leftbg('f_109269.png',0.5,4); place_right(c,'f_109265.png',960,1150,800,1.0); glowdots(c); vignette(c)
text_block(c,'जय  लक्ष्मी  माँ','आई  दीवाली','दीवाली  DJ  धमाका  2026',x_center=470,y0=120); logo_corner(c,150,(1740,30)); save(c,'thumb_A.jpg')
# B: Lakshmi in sky over crowd right, flags/fireworks left
c=leftbg('f_109271.png',0.5,4); place_right(c,'f_109267.png',960,1100,820,1.0); glowdots(c,5); vignette(c)
text_block(c,'जय  लक्ष्मी  माँ','आई  दीवाली','दीवाली  DJ  धमाका  2026',x_center=470,y0=120); logo_corner(c,150,(1740,30)); save(c,'thumb_B.jpg')
# C: Lakshmi + Ganesha both right, colour burst left
c=leftbg('f_109268.png',0.45,5)
place_right(c,'f_109264.png',960,820,760,0.82,feather=160); place_right(c,'f_109265.png',960,900,1160,0.9,feather=160)
glowdots(c,9); vignette(c)
text_block(c,'जय  लक्ष्मी  माँ','गणपति  बप्पा  मोरया','दीवाली  DJ  धमाका  2026',x_center=440,y0=120,msize=230); logo_corner(c,150,(1740,30)); save(c,'thumb_C.jpg')
print('ok')
