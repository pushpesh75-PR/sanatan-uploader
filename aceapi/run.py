"""Generate songs via the free official ACE-Step cloud API (api.acemusic.ai) using the official acestep.sh,
then transcribe each mp3 with faster-whisper for a pronunciation check. Key comes only from env ACE_MUSIC_API_KEY."""
import json, os, subprocess, glob, shutil, sys
S = "aceapi/s/acestep/scripts/acestep.sh"
OUT = "acestep_output"; DEST = "aceout"
os.makedirs(DEST, exist_ok=True)
cfg = json.load(open("aceapi/s/acestep/scripts/config.example.json"))
cfg["api_key"] = os.environ["ACE_MUSIC_API_KEY"]; cfg["api_mode"] = "completion"; cfg["generation"]["vocal_language"] = "hi"
json.dump(cfg, open("aceapi/s/acestep/scripts/config.json", "w"))
log = {}
for j in json.load(open(sys.argv[1] if len(sys.argv) > 1 else "aceapi/jobs.json")):
    shutil.rmtree(OUT, ignore_errors=True)
    cmd = ["bash", S, "generate", "-c", j["caption"], "-l", j["lyrics"], "--language", j.get("lang", "hi"),
           "--duration", str(j["duration"]), "--bpm", str(j["bpm"]), "--batch", str(j.get("batch", 1))]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3000)
    log[j["name"]] = (r.stdout[-3000:] + "\nERR:" + r.stderr[-1500:])
    for i, f in enumerate(sorted(glob.glob(f"{OUT}/*.mp3")), 1):
        shutil.copy(f, f"{DEST}/{j['name']}_{i}.mp3")
open(f"{DEST}/log.json", "w").write(json.dumps(log, ensure_ascii=False, indent=1))
os.remove("aceapi/s/acestep/scripts/config.json")
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sorted(glob.glob(f"{DEST}/*.mp3")):
    segs, info = m.transcribe(f, language="hi", beam_size=5)
    open(f[:-4] + ".txt", "w").write("\n".join(f"[{s.start:6.1f}] {s.text}" for s in segs))
