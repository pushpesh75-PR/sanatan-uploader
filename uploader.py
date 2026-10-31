"""Sanatan Beats auto-uploader.

Reads manifest.json (from a GitHub release) and, for every item:
  upload video (private + scheduled publishAt) -> set thumbnail -> add to playlist -> post comment.
Already-uploaded items are remembered in uploaded/<release>.json so a re-run never uploads twice.

Env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, RELEASE_TAG, ASSET_DIR, DRY_RUN (optional "1").
"""
import json, os, sys, time, datetime

ASSET_DIR = os.environ.get("ASSET_DIR", "assets")
TAG = os.environ.get("RELEASE_TAG", "local")
DRY = os.environ.get("DRY_RUN") == "1"
STATE = f"uploaded/{TAG}.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def log(*a):
    print(*a, flush=True)
    with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a", encoding="utf-8") as f:
        f.write(" ".join(str(x) for x in a) + "\n\n")


def check(item):
    need = ["key", "file", "title", "description", "publish_at_utc"]
    miss = [k for k in need if not item.get(k)]
    if miss:
        raise SystemExit(f"{item.get('key')}: missing {miss}")
    if len(item["title"]) > 100:
        raise SystemExit(f"{item['key']}: title {len(item['title'])} chars (max 100)")
    if len(item["description"].encode("utf-8")) > 5000:
        raise SystemExit(f"{item['key']}: description too long")
    if len(",".join(item.get("tags", []))) > 480:
        raise SystemExit(f"{item['key']}: tags too long")
    t = datetime.datetime.fromisoformat(item["publish_at_utc"].replace("Z", "+00:00"))
    if t <= datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=20):
        raise SystemExit(f"{item['key']}: publish time {item['publish_at_utc']} is in the past / too soon")
    for f in [item["file"]] + ([item["thumbnail"]] if item.get("thumbnail") else []):
        if not os.path.exists(os.path.join(ASSET_DIR, f)):
            raise SystemExit(f"{item['key']}: file not found in release: {f}")


def service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                        token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def retry(fn, tries=5):
    from googleapiclient.errors import HttpError
    for i in range(tries):
        try:
            return fn()
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504) and i < tries - 1:
                time.sleep(5 * (i + 1)); continue
            raise


def rec_details(loc):
    return {"location": {"latitude": loc["lat"], "longitude": loc["lng"], "altitude": 0},
            "locationDescription": loc.get("desc", "")}


def update_meta(yt, vid, item):
    """Change title/description/tags/location of an already-uploaded video (schedule untouched)."""
    body = {"id": vid, "snippet": {
        "title": item["title"], "description": item["description"], "tags": item.get("tags", []),
        "categoryId": str(item.get("category_id", "10")),
        "defaultLanguage": item.get("language", "hi"), "defaultAudioLanguage": item.get("language", "hi")}}
    parts = "snippet"
    if item.get("location"):
        body["recordingDetails"] = rec_details(item["location"]); parts += ",recordingDetails"
    return retry(lambda: yt.videos().update(part=parts, body=body).execute())


def upload(yt, item):
    from googleapiclient.http import MediaFileUpload
    body = {
        "snippet": {
            "title": item["title"],
            "description": item["description"],
            "tags": item.get("tags", []),
            "categoryId": str(item.get("category_id", "10")),
            "defaultLanguage": item.get("language", "hi"),
            "defaultAudioLanguage": item.get("language", "hi"),
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": item["publish_at_utc"],
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": bool(item.get("synthetic", True)),
            "embeddable": True,
            "license": "youtube",
        },
    }
    if item.get("location"):
        body["recordingDetails"] = rec_details(item["location"])
    media = MediaFileUpload(os.path.join(ASSET_DIR, item["file"]), mimetype="video/mp4",
                            chunksize=16 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status" + (",recordingDetails" if item.get("location") else ""), body=body, media_body=media, notifySubscribers=True)
    resp = None
    while resp is None:
        status, resp = retry(lambda: req.next_chunk())
        if status:
            print(f"   {item['key']}: {int(status.progress() * 100)}%", flush=True)
    return resp


def playlist_id(yt, name, cache):
    if name in cache:
        return cache[name]
    page = None
    while True:
        r = retry(lambda: yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=page).execute())
        for p in r.get("items", []):
            if p["snippet"]["title"].strip() == name.strip():
                cache[name] = p["id"]; return p["id"]
        page = r.get("nextPageToken")
        if not page:
            break
    r = retry(lambda: yt.playlists().insert(part="snippet,status", body={
        "snippet": {"title": name, "defaultLanguage": "hi"}, "status": {"privacyStatus": "public"}}).execute())
    cache[name] = r["id"]; log(f"   created playlist “{name}”")
    return r["id"]


