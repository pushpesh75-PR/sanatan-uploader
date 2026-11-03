"""छठी मैया के घाट चलीं — long (16:9) + 2 Shorts (9:16). Visuals reuse cn/sh shots; Ram-Aayenge ribbon subtitles."""
import sys, os, json, glob, random, subprocess
S='/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad'
sys.path.insert(0,S+'/work')
from ralib import *   # ribbon, rich, Image, ImageDraw, SAFF, WHITE
G=S+'/gc/'; os.chdir(G)
def run(c): subprocess.run(c,shell=True,check=True)
W,H,FPS=1920,1080,25
T0=11.9; END=181.8; T=END-T0
L=[(13.9,20.8,'जय जय छठी मैया',None),(21.0,26.7,'जय हो सूरज देव',None),(26.9,32.6,'अरघ देवे आइल बानी','अर्घ्य देने आई हूँ'),(32.7,38.5,'किरपा करीं सदैव','सदा कृपा करें'),
 (39.0,41.9,'भोरे भोरे घाट चलीं','सुबह-सुबह घाट चलीं'),(42.0,47.4,'सूप सजा के हाथ चलीं','हाथ में सजा हुआ सूप लेकर'),(47.5,53.9,'ठेकुआ केला नरियर लेके','ठेकुआ, केला, नारियल लेकर'),(54.0,59.0,'छठी मैया के साथ चलीं','छठी मैया के संग चलीं'),
 (59.1,64.7,'जय जय छठी मैया',None),(64.8,70.7,'जय हो सूरज देव',None),(70.8,77.6,'अरघ देवे आइल बानी','अर्घ्य देने आई हूँ'),(77.7,83.3,'किरपा करीं सदैव','सदा कृपा करें'),
 (83.4,86.6,'नहाय खाय से व्रत शुरू','नहाय-खाय से व्रत शुरू'),(86.7,90.8,'खरना के प्रसाद बने','खरना का प्रसाद बनता है'),(90.9,95.7,'तीन दिन के निर्जल पूजा','तीन दिन की निर्जला पूजा'),(95.8,100.6,'मैया के आशीष घने','मैया का भरपूर आशीर्वाद'),
 (118.5,124.3,'सांझ के अरघ डूबत सूरज','शाम का अर्घ्य, डूबते सूर्य को'),(124.4,127.4,'जल में ठाढ़ व्रती सब','सब व्रती जल में खड़ी हैं'),(127.5,131.5,'दीया बाती गीत सुहावन','दीया-बाती और सुहावने गीत'),(131.6,136.6,'घाट सजल बा अब','अब घाट सज गया है'),
 (137.2,142.3,'भोर के अरघ उगत सूरज','सुबह का अर्घ्य, उगते सूर्य को'),(142.4,146.2,'लाल किरन बरसाय','लाल किरणें बरस रही हैं'),(146.3,150.2,'गोदी भरल रहे सबके','सबकी गोद भरी रहे'),(150.3,154.9,'घर में सुख समाय','घर में सुख बना रहे'),
 (155.1,160.7,'जय जय छठी मैया',None),(160.8,165.5,'जय हो सूरज देव',None),(165.6,170.6,'अरघ देवे आइल बानी','अर्घ्य देने आई हूँ'),(170.7,175.5,'किरपा करीं सदैव','सदा कृपा करें'),
 (175.6,180.8,'जय जय छठी मैया','॥ जय छठी मैया ॥')]
