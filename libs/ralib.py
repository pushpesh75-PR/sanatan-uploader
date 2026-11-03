# Ram Aayenge — festive Diwali editor: dissolves, gentle Ken Burns, marigold petals, gold sparkles,
# NEW subtitle look: indigo-night ribbon with marigold borders + diya ends; lead line white (Tiro), chorus reply saffron (Yatra One)
import sys, os, subprocess, math, random
sys.path.insert(0,'/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad/work')
from hmlib import *   # numpy, PIL, cv2, rich, metal, place, ease, LOGO, soft_pill, warp, S
RA=S+'/ra/'; RZ=RA+'zip/'
SONG=RA+'song.wav'; T0=3.46          # audio starts here (cuts music intro: vocals at ~1.9 s)
FPS=24
# clean windows (source seconds) found by frame inspection
CW={'c05':(0,4.5),'c10':(0,4.0),'c01':(0,6.0),'c04':(0,10),'c03':(0,10),'c02':(0,10),'c06':(0,10),
    'c13':(0,10),'c09':(0,10),'c14':(0,10),'c12':(0,10),'c08':(0,8),'c00':(0,10),'c07':(0,5.5)}
VERT={'c00','c07','c08'}
def vf_for(clip,W,H,crop):
  if crop: return crop+f",scale={W}:{H}"
  if clip in VERT and W>H: return f"scale={W}:-2,crop={W}:{H}"
  if clip not in VERT and H>W: return f"scale=-2:{H},crop={W}:{H}"
  return f"scale={W}:{H}"
