"""Sahibine Telegram bildirimi. TELEGRAM_TOKEN/TELEGRAM_CHAT_ID yoksa sessizce hiçbir şey yapmaz."""
import os

import requests


def enabled():
    return bool(os.environ.get("TELEGRAM_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))


def _api(method):
    return f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/{method}"


def text(msg):
    if not enabled():
        return
    try:
        requests.post(_api("sendMessage"), data={"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": msg[:4000],
                                                  "disable_web_page_preview": "true"}, timeout=30)
    except requests.RequestException as e:
        print("telegram:", e)
