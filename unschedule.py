"""Cancel scheduled publishing (keep private, remove publishAt) for ids in changes/unschedule.txt. Nothing is deleted."""
from uploader import service, retry
yt = service()
for vid in [l.strip() for l in open("changes/unschedule.txt") if l.strip()]:
    try:
        retry(lambda: yt.videos().update(part="status", body={"id": vid, "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
              "embeddable": True, "license": "youtube", "containsSyntheticMedia": True}}).execute())
        r = retry(lambda: yt.videos().list(part="status", id=vid).execute())["items"][0]["status"]
        print("ok", vid, r.get("privacyStatus"), r.get("publishAt"))
    except Exception as e:
        print(f"::error::{vid}: {str(e)[:200]}")
