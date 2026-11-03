"""Ghat Chali v2: fresh scenes. Long 16:9 + 2 native 9:16 Shorts. Reuses build.py helpers for audio/subs/cards."""
import os, sys, subprocess, json
G='/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad/gc/'; os.chdir(G)
src=open('build.py').read().split('# ---------- visuals')[0]   # L, rib, sub_track, audio a.wav, constants
exec(src)
FPS=25; XF=0.5
CLEAN={'c01':5,'c02':2.5,'c03':1.8,'c04':1.3,'c05':1.5,'c06':2,'c07':5,'c08':1.5,'c09':1.5,'c10':5,'c11':2.2,'c12':3,'c13':1.2,'c14':2.5,
 'c15':1.2,'c16':5,'c17':4,'c18':4,'c19':5,'c20':1.8,'c21':3,'s11':5,'s12':5,
 'v05':1.2,'v06':5,'v07':1.5,'v08':3.5,'v09':1.2,'v10':2,'v13':5,'v14':2}
def shot(out,spec,dur,W,H):
  kind,name,*opt=spec
  n=int(round((dur+XF)*FPS))
  if kind=='c':
    off=opt[0] if opt else 0; cw=CLEAN[name]-off
    need=dur+XF
    if cw>=need*0.8:   # straight, slowed slightly if needed
      sp=min(1.0,cw/need)
      vf=f"trim={off}:{off+cw},setpts=(PTS-STARTPTS)/{sp:.3f}"
    else:              # ping-pong of the clean window, slowed
      sp=max(0.6,min(1.0,2*cw/need))
      vf=f"trim={off}:{off+cw},setpts=PTS-STARTPTS,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1,setpts=PTS/{sp:.3f}"
    vf=f"[0:v]{vf},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},tpad=stop_mode=clone:stop_duration=3,trim=0:{n/FPS},setpts=PTS-STARTPTS,format=yuv420p[v]"
    run(f'ffmpeg -v error -y -i vid/{name}.mp4 -filter_complex "{vf}" -map "[v]" -an -c:v libx264 -preset veryfast -crf 17 {out}')
  else:  # image Ken Burns: mode in/out/l/r
    mode=opt[0] if opt else 'in'
    if W>H: base=f"scale=3840:-2"
    else:   base=f"scale=-2:3840,crop=2160:3840"
    z={'in':f"z='1.0+0.10*on/{n}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'",'out':f"z='1.10-0.10*on/{n}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'",
       'l':f"z=1.10:x='(iw-iw/zoom)*on/{n}':y='(ih-ih/zoom)/2'",'r':f"z=1.10:x='(iw-iw/zoom)*(1-on/{n})':y='(ih-ih/zoom)/2'"}[mode]
    run(f'ffmpeg -v error -y -loop 1 -i img/{name}.jpg -vf "{base},zoompan={z}:d={n}:s={W}x{H}:fps={FPS},format=yuv420p" -frames:v {n} -c:v libx264 -preset veryfast -crf 17 {out}')
def assemble(plan,t0,t1,W,H,tag):
  os.makedirs(tag,exist_ok=True); files=[]; durs=[]
  for i,(s,spec) in enumerate(plan):
    e=plan[i+1][0] if i+1<len(plan) else t1
    d=e-s; f=f'{tag}/{i:02d}.mp4'; shot(f,spec,d,W,H); files.append(f); durs.append(d)
  ins=''.join(f'-i {f} ' for f in files); fc=''; prev='[0:v]'; off=0
  for i in range(1,len(files)):
    off+=durs[i-1]; fc+=f'{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off-XF/2:.3f}[x{i}];'; prev=f'[x{i}]'
  run(f'ffmpeg -v error -y {ins} -filter_complex "{fc[:-1]}" -map "{prev}" -t {t1-t0} -c:v libx264 -preset veryfast -crf 17 {tag}/vis.mp4')
  return f'{tag}/vis.mp4'
