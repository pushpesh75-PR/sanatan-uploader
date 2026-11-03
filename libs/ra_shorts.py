import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad/work')
import ralib
from ralib import *
W,H=1080,1920; TAIL=3.0
CX={'c13':0.42,'c12':0.66,'c09':0.45,'c14':0.58,'c05':0.5,'c10':0.5,'c04':0.38,'c03':0.4,'c02':0.5,'c01':0.5,'c06':0.45}
K12="crop=iw*0.8:ih*0.8:0:ih*0.1,"
def frame_vf(clip,W_,H_,crop):
  if clip in VERT: return f"scale={W_}:{H_}"
  pre=(crop+',') if crop else ''
  cx=CX.get(clip,0.5)
  return (pre+f"split[a][b];[a]scale=-2:{H_},crop={W_}:{H_},boxblur=28:3,eq=brightness=-0.12:saturation=1.1[bg];"
          f"[b]scale=-2:1300,crop={W_}:1300:'(iw-{W_})*{cx}':0[fg];[bg][fg]overlay=0:300")
ralib.vf_for=frame_vf
SH={
 'sh1':dict(A=T0,E=32.6,hook='अयोध्या में आज दीप जलाओ!',
   seg=[(T0,9.6,'c08',0,None),(9.6,13.6,'c04',0,None),(13.6,18.0,'c07',0,None),(18.0,22.6,'c05',0,None),(22.6,27.5,'c03',0,None),(27.5,32.6+TAIL+0.5,'c10',0,None)]),
 'sh2':dict(A=68.6,E=95.78,hook='14 बरस बाद लौटे श्री राम',
   seg=[(68.6,72.7,'c00',0,None),(72.7,77.36,'c12',0,K12[:-1]),(77.36,81.7,'c12',5.6,K12[:-1]),(81.7,86.84,'c04',4,None),(86.84,91.42,'c14',0,None),(91.42,95.78+TAIL+0.5,'c00',4.5,None)]),
 'sh3':dict(A=113.5,E=140.4,hook='आज राम घर आए!',
   seg=[(113.5,118.82,'c07',0,None),(118.82,122.6,'c09',0,None),(122.6,127.62,'c08',0,None),(127.62,132.0,'c00',2,None),(132.0,135.82,'c10',0,None),(135.82,140.4+TAIL+0.5,'c05',0,None)]),
 'sh4':dict(A=32.3,E=59.6,hook='राह निहारे पूरी अयोध्या',
   seg=[(32.3,37.06,'c13',0,None),(37.06,41.68,'c07',0,None),(41.68,45.64,'c03',5,None),(45.64,50.84,'c02',0,None),(50.84,55.06,'c08',0,None),(55.06,59.6+TAIL+0.5,'c01',1,None)]),
}
def lead_s(x): return rich(x,'tiro-devanagari-hindi',86,WHITE,stroke=(16,10,40),sw=5)
def white2(x): return rich(x,'tiro-devanagari-hindi',86,WHITE,stroke=(16,10,40),sw=5)
def reply_s(x): return rich(x,'yatra-one',74,SAFF,stroke=(40,10,0),sw=4)
LYS=[]
for a,b,l,r in ralib.LYR:
  if r: li,ri,rt=lead_s(l),reply_s(r),a+(b-a)*0.42
  elif ',' in l:
    p1,p2=[x.strip() for x in l.split(',',1)]; li,ri,rt=lead_s(p1+','),white2(p2),a
  else: li,ri,rt=lead_s(l),None,None
  base,ry=ribbon(li,Image.new('RGBA',ri.size,(0,0,0,0)) if ri else None)
  if base.width>1040:
    k=1040/base.width; base=base.resize((1040,int(base.height*k)),Image.LANCZOS); ry=int(ry*k)
    ri=ri.resize((int(ri.width*k),int(ri.height*k)),Image.LANCZOS) if ri else None
  LYS.append((a,b,base,ri,ry,rt))
LOGO_S=LOGO.resize((104,104),Image.LANCZOS); LOGO_B=LOGO.resize((360,360),Image.LANCZOS)
FULL=metal('पूरा गीत चैनल पर',92,font='yatra-one'); PILL=soft_pill('सब्सक्राइब करें',54)
JSR=metal('जय सियाराम',120,font='yatra-one')
SPK=sparkles(50,W,H,5); PET=petals(90,W,H,9)
for key in [k for k in sys.argv[1:] if k in SH] or list(SH):
  d=SH[key]; A,E=d['A'],d['E']; LEN=E-A+TAIL
  HOOK=metal(d['hook'],92,font='yatra-one')
  if HOOK.width>1000: HOOK=HOOK.resize((1000,int(HOOK.height*1000/HOOK.width)),Image.LANCZOS)
  def ov(t):
    c=Image.new('RGBA',(W,H),(0,0,0,0)); u=t-A
    draw_sparkles(c,SPK,t,W,H,0.6); draw_petals(c,PET,t,W,H,petal_amt(t))
    if t<E+0.2:
      place(c,LOGO_S,1,0.9*ease((u-0.3)/0.6),80,86)
      place(c,HOOK,1,ease((u-0.1)/0.5)*ease((E+0.2-t)/0.4),W/2,200)
      for a,b,rb,ri,ry,rt in LYS:
        if a-0.3<=t<b+0.05 and b>A+0.3: ann(rb,ri,ry,c,t,max(a,A+0.15),b,W/2,1690,rt)
    else:
      lt=t-(E+0.2); a=ease(lt/0.7)
      c.alpha_composite(Image.new('RGBA',(W,H),(10,8,30,int(150*a))))
      place(c,LOGO_B,0.95+0.05*ease(lt/2.5),a,W/2,640); place(c,JSR,1,ease((lt-0.3)/0.7),W/2,920)
      place(c,FULL,1,ease((lt-0.6)/0.7),W/2,1080); place(c,PILL,1,ease((lt-0.9)/0.7),W/2,1210)
    if u>LEN-0.6: c.alpha_composite(Image.new('RGBA',(W,H),(0,0,0,int(255*ease((u-(LEN-0.6))/0.6)))))
    return c
  if 'test' in sys.argv:
    for tt in [A+1.5,A+9,A+15,E-1,E+1.8]:
      s=[x for x in d['seg'] if x[0]<=tt<x[1]][0]
      fr=next(stream(s[2],s[3]+(tt-s[0])*0.85,1,W,H,1.0,s[4]))
      im=Image.fromarray(fr).convert('RGBA'); im.alpha_composite(ov(tt)); im.convert('RGB').resize((540,960)).save(RA+f'S_{key}_{tt-A:04.1f}.jpg',quality=85)
    continue
  print(key,'rc',render(d['seg'],ov,W,H,A,LEN,S+f'/out/Ram_Aayenge_{key}_Short.mp4',kb=True),flush=True)
