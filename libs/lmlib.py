# Lakshmi mantra 108 — design language: plum-rose lotus plaque, gold coin sparkle, lotus-bead mala
import math, random
from smlib import *
LM=S+'/lm/'; LZ=LM+'zip/'
for k in ['c%02d'%i for i in range(1,13)]+['c01p','c03p','c06p','c07p','c08p','c11p']:
  SRC[k]=LZ+k+'.mp4'
IVORY=(255,250,240); GOLDY=(255,214,120); PLUM=(58,10,28); ROSE=(236,120,160); GOLD2=(242,198,110)
def lotus_plaque(w,h,r=34):
  im=Image.new('RGBA',(w+60,h+70),(0,0,0,0)); ox,oy=30,40
  sh=Image.new('L',im.size); ImageDraw.Draw(sh).rounded_rectangle((ox,oy+8,ox+w,oy+8+h),r,fill=160)
  s=Image.new('RGBA',im.size,(0,0,0,0)); s.putalpha(sh.filter(ImageFilter.GaussianBlur(16))); im.alpha_composite(s)
  y=np.linspace(0,1,h)[:,None]; x=np.linspace(-1,1,w)[None,:]
  top=np.array((86,16,44),float); bot=np.array((40,6,22),float)
  col=top+(bot-top)*y[...,None]; col=col*(1+0.10*np.exp(-(x**2)*3)[...,None])   # soft centre glow
  pm=Image.new('L',(w,h)); ImageDraw.Draw(pm).rounded_rectangle((0,0,w-1,h-1),r,fill=205)
  b=Image.fromarray(np.clip(col,0,255).astype(np.uint8),'RGB').convert('RGBA'); b.putalpha(pm); im.alpha_composite(b,(ox,oy))
  d=ImageDraw.Draw(im)
  d.rounded_rectangle((ox,oy,ox+w-1,oy+h-1),r,outline=GOLD2+(255,),width=3)
  d.rounded_rectangle((ox+9,oy+9,ox+w-10,oy+h-10),r-9,outline=ROSE+(120,),width=1)
  # lotus crest on top
  cx=ox+w//2; cy=oy
  for ang,L,wd in [(0,30,13),(-38,24,11),(38,24,11),(-70,18,9),(70,18,9)]:
    a=math.radians(ang-90); tip=(cx+L*math.cos(a),cy+L*math.sin(a))
    pa=math.radians(ang); bl=(cx-wd*math.cos(pa)*0.5,cy-wd*math.sin(pa)*0.5); br=(cx+wd*math.cos(pa)*0.5,cy+wd*math.sin(pa)*0.5)
    d.polygon([bl,tip,br,(cx,cy+6)],fill=(250,170,196,255),outline=GOLD2+(255,))
  d.ellipse((cx-5,cy-2,cx+5,cy+8),fill=GOLD2+(255,))
  for sx in (-1,1):
    for k in range(3): d.ellipse((cx+sx*(40+k*14)-2.5,cy-2.5,cx+sx*(40+k*14)+2.5,cy+2.5),fill=GOLD2+(255,))
  return im
