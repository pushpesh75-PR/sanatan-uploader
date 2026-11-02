"""Read-only deep competitor + market scan (public data only) -> channel/deep.json
Quota plan (~6,000 units): ~52 search.list (100 each) + cheap list calls."""
import json, os, datetime, re, time, urllib.request, urllib.parse
from uploader import service, retry

LONG = ["hanuman bhajan", "hanuman chalisa", "shiv bhajan", "mahadev bhajan", "ram bhajan", "krishna bhajan",
        "radha krishna bhajan", "durga maa bhajan", "mata rani bhajan", "khatu shyam bhajan", "ganesh bhajan",
        "laxmi mata bhajan", "bhakti dj song", "dj bhajan nonstop", "morning bhajan", "subah ke bhajan",
        "sandhya aarti", "aarti sangrah", "mantra jaap 108", "om namah shivaya jaap", "meditation mantra",
        "sleep mantra music", "nonstop bhajan", "bhajan jukebox", "bhojpuri bhakti song", "chhath geet",
        "pauranik katha", "ramayan katha", "vedic gyan", "ai devotional song"]
MED = ["hanuman bhajan", "shiv bhajan", "ram bhajan", "krishna bhajan", "mata rani bhajan", "khatu shyam bhajan",
       "bhakti dj song", "morning bhajan", "aarti", "mantra", "bhojpuri bhakti", "chhath geet", "bhajan lyrics",
       "ai bhajan", "new bhajan 2026", "ekadashi bhajan", "kartik maas bhajan", "tulsi vivah geet",
       "dev deepawali", "bhajan marathi", "bhakti geet gujarati", "punjabi bhajan"]
SUGGEST = ["hanuman", "shiv", "ram", "krishna", "radha", "durga", "khatu shyam", "ganesh", "laxmi", "sai baba",
           "bhajan", "aarti", "mantra", "dj bhajan", "chhath", "tulsi vivah", "dev deepawali", "kartik purnima",
           "ekadashi", "morning bhajan", "sleep", "nonstop bhajan", "ram bhajan", "shiv bhajan", "hanuman chalisa"]


def secs(x):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", x or "")
    return sum(int(v or 0) * k for v, k in zip(m.groups(), (86400, 3600, 60, 1))) if m else 0


def vids_meta(yt, ids, store):
    ids = [i for i in ids if i not in store]
    for i in range(0, len(ids), 50):
        r = retry(lambda: yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute())
        for v in r.get("items", []):
            sn, st = v["snippet"], v.get("statistics", {})
            store[v["id"]] = {"title": sn["title"], "channelId": sn["channelId"], "channel": sn["channelTitle"],
                              "publishedAt": sn["publishedAt"], "sec": secs(v["contentDetails"]["duration"]),
                              "views": int(st.get("viewCount", 0)), "likes": int(st.get("likeCount", 0)),
                              "comments": int(st.get("commentCount", 0)), "tags": sn.get("tags", [])[:20],
                              "desc": sn.get("description", "")[:700], "lang": sn.get("defaultAudioLanguage"),
                              "thumb": (sn["thumbnails"].get("maxres") or sn["thumbnails"].get("high", {})).get("url")}


