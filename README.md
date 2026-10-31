# Sanatan Beats — YouTube auto-uploader

Claude pushes each batch to a branch `upload/<name>` containing `batch/manifest.json`, thumbnails and the
videos split into parts under 95 MB (`video.mp4.part000`, `.part001` …).
The push starts `.github/workflows/upload.yml`: it joins the parts, uploads every video as private +
scheduled (`publishAt`), sets thumbnail, playlists and a comment, saves the video IDs in `uploaded/<name>.json`
on `main`, and deletes the upload branch.

Secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (scope `youtube.force-ssl`).
If the secrets are missing the run only warns and leaves the branch, so it can be re-run later
(Actions → Upload to YouTube → Run workflow → branch).
