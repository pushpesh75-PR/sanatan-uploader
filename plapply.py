"""Applies changes/plan.json {rename:[{id,title}], remove:[playlistItemId], create:[{key,title,description}], add:[{pl (id or key), vid}]} if changes/approved.txt has 'plan'."""
import json, os
from uploader import service, retry, log


def main():
    if "plan" not in open("changes/approved.txt").read().split():
        log("not approved"); return
    P = json.load(open("changes/plan.json", encoding="utf-8")); yt = service(); keys = {}
    for r in P.get("rename", []):
        cur = retry(lambda: yt.playlists().list(part="snippet", id=r["id"]).execute())["items"][0]["snippet"]
        body = {"id": r["id"], "snippet": {"title": r["title"], "description": r.get("description", cur.get("description", "")),
                                          "defaultLanguage": cur.get("defaultLanguage", "hi")}}
        retry(lambda: yt.playlists().update(part="snippet", body=body).execute()); log(f"renamed {r['id']} -> {r['title']}")
    for c in P.get("create", []):
        n = retry(lambda: yt.playlists().insert(part="snippet,status", body={"snippet": {"title": c["title"], "description": c.get("description", ""), "defaultLanguage": "hi"},
                  "status": {"privacyStatus": "public"}}).execute())
        keys[c["key"]] = n["id"]; log(f"created {n['id']} {c['title']}")
    for i in P.get("remove", []):
        try:
            retry(lambda: yt.playlistItems().delete(id=i).execute()); log(f"removed {i}")
        except Exception as e:
            print(f"::warning::remove {i} failed: {str(e)[:160]}")
    for a in P.get("add", []):
        pid = keys.get(a["pl"], a["pl"])
        try:
            retry(lambda: yt.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": a["vid"]}}}).execute())
            log(f"added {a['vid']} -> {pid}")
        except Exception as e:
            print(f"::warning::add {a['vid']} -> {pid} failed: {str(e)[:160]}")


if __name__ == "__main__":
    main()
