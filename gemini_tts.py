import os, sys, json, time, urllib.request
KEY = os.environ["GEMINI_API_KEY"]
os.makedirs("ttsout", exist_ok=True)
out = []
def call(model, n=1):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"text": "Say ok"}]}], "generationConfig": {"maxOutputTokens": 5}}
    try:
        req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
        urllib.request.urlopen(req, timeout=60).read(); return 200, ""
    except Exception as e:
        b = getattr(e, "read", lambda: b"")().decode()[:600] if hasattr(e, "read") else str(e)[:300]
        return getattr(e, "code", 0), b.replace(KEY, "***")
model = None
try:
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers={"x-goog-api-key": KEY})
    ms = [m["name"].split("/")[-1] for m in json.loads(urllib.request.urlopen(req, timeout=60).read())["models"] if "generateContent" in m.get("supportedGenerationMethods", [])]
    out.append("models: " + ",".join(ms[:60]))
    for pref in ("flash-lite", "flash"):
        c = [m for m in ms if pref in m and "tts" not in m and "image" not in m and "live" not in m and "audio" not in m]
        if c: model = c[0]; break
except Exception as e:
    out.append("list err " + str(e)[:200])
out.append("model " + str(model))
ok = 0; fails = []
for i in range(40):
    s, b = call(model)
    if s == 200: ok += 1
    else: fails.append((i, s, b[:400]))
    time.sleep(0.15)
out.append(f"ok={ok} of 40")
for f in fails[:3]: out.append("FAIL " + str(f))
txt = "\n".join(out)
out.append("free_tier_in_errors=" + str(any(("free" in f[2].lower()) for f in fails)))
open("ttsout/keycheck.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
