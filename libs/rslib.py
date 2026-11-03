# Calm cinematic toolkit for Ram Stuti (dissolves, Ken Burns, soft text)
import os, glob, subprocess, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S='/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad'
RS=S+'/rs/'; F=S+'/fonts/'
FPS=24
D=1.2   # dissolve length
VID={'r01':6.0,'r02':10,'r03':10,'r06':10,'r07':10,'r09':10,'r11':10,'r04':10,'r05':10,'r08':10,'r10':10,'r12':10}
def img(p): return Image.open(p).convert('RGB')
PH={}
def still(name):
  if name not in PH: PH[name]=img(RS+'c/'+name+'.jpg')
  return PH[name]
def seg_still(out,name,boxes,N,W,H):
  im=still(name); (a0,b0,a1,b1),(c0,d0,c1,d1)=boxes
  p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
     '-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-g','48',out],stdin=subprocess.PIPE)
  ar=W/H
  for f in range(N):
    u=f/max(1,N-1); u=u*u*(3-2*u)
    x0=a0+(c0-a0)*u; y0=b0+(d0-b0)*u; x1=a1+(c1-a1)*u; y1=b1+(d1-b1)*u
    cx=(x0+x1)/2; cy=(y0+y1)/2; w=x1-x0; h=y1-y0
    if w/h>ar: w=h*ar
    else: h=w/ar
    p.stdin.write(im.resize((W,H),Image.BICUBIC,box=(cx-w/2,cy-h/2,cx+w/2,cy+h/2)).tobytes())
  p.stdin.close(); p.wait()
def seg_video(out,clip,off,speed,N,W,H):
  vf=[f'setpts=PTS/{speed:.4f}',f'fps={FPS}',f'scale={W}:{H}:force_original_aspect_ratio=increase',f'crop={W}:{H}','format=yuv420p']
  r=subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{off:.3f}','-i',RS+'c/'+clip+'.mp4','-an','-vf',','.join(vf),'-frames:v',str(N),'-r',str(FPS),
     '-c:v','libx264','-preset','veryfast','-crf','16','-g','48',out],capture_output=True,text=True)
  if r.returncode: raise SystemExit(r.stderr[-400:])
def build(segs,endt,W,H,d):
  """segs: list of (t_start, kind, spec). kind 'v': (clip, offset) ; kind 's': (photo, (startbox,endbox)). Dissolve D between segments."""
  os.makedirs(d,exist_ok=True)
  for f in glob.glob(d+'/*'): os.remove(f)
  segs=sorted(segs,key=lambda x:x[0]); files=[]; durs=[]
  for n,(t0,kind,spec) in enumerate(segs):
    t1=segs[n+1][0] if n+1<len(segs) else endt
    dur=t1-t0; last=(n==len(segs)-1)
    L=dur+(0 if last else D); N=int(round(L*FPS)); out=f'{d}/s{n:03d}.mp4'
    if kind=='s': seg_still(out,spec[0],spec[1],N,W,H)
    else:
      clip,off=spec[0],spec[1]; win=VID[clip]
      sp=min(1.0,(win-off)/L) if (win-off)<L else 1.0
      if 'slow' in spec[2:] : sp=min(sp,0.8)
      seg_video(out,clip,off,max(0.45,sp),N,W,H)
    files.append(out); durs.append(dur)
  # xfade chain
  inp=[]; [inp.extend(['-i',f]) for f in files]
  fc=[]; prev='[0:v]'; off=0.0
  for k in range(1,len(files)):
    off+=durs[k-1]
    lab=f'[x{k}]'
    fc.append(f'{prev}[{k}:v]xfade=transition=fade:duration={D}:offset={off:.3f}{lab}')
    prev=lab
  fc.append(f'{prev}format=yuv420p[vout]')
  r=subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fc),'-map','[vout]','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','16',d+'/base.mp4'],capture_output=True,text=True)
  if r.returncode: raise SystemExit(r.stderr[-600:])
  return d+'/base.mp4'
