import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad/work')
from ralib import *
import subprocess
from PIL import ImageEnhance
W,H=1080,1920
def frame(clip,t,landscape=False):
  vf="scale=-2:1920,crop=1080:1920" if landscape else "scale=1080:1920"
  b=subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',RZ+clip+'.mp4','-frames:v','1','-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
  im=Image.frombytes('RGB',(W,H),b); im=ImageEnhance.Contrast(im).enhance(1.08); im=ImageEnhance.Color(im).enhance(1.1)
  return im.convert('RGBA')
def shade(im,top=True,bottom=False):
  a=np.zeros((H,W),np.float32); y=np.arange(H)
  if top: a=np.maximum(a,(np.clip(1-y/760,0,1)**1.3*200)[:,None])
  if bottom: a=np.maximum(a,(np.clip((y-1100)/820,0,1)**1.2*215)[:,None])
  g=Image.new('RGBA',(W,H),(10,6,30,0)); g.putalpha(Image.fromarray(a.astype(np.uint8))); im.alpha_composite(g)
def fit(t,maxw=1000):
  return t if t.width<=maxw else t.resize((maxw,int(t.height*maxw/t.width)),Image.LANCZOS)
def make(key,clip,t,l1,l2,pos='top',landscape=False):
  im=frame(clip,t,landscape); shade(im,top=pos=='top',bottom=pos=='bottom')
  a=fit(metal(l1,150,font='yatra-one')); rb,_=ribbon(rich(l2,'yatra-one',84,SAFF,stroke=(40,10,0),sw=5),minw=700); rb=fit(rb,1020)
  y0=120 if pos=='top' else H-120-a.height-rb.height
  im.alpha_composite(a,((W-a.width)//2,y0)); im.alpha_composite(rb,((W-rb.width)//2,y0+a.height-10))
  lg=LOGO.resize((120,120),Image.LANCZOS); im.alpha_composite(lg,(36,H-160) if pos=='top' else (36,40))
  im.convert('RGB').save(S+f'/out/Ram_Aayenge_{key}_thumb.jpg',quality=90)
make('sh1','c08',1.0,'दीप जलाओ रे','राम आएँगे 🪔'.replace(' 🪔',''),'top')
make('sh2','c00',1.5,'14 साल बाद','लौटे श्री राम','bottom')
make('sh4','c07',1.0,'राम जी का','इंतज़ार — अयोध्या दीपोत्सव','top')
make('sh3','c10',1.5,'Happy Diwali','आज राम घर आए','bottom',landscape=True)
