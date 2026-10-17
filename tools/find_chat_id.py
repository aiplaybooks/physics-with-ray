"""Bota yazdığın mesajdan senin chat id'ni bulup .env'ye yazar (token yazdırılmaz).

Önce Telegram'da botuna bir mesaj yaz (/start), sonra:
python tools/find_chat_id.py
"""
import os
import re

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(ROOT, ".env")


def main():
    tok = ""
    for line in open(ENV, encoding="utf8"):
        if line.startswith("TELEGRAM_TOKEN="):
            tok = line.split("=", 1)[1].strip().strip("\"'")
    r = requests.get(f"https://api.telegram.org/bot{tok}/getUpdates", timeout=30).json()
    if not r.get("ok"):
        print("Token geçersiz görünüyor:", r.get("description"), "- BotFather'dan aldığın token'ı TELEGRAM_TOKEN'a tam yapıştır (iki nokta üst üste dahil, boşluksuz).")
        return
    chats = {}
    for u in r.get("result", []):
        m = u.get("message") or u.get("channel_post") or {}
        c = m.get("chat")
        if c and c.get("type") == "private":
            chats[c["id"]] = c.get("first_name") or c.get("username") or ""
    if not chats:
        print("Henüz mesaj yok: Telegram'da botuna /start yaz ve tekrar çalıştır.")
        return
    cid, name = list(chats.items())[-1]
    s = open(ENV, encoding="utf8").read()
    s = re.sub(r"(?m)^TELEGRAM_CHAT_ID=.*$", f"TELEGRAM_CHAT_ID={cid}", s)
    open(ENV, "w", encoding="utf8").write(s)
    print(f"TELEGRAM_CHAT_ID .env'ye yazıldı ({name}, {len(str(cid))} haneli id)")


if __name__ == "__main__":
    main()
