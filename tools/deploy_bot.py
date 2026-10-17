"""Telegram sohbet botunu Cloudflare Worker olarak kurar (token değerleri yazdırılmaz).

Önkoşullar (.env): TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GH_PAT (aşağıdaki rehbere bak), WEBHOOK_SECRET (rastgele uzun bir metin).
Bir kez: cd worker && npx wrangler login
Sonra:  python tools/deploy_bot.py
"""
import os
import re
import subprocess
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = os.path.join(ROOT, "worker")
NPX = "npx.cmd" if os.name == "nt" else "npx"


def main():
    e = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip("\"'")
    for k in ("TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID", "GH_PAT", "WEBHOOK_SECRET"):
        if not e.get(k) or e[k].startswith("<"):
            sys.exit(f"{k} .env'de boş.")
    toml = os.path.join(WORKER, "wrangler.toml")
    s = open(toml, encoding="utf8").read()
    open(toml, "w", encoding="utf8").write(re.sub(r'CHAT_ID = ".*"', f'CHAT_ID = "{e["TELEGRAM_CHAT_ID"]}"', s))
    for name, key in (("TG_TOKEN", "TELEGRAM_TOKEN"), ("GH_PAT", "GH_PAT"), ("WEBHOOK_SECRET", "WEBHOOK_SECRET")):
        subprocess.run([NPX, "wrangler", "secret", "put", name], cwd=WORKER, input=e[key], text=True, check=True)
    out = subprocess.run([NPX, "wrangler", "deploy"], cwd=WORKER, capture_output=True, text=True, check=True).stdout
    m = re.search(r"https://[\w.-]+\.workers\.dev", out)
    if not m:
        sys.exit("Worker URL'si bulunamadı:\n" + out[-500:])
    r = requests.post(f"https://api.telegram.org/bot{e['TELEGRAM_TOKEN']}/setWebhook",
                      data={"url": m.group(0), "secret_token": e["WEBHOOK_SECRET"], "allowed_updates": '["message"]'}, timeout=30).json()
    print("Worker:", m.group(0), "| webhook:", r.get("description"))


if __name__ == "__main__":
    main()
