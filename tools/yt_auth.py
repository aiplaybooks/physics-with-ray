"""YouTube için tek seferlik yetkilendirme: tarayıcıda izin ver, refresh token'ı .env'ye yazar.

python tools/yt_auth.py client_secret.json    # Google Cloud'dan indirilen 'Masaüstü uygulaması' OAuth istemci dosyası
Sonra: python tools/set_secrets.py
"""
import json
import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]


def main():
    cs = json.load(open(sys.argv[1], encoding="utf8"))
    cs = cs.get("installed") or cs["web"]
    flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    new = {"YT_CLIENT_ID": cs["client_id"], "YT_CLIENT_SECRET": cs["client_secret"], "YT_REFRESH_TOKEN": creds.refresh_token}
    p = os.path.join(ROOT, ".env")
    lines = [l for l in open(p, encoding="utf8").read().splitlines() if l.split("=", 1)[0].strip() not in new]
    lines += [f"{k}={v}" for k, v in new.items()]
    open(p, "w", encoding="utf8").write("\n".join(lines) + "\n")
    print(".env güncellendi (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN)")


if __name__ == "__main__":
    main()
