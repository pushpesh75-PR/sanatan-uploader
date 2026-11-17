"""Set privacyStatus for ids in changes/setprivacy.txt (one line: "<id> <private|unlisted|public>").
Does not touch publishAt. For QC use (e.g. temporarily unlisted to let yt-dlp fetch), revert after."""
from uploader import service, retry
yt = service()
for line in [l.strip() for l in open("changes/setprivacy.txt") if l.strip()]:
    vid, status = line.split()
    try:
        retry(lambda: yt.videos().update(part="status", body={"id": vid, "status": {"privacyStatus": status,
              "selfDeclaredMadeForKids": False, "embeddable": True, "license": "youtube", "containsSyntheticMedia": True}}).execute())
        r = retry(lambda: yt.videos().list(part="status", id=vid).execute())["items"][0]["status"]
        print("ok", vid, r.get("privacyStatus"))
    except Exception as e:
        print(f"::error::{vid}: {str(e)[:200]}")
