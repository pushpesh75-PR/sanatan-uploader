"""Read-only peer-cohort study -> channel/peers_katha.json
Cohort = devotional channels created 2025+ found two ways:
  (a) channels in deep.json (found via top results)            -> survivors
  (b) channels behind the NEWEST uploads (order=date) of 30 queries -> random new uploaders incl. failures
For every cohort channel: full upload history (up to 300 newest) with views/likes/comments/duration."""
import json, os, re, datetime
from uploader import service, retry

KW = ['bhakti', 'bhajan', 'भक्ति', 'भजन', 'mantra', 'मंत्र', 'devotional', 'sanatan', 'सनातन', 'shiv', 'शिव', 'ram', 'राम',
      'krishna', 'कृष्ण', 'hanuman', 'हनुमान', 'katha', 'कथा', 'kahani', 'कहानी', 'story', 'puran', 'पुराण', 'aarti', 'आरती', 'dharm', 'धर्म', 'mata', 'माता', 'spiritual',
      'kirtan', 'chalisa', 'mahadev', 'महादेव', 'radhe', 'राधे', 'jai', 'जय']
Q = ["bhakti kahani", "bhakt ki kahani", "chamatkar kahani", "भक्ति कहानी", "भक्त की कहानी", "चमत्कारी कहानी", "पौराणिक कथा", "pauranik katha", "ramayan katha", "रामायण की कहानी", "garud puran", "गरुड़ पुराण", "ekadashi vrat katha", "एकादशी व्रत कथा", "shiv katha", "शिव की कहानी", "hanuman ji ki kahani", "हनुमान जी की कहानी", "krishna leela kahani", "कृष्ण की कहानी", "jagannath kahani", "mahabharat katha", "devotional story hindi", "dharmik kahani", "धार्मिक कहानी", "ai devotional story", "sanatan katha", "mata rani kahani", "shani dev kahani", "tulsi vivah katha"]


def secs(x):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", x or "")
    return sum(int(v or 0) * k for v, k in zip(m.groups(), (86400, 3600, 60, 1))) if m else 0


def main():
    yt = service()
    src = {}
    yr = (datetime.datetime.utcnow() - datetime.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for q in Q:
        try:
            r = retry(lambda: yt.search().list(part="snippet", q=q, type="video", order="date", publishedAfter=since,
                                               regionCode="IN", relevanceLanguage="hi", maxResults=50).execute())
            for i in r.get("items", []):
                src.setdefault(i["snippet"]["channelId"], "new")
            r = retry(lambda: yt.search().list(part="snippet", q=q, type="video", order="viewCount", publishedAfter=yr,
                                               regionCode="IN", relevanceLanguage="hi", maxResults=50).execute())
            for i in r.get("items", []):
                src.setdefault(i["snippet"]["channelId"], "top")
        except Exception as e:
            print("search err", q, e)
    ids = list(src); chans = {}
    for i in range(0, len(ids), 50):
        r = retry(lambda: yt.channels().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute())
        for c in r.get("items", []):
            sn, st = c["snippet"], c.get("statistics", {})
            text = (sn["title"] + " " + sn.get("description", "")).lower()
            if sn["publishedAt"][:10] < "2025-01-01" or not any(w in text for w in KW):
                continue
            chans[c["id"]] = {"title": sn["title"], "created": sn["publishedAt"][:10], "src": src[c["id"]],
                              "subs": int(st.get("subscriberCount", 0)), "views": int(st.get("viewCount", 0)),
                              "nvideos": int(st.get("videoCount", 0)), "uploads": c["contentDetails"]["relatedPlaylists"]["uploads"]}
    print("cohort", len(chans))
    vids = {}
    for cid, c in chans.items():
        try:
            got, page = [], None
            while len(got) < 300:
                r = retry(lambda: yt.playlistItems().list(part="contentDetails", playlistId=c["uploads"], maxResults=50, pageToken=page).execute())
                got += [i["contentDetails"]["videoId"] for i in r.get("items", [])]; page = r.get("nextPageToken")
                if not page: break
            for i in range(0, len(got), 50):
                r = retry(lambda: yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(got[i:i + 50])).execute())
                for v in r.get("items", []):
                    s, st = v["snippet"], v.get("statistics", {})
                    vids[v["id"]] = [cid, s["publishedAt"][:16], secs(v["contentDetails"]["duration"]), int(st.get("viewCount", 0)),
                                     int(st.get("likeCount", 0)), int(st.get("commentCount", 0)), s["title"][:140]]
        except Exception as e:
            print("chan err", cid, str(e)[:120])
    os.makedirs("channel", exist_ok=True)
    json.dump({"generated": datetime.datetime.utcnow().isoformat() + "Z", "channels": chans,
               "cols": ["ch", "published", "sec", "views", "likes", "comments", "title"], "videos": vids},
              open("channel/peers_katha.json", "w"), ensure_ascii=False)
    print("videos", len(vids))


if __name__ == "__main__":
    main()
