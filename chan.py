"""Read-only: full public profile of channels listed in chan/handles.txt -> channel/chan_<handle>.json"""
import json, os, re
from uploader import service, retry
def secs(x):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", x or "")
    return sum(int(v or 0) * k for v, k in zip(m.groups(), (86400, 3600, 60, 1))) if m else 0
yt = service()
for h in [l.strip() for l in open("chan/handles.txt") if l.strip()]:
    c = retry(lambda: yt.channels().list(part="snippet,statistics,contentDetails,brandingSettings", forHandle=h).execute())["items"][0]
    up = c["contentDetails"]["relatedPlaylists"]["uploads"]; ids = []; page = None
    while len(ids) < 400:
        r = retry(lambda: yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=50, pageToken=page).execute())
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]; page = r.get("nextPageToken")
        if not page: break
    vids = []
    for i in range(0, len(ids), 50):
        r = retry(lambda: yt.videos().list(part="snippet,statistics,contentDetails,status", id=",".join(ids[i:i+50])).execute())
        for v in r["items"]:
            s = v["snippet"]; st = v.get("statistics", {})
            vids.append({"id": v["id"], "title": s["title"], "publishedAt": s["publishedAt"], "sec": secs(v["contentDetails"]["duration"]),
                         "views": int(st.get("viewCount", 0)), "likes": int(st.get("likeCount", 0)), "comments": int(st.get("commentCount", 0)),
                         "tags": s.get("tags", [])[:15], "desc": s.get("description", "")[:600], "made_for_kids": v["status"].get("madeForKids")})
    pls = retry(lambda: yt.playlists().list(part="snippet,contentDetails", channelId=c["id"], maxResults=50).execute())
    out = {"channel": {"id": c["id"], "title": c["snippet"]["title"], "created": c["snippet"]["publishedAt"], "country": c["snippet"].get("country"),
                       "desc": c["snippet"].get("description", ""), "stats": c["statistics"],
                       "keywords": c.get("brandingSettings", {}).get("channel", {}).get("keywords")},
           "playlists": [[p["snippet"]["title"], p["contentDetails"]["itemCount"]] for p in pls.get("items", [])], "videos": vids}
    os.makedirs("channel", exist_ok=True)
    json.dump(out, open(f"channel/chan_{h.strip('@')}.json", "w"), ensure_ascii=False)
    print(h, len(vids))
