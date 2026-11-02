"""Read-only niche scan -> channel/niches.json
For each candidate niche: channels CREATED in the last ~22 months that appear behind
(a) the most-viewed videos of the last 6 months and (b) the newest uploads (random newcomers, incl. failures).
Per channel: subs, views, video count, age, plus its 50 newest videos (views, duration)."""
import json, os, re, datetime
from uploader import service, retry

N = {
 "hi_bhakti_music": dict(lang="hi", reg="IN", q=["bhakti song", "bhajan new", "भजन", "devotional song hindi"]),
 "hi_bhakti_kahani": dict(lang="hi", reg="IN", q=["bhakti kahani", "पौराणिक कथा", "धार्मिक कहानी", "garud puran"]),
 "en_bible_stories": dict(lang="en", reg="US", q=["bible stories", "bible story animated", "story of jesus", "old testament story"]),
 "en_christian_worship": dict(lang="en", reg="US", q=["worship songs", "christian worship music", "praise and worship", "gospel songs"]),
 "en_history_doc": dict(lang="en", reg="US", q=["history documentary", "ancient history documentary", "history explained", "lost civilization"]),
 "en_sleep_stories": dict(lang="en", reg="US", q=["sleep story", "bedtime story for adults", "history for sleep", "boring history to fall asleep"]),
 "en_finance": dict(lang="en", reg="US", q=["personal finance explained", "how to invest", "money tips", "credit score explained"]),
 "en_stoic_psych": dict(lang="en", reg="US", q=["stoicism", "stoic philosophy", "psychology facts", "dark psychology"]),
 "en_true_crime": dict(lang="en", reg="US", q=["true crime documentary", "unsolved mystery", "true crime story", "missing person case"]),
 "en_meditation_music": dict(lang="en", reg="US", q=["meditation music", "528hz", "sleep music", "healing frequency"]),
 "hi_finance": dict(lang="hi", reg="IN", q=["share market hindi", "paisa kaise bachaye", "investment hindi", "personal finance hindi"]),
 "hi_ai_tech": dict(lang="hi", reg="IN", q=["ai tools hindi", "new ai tool", "tech news hindi", "chatgpt hindi"]),
}


def secs(x):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", x or "")
    return sum(int(v or 0) * k for v, k in zip(m.groups(), (86400, 3600, 60, 1))) if m else 0


def main():
    yt = service(); now = datetime.datetime.utcnow()
    six = (now - datetime.timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ")
    wk = (now - datetime.timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {"generated": now.isoformat() + "Z", "niches": {}}
    seen = set()
    for name, cfg in N.items():
        src = {}
        for q in cfg["q"]:
            for order, since, tag in (("viewCount", six, "top"), ("date", wk, "new")):
                if tag == "new" and q != cfg["q"][0] and q != cfg["q"][1]:
                    continue
                try:
                    r = retry(lambda: yt.search().list(part="snippet", q=q, type="video", order=order, publishedAfter=since,
                              regionCode=cfg["reg"], relevanceLanguage=cfg["lang"], maxResults=50).execute())
                    for i in r.get("items", []):
                        src.setdefault(i["snippet"]["channelId"], tag)
                except Exception as e:
                    print("search err", name, q, str(e)[:150])
        chans = {}
        ids = list(src)
        for i in range(0, len(ids), 50):
            r = retry(lambda: yt.channels().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute())
            for c in r.get("items", []):
                sn, st = c["snippet"], c.get("statistics", {})
                chans[c["id"]] = {"title": sn["title"], "created": sn["publishedAt"][:10], "src": src[c["id"]], "country": sn.get("country"),
                                  "subs": int(st.get("subscriberCount", 0)), "views": int(st.get("viewCount", 0)),
                                  "nvideos": int(st.get("videoCount", 0)), "uploads": c["contentDetails"]["relatedPlaylists"]["uploads"]}
        # recent videos only for channels created 2025-01-01+
        for cid, c in chans.items():
            if c["created"] < "2025-01-01" or cid in seen:
                continue
            seen.add(cid)
            try:
                r = retry(lambda: yt.playlistItems().list(part="contentDetails", playlistId=c["uploads"], maxResults=50).execute())
                got = [i["contentDetails"]["videoId"] for i in r.get("items", [])]
                if got:
                    r = retry(lambda: yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(got)).execute())
                    c["vids"] = [[v["snippet"]["publishedAt"][:10], secs(v["contentDetails"]["duration"]), int(v.get("statistics", {}).get("viewCount", 0)),
                                  v["snippet"]["title"][:100]] for v in r.get("items", [])]
            except Exception as e:
                print("chan err", cid, str(e)[:120])
        out["niches"][name] = chans
        print(name, len(chans), "channels", flush=True)
    os.makedirs("channel", exist_ok=True)
    json.dump(out, open("channel/niches.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
