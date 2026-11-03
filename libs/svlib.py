# Shared helpers for Shiv Tandav long video + shorts
import os, glob, subprocess, math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S='/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad'
SV=S+'/sv/'
sys.path.insert(0,S+'/work')
from txt import render
from gold import gold3d
FPS=24
B=np.load(SV+'beats.npy').astype(float)
def bt(t):
  i=int(np.argmin(abs(B-t))); return float(B[i])
def beats(a,b): return [float(x) for x in B if a-1e-6<=x<b-1e-6]
# clips: id -> (safe_end, mirror_ok)
CL={'c15':(10,1),'c08':(10,1),'c07':(10,1),'c12':(7,1),'c06':(7,1),'c05':(6,0),'c10':(10,0),'c04':(8,1),'c01':(10,0),
    'c16':(10,1),'c03':(10,1),'c14':(10,1),'c13':(7,1),'c09':(6,0),'c11':(10,0),'c02':(10,0)}
# stills: id -> (path, crop box in source (x0,y0,x1,y1))
def _img(p): return Image.open(p).convert('RGB')
RAV=_img(SV+'img/ravana.webp').crop((0,0,2580,1451))
MED=_img(SV+'img/shiva_med.png')
SP=_img(SV+'img/shivparvati.jpg')
SHV=_img(SV+'img/shiva_v.jpg')
STILL={
 'RAV':(RAV,(0,0,2580,1451),(260,90,2320,1250)),
 'MED':(MED,(0,0,1672,941),(330,40,1340,610)),
 'MEDFACE':(MED,(560,40,1110,350),(640,70,1030,290)),
 'MEDNECK':(MED,(420,150,1250,617),(500,200,1170,577)),
 'SP':(SP,(0,0,1920,1088),(300,40,1700,830)),
 'SPFACE':(SP,(560,60,1460,566),(640,90,1380,506)),
 'SHV':(SHV,(0,0,1088,1920),(110,190,978,1733)),
}
def seg_video(out,clip,off,speed,N,W,H,fx,mirror):
  vf=[]
  if mirror: vf.append('hflip')
  vf+= [f'setpts=PTS/{speed:.4f}',f'fps={FPS}']
  if 'punch' in fx:
    z="(1.04+0.08*max(0\\,1-t/0.28))"
    vf.append(f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame")
    vf.append(f"crop={W}:{H}:x='(iw-ow)/2+20*sin(t*38)*max(0\\,1-t/0.38)':y='(ih-oh)/2+12*cos(t*33)*max(0\\,1-t/0.38)'")
  else:
    vf.append(f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}')
  vf.append('format=yuv420p')
  r=subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{off:.3f}','-i',SV+'c/'+clip+'.mp4','-an','-vf',','.join(vf),'-frames:v',str(N),'-r',str(FPS),
     '-c:v','libx264','-preset','veryfast','-crf','16','-g','48',out],capture_output=True,text=True)
  if r.returncode: raise SystemExit(r.stderr[-400:])
