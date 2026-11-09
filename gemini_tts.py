import os, sys, json, base64, urllib.request, time
KEY = os.environ["GEMINI_API_KEY"]
P = "Instrumental only, no vocals, no voice, no lyrics. Soft devotional Indian background score for a 40 second Bhai Dooj festival video: gentle flute, soft tabla, light sitar, warm tanpura, tiny temple bells, calm, affectionate, warm, steady and unobtrusive so a narrator can speak over it; gentle fade at the end. Around 60 seconds."
os.makedirs("ttsout", exist_ok=True)
for model in ["lyria-3-pro-preview", "lyria-3-clip-preview"]:
    body = {"contents": [{"parts": [{"text": P}]}], "generationConfig": {"responseModalities": ["AUDIO", "TEXT"]}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    try:
        req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
        r = json.loads(urllib.request.urlopen(req, timeout=400).read())
        n = 0
        for p in r["candidates"][0]["content"]["parts"]:
            if "inlineData" in p:
                d = p["inlineData"]; print(model, d.get("mimeType"))
                open(f"ttsout/bgm_{model}.bin", "wb").write(base64.b64decode(d["data"])); n += 1
        if n: break
    except Exception as e:
        m=str(getattr(e, "read", lambda: b"")().decode()[:600] or e); print(model,"ERR",m); open("ttsout/err.txt","a").write(model+" "+m+"\n")
