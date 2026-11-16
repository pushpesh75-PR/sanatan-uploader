"""Read-only: save every playlist with its items (videoId, playlistItemId, position) to channel/playlists.json."""
import json, os
from uploader import service, retry


def main():
    yt = service(); out, page = [], None
    while True:
        r = retry(lambda: yt.playlists().list(part="snippet,contentDetails,status", mine=True, maxResults=50, pageToken=page).execute())
        for p in r.get("items", []):
            items, pg = [], None
            while True:
                q = retry(lambda: yt.playlistItems().list(part="snippet,contentDetails,status", playlistId=p["id"], maxResults=50, pageToken=pg).execute())
                items += [{"item": i["id"], "vid": i["contentDetails"]["videoId"], "title": i["snippet"]["title"], "pos": i["snippet"].get("position")} for i in q.get("items", [])]
                pg = q.get("nextPageToken")
                if not pg: break
            ids = [i["vid"] for i in items]
            dur = {}
            for k in range(0, len(ids), 50):
                for v in retry(lambda: yt.videos().list(part="contentDetails,snippet,status", id=",".join(ids[k:k+50])).execute()).get("items", []):
                    dur[v["id"]] = (v["contentDetails"]["duration"], v["status"]["privacyStatus"], v["snippet"]["title"])
            for i in items:
                i["dur"], i["privacy"], i["title"] = dur.get(i["vid"], (None, None, i["title"]))
            out.append({"id": p["id"], "title": p["snippet"]["title"], "description": p["snippet"].get("description", ""),
                        "privacy": p["status"]["privacyStatus"], "count": p["contentDetails"]["itemCount"], "items": items})
        page = r.get("nextPageToken")
        if not page: break
    os.makedirs("channel", exist_ok=True)
    json.dump(out, open("channel/playlists.json", "w"), ensure_ascii=False, indent=1)
    print(f"saved {len(out)} playlists")


if __name__ == "__main__":
    main()
