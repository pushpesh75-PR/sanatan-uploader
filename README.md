# Sanatan Beats — YouTube auto-uploader

A GitHub release holds the finished videos, thumbnails and `manifest.json`.
Publishing the release starts `.github/workflows/upload.yml`, which uploads each item to YouTube
as private + scheduled (`publishAt`), sets thumbnail, playlists and a comment, and records the video IDs in `uploaded/<tag>.json`.

Secrets needed: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (scope `youtube.force-ssl`).
Manual re-run: Actions → Upload to YouTube → Run workflow → tag (dry_run = 1 only checks).
