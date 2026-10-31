"""Change title/description/tags/location of EXISTING videos.
Reads changes/changes.json [{id, title?, description?, tags?, location?}] and applies ONLY ids listed in changes/approved.txt."""
import json, os, sys
from uploader import service, retry, rec_details, log


def main():
    ch = json.load(open("changes/changes.json", encoding="utf-8"))
    ap = "changes/approved.txt"
    approved = {l.strip() for l in open(ap, encoding="utf-8")} - {""} if os.path.exists(ap) else set()
    todo = [c for c in ch if c["id"] in approved]
    if not todo:
        log("Nothing approved — no change made."); return
    yt = service(); ok = 0
    for c in todo:
        cur = retry(lambda: yt.videos().list(part="snippet,recordingDetails", id=c["id"]).execute())["items"]
        if not cur:
            log(f"- {c['id']}: not found, skipped"); continue
        sn = cur[0]["snippet"]
        body = {"id": c["id"], "snippet": {
            "title": c.get("title", sn["title"]), "description": c.get("description", sn.get("description", "")),
            "tags": c.get("tags", sn.get("tags", [])), "categoryId": sn["categoryId"]}}
        for k in ("defaultLanguage", "defaultAudioLanguage"):
            if sn.get(k): body["snippet"][k] = sn[k]
        if len(",".join(body["snippet"]["tags"])) > 480 or len(body["snippet"]["title"]) > 100:
            log(f"- {c['id']}: title/tags too long, skipped"); continue
        parts = "snippet"
        if c.get("location"):
            body["recordingDetails"] = rec_details(c["location"]); parts += ",recordingDetails"
        retry(lambda: yt.videos().update(part=parts, body=body).execute())
        ok += 1; log(f"- ✅ {c['id']}: {body['snippet']['title']}")
    log(f"Done: {ok}/{len(todo)} videos updated.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"::error::{type(e).__name__}: {str(e)[:900]}", flush=True); sys.exit(1)
