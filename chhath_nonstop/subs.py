"""Subtitles in the Ram Aayenge ribbon design, burned onto final.mp4 -> final_sub.mp4"""
import sys, os, json, subprocess, difflib
S='/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad'
sys.path.insert(0,S+'/work')
from ralib import *          # ribbon, rich, SAFF, WHITE, Image
import kplib
CN=S+'/cn/'; W,H=1920,1080
TL=json.load(open(CN+'timeline.json')); ST=TL['starts']; T=TL['T']
def lead2(s): return rich(s,'tiro-devanagari-hindi',74,WHITE,stroke=(16,10,40),sw=5)
def mean2(s): return rich(s,'yatra-one',54,SAFF,stroke=(40,10,0),sw=4)
def make(main,meaning=None,maxw=1720):
  li=lead2(main); ri=mean2(meaning) if meaning else None
  rb,ry=ribbon(li,ri,minw=900)
  if ri: rb.alpha_composite(ri,((rb.width-ri.width)//2,ry-6))
  if rb.width>maxw:
    k=maxw/rb.width; rb=rb.resize((maxw,int(rb.height*k)),Image.LANCZOS)
  fr=Image.new('RGBA',(W,H),(0,0,0,0)); fr.alpha_composite(rb,((W-rb.width)//2,H-rb.height-36)); return fr
EV=[]   # (t0,t1,main,meaning)
# ---- song 1: Kanch (whisper-aligned) ----
KAN=[('काँच ही बाँस के बहँगिया','कच्चे बाँस की बहँगी (काँवर)'),('बहँगी लचकत जाय','बहँगी लचकती हुई जा रही है'),
 ('होई ना बलम जी कहरिया','हे स्वामी, आप ही कहार बन जाइए'),('बहँगी घाटे पहुँचाय','बहँगी को घाट तक पहुँचा दीजिए'),
 ('बाट जे पूछेला बटोहिया','राह में राहगीर पूछता है'),('बहँगी केकरा के जाय','यह बहँगी किसके लिए जा रही है?'),
 ('तू त आन्हर होवे रे बटोहिया','अरे राहगीर, क्या तुम्हें दिखता नहीं?'),('बहँगी छठी मइया के जाय','यह बहँगी छठी मैया के लिए जा रही है'),
 ('सूपवा में ठेकुआ सजल बा','सूप में ठेकुआ सजा है'),('दउरा में फल-फूल','दउरा (टोकरी) में फल-फूल'),
 ('छठी मइया के घाट चलीं','चलो छठी मैया के घाट'),('मिट जाई सब सूल','सारे दुख मिट जाएँगे')]
GHA=[('छठ के रौनक, छठ के धूम','छठ की रौनक, छठ की धूम'),('घाटे चलीं सब झूम झूम','सब झूमते हुए घाट चलो'),
 ('सूप सजल बा ठेकुआ संगे','ठेकुआ के साथ सूप सजा है'),('केला नरियर रंग बिरंगे','केला, नारियल — रंग-बिरंगे'),
 ('माई के दरबार सजल बा','मैया का दरबार सजा है'),('घाट पे सब परिवार चलल बा','पूरा परिवार घाट पर चला है'),
 ('ढोल बाजे ढमा ढम','ढोल बज रहा है ढमा-ढम'),('नाचे मनवा छम छम','मन छम-छम नाच रहा है'),
 ('जय छठी मैया, जय छठी मैया',None),('पार लगइहें हमरी नैया','मैया हमारी नैया पार लगाएँगी'),
 ('सूरज देव के लीं बलैया','सूर्यदेव की बलैया लें'),('डूबत सूरज के अरघ दिहीं','डूबते सूर्य को अर्घ्य दें'),
 ('उगत सूरज के पांव पड़ीं','उगते सूर्य के चरण छुएँ'),('दीया बाती जगमग जगमग','दीया-बाती जगमग जगमग'),
 ('नदिया किनारे रौनक हरदम','नदी किनारे हरदम रौनक'),('बोल जय जय छठी माई',None),('सबके घर में खुसी आई','सबके घर खुशियाँ आईं')]
def add(off,tl,lines):
  for t0,t1,i in tl: EV.append([off+t0,off+t1,lines[i][0],lines[i][1]])
kt=[(12,0),(18,1),(24,0),(30,1),(36,2),(42,3),(48,2),(54,3),(60,0),(66,1),(72,4),(78,5),(84,6),(90,7),
    (96,2),(102,3),(108,2),(114,3),(120,8),(126,9),(132,10),(138,11),(144,0),(150,1),(156,7)]
add(ST[0],[(t,t+6 if t!=156 else 165,i) for t,i in kt],KAN)
gt=[(18.7,22.0,0),(22.0,25.4,1),(25.4,29.7,2),(29.7,33.4,3),(48.4,55.7,6),(55.7,59.0,6),(59.0,62.2,7),(62.2,66.7,8),(66.7,70.1,9),
    (70.1,73.4,8),(73.4,77.0,10),(89.0,94.0,11),(94.0,99.0,12),(99.0,106.5,13),(106.5,114.0,14),(114.0,117.8,6),(117.8,121.6,7),
    (121.6,125.3,8),(125.3,128.7,9),(128.7,132.6,8),(132.6,136.6,10),(144.0,147.8,15),(147.8,151.6,16),
    (165.6,169.2,15),(169.2,172.6,16),(172.6,176.3,15),(176.3,180.0,16)]
# V1 removed (user: EDM-sounding)
# ---- song 2: Kelwa (known timings, line level) ----
for ph,st,end,mk in kplib.LINES:
  EV.append([ST[1]+st[0],ST[1]+end,' '.join(ph),kplib.M.get(mk) if mk else None])
# ---- song 4: Arghya (whisper or fallback) ----
ARGL=[('ॐ एहि सूर्य सहस्रांशो','हे हज़ार किरणों वाले सूर्यदेव'),('तेजोराशे जगत्पते','तेज के भंडार, संसार के स्वामी'),
 ('अनुकम्पय मां भक्त्या','भक्ति से मुझ पर कृपा करें'),('गृहाणार्घ्यं दिवाकर','हे दिवाकर, यह अर्घ्य स्वीकार करें')]
add(ST[2]-28.5,[(28.5,32.1,1),(32.1,39.5,2),(39.5,47.5,3)],ARGL)
EV.append([ST[2]-28.5+48.0,ST[3]-0.5,'ॐ घृणि सूर्याय नमः','हे तेजस्वी सूर्यदेव, आपको नमन'])
# ---- song 5: Jaap (steady) ----
EV.append([ST[3]+9.0,T-6,'ॐ घृणि सूर्याय नमः','हे तेजस्वी सूर्यदेव, आपको नमन'])
# ---- clean: sort, no overlap, hide during title cards (st+1.5..st+8.5) ----
EV=[e for e in EV if e[1]-e[0]>0.8]; EV.sort()
for i in range(len(EV)-1):
  if EV[i][1]>EV[i+1][0]-0.05: EV[i][1]=EV[i+1][0]-0.05
  elif EV[i+1][0]-EV[i][1]<1.5: EV[i][1]=EV[i+1][0]-0.05   # bridge small gaps -> steady
for e in EV:
  for s in ST:
    if e[0]<s+8.6 and e[1]>s+1.4:
      if e[0]>=s+1.4: e[0]=s+8.6
      else: e[1]=min(e[1],s+1.4)
EV=[e for e in EV if e[1]-e[0]>0.8]
json.dump(EV,open(CN+'subs.json','w'),ensure_ascii=False,indent=0)
print(len(EV),'events')
if 'list' in sys.argv:
  for e in EV: print(f'{e[0]:7.1f} {e[1]:7.1f}  {e[2]}  | {e[3]}')
  sys.exit()
# ---- render PNGs + concat list ----
os.makedirs(CN+'sb',exist_ok=True)
Image.new('RGBA',(W,H),(0,0,0,0)).save(CN+'sb/blank.png')
cache={}; L=[]; t=0.0
for k,(a,b,m,mn) in enumerate(EV):
  if a>t: L.append(('blank.png',a-t))
  key=(m,mn)
  if key not in cache:
    f=f's{len(cache):03d}.png'; make(m,mn).save(CN+'sb/'+f); cache[key]=f
  L.append((cache[key],b-a)); t=b
L.append(('blank.png',T-t+1)); L.append(('blank.png',0.04))
with open(CN+'sb/list.txt','w') as f:
  for fn,d in L: f.write(f"file '{fn}'\nduration {d:.3f}\n")
  f.write("file 'blank.png'\n")
if 'qc' in sys.argv: sys.exit()
subprocess.run(f'cd {CN} && ffmpeg -v error -y -i final.mp4 -f concat -safe 0 -i sb/list.txt -filter_complex "[1:v]fps=25,format=rgba[s];[0:v][s]overlay=0:0:eof_action=pass:format=auto[v]" -map "[v]" -map 0:a -c:v libx264 -preset veryfast -crf 20 -c:a copy -movflags +faststart final_sub.mp4',shell=True,check=True)
print('done')