def main():
    man = json.load(open(os.path.join(ASSET_DIR, "manifest.json"), encoding="utf-8"))
    all_items = man["items"]
    items = all_items
    # SAFETY (user rule 31 Oct): upload ONLY keys the user approved in chat, listed in approved.txt
    ap = os.path.join(ASSET_DIR, "approved.txt")
    approved = {l.strip() for l in open(ap, encoding="utf-8")} - {""} if os.path.exists(ap) else set()
    items = [it for it in items if it["key"] in approved]
    if not items:
        log(f"## `{TAG}`: nothing approved yet (approved.txt missing or empty) — no upload.")
        return
    prev = json.load(open(STATE)) if os.path.exists(STATE) else {}
    for it in items:
        if it["key"] not in prev:
            check(it)
    log(f"## Release `{TAG}` — {len(items)} videos, manifest OK")
    if DRY:
        for it in items:
            log(f"- DRY RUN {it['key']}: {it['title']} → {it['publish_at_utc']}")
        return
    os.makedirs("uploaded", exist_ok=True)
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    yt = service(); pl = {}
    for it in items:
        k = it["key"]
        if k in state:
            vid = state[k]["id"]
            update_meta(yt, vid, it)
            if it.get("thumbnail"):
                try:
                    from googleapiclient.http import MediaFileUpload
                    retry(lambda: yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(
                        os.path.join(ASSET_DIR, it["thumbnail"]))).execute())
                except Exception as e:
                    log(f"  ⚠️ {k}: thumbnail failed: {e}")
            state[k]["title"] = it["title"]
            json.dump(state, open(STATE, "w"), ensure_ascii=False, indent=1)
            log(f"- {k}: already uploaded → updated title/description/tags/location https://youtu.be/{vid}")
            continue
        log(f"- {k}: uploading {it['file']} …")
        v = upload(yt, it); vid = v["id"]
        rec = {"id": vid, "title": it["title"], "publish_at_utc": it["publish_at_utc"],
               "privacy": v["status"].get("privacyStatus")}
        state[k] = rec
        json.dump(state, open(STATE, "w"), ensure_ascii=False, indent=1)   # save after every video
        warn = []
        if it.get("thumbnail"):
            try:
                from googleapiclient.http import MediaFileUpload
                retry(lambda: yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(
                    os.path.join(ASSET_DIR, it["thumbnail"]))).execute())
            except Exception as e:
                warn.append(f"thumbnail failed: {e}")
        for name in it.get("playlists", []):
            try:
                pid = playlist_id(yt, name, pl)
                retry(lambda: yt.playlistItems().insert(part="snippet", body={"snippet": {
                    "playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute())
            except Exception as e:
                warn.append(f"playlist “{name}” failed: {e}")
        if it.get("comment"):
            try:
                retry(lambda: yt.commentThreads().insert(part="snippet", body={"snippet": {
                    "videoId": vid, "topLevelComment": {"snippet": {"textOriginal": it["comment"]}}}}).execute())
            except Exception as e:
                warn.append(f"comment failed (post it by hand): {e}")
        log(f"  ✅ {k}: https://youtu.be/{vid} · scheduled {it['publish_at_utc']} UTC · status {rec['privacy']}"
            + ("".join(f"\n  ⚠️ {w}" for w in warn)))
    if all(it["key"] in state for it in man["items"]):
        open("/tmp/all_done", "w").write("1")   # workflow deletes the branch only then
    log("Done. Open YouTube Studio → Content: every video should show “Scheduled”.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        msg = f"{type(e).__name__}: {e}".replace("\n", " ")[:900]
        print(f"::error::{msg}", flush=True)
        traceback.print_exc()
        sys.exit(1)
