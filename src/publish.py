"""Bir MP4'ü Instagram Reel (+kapak), Facebook Sayfası Reel ve YouTube Shorts olarak yayınlar.

Instagram videoyu/kapağı URL'den çeker: dosyalar repodaki herkese açık 'media' release'ine geçici yüklenir, iş bitince silinir.
"""
import os
import subprocess
import time

import requests

V = "v23.0"
IG = f"https://graph.instagram.com/{V}"
FB = f"https://graph.facebook.com/{V}"


def _check(r):
    if r.status_code >= 400:
        raise RuntimeError(f"{r.request.method} {r.url.split('?')[0]} -> {r.status_code}: {r.text[:400]}")
    return r.json()


def _repo():
    return os.environ["GITHUB_REPOSITORY"]


def _release_asset(path):
    subprocess.run(["gh", "release", "upload", "media", path, "--clobber", "-R", _repo()], check=True)
    return f"https://github.com/{_repo()}/releases/download/media/{os.path.basename(path)}"


def _drop_asset(path):
    subprocess.run(["gh", "release", "delete-asset", "media", os.path.basename(path), "-y", "-R", _repo()])


def ig_reel(path, caption, cover=None):
    tok, uid = os.environ["IG_TOKEN"], os.environ["IG_USER_ID"]
    assets = [path] + ([cover] if cover else [])
    try:
        data = {"media_type": "REELS", "video_url": _release_asset(path), "caption": caption,
                "share_to_feed": "true", "access_token": tok}
        if cover:
            data["cover_url"] = _release_asset(cover)
        cid = _check(requests.post(f"{IG}/{uid}/media", data=data))["id"]
        for _ in range(60):
            s = _check(requests.get(f"{IG}/{cid}", params={"fields": "status_code,status", "access_token": tok}))
            if s.get("status_code") == "FINISHED":
                break
            if s.get("status_code") == "ERROR":
                raise RuntimeError(f"IG processing error: {s}")
            time.sleep(10)
        else:
            raise RuntimeError("IG processing timeout")
        return _check(requests.post(f"{IG}/{uid}/media_publish", data={"creation_id": cid, "access_token": tok}))["id"]
    finally:
        for a in assets:
            _drop_asset(a)


def fb_reel(path, description, cover=None):
    tok, pid = os.environ["FB_PAGE_TOKEN"], os.environ["FB_PAGE_ID"]
    st = _check(requests.post(f"{FB}/{pid}/video_reels", data={"upload_phase": "start", "access_token": tok}))
    vid = st["video_id"]
    with open(path, "rb") as f:
        _check(requests.post(st.get("upload_url") or f"https://rupload.facebook.com/video-upload/{V}/{vid}", data=f, headers={
            "Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(os.path.getsize(path))}))
    _check(requests.post(f"{FB}/{pid}/video_reels", data={
        "upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED", "description": description, "access_token": tok}))
    if cover:
        fb_cover(vid, cover)
    return vid


def fb_cover(video_id, cover, tries=8):
    """Reel işlendikten sonra kapağı tercih edilen küçük resim yapar. Başarısızlık yayını bozmaz, sadece yazdırılır."""
    tok = os.environ["FB_PAGE_TOKEN"]
    for i in range(tries):
        time.sleep(15)
        with open(cover, "rb") as f:
            r = requests.post(f"{FB}/{video_id}/thumbnails", data={"is_preferred": "true", "access_token": tok}, files={"source": f})
        if r.status_code < 400:
            print("fb kapak ayarlandı:", video_id)
            return True
        print(f"fb kapak deneme {i + 1}/{tries}: {r.status_code} {r.text[:200]}")
    return False


def _yt_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
    return _check(r)["access_token"]


YT = "https://www.googleapis.com/youtube/v3"


def yt_fields(title, description, tags=(), privacy="public", publish_at=None):
    """Kanal ayarları: Education, English, ABD, yapay zekâ içeriği evet, ücretli tanıtım yok."""
    meta = {"snippet": {"title": title[:100], "description": description[:4900], "tags": list(tags), "categoryId": "27",
                        "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False, "embeddable": True, "publicStatsViewable": True,
                       "license": "youtube", "containsSyntheticMedia": True,
                       "paidProductPlacementDetails": {"hasPaidProductPlacement": False}},
            "recordingDetails": {"location": {"latitude": 39.8283, "longitude": -98.5795}, "locationDescription": "United States"}}
    if publish_at:
        meta["status"]["privacyStatus"] = "private"
        meta["status"]["publishAt"] = publish_at
    return meta


def yt_short(path, title, description, tags=(), privacy="public", publish_at=None):
    """YouTube Shorts yükler (resumable upload). Dönen değer video id."""
    auth = {"Authorization": f"Bearer {_yt_token()}"}
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status,recordingDetails",
                      headers={**auth, "X-Upload-Content-Type": "video/mp4",
                               "X-Upload-Content-Length": str(os.path.getsize(path))},
                      json=yt_fields(title, description, tags, privacy, publish_at))
    if r.status_code >= 400:
        raise RuntimeError(f"YT init -> {r.status_code}: {r.text[:400]}")
    with open(path, "rb") as f:
        up = requests.put(r.headers["Location"], data=f, headers={**auth, "Content-Type": "video/mp4"}, timeout=600)
    return _check(up)["id"]


def yt_thumbnail(video_id, cover):
    with open(cover, "rb") as f:
        return _check(requests.post(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}",
                                    headers={"Authorization": f"Bearer {_yt_token()}", "Content-Type": "image/png"}, data=f))


def yt_playlist_create(title, description=""):
    body = {"snippet": {"title": title, "description": description}, "status": {"privacyStatus": "public"}}
    return _check(requests.post(f"{YT}/playlists?part=snippet,status", headers={"Authorization": f"Bearer {_yt_token()}"}, json=body))["id"]


def yt_playlist_add(video_id, playlist_id):
    body = {"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}
    return _check(requests.post(f"{YT}/playlistItems?part=snippet", headers={"Authorization": f"Bearer {_yt_token()}"}, json=body))["id"]


def yt_comment(video_id, message):
    body = {"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": message}}}}
    return _check(requests.post("https://www.googleapis.com/youtube/v3/commentThreads?part=snippet",
                                headers={"Authorization": f"Bearer {_yt_token()}"}, json=body))["id"]


def yt_link(video_id):
    return f"https://www.youtube.com/shorts/{video_id}"


def ig_comment(media_id, message):
    return _check(requests.post(f"{IG}/{media_id}/comments", data={"message": message, "access_token": os.environ["IG_TOKEN"]}))["id"]


def fb_comment(video_id, message):
    return _check(requests.post(f"{FB}/{video_id}/comments", data={"message": message, "access_token": os.environ["FB_PAGE_TOKEN"]}))["id"]


def ig_link(media_id):
    """Reel'in herkese açık bağlantısı (alınamazsa None)."""
    try:
        return requests.get(f"{IG}/{media_id}", params={"fields": "permalink", "access_token": os.environ["IG_TOKEN"]}, timeout=30).json().get("permalink")
    except requests.RequestException:
        return None


def fb_link(video_id):
    return f"https://www.facebook.com/reel/{video_id}"
