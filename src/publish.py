"""Bir MP4'ü Instagram Reel (+kapak) ve Facebook Sayfası Reel olarak yayınlar.

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


def fb_reel(path, description):
    tok, pid = os.environ["FB_PAGE_TOKEN"], os.environ["FB_PAGE_ID"]
    st = _check(requests.post(f"{FB}/{pid}/video_reels", data={"upload_phase": "start", "access_token": tok}))
    vid = st["video_id"]
    with open(path, "rb") as f:
        _check(requests.post(st.get("upload_url") or f"https://rupload.facebook.com/video-upload/{V}/{vid}", data=f, headers={
            "Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(os.path.getsize(path))}))
    _check(requests.post(f"{FB}/{pid}/video_reels", data={
        "upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED", "description": description, "access_token": tok}))
    return vid


def ig_comment(media_id, message):
    return _check(requests.post(f"{IG}/{media_id}/comments", data={"message": message, "access_token": os.environ["IG_TOKEN"]}))["id"]


def fb_comment(video_id, message):
    return _check(requests.post(f"{FB}/{video_id}/comments", data={"message": message, "access_token": os.environ["FB_PAGE_TOKEN"]}))["id"]
