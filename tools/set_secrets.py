"""Yerel .env'deki gerçek değerleri GitHub Actions secrets'a yükler ('<' ile başlayan yer tutucuları atlar).

python tools/set_secrets.py        # gh CLI giriş yapmış olmalı
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEYS = ["IG_USER_ID", "IG_TOKEN", "FB_PAGE_ID", "FB_PAGE_TOKEN", "YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID", "CLAUDE_CODE_OAUTH_TOKEN"]


def main():
    env = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    repo = env.get("GITHUB_REPO")
    if not repo:
        sys.exit("GITHUB_REPO .env'de yok")
    for k in SECRET_KEYS:
        v = env.get(k, "")
        if not v or v.startswith("<"):
            print("atlandı (yer tutucu):", k)
            continue
        subprocess.run(["gh", "secret", "set", k, "-R", repo], input=v, text=True, check=True)
        print("yüklendi:", k)


if __name__ == "__main__":
    main()
