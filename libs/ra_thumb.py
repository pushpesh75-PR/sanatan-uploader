import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad/work')
from ralib import *
im=Image.open(RA+'thumb_src.jpg').convert('RGB').resize((1920,1080),Image.LANCZOS).convert('RGBA')
from PIL import ImageEnhance
im=ImageEnhance.Contrast(im.convert('RGB')).enhance(1.08).convert('RGBA')
W,H=im.size
# left dark gradient for text
a=np.zeros((H,W),np.float32); x=np.arange(W); a[:]=(np.clip(1-x/1100,0,1)**1.4*150)[None,:]
g=Image.new('RGBA',(W,H),(8,6,30,0)); g.putalpha(Image.fromarray(a.astype(np.uint8))); im.alpha_composite(g)
def big(text,size):
  f=FT('yatra-one',size); sw=14; pad=60
  bb=ImageDraw.Draw(Image.new('L',(8,8))).textbbox((0,0),text,font=f,stroke_width=sw)
  Wt,Ht=bb[2]-bb[0]+2*pad,bb[3]-bb[1]+2*pad; o=(pad-bb[0],pad-bb[1])
  m=Image.new('L',(Wt,Ht)); ImageDraw.Draw(m).text(o,text,font=f,fill=255)
  ms=Image.new('L',(Wt,Ht)); ImageDraw.Draw(ms).text(o,text,font=f,fill=255,stroke_width=sw,stroke_fill=255)
  out=Image.new('RGBA',(Wt,Ht),(0,0,0,0))
  gl=Image.new('RGBA',(Wt,Ht),(255,150,20,0)); gl.putalpha(ms.filter(ImageFilter.GaussianBlur(26)).point(lambda v:int(v*0.9))); out.alpha_composite(gl)
  for k in range(10,0,-1):   # 3D extrusion
    e=Image.new('RGBA',(Wt,Ht),(90,20,0,255)); e.putalpha(ms); out.alpha_composite(e,(k,k))
  st=Image.new('RGBA',(Wt,Ht),(60,8,0,255)); st.putalpha(ms); out.alpha_composite(st)
  yy=np.linspace(0,1,Ht)[:,None]; stops=[(0,(255,252,215)),(0.45,(255,214,70)),(0.6,(255,150,20)),(1,(230,90,0))]
  col=np.zeros((Ht,1,3))
  for (p0,c0),(p1,c1) in zip(stops,stops[1:]):
    sel=(yy>=p0)&(yy<=p1); tt=((yy-p0)/(p1-p0)).clip(0,1)
    for k in range(3): col[...,k]=np.where(sel,c0[k]+(c1[k]-c0[k])*tt,col[...,k])
  fl=Image.fromarray(np.broadcast_to(col,(Ht,Wt,3)).astype(np.uint8),'RGB').convert('RGBA'); fl.putalpha(m); out.alpha_composite(fl)
  return out.crop(out.getbbox())
T1=big('राम',215); T2=big('आएँगे',190)
cx=345
Y=40; im.alpha_composite(T1,(cx-T1.width//2,Y)); im.alpha_composite(T2,(cx-T2.width//2,Y+T1.height-70))
rb,_=ribbon(rich('दीप जलाओ रे','yatra-one',80,SAFF,stroke=(40,10,0),sw=5),minw=600)
rb=rb.resize((int(rb.width*0.84),int(rb.height*0.84)),Image.LANCZOS); RY=Y+T1.height+T2.height-80; im.alpha_composite(rb,(18,RY))
sub=rich('अवध की पहली दिवाली','tiro-devanagari-hindi',62,WHITE,stroke=(16,10,40),sw=5)
im.alpha_composite(sub,(cx-sub.width//2,RY+rb.height+6))
lg=LOGO.resize((120,120),Image.LANCZOS); im.alpha_composite(lg,(W-150,H-150))
im.convert('RGB').resize((1280,720),Image.LANCZOS).save(S+'/out/Ram_Aayenge_thumbnail.jpg',quality=93)
print(T1.size,T2.size,rb.size)
