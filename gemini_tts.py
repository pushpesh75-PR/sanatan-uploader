"""Gemini TTS: tts/<name>/*.txt -> ttsout/*.wav. First line '#gemini voice=<Name> model=<id>' optional.
Style prompt (storyteller) is prepended. Key from env GEMINI_API_KEY only."""
import os, sys, glob, json, base64, wave, time, urllib.request, re
KEY = os.environ["GEMINI_API_KEY"]
STYLE = os.environ.get("TTS_STYLE", "Read aloud in Hindi like a warm, emotional, experienced Indian kathavachak telling a devotional story to a family: natural flowing pace, gentle pauses at commas and full stops, soft and heartfelt, never robotic, never rushed:")
def tts(text, voice, model):
    body = {"contents": [{"parts": [{"text": STYLE + "\n\n" + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for a in range(6):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
            r = json.loads(urllib.request.urlopen(req, timeout=300).read())
            return base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
        except Exception as e:
            msg = getattr(e, "read", lambda: b"")().decode()[:1800] if hasattr(e, "read") else str(e)
            print("retry", a, msg)
            if "quota" in msg.lower() and "exceeded" in msg.lower():
                if "perday" in msg.lower().replace(" ","").replace("_","") or "per day" in msg.lower(): return None
                time.sleep(65); continue
            time.sleep(20 * (a + 1))
    print("::error::gemini quota/err, stopping; partial outputs kept"); return None
name = sys.argv[1]; os.makedirs("ttsout", exist_ok=True)
for f in sorted(glob.glob(f"tts/{name}/*.txt")):
    lines = open(f, encoding="utf-8").read().split("\n")
    voice, model = "Charon", "gemini-3.1-flash-tts-preview"
    if lines[0].startswith("#"):
        m = re.search(r"voice=(\S+)", lines[0]); voice = m.group(1) if m else voice
        m = re.search(r"model=(\S+)", lines[0]); model = m.group(1) if m else model
        lines = lines[1:]
    out = "ttsout/" + os.path.basename(f)[:-4] + ".wav"
    if os.path.exists(out): print("skip", out); continue
    sf = os.path.join(os.path.dirname(f), "style.txt")
    if os.path.exists(sf): STYLE = "Read the text that follows aloud, exactly as written, in Hindi. Delivery instructions (do not read these aloud): " + open(sf, encoding="utf-8").read().strip()
    pcm = tts("\n".join(lines).strip(), voice, model)
    if pcm is None: break
    with wave.open(out, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    print(out, len(pcm) / 48000, "s"); time.sleep(4)