# ---------- LONG (song-time plan) ----------
LP=[(13.8,('c','c21')),(17.3,('i','s01','in')),(20.8,('c','c20')),(23.3,('i','s02','l')),(25.8,('c','c19')),(30.7,('c','c18')),(33.8,('i','s04','out')),
 (36.8,('c','c17')),(39.4,('c','c16')),(42.0,('c','c15')),(44.7,('c','c08')),
 (47.3,('c','c14')),(50.1,('c','c13')),(53.0,('c','c12')),(55.8,('c','c03')),
 (58.6,('c','c07')),(60.9,('i','s06','r')),(63.2,('c','c06')),(65.9,('i','s05','in')),
 (69.5,('c','s12')),(74.5,('i','s12','l')),(78.0,('c','c09')),(80.5,('i','s15','in')),
 (85.4,('c','s11')),(88.5,('i','s11','r')),(91.2,('c','c05')),(94.0,('i','s09','out')),
 (95.6,('i','s07','in')),(98.1,('c','c16',2.5)),(100.6,('c','c15')),(103.3,('i','s03','r')),
 (106.1,('c','c11')),(109.0,('c','c02')),(111.9,('c','c10')),(114.5,('c','c01')),
 (117.1,('c','c17',1.5)),(119.5,('i','s13','l')),(121.9,('i','s10','in')),(124.6,('i','s08','r')),(127.3,('i','s14','out')),(130.0,('i','s15','r'))]
LP=[(s-T0,sp) for s,sp in LP]
if 'long' in sys.argv:
  vis=assemble(LP,0,T,1920,1080,'L2')
  lst=sub_track(1920,1080,lambda rb:1080-rb.height-36,T0,END,1720,(74,54),'sbL')
  run(f'ffmpeg -v error -y -i {vis} -i logo.png -i card.png -i sub.png -f concat -safe 0 -i {lst} -i a.wav -filter_complex '
      f'"[0:v][1:v]overlay=W-w-40:30[a];[a][2:v]overlay=0:0:enable=\'between(t,0.3,2.0)\'[b];[4:v]fps=25,format=rgba[s];[b][s]overlay=0:0:eof_action=pass[c];'
      f'[c][3:v]overlay=(W-w)/2:60:enable=\'between(t,{T-12:.1f},{T-4:.1f})\'[d];[d]fade=t=in:d=0.5,fade=t=out:st={T-2}:d=2[v]" '
      f'-map "[v]" -map 5:a -t {T} -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 192k -movflags +faststart ghat_long_v2.mp4')
# ---------- SHORTS: native vertical ----------
SW,SH=1080,1920
def short(name,a,b,plan,hook):
  dur=b-a; plan=[(s-a,sp) for s,sp in plan]
  vis=assemble(plan,0,dur,SW,SH,name)
  top=Image.new('RGBA',(SW,SH),(0,0,0,0))
  h1=rich(hook,'rozha-one',86,WHITE,sw=5,glow=(255,170,60),maxw=1000); top.alpha_composite(h1,((SW-h1.width)//2,170))
  h2=rich('पूरा गीत चैनल पर','martel600',48,SAFF,sw=3); top.alpha_composite(h2,((SW-h2.width)//2,1720))
  lg2=Image.open('logo.png'); top.alpha_composite(lg2,(SW-lg2.width-30,40)); top.save(f'{name}_top.png')
  ls=sub_track(SW,SH,lambda rb:1380,a,b,1040,(70,50),f'sb_{name}')
  run(f'ffmpeg -v error -y -i {vis} -ss {a-T0} -t {dur} -i a.wav -i {name}_top.png -f concat -safe 0 -i {ls} -filter_complex '
      f'"[0:v][2:v]overlay=0:0[n];[3:v]fps=25,format=rgba[s];[n][s]overlay=0:0:eof_action=pass,fade=t=in:d=0.3,fade=t=out:st={dur-0.8}:d=0.8[v];'
      f'[1:a]afade=t=in:d=0.2,afade=t=out:st={dur-1}:d=1[aa]" -map "[v]" -map "[aa]" -t {dur} -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 192k -movflags +faststart {name}.mp4')
if 'shorts' in sys.argv:
  short('ghat_sh1v2',36.6,69.3,[(36.6,('c','v05')),(39.4,('c','v06')),(42.0,('c','v07')),(44.7,('c','v05')),(47.3,('c','v08')),(50.1,('c','v09')),(53.0,('c','v10')),
        (55.8,('i','s10','in')),(58.6,('c','v06',2.5)),(60.9,('i','s05','in')),(63.2,('i','s07','r')),(65.9,('c','v10'))],'छठी मैया का नया गीत')
  short('ghat_sh2v2',105.9,132.6,[(105.9,('c','v13')),(109.0,('c','v13',2.5)),(111.9,('c','v14')),(114.5,('i','s14','in')),(117.1,('c','v05')),(119.5,('c','v06')),
        (121.9,('c','v07')),(124.6,('i','s13','r')),(127.3,('c','v08')),(130.0,('i','s05','out'))],'उगते सूरज को अर्घ्य')
print('ok')
