# Kelwa ke paat par — calm cinematic toolkit (extends rslib)
import os, glob, subprocess
from rslib import *
KP=S+'/kp/'
SRC={**{f'k{i:02d}':KP+f'c/k{i:02d}.mp4' for i in range(1,10)}, 'r03':RS+'c/r03.mp4','r06':RS+'c/r06.mp4'}
WIN={**{f'k{i:02d}':7.0 for i in range(1,10)}, 'r03':10.0,'r06':10.0}
D2=1.6  # dissolve
def seg(out,clip,off,L,W,H,crop=None,slow=False):
  """crop=(cx,cy,zoom) in source-normalised coords; zoom>=1. Fill W x H."""
  win=WIN[clip]; avail=max(0.5,win-off)
  sp=min(1.0,avail/L)
  if slow: sp=min(sp,0.75)
  sp=max(0.42,sp)
  N=int(round(L*FPS))
  if crop:
    cx,cy,z=crop
    vf=[f'setpts=PTS/{sp:.4f}',f'fps={FPS}',
        f"scale=w='if(gt(iw/ih,{W}/{H}),-2,{W}*{z})':h='if(gt(iw/ih,{W}/{H}),{H}*{z},-2)'",
        f"crop={W}:{H}:'max(0,min(iw-{W},iw*{cx}-{W}/2))':'max(0,min(ih-{H},ih*{cy}-{H}/2))'",'format=yuv420p']
  else:
    vf=[f'setpts=PTS/{sp:.4f}',f'fps={FPS}',f'scale={W}:{H}:force_original_aspect_ratio=increase',f'crop={W}:{H}','format=yuv420p']
  r=subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{off:.3f}','-i',SRC[clip],'-an','-vf',','.join(vf),'-frames:v',str(N),'-r',str(FPS),
     '-c:v','libx264','-preset','veryfast','-crf','16','-g','48',out],capture_output=True,text=True)
  if r.returncode: raise SystemExit(r.stderr[-500:])
  # pad if short (freeze last frame)
  n=int(subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames','-of','csv=p=0',out],capture_output=True,text=True).stdout.strip() or 0)
  if n<N:
    tmp=out+'.p.mp4'; os.rename(out,tmp)
    subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-vf',f'tpad=stop_mode=clone:stop={N-n},format=yuv420p','-frames:v',str(N),'-c:v','libx264','-preset','veryfast','-crf','16',out],check=True); os.remove(tmp)
def build2(segs,endt,W,H,d):
  os.makedirs(d,exist_ok=True)
  for f in glob.glob(d+'/*'): os.remove(f)
  segs=sorted(segs,key=lambda x:x[0]); files=[]; durs=[]
  for n,(t0,clip,off,kw) in enumerate(segs):
    t1=segs[n+1][0] if n+1<len(segs) else endt
    dur=t1-t0; last=(n==len(segs)-1)
    L=dur+(0 if last else D2); out=f'{d}/s{n:03d}.mp4'
    seg(out,clip,off,L,W,H,**kw); files.append(out); durs.append(dur)
  inp=[]; [inp.extend(['-i',f]) for f in files]
  fc=[]; prev='[0:v]'; off=0.0
  for k in range(1,len(files)):
    off+=durs[k-1]; lab=f'[x{k}]'
    fc.append(f'{prev}[{k}:v]xfade=transition=fade:duration={D2}:offset={off:.3f}{lab}'); prev=lab
  fc.append(f'{prev}format=yuv420p[vout]')
  r=subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fc),'-map','[vout]','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','16',d+'/base.mp4'],capture_output=True,text=True)
  if r.returncode: raise SystemExit(r.stderr[-800:])
  return d+'/base.mp4'
# ---- lyrics timing (phrase-level) ----
CA=['केलवा के पात पर','उगेलन सुरुजमल','झाँके झुके']
CB=['हो करेलू छठ बरतिया','से झाँके झुके']
Q1=['हम तोहसे पूछीं बरतिया','ए बरतिया, से केकरा लागी?']
Q2=['हो करेलू छठ बरतिया','से केकरा लागी?']
A2=['हो करेलू छठ बरतिया','से उनके लागी']
def ans(w): return [f'हमरो जे {w}',f'कवन अइसन {w}','से उनके लागी']
M={'CA':'केले के पत्तों के बीच से सूर्यदेव उदित होकर झाँक रहे हैं',
   'CB':'व्रती छठ का व्रत कर रही हैं — सूर्यदेव झुककर निहार रहे हैं',
   'Q1':'मैं पूछती हूँ, हे व्रती — यह व्रत किसके लिए?',
   'Q2':'हे छठ व्रती, यह व्रत किसके लिए कर रही हो?',
   'बेटवा':'मेरे बेटे के लिए — मेरे दुलारे बेटे के लिए',
   'स्वामी':'मेरे स्वामी के लिए — मेरे जीवनसाथी के लिए',
   'बेटी':'मेरी बेटी के लिए — मेरी लाडली बेटी के लिए',
   'A2':'छठ का यह व्रत उन्हीं के लिए है'}
# (phrase list, starts, end, meaning key)
LINES=[
 (['हो… दीनानाथ…'],[8.4],18.6,None),
 (CA,[42.4,45.1,47.9],50.0,'CA'),(CB,[50.3,52.7],54.8,'CB'),
 (CA,[55.0,57.6,60.4],62.5,'CA'),(CB,[62.6,65.2],67.6,'CB'),
 (Q1,[69.6,73.6],77.2,'Q1'),(Q2,[77.4,80.6],82.2,'Q2'),(ans('बेटवा'),[82.3,84.9,87.5],89.4,'बेटवा'),(A2,[89.5,92.9],94.8,'A2'),
 (CA,[95.0,97.8,100.1],102.3,'CA'),(CB,[102.5,105.0],107.2,'CB'),
 (Q1,[126.5,130.4],134.5,'Q1'),(Q2,[134.8,137.6],139.1,'Q2'),(ans('स्वामी'),[139.2,142.0,144.6],146.6,'स्वामी'),(A2,[146.7,149.6],152.0,'A2'),
 (Q1,[171.4,174.8],179.0,'Q1'),(Q2,[179.0,182.4],184.4,'Q2'),(ans('बेटी'),[184.6,186.6,189.5],191.7,'बेटी'),(A2,[191.8,194.8],196.4,'A2'),
 (CA,[196.5,199.6,202.0],203.9,'CA'),(CB,[204.0,207.0],208.9,'CB'),
 (CA,[209.0,212.2,214.0],216.1,'CA'),(CB,[216.2,221.6],225.5,'CB'),
 (['हो… छठी मईया…'],[227.6],235.0,None),(['हो… दीनानाथ…'],[236.4],240.6,None)]
def phrases():
  out=[]
  for ph,st,end,mk in LINES:
    for i,(p,s0) in enumerate(zip(ph,st)):
      e=st[i+1] if i+1<len(st) else end
      out.append((s0,e,p,mk,st[0],end))
  return out
