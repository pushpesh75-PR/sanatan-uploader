import glob, json, os
from faster_whisper import WhisperModel
os.makedirs("asrout", exist_ok=True)
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sorted(glob.glob("asrin/*.mp3")):
    segs, _ = m.transcribe(f, language="hi", beam_size=5, word_timestamps=True)
    out = []
    for s in segs:
        out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text,
                    "words": [[round(w.start, 2), round(w.end, 2), w.word] for w in (s.words or [])]})
    json.dump(out, open("asrout/" + os.path.basename(f)[:-4] + ".json", "w"), ensure_ascii=False, indent=1)
