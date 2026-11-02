"""Read-only: save every video of the channel (title, description, tags, status, views) to channel/videos.json."""
import json, os
from uploader import service, retry


def main():
    yt = service()
    ch = retry(lambda: yt.channels().list(part="snippet,contentDetails,statistics", mine=True).execute())["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        r = retry(lambda: yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=page).execute())
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        page = r.get("nextPageToken")
        if not page:
            break
    vids = []
    for i in range(0, len(ids), 50):
        r = retry(lambda: yt.videos().list(part="snippet,status,statistics,contentDetails,recordingDetails",
                                           id=",".join(ids[i:i + 50])).execute())
        for v in r.get("items", []):
            sn, st = v["snippet"], v["status"]
            vids.append({"id": v["id"], "title": sn["title"], "description": sn.get("description", ""),
                         "tags": sn.get("tags", []), "categoryId": sn.get("categoryId"),
                         "defaultLanguage": sn.get("defaultLanguage"), "defaultAudioLanguage": sn.get("defaultAudioLanguage"),
                         "publishedAt": sn.get("publishedAt"), "privacy": st.get("privacyStatus"), "publishAt": st.get("publishAt"),
                         "duration": v["contentDetails"].get("duration"),
                         "views": int(v.get("statistics", {}).get("viewCount", 0)),
                         "likes": int(v.get("statistics", {}).get("likeCount", 0)),
                         "location": v.get("recordingDetails", {}).get("locationDescription")})
    pls, page = [], None
    while True:
        r = retry(lambda: yt.playlists().list(part="snippet,contentDetails,status", mine=True, maxResults=50, pageToken=page).execute())
        pls += [{"id": p["id"], "title": p["snippet"]["title"], "description": p["snippet"].get("description", ""),
                 "count": p["contentDetails"]["itemCount"], "privacy": p["status"]["privacyStatus"]} for p in r.get("items", [])]
        page = r.get("nextPageToken")
        if not page:
            break
    full = retry(lambda: yt.channels().list(part="snippet,statistics,brandingSettings,status,topicDetails", mine=True).execute())["items"][0]
    os.makedirs("channel", exist_ok=True)
    json.dump({"channel": full, "playlists": pls}, open("channel/channel.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"channel": ch["snippet"]["title"], "subscribers": ch["statistics"].get("subscriberCount"),
               "videos": vids}, open("channel/videos.json", "w"), ensure_ascii=False, indent=1)
    print(f"saved {len(vids)} videos")


if __name__ == "__main__":
    main()
