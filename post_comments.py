"""Post top-level comments: changes/comments.json = [{"id": videoId, "text": "..."}]"""
import json
from uploader import service, retry
yt = service()
for c in json.load(open("changes/comments.json", encoding="utf-8")):
    try:
        retry(lambda: yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": c["id"], "topLevelComment": {"snippet": {"textOriginal": c["text"]}}}}).execute())
        print("ok", c["id"])
    except Exception as e:
        print(f"::error::comment {c['id']} failed: {str(e)[:200]}")
