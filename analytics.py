"""Read-only: YouTube Analytics API v2 reports -> channel/analytics.json (needs yt-analytics.readonly in the token)."""
import json, os, datetime, re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                    client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token")
ya = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
today = datetime.date.today()
START = "2026-10-20"
END = (today - datetime.timedelta(days=0)).isoformat()
out = {"generated": datetime.datetime.utcnow().isoformat() + "Z", "range": [START, END], "reports": {}, "errors": {}}


def q(name, **kw):
    try:
        r = ya.reports().query(ids="channel==MINE", startDate=kw.pop("startDate", START), endDate=END, **kw).execute()
        out["reports"][name] = {"columns": [h["name"] for h in r.get("columnHeaders", [])], "rows": r.get("rows", [])}
    except Exception as e:
        out["errors"][name] = str(e)[:500]


BASIC = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained,subscribersLost"
q("daily", dimensions="day", metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost,likes,comments,shares", sort="day")
q("by_video", dimensions="video", metrics=BASIC, sort="-views", maxResults=200)
q("by_content_type", dimensions="creatorContentType", metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained")
q("traffic_sources", dimensions="insightTrafficSourceType", metrics="views,estimatedMinutesWatched", sort="-views")
q("traffic_by_type_and_content", dimensions="insightTrafficSourceType,creatorContentType", metrics="views", sort="-views")
q("search_terms", dimensions="insightTrafficSourceDetail", filters="insightTrafficSourceType==YT_SEARCH", metrics="views", sort="-views", maxResults=25)
q("suggested_from", dimensions="insightTrafficSourceDetail", filters="insightTrafficSourceType==RELATED_VIDEO", metrics="views", sort="-views", maxResults=25)
q("country", dimensions="country", metrics="views,estimatedMinutesWatched,averageViewDuration", sort="-views", maxResults=25)
q("age_gender", dimensions="ageGroup,gender", metrics="viewerPercentage")
q("device", dimensions="deviceType", metrics="views,estimatedMinutesWatched", sort="-views")
q("subscribed_status", dimensions="subscribedStatus", metrics="views,estimatedMinutesWatched,averageViewDuration")
q("hour_of_day_proxy", dimensions="day,creatorContentType", metrics="views", sort="day")
q("playlists", dimensions="playlist", metrics="views,estimatedMinutesWatched", sort="-views", maxResults=25)
q("sharing", dimensions="sharingService", metrics="shares", sort="-shares", maxResults=10)
# audience retention curve for every long video with views
vids = json.load(open("channel/videos.json"))["videos"] if os.path.exists("channel/videos.json") else []
def secs(x):
    m = re.match(r"P(?:\d+D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", x or "")
    return sum(int(v or 0) * k for v, k in zip(m.groups(), (3600, 60, 1))) if m else 0
for v in vids:
    if v.get("privacy") == "public" and v.get("views", 0) >= 5:
        q(f"retention_{v['id']}", dimensions="elapsedVideoTimeRatio", filters=f"video=={v['id']}",
          metrics="audienceWatchRatio,relativeRetentionPerformance")
os.makedirs("channel", exist_ok=True)
json.dump(out, open("channel/analytics.json", "w"), ensure_ascii=False, indent=1)
print("reports", len(out["reports"]), "errors", len(out["errors"]))
for k, e in out["errors"].items():
    print("ERR", k, e[:200])
