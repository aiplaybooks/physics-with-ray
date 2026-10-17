"""Yerel .env'yi kontrol eder; token değerlerini YAZDIRMAZ (sadece dolu/boş, uzunluk ve API sonucu).

python tools/check_env.py
"""
import os

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = "v23.0"


def g(url, **p):
    try:
        r = requests.get(url, params=p, timeout=30)
        return r.status_code, r.json()
    except requests.RequestException as e:
        return 0, {"error": str(e)}


def main():
    e = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip("\"'")
    for k, v in e.items():
        print(f"{k:26}", "YER TUTUCU/BOŞ" if not v or v.startswith("<") else f"dolu ({len(v)} karakter)")
    ok = lambda k: e.get(k) and not e[k].startswith("<")
    print()
    if ok("IG_TOKEN"):
        s, d = g(f"https://graph.instagram.com/{V}/me", fields="user_id,username,account_type", access_token=e["IG_TOKEN"])
        print("IG token:", s, d if s != 200 else {**d, "env_IG_USER_ID_eşleşiyor": str(d.get("user_id")) == e.get("IG_USER_ID")})
    if ok("FB_PAGE_TOKEN"):
        s, d = g(f"https://graph.facebook.com/{V}/me", fields="id,name", access_token=e["FB_PAGE_TOKEN"])
        print("FB token:", s, d if s != 200 else {**d, "env_FB_PAGE_ID_eşleşiyor": d.get("id") == e.get("FB_PAGE_ID")})
        s, d = g(f"https://graph.facebook.com/{V}/debug_token", input_token=e["FB_PAGE_TOKEN"], access_token=e["FB_PAGE_TOKEN"])
        dd = d.get("data", {})
        print("FB token türü/süre/izinler:", dd.get("type"), dd.get("expires_at"), dd.get("scopes"))
        print("FB token granular (izin -> hedef sayfa/hesap id'leri):", dd.get("granular_scopes"))
        s, d = g(f"https://graph.facebook.com/{V}/me/accounts", access_token=e["FB_PAGE_TOKEN"])
        print("FB /me/accounts:", s, [(p.get("name"), p.get("id")) for p in d.get("data", [])], d.get("error", {}).get("message"))
        s, d = g(f"https://graph.facebook.com/{V}/me/businesses", access_token=e["FB_PAGE_TOKEN"])
        print("FB /me/businesses:", s, [(b.get("name"), b.get("id")) for b in d.get("data", [])], d.get("error", {}).get("message"))


if __name__ == "__main__":
    main()