def lead2(s,sz=74): return rich(s,'tiro-devanagari-hindi',sz,WHITE,stroke=(16,10,40),sw=5)
def mean2(s,sz=54): return rich(s,'yatra-one',sz,SAFF,stroke=(40,10,0),sw=4)
def rib(main,meaning,maxw,sz=(74,54)):
  li=lead2(main,sz[0]); ri=mean2(meaning,sz[1]) if meaning else None
  rb,ry=ribbon(li,ri,minw=min(900,maxw))
  if ri: rb.alpha_composite(ri,((rb.width-ri.width)//2,ry-6))
  if rb.width>maxw: k=maxw/rb.width; rb=rb.resize((maxw,int(rb.height*k)),Image.LANCZOS)
  return rb
def sub_track(fw,fh,y_of,t0,t1,maxw,sz,name):
  os.makedirs(name,exist_ok=True)
  Image.new('RGBA',(fw,fh),(0,0,0,0)).save(f'{name}/blank.png')
  ev=[(max(a,t0)-t0,min(b,t1)-t0,m,n) for a,b,m,n in L if b>t0 and a<t1]
  lst=[]; t=0.0; cache={}
  for a,b,m,n in ev:
    if a>t: lst.append(('blank.png',a-t))
    k=(m,n)
    if k not in cache:
      rb=rib(m,n,maxw,sz); fr=Image.new('RGBA',(fw,fh),(0,0,0,0)); fr.alpha_composite(rb,((fw-rb.width)//2,y_of(rb)))
      cache[k]=f's{len(cache):02d}.png'; fr.save(f'{name}/'+cache[k])
    lst.append((cache[k],b-a)); t=b
  lst.append(('blank.png',max(0.1,(t1-t0)-t+1)))
  with open(f'{name}/list.txt','w') as f:
    for fn,d in lst: f.write(f"file '{fn}'\nduration {d:.3f}\n")
    f.write("file 'blank.png'\n")
  return f'{name}/list.txt'
# ---------- audio ----------
run(f'ffmpeg -v error -y -ss {T0} -t {T} -i song_flow.wav -af "afade=t=in:d=0.4,afade=t=out:st={T-3}:d=3,loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -ac 2 a.wav')
# ---------- visuals: shuffled shots from the nonstop pool ----------
shots=sorted(glob.glob(S+'/cn/sh/*.mp4')); random.seed(21); random.shuffle(shots)
SH=7.0; n=int(T/(SH-1))+2; pick=shots[:n]
ins=''.join(f'-i {p} ' for p in pick); fc=''; prev='[0:v]'; off=0
for i in range(1,len(pick)):
  off+=SH-1; fc+=f'{prev}[{i}:v]xfade=transition=fade:duration=1:offset={off}[v{i}];'; prev=f'[v{i}]'
run(f'ffmpeg -v error -y {ins} -filter_complex "{fc[:-1]}" -map "{prev}" -t {T} -c:v libx264 -preset veryfast -crf 18 vis.mp4')
# ---------- long ----------
lg=Image.open(S+'/brand/logo.png').convert('RGBA'); lg.thumbnail((150,150)); lg.save('logo.png')
card=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(card)
t1=rich('छठी मैया के घाट चलीं','rozha-one',96,WHITE,sw=5,glow=(255,170,60)); t2=rich('नया छठ गीत 2026  •  हिंदी अर्थ के साथ','martel600',44,SAFF,sw=3)
card.alpha_composite(t1,((W-t1.width)//2,H//2-140)); card.alpha_composite(t2,((W-t2.width)//2,H//2-140+t1.height+10)); card.save('card.png')
sub=Image.new('RGBA',(620,96),(0,0,0,0)); d=ImageDraw.Draw(sub); d.rounded_rectangle([0,0,619,95],48,fill=(200,20,20,235))
from PIL import ImageFont
d.text((310,48),'Subscribe · Like · Share',font=ImageFont.truetype(S+'/fonts/laila500.ttf',44),fill='white',anchor='mm'); sub.save('sub.png')
lst=sub_track(W,H,lambda rb:H-rb.height-36,T0,END,1720,(74,54),'sbL')
run(f'ffmpeg -v error -y -i vis.mp4 -i logo.png -i card.png -i sub.png -f concat -safe 0 -i {lst} -i a.wav -filter_complex '
    f'"[0:v][1:v]overlay=W-w-40:30[a];[a][2:v]overlay=0:0:enable=\'between(t,0.3,2.0)\'[b];[4:v]fps=25,format=rgba[s];[b][s]overlay=0:0:eof_action=pass[c];'
    f'[c][3:v]overlay=(W-w)/2:60:enable=\'between(t,{T-12:.1f},{T-4:.1f})\'[d];[d]fade=t=in:d=0.5,fade=t=out:st={T-2}:d=2[v]" '
    f'-map "[v]" -map 5:a -t {T} -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 192k -movflags +faststart ghat_long.mp4')
# ---------- Shorts (9:16): blurred fill + 16:9 picture + big ribbon ----------
SW,SHh=1080,1920
def short(name,a,b,hook):
  dur=b-a; s0=a-T0
  top=Image.new('RGBA',(SW,SHh),(0,0,0,0))
  h1=rich(hook,'rozha-one',84,WHITE,sw=5,glow=(255,170,60),maxw=1000); top.alpha_composite(h1,((SW-h1.width)//2,250))
  h2=rich('पूरा गीत चैनल पर 👆'.replace(' 👆',''),'martel600',46,SAFF,sw=3); top.alpha_composite(h2,((SW-h2.width)//2,1740))
  lg2=Image.open('logo.png'); top.alpha_composite(lg2,(SW-lg2.width-30,60)); top.save(f'{name}_top.png')
  ls=sub_track(SW,SHh,lambda rb:1270,a,b,1040,(70,50),f'sb_{name}')
  run(f'ffmpeg -v error -y -ss {s0} -t {dur} -i vis.mp4 -ss {s0} -t {dur} -i a.wav -i {name}_top.png -f concat -safe 0 -i {ls} -filter_complex '
      f'"[0:v]split[x][y];[x]scale=-2:{SHh},crop={SW}:{SHh},gblur=sigma=30,eq=brightness=-0.12[bg];[y]scale={SW}:-2[fg];[bg][fg]overlay=0:(H-h)/2-60[m];'
      f'[m][2:v]overlay=0:0[n];[3:v]fps=25,format=rgba[s];[n][s]overlay=0:0:eof_action=pass,fade=t=in:d=0.3,fade=t=out:st={dur-0.8}:d=0.8[v];'
      f'[1:a]afade=t=in:d=0.2,afade=t=out:st={dur-1}:d=1[aa]" -map "[v]" -map "[aa]" -t {dur} -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 192k -movflags +faststart {name}.mp4')
short('ghat_sh1',36.6,69.3,'छठी मैया का नया गीत')
short('ghat_sh2',105.9,132.6,'उगते सूरज को अर्घ्य')
print('done')
