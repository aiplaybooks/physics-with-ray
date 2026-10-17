"""Telegram bildirimini dener: botun sohbetine test mesajı yollar (token yazdırılmaz).

python tools/test_telegram.py
"""
import os

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    e = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip("\"'")
    r = requests.post(f"https://api.telegram.org/bot{e['TELEGRAM_TOKEN']}/sendMessage",
                      data={"chat_id": e["TELEGRAM_CHAT_ID"], "text": "✅ Physics with Ray autopilot: Telegram bildirimi çalışıyor."}, timeout=30)
    print(r.status_code, r.json().get("description", "mesaj gönderildi"))


if __name__ == "__main__":
    main()
