import json,os,re,subprocess,sys
sys.path.insert(0,"/home/claude/work/v5/lib")
from cards import *
B="/home/claude/work/v5"; P=B+"/pics/"; C=B+"/clips/"; O=B+"/build/"
SH="/home/claude/work/sh/"
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode: print(" ".join(c)[:300]); print(r.stderr[-1500:]); raise SystemExit(1)
    return r
def dur(f): return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).stdout)
def split_phr(text):
    parts=[p.strip() for p in re.split(r"(?<=[,।?])\s*",text) if p.strip()]
    out=[]
    for p in parts:
        ws=p.split(" "); cur=""
        for w in ws:
            if len((cur+" "+w).strip())<=26: cur=(cur+" "+w).strip()
            else:
                if cur: out.append(cur)
                cur=w
        if cur: out.append(cur)
    # merge tiny chunks (<8 chars) into previous
    m=[]
    for p in out:
        if m and len(p)<8 and len(m[-1])+1+len(p)<=31: m[-1]=m[-1]+" "+p
        else: m.append(p)
    return m
def caps_for(sentences):
    caps=[]
    for text,a,b in sentences:
        ph=split_phr(text); tot=sum(len(p.replace(" ","")) for p in ph); t=a
        for p in ph:
            d=(b-a)*len(p.replace(" ",""))/tot
            caps.append((p,round(t,2),round(t+d,2))); t+=d
    return caps
TAIL=4.0
def endcard_png(path):
    from PIL import Image,ImageDraw,ImageFont
    import sys; sys.path.insert(0,"/home/claude/work/v5")
    from lib.cards import TIRO
    im=Image.new("RGBA",(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle((0,0,1080,1920),fill=(0,0,0,135))
    lg=Image.open(B+"/tk/brand/logo_512q.png").convert("RGBA").resize((260,260)); im.alpha_composite(lg,(410,830))
    f1=ImageFont.truetype(TIRO,92); f2=ImageFont.truetype(TIRO,62)
    t="सब्सक्राइब करें"; w=d.textlength(t,font=f1)
    d.rounded_rectangle((540-w/2-60,1120,540+w/2+60,1260),radius=70,fill=(214,24,24,255))
    d.text((540,1190),t,font=f1,fill=(255,255,255,255),anchor="mm",stroke_width=2,stroke_fill=(120,0,0,255))
    t2="लाइक  ·  कमेंट  ·  शेयर"; d.text((540,1345),t2,font=f2,fill=(255,255,255,255),anchor="mm",stroke_width=3,stroke_fill=(0,0,0,255))
    im.save(path)

def build(name,total,scenes,sentences,narr,card_fn=None,ec_start=None):
    segs=[]; os.makedirs(O+name,exist_ok=True)
    for i,s in enumerate(scenes):
        d=s["end"]-s["start"]; n=int(round(d*30)); out=f"{O}{name}/seg{i:02d}.mp4"
        if os.path.exists(out) and os.path.getsize(out)>10000: segs.append(out); continue
        if s["kind"]=="pic":
            src=s["src"]
            run(["ffmpeg","-v","error","-y","-loop","1","-framerate","30","-i",src,"-vf",
             f"scale=2160:3840:flags=lanczos,zoompan=z='1+0.045*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30,format=yuv420p",
             "-frames:v",str(n),"-c:v","libx264","-preset","veryfast","-crf","18",out])
        else:
            run(["ffmpeg","-v","error","-y","-ss",str(s.get("off",0)),"-i",s["src"],"-t",f"{d:.3f}","-vf","scale=1080:1920:flags=lanczos,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=4,format=yuv420p",
             "-an","-c:v","libx264","-preset","veryfast","-crf","18",out])
        segs.append(out)
    open(f"{O}{name}/list.txt","w").write("".join(f"file '{s}'\n" for s in segs))
    base=f"{O}{name}/base.mp4"
    run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{O}{name}/list.txt","-c","copy",base])
    nd0=dur(narr); caps=[(t,a,min(b,nd0)) for (t,a,b) in caps_for(sentences)]; capfiles=[]
    for j,(t,a,b) in enumerate(caps):
        f=f"{O}{name}/cap{j:02d}.png"; caption_png(t,f); capfiles.append((f,a,b))
    ecf=f"{O}{name}/endcard.png"; endcard_png(ecf)
    ins=["-i",base,"-i",B+"/tk/brand/logo_512q.png"]
    for f,_,_ in capfiles: ins+=["-i",f]
    fc="[1:v]scale=150:150,format=rgba,colorchannelmixer=aa=0.92[lg];[0:v][lg]overlay=28:70[v0]"
    last="v0"
    ecidx=len(capfiles)+2; ins+=["-i",ecf]
    for j,(f,a,b) in enumerate(capfiles):
        fc+=f";[{last}][{j+2}:v]overlay=0:0:enable='between(t,{a:.2f},{b-0.02:.2f})'[v{j+1}]"; last=f"v{j+1}"
    fc+=f";[{last}][{ecidx}:v]overlay=0:0:enable='gte(t,{(ec_start if ec_start is not None else nd0+0.2):.2f})'[vend]"; last="vend"
    vid=f"{O}{name}/video.mp4"
    run(["ffmpeg","-v","error","-y"]+ins+["-filter_complex",fc,"-map",f"[{last}]","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r","30",vid])
    # audio
    nd=dur(narr)+TAIL; aud=f"{O}{name}/audio.m4a"
    run(["ffmpeg","-v","error","-y","-i",narr,"-i",SH+"bgm_lak.mp3","-filter_complex",
     f"[0:a]loudnorm=I=-15,apad=pad_dur={TAIL},asplit=2[v1][v2];[1:a]atrim=0:{nd:.2f},asetpts=PTS-STARTPTS,dynaudnorm=f=1500:g=25:m=12:p=0.7,loudnorm=I=-29:TP=-4:LRA=6,afade=t=out:st={nd-2:.2f}:d=2,volume=3dB[bg];[bg][v1]sidechaincompress=threshold=0.08:ratio=2:attack=20:release=400[bgd];[bgd][v2]amix=inputs=2:normalize=0,volume=2dB,alimiter=limit=0.85[a]",
     "-map","[a]","-c:a","aac","-b:a","192k","-ar","48000",aud])
    fin=f"{O}{name}.mp4"
    run(["ffmpeg","-v","error","-y","-i",vid,"-i",aud,"-map","0:v","-map","1:a","-c:v","copy","-c:a","copy","-t",f"{nd:.2f}","-movflags","+faststart",fin])
    print(name,"video",round(dur(vid),2),"audio",round(dur(aud),2),"final",round(dur(fin),2),"narr",round(nd,2))