def main():
    yt = service()
    now = datetime.datetime.utcnow()
    out = {"generated": now.isoformat() + "Z", "search": {}, "videos": {}, "channels": {}, "uploads": {},
           "comments": {}, "suggest": {}, "trends": {}, "errors": []}
    s90 = (now - datetime.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    s30 = (now - datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    allids = set()
    for kind, qs, since in (("long", LONG, s90), ("medium", MED, s30)):
        for q in qs:
            try:
                r = retry(lambda: yt.search().list(part="id", q=q, type="video", order="viewCount", publishedAfter=since,
                                                   regionCode="IN", relevanceLanguage="hi", videoDuration=kind,
                                                   maxResults=25).execute())
                ids = [i["id"]["videoId"] for i in r.get("items", [])]
                out["search"][f"{kind}|{q}"] = ids; allids.update(ids)
            except Exception as e:
                out["errors"].append(f"search {kind} {q}: {e}"[:300])
    vids_meta(yt, list(allids), out["videos"])
    # channels of everything found
    chans = {}
    for v in out["videos"].values():
        chans.setdefault(v["channelId"], 0); chans[v["channelId"]] += v["views"]
    cids = list(chans)
    for i in range(0, len(cids), 50):
        r = retry(lambda: yt.channels().list(part="snippet,statistics,contentDetails,brandingSettings",
                                             id=",".join(cids[i:i + 50])).execute())
        for c in r.get("items", []):
            st = c.get("statistics", {})
            out["channels"][c["id"]] = {"title": c["snippet"]["title"], "created": c["snippet"]["publishedAt"][:10],
                                        "country": c["snippet"].get("country"), "subs": int(st.get("subscriberCount", 0)),
                                        "views": int(st.get("viewCount", 0)), "videos": int(st.get("videoCount", 0)),
                                        "desc": c["snippet"].get("description", "")[:500],
                                        "keywords": c.get("brandingSettings", {}).get("channel", {}).get("keywords", "")[:300],
                                        "uploads": c["contentDetails"]["relatedPlaylists"]["uploads"],
                                        "found_views": chans[c["id"]]}
    # deep-dive: top 60 channels by views found -> last 50 uploads
    top = sorted(out["channels"], key=lambda k: -out["channels"][k]["found_views"])[:60]
    for cid in top:
        try:
            r = retry(lambda: yt.playlistItems().list(part="contentDetails", playlistId=out["channels"][cid]["uploads"],
                                                      maxResults=50).execute())
            ids = [i["contentDetails"]["videoId"] for i in r.get("items", [])]
            out["uploads"][cid] = ids
            vids_meta(yt, ids, out["videos"])
            pl = retry(lambda: yt.playlists().list(part="snippet,contentDetails", channelId=cid, maxResults=25).execute())
            out["channels"][cid]["playlists"] = [[p["snippet"]["title"], p["contentDetails"]["itemCount"]] for p in pl.get("items", [])]
        except Exception as e:
            out["errors"].append(f"uploads {cid}: {e}"[:300])
    # comments: top 40 long videos by views
    longv = sorted([k for k, v in out["videos"].items() if v["sec"] >= 240], key=lambda k: -out["videos"][k]["views"])[:40]
    for vid in longv:
        try:
            r = retry(lambda: yt.commentThreads().list(part="snippet", videoId=vid, order="relevance", maxResults=20,
                                                       textFormat="plainText").execute())
            out["comments"][vid] = [i["snippet"]["topLevelComment"]["snippet"]["textDisplay"][:300] for i in r.get("items", [])]
        except Exception as e:
            out["comments"][vid] = [f"ERR {str(e)[:120]}"]
    # YouTube search suggestions (free endpoint)
    for s in SUGGEST:
        for lang in ("hi", "en"):
            try:
                u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
                    {"client": "firefox", "ds": "yt", "hl": lang, "gl": "IN", "q": s})
                out["suggest"][f"{lang}|{s}"] = json.loads(urllib.request.urlopen(u, timeout=15).read().decode("utf-8", "ignore"))[1]
            except Exception as e:
                out["errors"].append(f"suggest {s}: {e}"[:200])
            time.sleep(0.3)
    # Google Trends (best effort)
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="hi-IN", tz=330)
        groups = [["hanuman bhajan", "shiv bhajan", "ram bhajan", "krishna bhajan", "khatu shyam bhajan"],
                  ["dj bhajan", "morning bhajan", "mantra", "aarti", "bhakti song"],
                  ["hanuman chalisa", "shiv tandav", "om namah shivaya", "gayatri mantra", "ram ram"]]
        for g in groups:
            for gprop in ("youtube", ""):
                try:
                    pt.build_payload(g, timeframe="today 12-m", geo="IN", gprop=gprop)
                    df = pt.interest_over_time()
                    out["trends"][f"{gprop or 'web'}|{','.join(g)}"] = {
                        "dates": [str(d.date()) for d in df.index], **{k: [int(x) for x in df[k]] for k in g}}
                except Exception as e:
                    out["errors"].append(f"trends {g} {gprop}: {e}"[:200])
                time.sleep(8)
    except Exception as e:
        out["errors"].append(f"pytrends: {e}"[:200])
    os.makedirs("channel", exist_ok=True)
    json.dump(out, open("channel/deep.json", "w"), ensure_ascii=False)
    print(len(out["videos"]), "videos", len(out["channels"]), "channels", len(out["errors"]), "errors")


if __name__ == "__main__":
    main()