def lcard(main,mean=None,minw=980,padx=80,pady=34,gap=10):
  cw=max(minw,main.width+2*padx,(mean.width+2*padx) if mean else 0)
  dv=divider(min(cw-2*padx,460)) if mean else None
  ch=pady+main.height+((gap+dv.height+gap+mean.height) if mean else 0)+pady-6
  im=lotus_plaque(cw,ch); y=40+pady
  mo=(30+(cw-main.width)//2,y); im.alpha_composite(main,mo); y+=main.height
  if mean:
    y+=gap; im.alpha_composite(dv,(30+(cw-dv.width)//2,y)); y+=dv.height+gap
    im.alpha_composite(mean,(30+(cw-mean.width)//2,y))
  return im,mo
_LM={}
def lmala(n,R=96):
  if n in _LM: return _LM[n]
  S2=2*R+84; im=Image.new('RGBA',(S2,S2),(0,0,0,0)); c=S2/2
  bg=Image.new('L',im.size); ImageDraw.Draw(bg).ellipse((c-R-26,c-R-26,c+R+26,c+R+26),fill=195)
  disc=Image.new('RGBA',im.size,PLUM+(0,)); disc.putalpha(bg.filter(ImageFilter.GaussianBlur(3))); im.alpha_composite(disc)
  d=ImageDraw.Draw(im); d.ellipse((c-R-26,c-R-26,c+R+26,c+R+26),outline=GOLD2+(235,),width=2)
  glow=Image.new('RGBA',im.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
  for k in range(108):
    a=-math.pi/2+2*math.pi*(k+0.5)/108; x=c+R*math.cos(a); y=c+R*math.sin(a)
    if k<n:
      gd.ellipse((x-7,y-7,x+7,y+7),fill=(255,150,190,190)); d.ellipse((x-4.2,y-4.2,x+4.2,y+4.2),fill=(255,226,170,255))
    else: d.ellipse((x-3,y-3,x+3,y+3),fill=(255,220,235,110))
  g2=glow.filter(ImageFilter.GaussianBlur(4)); g2.alpha_composite(im); im=g2; d=ImageDraw.Draw(im)
  # small lotus at top (sumeru)
  for ang in (-40,0,40):
    a=math.radians(ang-90); d.polygon([(c-6,c-R-2),(c+16*math.cos(a),c-R-2+16*math.sin(a)),(c+6,c-R-2)],fill=(250,170,196,255),outline=GOLD2+(255,))
  num=rich(str(n),'martel600',72,IVORY,stroke=PLUM,sw=3); of=rich('/ 108','martel600',27,GOLDY,stroke=PLUM,sw=2)
  im.alpha_composite(num,(int(c-num.width/2),int(c-num.height/2-14))); im.alpha_composite(of,(int(c-of.width/2),int(c+30)))
  _LM[n]=im; return im
def mandala(D=1000,n=16):
  """soft rotating lotus mandala (gold line petals) for title"""
  im=Image.new('RGBA',(D,D),(0,0,0,0)); d=ImageDraw.Draw(im); c=D/2
  for ring,(r0,r1,cnt,a) in enumerate([(120,300,n,120),(260,430,n*2,80),(380,490,n*2,45)]):
    for k in range(cnt):
      t=2*math.pi*(k+0.5*(ring%2))/cnt; w=math.pi/cnt*0.9
      pts=[]
      for s in np.linspace(-1,1,24):
        rr=r0+(r1-r0)*(1-s*s); aa=t+w*s*(1-0.35*(1-s*s))
        pts.append((c+rr*math.cos(aa),c+rr*math.sin(aa)))
      d.line(pts+[pts[0]],fill=(255,214,150,a),width=2)
  m=np.hypot(*np.meshgrid(np.arange(D)-c,np.arange(D)-c)); fall=np.clip(1-m/c,0,1)**0.8
  a=(np.asarray(im.getchannel('A'),np.float32)*fall).astype(np.uint8); im.putalpha(Image.fromarray(a))
  return im.filter(ImageFilter.GaussianBlur(1.2))
def coins(n,W,H,seed=8):
  r=random.Random(seed); return [(r.uniform(0,W),r.uniform(0,H),r.uniform(10,26),r.uniform(1.6,3.8),r.uniform(0,6.28),r.uniform(-6,6)) for _ in range(n)]
def draw_coins(c,P,t,W,H,alpha=1.0):
  """gold sparkles drifting gently DOWN with twinkle (Lakshmi's blessing)"""
  d=ImageDraw.Draw(c)
  for (x,y,v,s,ph,dx) in P:
    yy=(y+v*t)%H; xx=(x+dx*t+16*math.sin(t*0.35+ph))%W
    tw=0.5+0.5*math.sin(t*2.1+ph)
    a=int(255*alpha*(0.25+0.6*tw))
    if a<14: continue
    d.ellipse((xx-s,yy-s,xx+s,yy+s),fill=(255,214,130,a))
    if tw>0.85: d.line((xx-s*2.6,yy,xx+s*2.6,yy),fill=(255,240,200,int(a*0.7)),width=1); d.line((xx,yy-s*2.6,xx,yy+s*2.6),fill=(255,240,200,int(a*0.7)),width=1)
