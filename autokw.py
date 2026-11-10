"""Daily auto keyword refresh: real YouTube search terms (Analytics API) -> description line + tags of recent public videos.
DRY_RUN=1 -> only print. State: autokw/state.json"""
import json, os, re, datetime, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from uploader import service, retry, log

DRY = os.environ.get("DRY_RUN") == "1"
MAX_AGE_DAYS = 30
STOP = set("kab hai h kaise kare karen kar ka ki ke ko me mein se hain kya kaun aur par pe the is to hota hota jata jaate jaaye rakhe rakha rakhte 2026 2025 video videos new live full hd".split())
MARK = "🔎 लोग यह भी खोजते हैं (ताज़ा):"
creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                    client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token")
ya = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
yt = service()
state = json.load(open("autokw/state.json")) if os.path.exists("autokw/state.json") else {}
cost = lambda T: sum(len(t) + (2 if " " in t else 0) for t in T) + max(len(T) - 1, 0)
toks = lambda s: {w for w in re.findall(r"[a-zऀ-ॿ]{3,}", s.lower()) if w not in STOP}
today = datetime.date.today()
vids = json.load(open("channel/videos.json"))["videos"]
changed = 0
for v in vids:
    if v.get("privacy") != "public" or not v.get("publishedAt"): continue
    pub = datetime.date.fromisoformat(v["publishedAt"][:10])
    if (today - pub).days > MAX_AGE_DAYS: continue
    vid = v["id"]
    r = None
    for attempt in range(3):
      try:
        r = ya.reports().query(ids="channel==MINE", startDate=pub.isoformat(), endDate=today.isoformat(),
            dimensions="insightTrafficSourceDetail", metrics="views", sort="-views", maxResults=50,
            filters=f"video=={vid};insightTrafficSourceType==YT_SEARCH").execute(); break
      except Exception as e:
        import time; time.sleep(1 + attempt); err = str(e)[:120]
    if r is None:
        log(f"- {vid}: analytics error {err}"); continue
    rows = r.get("rows", [])
    log(f"  {vid}: api rows={len(rows)} {rows[:3]}")
    st = state.setdefault(vid, {})
    core = toks(v["title"] + " " + " ".join(v.get("tags", [])))
    for term, views in rows:
        t = re.sub(r"\s+", " ", term.strip().lower())
        if not (3 <= len(t) <= 60) or re.search(r"http|www|\.com", t) or not (toks(t) & core): continue
        st[t] = max(st.get(t, 0), views)
    if not st: log(f"- {vid}: no relevant terms yet"); continue
    sn = retry(lambda: yt.videos().list(part="snippet", id=vid).execute())["items"][0]["snippet"]
    desc, tags = sn.get("description", ""), sn.get("tags", [])
    auto_terms = sorted(st, key=lambda k: -st[k])
    low = desc.lower()
    lines = [l for l in desc.split("\n") if not l.startswith(MARK)]
    base = "\n".join(lines)
    newterms = [t for t in auto_terms if t not in base.lower()]
    line = MARK + " " + ", ".join(newterms[:40])
    ndesc = base
    if newterms:
        idx = base.find("\nघोषणा:")
        ndesc = (base[:idx].rstrip("\n") + "\n" + line + "\n" + base[idx:]) if idx > 0 else base.rstrip("\n") + "\n" + line
    while len(ndesc.encode()) > 4900 and newterms:
        newterms.pop(); line = MARK + " " + ", ".join(newterms)
        ndesc = (base[:idx].rstrip("\n") + "\n" + line + "\n" + base[idx:]) if idx > 0 else base.rstrip("\n") + "\n" + line
    ntags = list(tags)
    have = {t.lower() for t in ntags}
    for t in auto_terms:
        if t in have: continue
        if cost(ntags + [t]) <= 470 and len(",".join(ntags + [t])) <= 470:
            ntags.append(t); have.add(t)
    if ndesc == desc and ntags == tags:
        log(f"- {vid}: no change"); continue
    log(f"- {vid} {v['title'][:40]}: +{len(ntags)-len(tags)} tags, {len(newterms)} terms in description; top: {auto_terms[:5]}")
    if DRY: continue
    body = {"id": vid, "snippet": {"title": sn["title"], "description": ndesc, "tags": ntags, "categoryId": sn["categoryId"]}}
    for k in ("defaultLanguage", "defaultAudioLanguage"):
        if sn.get(k): body["snippet"][k] = sn[k]
    retry(lambda: yt.videos().update(part="snippet", body=body).execute()); changed += 1
os.makedirs("autokw", exist_ok=True)
json.dump(state, open("autokw/state.json", "w"), ensure_ascii=False, indent=1)
log(f"Done. updated={changed} dry={DRY}")
