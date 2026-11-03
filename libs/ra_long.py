import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad/work')
from ralib import *
W,H=1920,1080; A=T0; ENDS=152.0; LEN=ENDS-A
K12="crop=iw*0.8:ih*0.8:0:ih*0.1"          # Kaushalya: cut bearded man on right
Z02="crop=iw*0.62:ih*0.62:iw*0.19:ih*0.38"  # petal path close
# (t0,t1,clip,offset,crop) in song time
SEG=[(A,9.6,'c05',0,None),(9.6,13.6,'c04',0,None),(13.6,18.0,'c02',0,None),(18.0,22.6,'c01',0,None),
 (22.6,27.5,'c03',0,None),(27.5,32.6,'c10',0,None),
 (32.6,37.06,'c13',0,None),(37.06,41.68,'c02',4.5,None),(41.68,45.64,'c03',5,None),(45.64,50.84,'c02',0,Z02),
 (50.84,55.06,'c05',0,None),(55.06,59.6,'c01',1,None),
 (59.6,69.06,'c06',0,None),
 (69.06,72.7,'c13',5,None),(72.7,77.36,'c12',0,K12),(77.36,81.7,'c12',5.6,K12),(81.7,86.84,'c04',4,None),
 (86.84,95.78,'c14',0,None),(95.78,100.34,'c10',0,None),(100.34,104.84,'c03',3,None),
 (104.84,109.36,'c03',5.5,None),(109.36,113.94,'c02',2,None),(113.94,118.82,'c01',0,None),(118.82,122.6,'c09',0,None),
 (122.6,127.62,'c09',4,None),(127.62,132.0,'c05',0,None),(132.0,135.82,'c10',0,None),(135.82,140.4,'c04',5,None),
 (140.4,146.0,'c05',0,None),(146.0,ENDS+0.5,'c10',0,None)]
LY=build_lyrics(1500)
TITLE=metal('अवध की पहली दिवाली',112,font='yatra-one')
JSR=metal('जय सियाराम',190,font='yatra-one')
JSR2=rich('जय जय सियाराम','tiro-devanagari-hindi',70,WHITE,stroke=(16,10,40),sw=5)
LOGO_S=LOGO.resize((112,112),Image.LANCZOS); LOGO_B=LOGO.resize((330,330),Image.LANCZOS)
CTA=soft_pill('लाइक  •  शेयर  •  सब्सक्राइब',46)
SUB=soft_pill('सब्सक्राइब करें',56); DIW=metal('शुभ दीपावली',120,font='yatra-one')
SPK=sparkles(60,W,H); PET=petals(110,W,H)
def ov(t):
  c=Image.new('RGBA',(W,H),(0,0,0,0))
  draw_sparkles(c,SPK,t,W,H,0.6); draw_petals(c,PET,t,W,H,petal_amt(t))
  lo=ease((t-A-0.6)/0.8)*ease((146-t)/0.6); place(c,LOGO_S,1,0.9*lo,86,84)
  if t<13.2: place(c,TITLE,1,ease((t-A-0.2)/0.7)*ease((13.2-t)/0.6),W/2,130)
  for a,b,rb,ri,ry,rt in LY:
    if a-0.3<=t<b+0.05: ann(rb,ri,ry,c,t,a,b,W/2,H-30-rb.height/2,rt)
  if 60.5<=t<68.6: place(c,CTA,1,min(ease((t-60.5)/0.5),ease((68.6-t)/0.5)),W-CTA.width/2-40,90)
  if 140.4<=t<146.2:
    al=min(ease((t-140.4)/0.5),ease((146.2-t)/0.5)); pop=1+0.1*math.exp(-(t-140.4)/0.25)
    place(c,JSR,pop,al,W/2,430); place(c,JSR2,1,al,W/2,600)
  if t>=146.0:
    u=t-146; a=ease(u/0.8)
    c.alpha_composite(Image.new('RGBA',(W,H),(10,8,30,int(140*a))))
    place(c,LOGO_B,0.95+0.05*ease(u/2.5),a,W/2,360); place(c,DIW,1,ease((u-0.4)/0.8),W/2,620)
    place(c,SUB,1,ease((u-0.8)/0.8),W/2,760)
  if t>ENDS-0.8: c.alpha_composite(Image.new('RGBA',(W,H),(0,0,0,int(255*ease((t-(ENDS-0.8))/0.8)))))
  return c
if 'test' in sys.argv:
  import numpy as np
  for tt in [4.5,8.0,12.0,17,25,35,62,74,80,88,107,141,149]:
    s=[x for x in SEG if x[0]<=tt<x[1]][0]; clip,off,crop=s[2],s[3],s[4]
    fr=next(stream(clip,off+(tt-s[0])*0.85,1,W,H,1.0,crop))
    im=Image.fromarray(fr).convert('RGBA'); im.alpha_composite(ov(tt)); im.convert('RGB').resize((960,540)).save(RA+f'T_{tt:05.1f}.jpg',quality=85)
  sys.exit()
print('rc',render(SEG,ov,W,H,A,LEN,S+'/out/Ram_Aayenge_LONG.mp4'))
