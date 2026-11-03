# Surya mantra v2 — new rich, high-readability style (plaque + mala counter)
import os, glob, subprocess, math
from kplib import *
SM=S+'/sm/'; Z=SM+'zip/'
SRC.update({f'z{i:02d}':Z+f'z{i:02d}.mp4' for i in range(1,11)})
WHITE=(255,252,244); GOLD=(240,196,104); YEL=(255,214,110); MAR=(52,14,6)
def FT(font,size): return ImageFont.truetype(F+font+'.ttf',size,layout_engine=ImageFont.Layout.RAQM)
def rich(text,font,size,fill=WHITE,stroke=None,sw=None,shadow=True,glow=None,maxw=None):
  """Solid high-contrast text: fill + dark stroke + soft drop shadow (+ optional warm glow)."""
  f=FT(font,size); sw=sw if sw is not None else max(2,size//16); stroke=stroke or (34,12,4)
  pad=int(size*0.6)+sw
  bb=ImageDraw.Draw(Image.new('L',(8,8))).textbbox((0,0),text,font=f,stroke_width=sw)
  W=bb[2]-bb[0]+2*pad; H=bb[3]-bb[1]+2*pad; o=(pad-bb[0],pad-bb[1])
  out=Image.new('RGBA',(W,H),(0,0,0,0))
  m=Image.new('L',(W,H)); ImageDraw.Draw(m).text(o,text,font=f,fill=255,stroke_width=sw,stroke_fill=255)
  if glow:
    g=Image.new('RGBA',(W,H),glow+(0,)); g.putalpha(m.filter(ImageFilter.GaussianBlur(size/4)).point(lambda v:int(v*0.6))); out.alpha_composite(g)
  if shadow:
    s=Image.new('RGBA',(W,H),(0,0,0,0)); s.putalpha(m.filter(ImageFilter.GaussianBlur(size/10)).point(lambda v:int(v*0.85)))
    out.alpha_composite(s,(0,max(2,size//24)))
  d=ImageDraw.Draw(out); d.text(o,text,font=f,fill=fill+(255,),stroke_width=sw,stroke_fill=stroke+(255,))
  out=out.crop(out.getbbox())
  if maxw and out.width>maxw: out=out.resize((maxw,int(out.height*maxw/out.width)),Image.LANCZOS)
  return out
def plaque(w,h,r=26):
  """Deep maroon glass panel with double gold border and lotus-diamond crests."""
  im=Image.new('RGBA',(w+40,h+40),(0,0,0,0))
  sh=Image.new('L',im.size); ImageDraw.Draw(sh).rounded_rectangle((20,26,20+w,26+h),r,fill=150)
  shadow=Image.new('RGBA',im.size,(0,0,0,0)); shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(shadow)
  y=np.linspace(0,1,h)[:,None]; top=np.array((70,20,8),float); bot=np.array((34,8,4),float)
  col=(top+(bot-top)*y[...,None]); body=np.broadcast_to(col,(h,w,3)).astype(np.uint8)
  pm=Image.new('L',(w,h)); ImageDraw.Draw(pm).rounded_rectangle((0,0,w-1,h-1),r,fill=200)
  b=Image.fromarray(body,'RGB').convert('RGBA'); b.putalpha(pm); im.alpha_composite(b,(20,20))
  d=ImageDraw.Draw(im)
  d.rounded_rectangle((20,20,20+w-1,20+h-1),r,outline=GOLD+(255,),width=3)
  d.rounded_rectangle((29,29,20+w-10,20+h-10),r-8,outline=GOLD+(150,),width=1)
  cx=20+w//2
  for cy in (20,20+h-1):
    d.polygon([(cx,cy-13),(cx+13,cy),(cx,cy+13),(cx-13,cy)],fill=MAR+(255,),outline=GOLD+(255,))
    d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=GOLD+(255,))
    for s in (-1,1): d.ellipse((cx+s*24-3,cy-3,cx+s*24+3,cy+3),fill=GOLD+(255,))
  return im
def divider(w):
  im=Image.new('RGBA',(w,18),(0,0,0,0)); d=ImageDraw.Draw(im)
  for s in (-1,1): d.line([(w//2+s*14,9),(w//2+s*(w//2-2),9)],fill=GOLD+(170,),width=2)
  d.polygon([(w//2,2),(w//2+7,9),(w//2,16),(w//2-7,9)],fill=GOLD+(230,)); return im
def card(main,mean=None,minw=900,padx=70,pady=30,gap=8):
  """Assemble plaque + main text (+ divider + meaning). Returns RGBA image."""
  cw=max(minw,main.width+2*padx,(mean.width+2*padx) if mean else 0)
  dv=divider(min(cw-2*padx,520)) if mean else None
  ch=pady+main.height+((gap+dv.height+gap+mean.height) if mean else 0)+pady
  im=plaque(cw,ch); y=20+pady
  im.alpha_composite(main,(20+(cw-main.width)//2,y)); y+=main.height
  if mean:
    y+=gap; im.alpha_composite(dv,(20+(cw-dv.width)//2,y)); y+=dv.height+gap
    im.alpha_composite(mean,(20+(cw-mean.width)//2,y))
  return im
# ---- 108-bead mala counter ----
_MALA={}
def mala(n,R=108):
  if n in _MALA: return _MALA[n]
  S2=2*R+80; im=Image.new('RGBA',(S2,S2),(0,0,0,0)); c=S2/2
  bg=Image.new('L',im.size); ImageDraw.Draw(bg).ellipse((c-R-24,c-R-24,c+R+24,c+R+24),fill=190)
  disc=Image.new('RGBA',im.size,MAR+(0,)); disc.putalpha(bg.filter(ImageFilter.GaussianBlur(3))); im.alpha_composite(disc); ImageDraw.Draw(im).ellipse((c-R-24,c-R-24,c+R+24,c+R+24),outline=GOLD+(230,),width=2)
  glow=Image.new('RGBA',im.size,(0,0,0,0)); gd=ImageDraw.Draw(glow); d=ImageDraw.Draw(im)
  for k in range(108):
    a=-math.pi/2+2*math.pi*(k+0.5)/108; x=c+R*math.cos(a); y=c+R*math.sin(a)
    if k<n:
      gd.ellipse((x-7,y-7,x+7,y+7),fill=(255,180,60,200)); d.ellipse((x-4.2,y-4.2,x+4.2,y+4.2),fill=(255,232,160,255))
    else: d.ellipse((x-3,y-3,x+3,y+3),fill=(255,240,220,120))
  g2=glow.filter(ImageFilter.GaussianBlur(4)); g2.alpha_composite(im); im=g2; d=ImageDraw.Draw(im)
  d.polygon([(c,c-R-15),(c+8,c-R-4),(c,c-R+6),(c-8,c-R-4)],fill=GOLD+(255,))   # sumeru bead
  num=rich(str(n),'martel600',74,WHITE,sw=3); of=rich('/ 108','martel600',28,YEL,sw=2)
  im.alpha_composite(num,(int(c-num.width/2),int(c-num.height/2-14))); im.alpha_composite(of,(int(c-of.width/2),int(c+30)))
  _MALA[n]=im; return im
# ---- radiant sun rays (for title) ----
def rays(D=1000,n=36):
  im=Image.new('RGBA',(D,D),(0,0,0,0)); d=ImageDraw.Draw(im); c=D/2
  for k in range(n):
    a=2*math.pi*k/n; w=0.035 if k%2 else 0.02; L=c*(0.98 if k%2==0 else 0.75)
    d.polygon([(c,c),(c+L*math.cos(a-w),c+L*math.sin(a-w)),(c+L*math.cos(a+w),c+L*math.sin(a+w))],fill=(255,206,120,70))
  m=Image.new('L',(D,D)); ImageDraw.Draw(m).ellipse((0,0,D,D),fill=255); m=m.filter(ImageFilter.GaussianBlur(D/6))
  rr=np.hypot(*np.meshgrid(np.arange(D)-c,np.arange(D)-c)); fall=np.clip(1-rr/c,0,1)**1.2
  a=(np.asarray(im.getchannel('A'),np.float32)*fall).astype(np.uint8); im.putalpha(Image.fromarray(a))
  return im.filter(ImageFilter.GaussianBlur(2))
def shimmer(im,ph):
  """Gold gleam sweeping across text; ph in [0,1]."""
  if ph<=0 or ph>=1: return im
  w,h=im.size; x=np.arange(w)[None,:]; y=np.arange(h)[:,None]
  pos=-0.3*w+ph*1.6*w; band=np.clip(1-abs((x+0.35*y)-pos)/(0.09*w),0,1)**2
  a=np.asarray(im.getchannel('A'),np.float32)/255*band*190
  hl=Image.new('RGBA',(w,h),(255,236,180,0)); hl.putalpha(Image.fromarray(a.astype(np.uint8)))
  o=im.copy(); o.alpha_composite(hl); return o
# ---- segments: window [a,b] of source, slowed with frame blending, optional reverse/crop ----
def seg3(out,clip,a,b,L,W,H,crop=None,rev=False):
  win=b-a; sp=max(0.40,min(1.0,win/L)); N=int(round(L*FPS))
  vf=[f'trim={a}:{b}','setpts=PTS-STARTPTS']+(['reverse','setpts=PTS-STARTPTS'] if rev else [])+[f'setpts=PTS/{sp:.4f}']
  vf+=[f'framerate=fps={FPS}' if sp<0.95 else f'fps={FPS}']
  if crop:
    cx,cy,z=crop
    vf+=[f"scale=w='if(gt(iw/ih,{W}/{H}),-2,{W}*{z})':h='if(gt(iw/ih,{W}/{H}),{H}*{z},-2)'",
         f"crop={W}:{H}:'max(0,min(iw-{W},iw*{cx}-{W}/2))':'max(0,min(ih-{H},ih*{cy}-{H}/2))'"]
  else: vf+=[f'scale={W}:{H}:force_original_aspect_ratio=increase',f'crop={W}:{H}']
  vf+=['tpad=stop_mode=clone:stop=-1' if False else 'format=yuv420p']
  r=subprocess.run(['ffmpeg','-v','error','-y','-i',SRC[clip],'-an','-vf',','.join(vf)+f',tpad=stop_mode=clone:stop_duration={L}','-frames:v',str(N),'-r',str(FPS),
     '-c:v','libx264','-preset','veryfast','-crf','16','-g','48',out],capture_output=True,text=True)
  if r.returncode: raise SystemExit(clip+' '+r.stderr[-600:])
def build3(segs,endt,W,H,d,D=1.6):
  """segs=(t0,clip,a,b,kw)"""
  os.makedirs(d,exist_ok=True)
  for f in glob.glob(d+'/*'): os.remove(f)
  segs=sorted(segs,key=lambda x:x[0]); files=[]; durs=[]
  for n,(t0,clip,a,b,kw) in enumerate(segs):
    t1=segs[n+1][0] if n+1<len(segs) else endt
    dur=t1-t0; L=dur+(0 if n==len(segs)-1 else D); out=f'{d}/s{n:03d}.mp4'
    seg3(out,clip,a,b,L,W,H,**kw); files.append(out); durs.append(dur)
  # chain in groups to keep filter graph small
  def chain(fs,ds,o):
    inp=[]; [inp.extend(['-i',f]) for f in fs]; fc=[]; prev='[0:v]'; off=0.0
    for k in range(1,len(fs)):
      off+=ds[k-1]; lab=f'[x{k}]'; fc.append(f'{prev}[{k}:v]xfade=transition=fade:duration={D}:offset={off:.3f}{lab}'); prev=lab
    fc.append(f'{prev}format=yuv420p[vout]')
    r=subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fc),'-map','[vout]','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','16',o],capture_output=True,text=True)
    if r.returncode: raise SystemExit(r.stderr[-800:])
  chain(files,durs,d+'/base.mp4'); return d+'/base.mp4'