def stream(clip,off,n,W,H,sp,crop=None):
  vf=f"setpts=PTS/{sp},fps={FPS},"+vf_for(clip,W,H,crop)+",tpad=stop_mode=clone:stop_duration=20"
  p=subprocess.Popen(['ffmpeg','-v','error','-ss',f'{off:.3f}','-i',RZ+clip+'.mp4','-an','-vf',vf,'-frames:v',str(n),
                      '-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
  sz=W*H*3; last=None
  try:
    for i in range(n):
      b=p.stdout.read(sz)
      if len(b)<sz: b=last
      last=b; yield np.frombuffer(b,np.uint8).reshape(H,W,3)
  finally:
    try: p.kill()
    except Exception: pass
    p.stdout.close(); p.wait()
def speed_for(clip,off,L,base=0.85):
  a,b=CW[clip]; return max(0.45,min(base,(b-off)/L))
# ---------- text design ----------
IND=(18,16,58); MARI=(255,150,28); SAFF=(255,204,74)
def diya(sz=34):
  im=Image.new('RGBA',(sz*2,sz*2),(0,0,0,0)); d=ImageDraw.Draw(im); c=sz
  g=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(g).ellipse((c-sz*0.8,c-sz*1.1,c+sz*0.8,c+sz*0.3),fill=(255,170,40,150))
  im.alpha_composite(g.filter(ImageFilter.GaussianBlur(sz/4)))
  d.chord((c-sz*0.8,c-sz*0.2,c+sz*0.8,c+sz*0.75),0,180,fill=(170,70,20,255),outline=(255,190,90,255),width=2)
  d.polygon([(c,c-sz*0.75),(c+sz*0.18,c-sz*0.12),(c,c+sz*0.05),(c-sz*0.18,c-sz*0.12)],fill=(255,236,150,255))
  return im
DIYA=diya()
def ribbon(main,reply=None,W=1920,minw=1100):
  """main/reply are RGBA text images; returns ribbon image and y-offset of reply."""
  gap=0; pad=16
  w=max(main.width,reply.width if reply else 0)+260; w=max(w,minw)
  h=pad+main.height+((gap+reply.height) if reply else 0)+pad
  im=Image.new('RGBA',(w,h+30),(0,0,0,0))
  sh=Image.new('L',im.size); ImageDraw.Draw(sh).rounded_rectangle((10,18,w-10,h+12),h//2,fill=170)
  s=Image.new('RGBA',im.size,(0,0,0,0)); s.putalpha(sh.filter(ImageFilter.GaussianBlur(12))); im.alpha_composite(s)
  body=Image.new('L',im.size); ImageDraw.Draw(body).rounded_rectangle((0,8,w-1,h+8),h//2,fill=215)
  b=Image.new('RGBA',im.size,IND+(0,)); b.putalpha(body); im.alpha_composite(b)
  d=ImageDraw.Draw(im)
  d.rounded_rectangle((0,8,w-1,h+8),h//2,outline=MARI+(255,),width=4)
  d.rounded_rectangle((9,17,w-10,h-1),h//2-9,outline=SAFF+(120,),width=1)
  for x in (48,w-48): im.alpha_composite(DIYA,(x-DIYA.width//2,8+h//2-DIYA.height//2-4))
  y=8+pad; im.alpha_composite(main,((w-main.width)//2,y)); ry=y+main.height+gap
  return im,ry
def lead(s): return rich(s,'tiro-devanagari-hindi',92,WHITE,stroke=(16,10,40),sw=5)
def reply(s): return rich(s,'yatra-one',72,SAFF,stroke=(40,10,0),sw=4)
# lyrics: (start,end,lead,reply-or-None, reply_delay)
LYR=[(5.3,9.6,'दीप जलाओ रे','राम आएँगे'),(9.6,13.6,'अवध नगरी में','खुशियाँ लाएँगे'),
 (13.6,18.0,'दीप जलाओ रे','राम आएँगे'),(18.0,22.5,'अवध नगरी में','खुशियाँ लाएँगे'),
 (22.6,27.5,'बाजे बधाई, बाजे बधाई',None),(27.5,32.4,'आज अवध में, बाजे बधाई',None),
 (32.6,37.0,'चौदह बरस की, लंबी थी रैना',None),(37.06,41.6,'राह निहारें, अवध के नैना',None),
 (41.68,45.6,'दीपों से सज गई, सारी नगरी',None),(45.64,50.5,'फूलों से भर गई, हर एक डगरी',None),
 (50.84,55.0,'दीप जलाओ रे','राम आएँगे'),(55.06,59.6,'अवध नगरी में','खुशियाँ लाएँगे'),
 (69.06,72.7,'संग में सीता, संग लखन भैया',None),(72.7,77.3,'द्वार पे खड़ी हैं, कौशल्या मैया',None),
 (77.36,81.7,'आरती उतारें, भर-भर थाली',None),(81.7,86.5,'अवध में आई, पहली दिवाली',None),
 (86.84,91.4,'दीप जलाओ रे','राम आएँगे'),(91.42,95.7,'अवध नगरी में','खुशियाँ लाएँगे'),
 (95.78,100.3,'बाजे बधाई, बाजे बधाई',None),(100.34,104.8,'आज अवध में, बाजे बधाई',None),
 (104.84,109.3,'सरयू की लहरें','गाएँ बधाई'),(109.36,113.9,'घर-घर में देखो','खुशियाँ समाईं'),
 (113.94,118.7,'झिलमिल दीये, हर एक द्वारे',None),(118.82,122.5,'आज अवध में, राम पधारे',None),
 (122.6,127.5,'दीप जलाओ रे','आज राम घर आए'),(127.62,132.0,'अवध नगरी में','खुशियाँ भर लाए'),
 (132.0,135.8,'दीप जलाओ रे','राम आएँगे'),(135.82,140.2,'अवध नगरी में','खुशियाँ लाएँगे')]
def build_lyrics(maxw):
  out=[]
  for a,b,l,r in LYR:
    li=lead(l); ri=reply(r) if r else None
    rb,ry=ribbon(li,ri)
    rb_lead,_=ribbon(li,None) if r is None else (None,None)
    if rb.width>maxw:
      k=maxw/rb.width; rb=rb.resize((maxw,int(rb.height*k)),Image.LANCZOS); ry=int(ry*k)
      ri2=ri.resize((int(ri.width*k),int(ri.height*k)),Image.LANCZOS) if ri else None
    else: ri2=ri
    # ribbon without reply text drawn (reply composited later with its own fade)
    base,_=ribbon(li,Image.new('RGBA',ri.size,(0,0,0,0)) if ri else None)
    if base.width>maxw: base=base.resize(rb.size,Image.LANCZOS)
    out.append((a,b,base,ri2,ry,(a+(b-a)*0.42) if r else None))
  return out
def ann(ribbon_img,ri,ry,c,t,a,b,cx,cy,rt):
  al=min(ease((t-a+0.25)/0.35),ease((b-t)/0.3))
  if al<=0: return
  sl=1-0.04*(1-ease((t-a+0.25)/0.4))
  place(c,ribbon_img,sl,al,cx,cy)
  if ri is not None and t>=rt:
    ra=min(al,ease((t-rt)/0.25)); pop=1+0.12*math.exp(-(t-rt)/0.12)
    top=cy-ribbon_img.height*sl/2
    place(c,ri,pop,ra,cx,top+(ry+ri.height/2)*sl)
# petals + sparkles
def petals(n,W,H,seed=7):
  r=random.Random(seed); cols=[(255,140,0),(255,170,20),(220,40,60),(255,200,60)]
  return [(r.uniform(0,W),r.uniform(-H,H),r.uniform(70,150),r.uniform(5,11),r.uniform(0,6.28),r.uniform(1,3),r.choice(cols)) for _ in range(n)]
def draw_petals(c,P,t,W,H,amt):
  if amt<=0.02: return
  d=ImageDraw.Draw(c)
  for k,(x,y,v,s,ph,rs,col) in enumerate(P):
    if k>len(P)*amt: break
    yy=(y+v*t)%(H+60)-30; xx=(x+30*math.sin(t*0.9+ph))%W
    a=abs(math.cos(t*rs+ph)); w=s*(0.35+0.65*a)
    d.ellipse((xx-w,yy-s*0.6,xx+w,yy+s*0.6),fill=col+(225,))
def sparkles(n,W,H,seed=3):
  r=random.Random(seed); return [(r.uniform(0,W),r.uniform(0,H),r.uniform(10,35),r.uniform(1.2,2.6),r.uniform(0,6.28)) for _ in range(n)]
def draw_sparkles(c,P,t,W,H,amt=1):
  d=ImageDraw.Draw(c)
  for k,(x,y,v,s,ph) in enumerate(P):
    if k>len(P)*amt: break
    yy=(y-v*t)%H; fl=0.5+0.5*math.sin(t*3+ph)
    d.ellipse((x-s,yy-s,x+s,yy+s),fill=(255,226,150,int(200*fl)))
PETAL_T=[(22.6,32.6),(95.78,104.84),(118.82,140.4)]
def petal_amt(t):
  for a,b in PETAL_T:
    if a-0.5<=t<b+0.8: return min(ease((t-a+0.5)/0.8),ease((b+0.8-t)/0.8))
  return 0
GRADE="eq=contrast=1.06:saturation=1.10:gamma=0.98,colorbalance=rs=0.03:bs=-0.03:rh=0.04:bh=-0.03,vignette=PI/5,noise=alls=4:allf=t"
def render(segs,ov,W,H,A,LEN,out,D=0.4,kb=True):
  """segs: list (t0,t1,clip,off,crop) in song time; ov(t)->RGBA overlay; A song start; LEN seconds."""
  aud=f"atrim=start={A}:end={A+LEN},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={LEN-2.2}:d=2.2,loudnorm=I=-14:TP=-1.5:linear=true"
  p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',SONG,
     '-filter_complex',f'[0:v]{GRADE},format=yuv420p[v];[1:a]{aud}[a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','medium','-crf','19',
     '-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-shortest',out],stdin=subprocess.PIPE)
  NF=int(round(LEN*FPS)); gens={}
  def seg_gen(i):
    t0,t1,clip,off,crop=segs[i]; s0=t0-(D if i>0 else 0); L=t1-s0
    sp=speed_for(clip,off,L); n=int(round(L*FPS))+2
    return dict(g=stream(clip,off,n,W,H,sp,crop),s0=s0,t0=t0,t1=t1,L=L,i=i)
  cur=0; gens[0]=seg_gen(0)
  for f in range(NF):
    t=A+f/FPS
    while cur<len(segs)-1 and t>=segs[cur][1]:
      G=gens.pop(cur,None)
      if G: G['g'].close()
      cur+=1
      if cur not in gens: gens[cur]=seg_gen(cur)
    if cur<len(segs)-1 and t>=segs[cur+1][0]-D and (cur+1) not in gens: gens[cur+1]=seg_gen(cur+1)
    def frame(i):
      G=gens[i]; fr=next(G['g'])
      if kb:
        u=(t-G['s0'])/max(0.1,G['L']); z=1.02+0.05*(u if i%2==0 else 1-u)
        fr=warp(fr,z,(8 if i%3==0 else -8)*u,0)
      return fr
    fr=frame(cur)
    if (cur+1) in gens and t>=segs[cur+1][0]-D:
      fn=frame(cur+1); k=ease((t-(segs[cur+1][0]-D))/D)
      fr=(fr.astype(np.float32)*(1-k)+fn.astype(np.float32)*k).astype(np.uint8)
    im=Image.fromarray(fr).convert('RGBA'); im.alpha_composite(ov(t)); p.stdin.write(im.convert('RGB').tobytes())
  for G in gens.values(): G['g'].close()
  p.stdin.close(); p.wait(); return p.returncode
