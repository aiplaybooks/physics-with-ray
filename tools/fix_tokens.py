"""Explorer'dan alınan kısa ömürlü FB USER token'ını süresiz PAGE token'a çevirip .env'yi günceller (değerleri yazdırmaz).

Önce .env'de FB_APP_ID, FB_APP_SECRET ve FB_PAGE_TOKEN (= Explorer'dan alınan user token) dolu olmalı.
python tools/fix_tokens.py [sayfa adının bir parçası]
Ayrıca IG_USER_ID'yi Instagram token'ının döndürdüğü gerçek kullanıcı id'siyle düzeltir.
"""
import os
import re
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(ROOT, ".env")
V = "v23.0"


def load():
    e = {}
    for line in open(ENV, encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip().strip("\"'")
    return e


def put(k, v):
    s = open(ENV, encoding="utf8").read()
    s, n = re.subn(rf"(?m)^{k}=.*$", lambda m: f"{k}={v}", s)
    if not n:
        s += f"\n{k}={v}\n"
    open(ENV, "w", encoding="utf8").write(s)


def main():
    e = load()
    r = requests.get(f"https://graph.instagram.com/{V}/me", params={"fields": "user_id", "access_token": e["IG_TOKEN"]}, timeout=30).json()
    if r.get("user_id"):
        put("IG_USER_ID", r["user_id"])
        print("IG_USER_ID güncellendi")
    for k in ("FB_APP_ID", "FB_APP_SECRET"):
        if not e.get(k) or e[k].startswith("<"):
            sys.exit(f"{k} .env'de boş. Uygulama ayarları > Basic sayfasından doldur.")
    r = requests.get(f"https://graph.facebook.com/{V}/oauth/access_token", params={
        "grant_type": "fb_exchange_token", "client_id": e["FB_APP_ID"], "client_secret": e["FB_APP_SECRET"],
        "fb_exchange_token": e["FB_PAGE_TOKEN"]}, timeout=30).json()
    if "access_token" not in r:
        sys.exit("Long-lived dönüşüm başarısız: " + str(r.get("error", {}).get("message")))
    pages = requests.get(f"https://graph.facebook.com/{V}/me/accounts", params={"access_token": r["access_token"], "limit": 100}, timeout=30).json().get("data", [])
    if not pages:  # Business portfolio sayfalarında /me/accounts boş gelebilir: izin verilen sayfa id'sini doğrudan sorgula
        dbg = requests.get(f"https://graph.facebook.com/{V}/debug_token", params={"input_token": r["access_token"], "access_token": r["access_token"]}, timeout=30).json()
        ids = {i for s in dbg.get("data", {}).get("granular_scopes", []) if s["scope"] == "pages_manage_posts" for i in s.get("target_ids", [])}
        for pid in ids:
            p = requests.get(f"https://graph.facebook.com/{V}/{pid}", params={"fields": "name,access_token", "access_token": r["access_token"]}, timeout=30).json()
            if p.get("access_token"):
                pages.append({"id": pid, "name": p.get("name", pid), "access_token": p["access_token"]})
    print("Sayfalar:", [(p["name"], p["id"]) for p in pages])
    want = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    pick = [p for p in pages if want in p["name"].lower()]
    if len(pick) != 1:
        sys.exit("Tek bir sayfa seçilemedi; sayfa adının bir parçasını argüman olarak ver.")
    put("FB_PAGE_ID", pick[0]["id"])
    put("FB_PAGE_TOKEN", pick[0]["access_token"])
    print("Seçilen sayfa:", pick[0]["name"], "-> FB_PAGE_ID ve FB_PAGE_TOKEN (süresiz) .env'ye yazıldı")


if __name__ == "__main__":
    main()
