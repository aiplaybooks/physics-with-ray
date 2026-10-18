"""Sahibine Telegram bildirimi. TELEGRAM_TOKEN/TELEGRAM_CHAT_ID yoksa sessizce hiçbir şey yapmaz."""
import json
import os

import requests


def enabled():
    return bool(os.environ.get("TELEGRAM_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))


def _api(method):
    return f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/{method}"


def _chat():
    return os.environ["TELEGRAM_CHAT_ID"]


def text(msg, markup=None):
    if not enabled():
        return
    data = {"chat_id": _chat(), "text": msg[:4000], "disable_web_page_preview": "true"}
    if markup:
        data["reply_markup"] = json.dumps(markup)
    try:
        requests.post(_api("sendMessage"), data=data, timeout=30)
    except requests.RequestException as e:
        print("telegram:", e)


def preview(item_id, mp4, cover, hook, body):
    """Kapak + video + (caption, ilk yorum, saat) mesajı; altında Onayla / Revize / Reddet düğmeleri."""
    if not enabled():
        return
    try:
        if cover:
            with open(cover, "rb") as f:
                requests.post(_api("sendPhoto"), data={"chat_id": _chat(), "caption": "Kapak"}, files={"photo": f}, timeout=60)
        with open(mp4, "rb") as f:
            requests.post(_api("sendVideo"), data={"chat_id": _chat(), "caption": "Reel önizleme\n" + hook[:900], "supports_streaming": "true"},
                          files={"video": f}, timeout=300)
    except requests.RequestException as e:
        print("telegram önizleme medyası:", e)
    text(body, {"inline_keyboard": [[
        {"text": "✅ Onayla", "callback_data": f"ok:{item_id}"},
        {"text": "✏️ Revize", "callback_data": f"rv:{item_id}"},
        {"text": "❌ Reddet", "callback_data": f"no:{item_id}"},
    ]]})


def remove_buttons(message_id):
    if not enabled() or not message_id:
        return
    try:
        requests.post(_api("editMessageReplyMarkup"), data={"chat_id": _chat(), "message_id": message_id,
                                                              "reply_markup": json.dumps({"inline_keyboard": []})}, timeout=30)
    except requests.RequestException as e:
        print("telegram:", e)
