"""Chhath nonstop: audio mix + visual shots + overlays. Run: python3 build.py"""
import json, os, random, subprocess, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(D)
os.chdir(D); random.seed(7)
W, H, FPS = 1920, 1080, 25
def run(c): subprocess.run(c, shell=True, check=True)
def dur(f): return float(subprocess.check_output(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{f}"', shell=True))

# ---------- 1. audio ----------
SONGS = json.load(open("songs.json"))  # [{file, start, end, title}]
XF = 3.0
os.makedirs("a", exist_ok=True)
parts = []
for i, s in enumerate(SONGS):
    o = f"a/{i}.wav"; L = s["end"] - s["start"]
    run(f'ffmpeg -v error -y -ss {s["start"]} -t {L} -i {s["file"]} -af "afade=t=in:d=0.3,afade=t=out:st={L-XF}:d={XF},loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -ac 2 {o}')
    parts.append((o, L))
# crossfade chain
inputs = "".join(f'-i {p} ' for p, _ in parts)
fc = ""; prev = "[0:a]"
for i in range(1, len(parts)):
    fc += f"{prev}[{i}:a]acrossfade=d={XF}:c1=tri:c2=tri[x{i}];"; prev = f"[x{i}]"
run(f'ffmpeg -v error -y {inputs} -filter_complex "{fc[:-1]}" -map "[x{len(parts)-1}]" -c:a pcm_s16le mix.wav')
T = dur("mix.wav")
starts = []; t = 0
for i, (_, L) in enumerate(parts):
    starts.append(t); t += L - XF
json.dump({"T": T, "starts": starts}, open("timeline.json", "w"))
print("audio", T, starts)

# ---------- 2. shots ----------
clips = sorted(glob.glob("v/*.mp4")); imgs = sorted(glob.glob("i/*.jpg"))
pool = [("v", c) for c in clips] + [("i", i) for i in imgs]
os.makedirs("sh", exist_ok=True)
SH = 7.0; n = int(T / (SH - 1.0)) + 2
order = []
while len(order) < n:
    p = pool[:]; random.shuffle(p)
    if order and p[0] == order[-1]: p.append(p.pop(0))
    order += p
order = order[:n]
for k, (typ, src) in enumerate(order):
    o = f"sh/{k:04d}.mp4"
    if os.path.exists(o): continue
    if typ == "v":
        d = dur(src); CL={"n1":2.5,"n2":3.0,"n3":3.0,"n4":3.0}; clean = min(d, CL.get(os.path.basename(src)[:-4], 6.5))
        # forward then reverse (ping-pong) of the clean window, slow, never zoom-in
        z = random.choice([1.0, 1.06]); x = random.choice(["(iw-ow)/2", "0", "iw-ow"])
        run(f'ffmpeg -v error -y -i "{src}" -filter_complex "[0:v]trim=0:{clean},setpts=PTS-STARTPTS,scale={int(W*z)}:{int(H*z)},crop={W}:{H}:{x}:(ih-oh)/2,fps={FPS},split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1,setpts=(PTS-STARTPTS)*{max(1.0, SH/(2*clean)):.3f},trim=0:{SH},setpts=PTS-STARTPTS,format=yuv420p" -an -c:v libx264 -preset veryfast -crf 20 {o}')
    else:
        # slow Ken Burns: zoom OUT (pull-back feel) or slow pan
        fr = int(SH * FPS); mode = random.choice(["out", "panl", "panr"])
        if mode == "out": zp = f"z='1.12-0.10*on/{fr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
        elif mode == "panl": zp = f"z=1.10:x='(iw-iw/zoom)*on/{fr}':y='(ih-ih/zoom)/2'"
        else: zp = f"z=1.10:x='(iw-iw/zoom)*(1-on/{fr})':y='(ih-ih/zoom)/2'"
        run(f'ffmpeg -v error -y -loop 1 -i "{src}" -vf "scale=3840:-2,zoompan={zp}:d={fr}:s={W}x{H}:fps={FPS},format=yuv420p" -t {SH} -c:v libx264 -preset veryfast -crf 20 {o}')
print("shots", n)

# ---------- 3. concat shots with 1 s dissolves (in groups) ----------
def xfade_chain(files, out):
    ins = "".join(f'-i {f} ' for f in files); fc = ""; prev = "[0:v]"; off = 0
    for i in range(1, len(files)):
        off += SH - 1.0
        fc += f"{prev}[{i}:v]xfade=transition=fade:duration=1:offset={off}[v{i}];"; prev = f"[v{i}]"
    run(f'ffmpeg -v error -y {ins} -filter_complex "{fc[:-1]}" -map "{prev}" -c:v libx264 -preset veryfast -crf 20 {out}')
shots = sorted(glob.glob("sh/*.mp4")); G = 20; groups = []
for g in range(0, len(shots), G):
    out = f"g{g//G:03d}.mp4"
    if not os.path.exists(out): xfade_chain(shots[g:g+G], out)
    groups.append(out)
open("glist.txt", "w").write("".join(f"file '{g}'\n" for g in groups))
run('ffmpeg -v error -y -f concat -safe 0 -i glist.txt -c copy vis.mp4')

# ---------- 4. overlays (title cards per song, logo, subscribe) ----------
F1 = f"{S}/fonts/eczar500.ttf"; F2 = f"{S}/fonts/laila500.ttf"
os.makedirs("ov", exist_ok=True)
def card(i, title, sub):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(F1, 78); f2 = ImageFont.truetype(F2, 40)
    tw = max(d.textlength(title, font=f1), d.textlength(sub, font=f2)) + 120
    x0, y0 = 80, H - 300
    d.rounded_rectangle([x0, y0, x0 + tw, y0 + 200], 28, fill=(60, 10, 10, 200), outline=(240, 190, 80, 255), width=4)
    d.text((x0 + 60, y0 + 22), title, font=f1, fill="white", stroke_width=3, stroke_fill="black")
    d.text((x0 + 60, y0 + 128), sub, font=f2, fill=(255, 220, 90))
    im.save(f"ov/card{i}.png")
for i, s in enumerate(SONGS): card(i, s["title"], s.get("sub", f"छठ गीत {i+1}/{len(SONGS)}"))
lg = Image.open(f"{S}/brand/logo.png").convert("RGBA"); lg.thumbnail((150, 150)); lg.save("ov/logo.png")
im = Image.new("RGBA", (620, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle([0, 0, 619, 95], 48, fill=(200, 20, 20, 235)); f = ImageFont.truetype(F2, 44)
d.text((40, 18), "🔔 Subscribe · Like · Share".replace("🔔 ", ""), font=f, fill="white"); im.save("ov/sub.png")
tl = json.load(open("timeline.json")); fc = "[0:v][1:v]overlay=W-w-40:30[b0];"; ins = "-i ov/logo.png "; cur = "b0"; k = 2
for i, st in enumerate(tl["starts"]):
    a, b = st + 1.5, st + 8.5
    ins += f"-i ov/card{i}.png "; fc += f"[{cur}][{k}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[b{k}];"; cur = f"b{k}"; k += 1
for t0 in [60, tl["T"] * 0.5, tl["T"] - 40]:
    ins += "-i ov/sub.png "; fc += f"[{cur}][{k}:v]overlay=(W-w)/2:H-150:enable='between(t,{t0:.1f},{t0+6:.1f})'[b{k}];"; cur = f"b{k}"; k += 1
fc += f"[{cur}]fade=t=in:d=1,fade=t=out:st={tl['T']-2}:d=2[vout]"
run(f'ffmpeg -v error -y -i vis.mp4 {ins} -i mix.wav -filter_complex "{fc}" -map "[vout]" -map {k}:a -t {tl["T"]} -c:v libx264 -preset veryfast -crf 21 -c:a aac -b:a 192k -movflags +faststart final.mp4')
print("done", dur("final.mp4"))
