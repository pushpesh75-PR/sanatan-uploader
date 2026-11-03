"""Ghat Chali v2: fresh scenes. Long 16:9 + 2 native 9:16 Shorts. Reuses build.py helpers for audio/subs/cards."""
import os, sys, subprocess, json
G='/tmp/claude-0/-home-claude/b66cce68-2f99-5d23-8500-e19798027cfd/scratchpad/gc/'; os.chdir(G)
src=open('build_flow.py').read().split('# ---------- visuals')[0]   # L, rib, sub_track, audio a.wav, constants
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
LP=[(11.9,('c','c17')),(17.4,('c','c16')),(21.0,('i','s06','r')),(26.9,('c','c15')),(30.0,('i','s07','in')),(32.7,('c','c08')),(35.5,('i','s05','in')),
 (39.0,('c','c21')),(42.0,('c','c20')),(44.8,('i','s02','l')),(47.5,('c','c19')),(52.0,('i','s03','in')),(54.0,('c','c18')),(57.0,('i','s04','out')),
 (59.1,('c','c07')),(62.0,('i','s01','in')),(64.8,('c','c16',2.5)),(68.0,('i','s13','l')),(70.8,('c','c06')),(74.2,('i','s07','r')),(77.7,('c','c17',1.5)),(80.5,('i','s05','out')),
 (83.4,('c','c14')),(86.7,('c','c13')),(89.0,('i','s09','in')),(90.9,('c','c12')),(93.3,('c','c03')),(95.8,('i','s10','r')),(98.2,('c','c05')),
 (100.6,('c','s12')),(105.6,('i','s12','l')),(109.6,('c','c09')),(112.0,('i','s15','in')),(115.5,('c','c04')),
 (118.5,('c','s11')),(122.0,('i','s11','r')),(124.4,('i','s06','l')),(127.5,('c','s12',2.5)),(130.0,('i','s15','r')),(131.6,('c','c01')),(134.4,('i','s08','in')),
 (137.2,('c','c11')),(139.8,('c','c02')),(142.4,('i','s13','in')),(146.3,('c','c10')),(150.3,('i','s14','in')),(153.0,('i','s01','r')),
 (155.1,('c','c17')),(158.0,('i','s05','r')),(160.8,('c','c16',1.0)),(163.2,('i','s06','in')),(165.6,('c','c15')),(168.0,('i','s02','r')),(170.7,('c','c08')),(173.2,('i','s10','in')),
 (175.6,('i','s15','out')),(178.4,('c','s12',1.0))]
LP=[(s-T0,sp) for s,sp in LP]
if 'long' in sys.argv:
  vis=assemble(LP,0,T,1920,1080,'L2')
  lst=sub_track(1920,1080,lambda rb:1080-rb.height-36,T0,END,1720,(74,54),'sbL')
  run(f'ffmpeg -v error -y -i {vis} -i logo.png -i card.png -i sub.png -f concat -safe 0 -i {lst} -i a.wav -filter_complex '
      f'"[0:v][1:v]overlay=W-w-40:30[a];[a][2:v]overlay=0:0:enable=\'between(t,0.3,2.0)\'[b];[4:v]fps=25,format=rgba[s];[b][s]overlay=0:0:eof_action=pass[c];'
      f'[c][3:v]overlay=(W-w)/2:60:enable=\'between(t,{T-12:.1f},{T-4:.1f})\'[d];[d]fade=t=in:d=0.5,fade=t=out:st={T-2}:d=2[v]" '
      f'-map "[v]" -map 5:a -t {T} -c:v libx264 -preset veryfast -crf 19 -c:a aac -b:a 192k -movflags +faststart ghat_long_flow.mp4')
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
  short('ghat_sh1f',59.0,100.6,[(59.0,('c','v05')),(62.0,('c','v06')),(64.8,('c','v06',2.5)),(67.8,('i','s06','in')),(70.8,('c','v07')),(74.2,('i','s07','r')),(77.7,('c','v05')),(80.5,('i','s05','in')),
        (83.4,('c','v08')),(86.7,('c','v09')),(89.0,('i','s09','in')),(90.9,('c','v10')),(93.3,('i','s10','r')),(95.8,('c','v10',0.5)),(98.2,('i','s05','out'))],'छठी मैया का नया गीत')
  short('ghat_sh2f',137.0,176.0,[(137.0,('c','v13')),(139.8,('c','v13',2.5)),(142.4,('i','s13','in')),(146.3,('c','v14')),(150.3,('i','s14','in')),(153.0,('c','v08')),
        (155.1,('c','v05')),(158.0,('c','v06')),(160.8,('i','s06','r')),(163.2,('c','v06',2.5)),(165.6,('c','v07')),(168.0,('i','s07','in')),(170.7,('c','v05')),(173.2,('i','s05','out'))],'उगते सूरज को अर्घ्य')
print('ok')
