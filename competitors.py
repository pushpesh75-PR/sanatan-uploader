"""Read-only competitor scan via YouTube Data API (public data only).
For each query: top videos of the last 30 days in India/Hindi, plus their channels' public stats."""
import json, os, datetime
from uploader import service, retry

Q = ["hanuman bhajan", "हनुमान भजन", "ram bhajan", "राम भजन", "shiv bhajan", "krishna bhajan", "bhakti dj song",
     "diwali bhajan", "laxmi mata bhajan", "chhath geet", "chhath puja kab hai", "mantra 108 times",
     "morning bhajan", "hanuman chalisa", "devotional song ai", "ram aayenge", "shiv tandav stotram",
     "durga maa bhajan", "bhojpuri bhakti song", "meditation mantra"]


def main():
    yt = service()
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {"generated": datetime.datetime.utcnow().isoformat() + "Z", "queries": {}, "videos": {}, "channels": {}}
    vids = set()
    for q in Q:
        r = retry(lambda: yt.search().list(part="snippet", q=q, type="video", order="viewCount", publishedAfter=since,
                                           regionCode="IN", relevanceLanguage="hi", maxResults=25).execute())
        ids = [i["id"]["videoId"] for i in r.get("items", [])]
        out["queries"][q] = ids; vids.update(ids)
    vids = list(vids); chans = set()
    for i in range(0, len(vids), 50):
        r = retry(lambda: yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(vids[i:i + 50])).execute())
        for v in r.get("items", []):
            sn, st = v["snippet"], v.get("statistics", {})
            out["videos"][v["id"]] = {"title": sn["title"], "channelId": sn["channelId"], "channel": sn["channelTitle"],
                                      "publishedAt": sn["publishedAt"], "duration": v["contentDetails"]["duration"],
                                      "views": int(st.get("viewCount", 0)), "likes": int(st.get("likeCount", 0)),
                                      "comments": int(st.get("commentCount", 0)), "tags": sn.get("tags", [])[:15],
                                      "thumb": sn["thumbnails"].get("high", {}).get("url")}
            chans.add(sn["channelId"])
    chans = list(chans)
    for i in range(0, len(chans), 50):
        r = retry(lambda: yt.channels().list(part="snippet,statistics", id=",".join(chans[i:i + 50])).execute())
        for c in r.get("items", []):
            st = c.get("statistics", {})
            out["channels"][c["id"]] = {"title": c["snippet"]["title"], "created": c["snippet"]["publishedAt"][:10],
                                        "country": c["snippet"].get("country"), "subs": int(st.get("subscriberCount", 0)),
                                        "views": int(st.get("viewCount", 0)), "videos": int(st.get("videoCount", 0))}
    os.makedirs("channel", exist_ok=True)
    json.dump(out, open("channel/competitors.json", "w"), ensure_ascii=False, indent=1)
    print(len(out["videos"]), "videos", len(out["channels"]), "channels")


if __name__ == "__main__":
    main()