def seg_still(out,sid,N,W,H,fx,rev=False):
  im,(a0,b0,a1,b1),(c0,d0,c1,d1)=STILL[sid]
  # interpolate crop box from start box to end box (Ken Burns), keep output aspect
  p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
     '-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-g','48',out],stdin=subprocess.PIPE)
  ar=W/H
  for f in range(N):
    u=f/max(1,N-1); u=u*u*(3-2*u)
    if rev: u=1-u
    x0=a0+(c0-a0)*u; y0=b0+(d0-b0)*u; x1=a1+(c1-a1)*u; y1=b1+(d1-b1)*u
    cx=(x0+x1)/2; cy=(y0+y1)/2; w=x1-x0; h=y1-y0
    if w/h>ar: w=h*ar
    else: h=w/ar
    if 'punch' in fx:
      lt=f/FPS; z=1+0.08*max(0,1-lt/0.28); w/=z; h/=z
      cx+=18*math.sin(lt*38)*max(0,1-lt/0.38); cy+=10*math.cos(lt*33)*max(0,1-lt/0.38)
    box=(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
    fr=im.resize((W,H),Image.BICUBIC,box=box)
    p.stdin.write(fr.tobytes())
  p.stdin.close(); p.wait()
def render_timeline(segs,W,H,d,endt):
  """segs: list of (t_out, src, fx) sorted; each runs to next; src = clip id or still id."""
  os.makedirs(d,exist_ok=True)
  for f in glob.glob(d+'/*'): os.remove(f)
  cur={}; mir={}; lst=open(d+'/list.txt','w')
  segs=sorted(segs,key=lambda x:x[0])
  for n,(t0,src,fx) in enumerate(segs):
    t1=segs[n+1][0] if n+1<len(segs) else endt
    N=round(t1*FPS)-round(t0*FPS)
    if N<=0: continue
    dur=N/FPS; out=f'{d}/s{n:03d}.mp4'
    if src in STILL:
      seg_still(out,src,N,W,H,fx,rev=('out' in fx))
    else:
      win,mok=CL[src]; sp=0.6 if 'slow' in fx else 1.0
      need=dur*sp
      if need>win: sp=win/dur; need=win
      off=cur.get(src,0.0)
      if off+need>win: off=0.0
      cur[src]=off+need*0.7+0.3
      if cur[src]>=win-0.6: cur[src]=(n*1.3)%max(0.1,win-need)
      m=False
      if mok: mir[src]=not mir.get(src,False); m=mir[src]
      seg_video(out,src,off,sp,N,W,H,fx,m)
    lst.write(f"file '{out}'\n")
  lst.close()
  subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',d+'/list.txt','-c','copy',d+'/base.mp4'],check=True)
  return d+'/base.mp4'
# ---------- overlay helpers ----------
def fitw(im,maxw):
  return im if im.width<=maxw else im.resize((maxw,int(im.height*maxw/im.width)),Image.LANCZOS)
FIRE=((255,246,220),(255,196,90),(235,95,20))
def skt(text,size=84,maxw=1720):
  return fitw(render(text,'eczar',size,glow=(255,90,10),grad=FIRE),maxw)
def mean(text,size=40,maxw=1760):
  return fitw(render(text,'martel',size,glow=(0,0,0),grad=((255,255,255),(250,240,220),(230,215,190))),maxw)
def chant(text,size=170,maxw=1500): return fitw(gold3d(text,'eczar',size),maxw)
def pulse(t_song):
  i=np.searchsorted(B,t_song)-1
  return 0 if i<0 else max(0.0,1-(t_song-B[i])/0.18)
def place(c,sp,s,alpha,cx,cy):
  if alpha<=0: return
  w=max(1,int(sp.width*s)); h=max(1,int(sp.height*s)); im=sp.resize((w,h),Image.BILINEAR) if s!=1 else sp
  if alpha<1:
    im=im.copy(); a=(np.asarray(im.getchannel('A'),np.float32)*alpha).astype(np.uint8); im.putalpha(Image.fromarray(a))
  c.alpha_composite(im,(int(cx-w/2),int(cy-h/2)))
def reveal(c,sp,prog,alpha,cx,cy):
  """left-to-right wipe reveal with soft edge"""
  if alpha<=0: return
  w,h=sp.size; im=sp.copy(); a=np.asarray(im.getchannel('A'),np.float32)
  edge=int(w*min(1.0,prog)*1.15)
  ramp=np.clip((edge-np.arange(w))/90.0,0,1)[None,:]
  a=a*ramp*alpha; im.putalpha(Image.fromarray(a.astype(np.uint8)))
  c.alpha_composite(im,(int(cx-w/2),int(cy-h/2)))
def flash_alpha(lt):
  if lt<0 or lt>0.35: return 0
  if lt<0.04: return 0.95
  if lt<0.08: return 0.25
  if lt<0.13: return 0.75
  return 0.75*(1-(lt-0.13)/0.22)
def make_embers(n,W,H,seed=11):
  r=random.Random(seed); return [(r.uniform(0,W),r.uniform(0,H),r.uniform(60,220),r.uniform(1.5,4.5),r.uniform(0,6.28),r.uniform(-30,30)) for _ in range(n)]
def draw_embers(c,E,t,W,H,alpha=1.0):
  d=ImageDraw.Draw(c)
  for (x,y,v,s,ph,dx) in E:
    yy=(y-v*t)%H; xx=(x+dx*t+12*math.sin(t*2+ph))%W
    a=int(255*alpha*(0.55+0.45*math.sin(t*5+ph)))
    if a<20: continue
    d.ellipse((xx-s,yy-s,xx+s,yy+s),fill=(255,150+int(60*math.sin(ph)),40,a))
def pill(text,size=70,fill=(205,25,25)):
  t=render(text,'teko',size,glow=(110,0,0),grad=((255,255,255),(255,255,255),(255,232,232)))
  pw,ph=t.width+90,t.height+36
  im=Image.new('RGBA',(pw+40,ph+40),(0,0,0,0)); d=ImageDraw.Draw(im)
  sh=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((26,30,26+pw,30+ph),radius=ph//2,fill=(0,0,0,160)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
  d.rounded_rectangle((20,20,20+pw,20+ph),radius=ph//2,fill=fill+(255,),outline=(255,210,120,255),width=4)
  im.alpha_composite(t,(20+(pw-t.width)//2,20+(ph-t.height)//2)); return im
LOGO=Image.open(S+'/brand/logo.png').convert('RGBA')
