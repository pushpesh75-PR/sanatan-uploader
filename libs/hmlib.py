# Hanuman dhol-tasha DJ — frame-level beat editor (punch zoom, shake, flash, embers, chant bursts)
import os, sys, math, random, subprocess
import numpy as np, cv2
from smlib import *
HM=S+'/hm/'; HZ=HM+'zip/'
FPSV=24
VERT={'h02','h03','h04'}
DEITY={'h04','h13'}
def src_frames(clip,off,n,W,H,speed=1.0,cy=None,cx=0.5,zoom=1.0):
  """decode n frames of clip from off (sec of source) at speed, filled to W x H (vertical clips cropped at cy)."""
  path=HZ+clip+'.mp4'
  if clip in VERT and W>H:   # vertical source into landscape
    cy=0.35 if cy is None else cy
    vf=f"scale={W}*{zoom}:-2,crop={W}:{H}:(iw-{W})/2:'max(0,min(ih-{H},ih*{cy}-{H}/2))'"
  elif clip not in VERT and H>W:  # landscape into vertical
    vf=f"scale=-2:{H}*{zoom},crop={W}:{H}:'max(0,min(iw-{W},iw*{cx}-{W}/2))':(ih-{H})/2"
  else:
    vf=f"scale={W}*{zoom}:{H}*{zoom},crop={W}:{H}"
  vf=f"setpts=PTS/{speed},fps={FPSV},"+vf+",tpad=stop_mode=clone:stop_duration=12"
  p=subprocess.run(['ffmpeg','-v','error','-ss',f'{off:.3f}','-i',path,'-an','-vf',vf,'-frames:v',str(n),'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True)
  a=np.frombuffer(p.stdout,np.uint8)
  k=len(a)//(W*H*3); a=a[:k*W*H*3].reshape(k,H,W,3)
  if k<n: a=np.concatenate([a,np.repeat(a[-1:],n-k,0)])
  return a
def warp(fr,z,dx,dy):
  H,W=fr.shape[:2]
  if abs(z-1)<1e-3 and dx==0 and dy==0: return fr
  M=np.float32([[z,0,(1-z)*W/2+dx],[0,z,(1-z)*H/2+dy]])
  return cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
# ---------- text styles ----------
def metal(text,size,font='teko',sw=6):
  f=FT(font,size); pad=size//2+sw+10
  bb=ImageDraw.Draw(Image.new('L',(8,8))).textbbox((0,0),text,font=f,stroke_width=sw)
  Wt,Ht=bb[2]-bb[0]+2*pad,bb[3]-bb[1]+2*pad; o=(pad-bb[0],pad-bb[1])
  m=Image.new('L',(Wt,Ht)); ImageDraw.Draw(m).text(o,text,font=f,fill=255)
  ms=Image.new('L',(Wt,Ht)); ImageDraw.Draw(ms).text(o,text,font=f,fill=255,stroke_width=sw,stroke_fill=255)
  out=Image.new('RGBA',(Wt,Ht),(0,0,0,0))
  g=Image.new('RGBA',(Wt,Ht),(255,110,0,0)); g.putalpha(ms.filter(ImageFilter.GaussianBlur(size/5)).point(lambda v:int(v*0.8))); out.alpha_composite(g)
  sd=Image.new('RGBA',(Wt,Ht),(0,0,0,0)); sd.putalpha(ms.filter(ImageFilter.GaussianBlur(4))); out.alpha_composite(sd,(0,5))
  st=Image.new('RGBA',(Wt,Ht),(70,8,0,255)); st.putalpha(ms); out.alpha_composite(st)
  yy=np.linspace(0,1,Ht)[:,None]
  stops=[(0,(255,250,210)),(0.40,(255,206,70)),(0.55,(240,130,10)),(0.66,(255,200,80)),(1,(200,90,0))]
  col=np.zeros((Ht,1,3))
  for (p0,c0),(p1,c1) in zip(stops,stops[1:]):
    sel=(yy>=p0)&(yy<=p1); tt=((yy-p0)/(p1-p0)).clip(0,1)
    for k in range(3): col[...,k]=np.where(sel,c0[k]+(c1[k]-c0[k])*tt,col[...,k])
  fl=Image.fromarray(np.broadcast_to(col,(Ht,Wt,3)).astype(np.uint8),'RGB').convert('RGBA'); fl.putalpha(m); out.alpha_composite(fl)
  return out.crop(out.getbbox())
def embers(n,W,H,seed=4):
  r=random.Random(seed); return [(r.uniform(0,W),r.uniform(0,H),r.uniform(60,190),r.uniform(1.4,3.6),r.uniform(0,6.28),r.uniform(-25,25)) for _ in range(n)]
def draw_embers(c,P,t,W,H,amt):
  if amt<=0.02: return
  d=ImageDraw.Draw(c)
  for k,(x,y,v,s,ph,dx) in enumerate(P):
    if k>len(P)*amt: break
    yy=(y-v*t)%H; xx=(x+dx*t+22*math.sin(t*1.3+ph))%W
    fl=0.55+0.45*math.sin(t*9+ph)
    a=int(255*fl*min(1,amt*1.2))
    d.ellipse((xx-s,yy-s,xx+s,yy+s),fill=(255,int(140+80*fl),40,a))
