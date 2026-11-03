"""Approved channel fixes (user said '5 fixes krdo', 2 Nov 2026). Runs only actions listed in fix/approved.txt.
Writes channel/fix_report.json (incl. our own comments per video, for pinning)."""
import json, os
from uploader import service, retry

NEW_DESC = """🚩 सनातन बीट्स में आपका स्वागत है! सनातन धर्म की भक्ति को संगीत के ज़रिए घर-घर पहुँचाने का प्रयास — हर भजन, हर बीट में भक्ति की शक्ति। 🚩

🔱 शिव भजन एवं DJ भजन
🚩 श्री राम भजन
🦚 हनुमान जी के DJ एवं पारंपरिक भजन
🌺 छठ पूजा एवं त्योहार विशेष गीत (दिवाली, नवरात्रि)
🔴 Nonstop भक्ति जुकबॉक्स — पूजा, सफ़र और सुबह-शाम सुनने के लिए

|| जय श्री राम || हर हर महादेव || जय बजरंगबली || जय छठी मैया ||

🔔 Subscribe करें: @thesanatanbeat

संगीत व दृश्य AI tools से बनाए गए हैं; बोल पारंपरिक/मौलिक हैं।

#SanatanBeats #Bhajan #HanumanDJ #ShivBhajan #RamBhajan #ChhathPujaSong #BhaktiDJ #NonstopBhajan #DevotionalSongs #JaiShreeRam #HarHarMahadev #BhaktiJukebox"""

NEW_KEYWORDS_ADD = ["chhath puja song", "chhath geet 2026", "hanuman dj song", "shiv dj bhajan",
                     "nonstop bhajan jukebox", "bhakti jukebox", "diwali dj song", "navratri dj song",
                     "bhojpuri chhath geet", "long drive bhajan", "morning bhajan"]


def merge_keywords(old, add):
    """YouTube keywords field: space-separated, multi-word terms "quoted"; hard limit 500 chars."""
    def tok(k):
        return f'"{k}"' if " " in k else k
    seen = set((old or "").split())
    out = (old or "").strip()
    for k in add:
        t = tok(k)
        if t in seen:
            continue
        cand = (out + " " + t).strip()
        if len(cand) > 500:
            break
        out = cand; seen.add(t)
    return out
PLAYLISTS = {
    "छठ पूजा गीत 2026 | Chhath Puja Songs": (
        "छठी मैया के पारंपरिक गीत, सूर्य मंत्र और छठ पूजा की जानकारी — नहाय-खाय से उषा अर्घ्य तक। जय छठी मैया 🙏",
        ["gvj24Hp90ZU", "ueFr4JyC5Ws", "1sarcxHV38Y", "CHKCHB5-46A", "cnhsueJKOHs", "yeLQV-K_snI", "IgTFvkbbSTE",
         "TWPlo0m2OK4", "VAKP0h1_PmM", "tu_ewgj4hpU", "e4Z8FdhnEv0", "h9zLbb0Jmvc"]),
    "हनुमान भजन | Hanuman Bhajan": (
        "बजरंगबली के भजन — सुबह की पूजा, मंगलवार और शनिवार के लिए। जय श्री राम, जय हनुमान 🚩",
        ["NMXxX5XOFTM", "4BU59ubdt9w", "3nSzqFKD-R0", "UfT1BZZ7gEw", "QRRNnXMJMI0", "W9t0Ym0Tsa4", "QyXEaBy7GJY"]),
    "शिव भजन | Shiv Bhajan": (
        "महादेव के भजन और स्तोत्र — सोमवार और हर दिन की शिव भक्ति के लिए। हर हर महादेव 🔱",
        ["toUzUM38Rko", "d4gYTmYr4Pc", "1kw-xaCuT4s", "5N0KLIgK5Rs", "KGuLwX6XA6Q", "Jgfndqsjq48", "eVrm1GiEpCs"]),
}


def main():
    ap = {l.strip() for l in open("fix/approved.txt", encoding="utf-8")} - {""}
    yt = service(); rep = {"done": [], "errors": [], "comments": {}}
    ch = retry(lambda: yt.channels().list(part="brandingSettings,snippet", mine=True).execute())["items"][0]
    my_id = ch["id"]
    if "description" in ap:
        b = ch["brandingSettings"]; chb = b.setdefault("channel", {})
        old_kw = chb.get("keywords", "")
        chb["description"] = NEW_DESC
        chb["keywords"] = merge_keywords(old_kw, NEW_KEYWORDS_ADD)
        retry(lambda: yt.channels().update(part="brandingSettings", body={"id": my_id, "brandingSettings": b}).execute())
        rep["done"].append("description updated")
        rep["done"].append(f"keywords: {len(old_kw)} -> {len(chb['keywords'])} chars")
    pls, page = [], None
    while True:
        r = retry(lambda: yt.playlists().list(part="snippet,contentDetails", mine=True, maxResults=50, pageToken=page).execute())
        pls += r.get("items", []); page = r.get("nextPageToken")
        if not page: break
    if "delete_empty_diwali" in ap:
        for p in pls:
            if p["snippet"]["title"].strip() == "दिवाली 2026" and p["contentDetails"]["itemCount"] == 0:
                retry(lambda: yt.playlists().delete(id=p["id"]).execute()); rep["done"].append(f"deleted empty playlist {p['id']}")
    if "playlists" in ap:
        have = {p["snippet"]["title"].strip(): p["id"] for p in pls}
        for title, (desc, vids) in PLAYLISTS.items():
            pid = have.get(title)
            existing = set()
            if not pid:
                pid = retry(lambda: yt.playlists().insert(part="snippet,status", body={
                    "snippet": {"title": title, "description": desc, "defaultLanguage": "hi"},
                    "status": {"privacyStatus": "public"}}).execute())["id"]
                rep["done"].append(f"created playlist {title} {pid}")
            else:
                r = retry(lambda: yt.playlistItems().list(part="contentDetails", playlistId=pid, maxResults=50).execute())
                existing = {i["contentDetails"]["videoId"] for i in r.get("items", [])}
            for v in vids:
                if v in existing: continue
                try:
                    retry(lambda: yt.playlistItems().insert(part="snippet", body={"snippet": {
                        "playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": v}}}).execute())
                    rep["done"].append(f"added {v} to {title}")
                except Exception as e:
                    rep["errors"].append(f"add {v}: {str(e)[:150]}")
    if "list_comments" in ap:
        up = retry(lambda: yt.channels().list(part="contentDetails", id=my_id).execute())["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        ids, page = [], None
        while True:
            r = retry(lambda: yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=50, pageToken=page).execute())
            ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]; page = r.get("nextPageToken")
            if not page: break
        for v in ids:
            try:
                r = retry(lambda: yt.commentThreads().list(part="snippet", videoId=v, maxResults=50, textFormat="plainText").execute())
                mine = [{"id": t["id"], "text": t["snippet"]["topLevelComment"]["snippet"]["textDisplay"][:300]}
                        for t in r.get("items", []) if t["snippet"]["topLevelComment"]["snippet"].get("authorChannelId", {}).get("value") == my_id]
                rep["comments"][v] = mine
            except Exception as e:
                rep["comments"][v] = f"ERR {str(e)[:100]}"
    os.makedirs("channel", exist_ok=True)
    json.dump(rep, open("channel/fix_report.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep["done"], ensure_ascii=False)); print(rep["errors"])


if __name__ == "__main__":
    main()