# ---------- soft elegant text ----------
def soft(text,font,size,grad=((255,246,222),(250,222,160),(225,180,110)),shadow=170,maxw=None,glow=None):
  f=ImageFont.truetype(F+font+'.ttf',size,layout_engine=ImageFont.Layout.RAQM)
  pad=int(size*0.7)
  bb=ImageDraw.Draw(Image.new('L',(8,8))).textbbox((0,0),text,font=f)
  W=bb[2]-bb[0]+2*pad; H=bb[3]-bb[1]+2*pad; o=(pad-bb[0],pad-bb[1])
  m=Image.new('L',(W,H)); ImageDraw.Draw(m).text(o,text,font=f,fill=255)
  y=np.linspace(0,1,H)[:,None]; g0,g1,g2=[np.array(c,float) for c in grad]
  col=np.where((y<0.5)[...,None], g0+(g1-g0)*(y/0.5)[...,None], g1+(g2-g1)*((y-0.5)/0.5)[...,None])
  fill=Image.fromarray(np.broadcast_to(col,(H,W,3)).astype(np.uint8),'RGB').convert('RGBA'); fill.putalpha(m)
  out=Image.new('RGBA',(W,H),(0,0,0,0))
  sh=Image.new('RGBA',(W,H),(10,5,0,0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(size/9)).point(lambda v:min(255,int(v*shadow/100))))
  out.alpha_composite(sh,(0,0)); out.alpha_composite(sh,(2,3))
  if glow:
    gl=Image.new('RGBA',(W,H),glow+(0,)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(size/5)).point(lambda v:int(v*0.55))); out.alpha_composite(gl)
  out.alpha_composite(fill)
  out=out.crop(out.getbbox())
  if maxw and out.width>maxw: out=out.resize((maxw,int(out.height*maxw/out.width)),Image.LANCZOS)
  return out
def ornament(w,col=(240,205,140),a=230):
  im=Image.new('RGBA',(w,40),(0,0,0,0)); d=ImageDraw.Draw(im); cy=20
  for side in (-1,1):
    x0=w//2+side*26; x1=w//2+side*(w//2-12)
    d.line([(x0,cy),(x1,cy)],fill=col+(a,),width=2)
    d.ellipse((x1-4,cy-4,x1+4,cy+4),fill=col+(a,))
  d.polygon([(w//2,cy-11),(w//2+11,cy),(w//2,cy+11),(w//2-11,cy)],outline=col+(a,),width=2)
  d.ellipse((w//2-3,cy-3,w//2+3,cy+3),fill=col+(a,))
  return im
def place(c,sp,s,alpha,cx,cy,blur=0):
  if alpha<=0.01: return
  im=sp if s==1 else sp.resize((max(1,int(sp.width*s)),max(1,int(sp.height*s))),Image.BILINEAR)
  if blur>0.3: im=im.filter(ImageFilter.GaussianBlur(blur))
  if alpha<1:
    im=im.copy(); a=(np.asarray(im.getchannel('A'),np.float32)*alpha).astype(np.uint8); im.putalpha(Image.fromarray(a))
  c.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def dust(n,W,H,seed=3):
  r=random.Random(seed); return [(r.uniform(0,W),r.uniform(0,H),r.uniform(6,22),r.uniform(1.2,3.6),r.uniform(0,6.28),r.uniform(-8,8)) for _ in range(n)]
def draw_dust(c,P,t,W,H,alpha=1.0):
  d=ImageDraw.Draw(c)
  for (x,y,v,s,ph,dx) in P:
    yy=(y-v*t)%H; xx=(x+dx*t+20*math.sin(t*0.4+ph))%W
    a=int(255*alpha*(0.35+0.35*math.sin(t*1.3+ph)))
    if a<12: continue
    d.ellipse((xx-s,yy-s,xx+s,yy+s),fill=(255,226,160,a))
def bottom_grad(W,H,h=430,amax=175):
  a=np.zeros((H,W),np.uint8); g=(np.clip((np.arange(H)-(H-h))/h,0,1)**1.4*amax).astype(np.uint8); a[:]=g[:,None]
  im=Image.new('RGBA',(W,H),(8,4,2,0)); im.putalpha(Image.fromarray(a)); return im
LOGO=Image.open(S+'/brand/logo.png').convert('RGBA')
def soft_pill(text,size=52):
  t=soft(text,'eczar500',size,grad=((255,255,255),(255,246,230),(245,230,205)),shadow=60)
  pw,ph=t.width+80,t.height+30
  im=Image.new('RGBA',(pw+30,ph+30),(0,0,0,0)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((15,15,15+pw,15+ph),radius=ph//2,fill=(150,30,25,235),outline=(240,205,140,255),width=3)
  im.alpha_composite(t,(15+(pw-t.width)//2,15+(ph-t.height)//2)); return im
