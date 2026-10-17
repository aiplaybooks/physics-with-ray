"""Bir autopilot döngüsü: slot vakti geldiyse kuyruktaki sıradaki videoyu IG + FB'ye yayınla.

python src/run.py              # normal (GitHub Actions her 30 dk çalıştırır)
python src/run.py --dry-run    # ne yapacağını yazar, yayınlamaz
python src/run.py --force      # slot beklemeden sıradakini şimdi yayınla
python src/run.py --only ig    # tek ağ
python src/run.py --item ID    # kuyruktaki belirli videoyu şimdi yayınla (Telegram "Yayınla" düğmesi)
python src/run.py --preview    # sıradaki video için Telegram onay önizlemesini şimdi gönder
"""
import sys as _s
_s.stdout.reconfigure(encoding='utf-8', errors='replace')
import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, "queue")
QFILE = os.path.join(QDIR, "queue.json")
POSTS = os.path.join(ROOT, "state", "posts.json")
PREVIEW = os.path.join(ROOT, "state", "preview.json")
MAX_TRIES = 3


def load_env():
    """Yerelde çalıştırırken .env'yi oku (Actions'ta secrets zaten ortamda)."""
    p = os.path.join(ROOT, ".env")
    if not os.path.exists(p):
        return
    for line in open(p, encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            if not v.startswith("<"):
                os.environ.setdefault(k.strip(), v.strip())
    if os.environ.get("GITHUB_REPO"):
        os.environ.setdefault("GITHUB_REPOSITORY", os.environ["GITHUB_REPO"])


def jload(p, default):
    return json.load(open(p, encoding="utf8")) if os.path.exists(p) else default


def jsave(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def build_caption(item, cfg):
    c = cfg["caption"]
    core = c["tags_core"]
    rot = c["tags_rotating"]
    k = max(0, c["tags_per_post"] - len(core) - len(item.get("tags", [])))
    start = (item["order"] * 3) % max(1, len(rot))
    picked = [rot[(start + i) % len(rot)] for i in range(min(k, len(rot)))]
    tags = list(dict.fromkeys(core + item.get("tags", []) + picked))
    return f"{item['hook']}\n\n{item['body']}\n\n{c['outro']}\n\n{' '.join(tags)}"


def first_comment(item, cfg):
    pool = cfg["first_comment"]
    return item.get("first_comment") or pool[item["order"] % len(pool)]


def pending(q):
    return [i for i in q if (not i.get("ig_id") or not i.get("fb_id")) and i.get("tries", 0) < MAX_TRIES
            and not i.get("skipped") and os.path.exists(os.path.join(QDIR, i["file"]))]


def due_slot(cfg, posts, now):
    used = {p.get("slot") for p in posts}
    for day in (now.date() - dt.timedelta(days=1), now.date()):
        for s in sorted(cfg["slots_utc"]):
            h, m = map(int, s.split(":"))
            t = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=dt.timezone.utc)
            key = t.strftime("%Y-%m-%d %H:%M")
            if key not in used and t <= now <= t + dt.timedelta(hours=cfg.get("catchup_hours", 3)):
                return key
    return None


def slot_dt(key):
    return dt.datetime.strptime(key, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)


def upcoming_slot(cfg, posts, now):
    """Bir sonraki (henüz kullanılmamış) slot: (anahtar, datetime) ya da None."""
    used = {p.get("slot") for p in posts}
    for day in (now.date(), now.date() + dt.timedelta(days=1)):
        for s in sorted(cfg["slots_utc"]):
            h, m = map(int, s.split(":"))
            t = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=dt.timezone.utc)
            key = t.strftime("%Y-%m-%d %H:%M")
            if t > now and key not in used:
                return key, t
    return None


def send_preview(item, cfg, nxt):
    """Telegram'a onay önizlemesi gönder (kapak, video, caption, ilk yorum, saat + düğmeler)."""
    import notify
    key, t = nxt
    mp4 = os.path.join(QDIR, item["file"])
    cover = os.path.join(QDIR, item["cover"]) if item.get("cover") and os.path.exists(os.path.join(QDIR, item["cover"])) else None
    tr = t + dt.timedelta(hours=3)
    body = (f"Caption:\n{build_caption(item, cfg)}\n\n💬 İlk yorum: {first_comment(item, cfg)}\n\n"
            f"🤖 Otopilot onaylayacak: {tr:%d.%m %H:%M}'de IG + FB'ye yayınlanacak. "
            f"Müdahale etmezsen o saatte kendiliğinden çıkar.")
    notify.preview(item["id"], mp4, cover, item["hook"], body)
    jsave(PREVIEW, {"item": item["id"], "slot": key, "status": "pending"})


def maybe_preview(cfg, item, posts, now, dry):
    ap = cfg.get("approval", {})
    if not ap.get("enabled") or item.get("ig_id") or item.get("fb_id"):
        return
    nxt = upcoming_slot(cfg, posts, now)
    if not nxt or nxt[1] - now > dt.timedelta(minutes=ap.get("lead_minutes", 60)):
        return
    cur = jload(PREVIEW, {})
    if cur.get("item") == item["id"] and cur.get("slot") == nxt[0]:
        return
    if dry:
        print("önizleme gönderilecek:", item["id"], nxt[0])
        return
    send_preview(item, cfg, nxt)


def held_for_revision(item):
    cur = jload(PREVIEW, {})
    return cur.get("item") == item["id"] and cur.get("status") == "revise"


def post_item(item, cfg, networks, dry):
    import notify
    import publish
    mp4 = os.path.join(QDIR, item["file"])
    cover = os.path.join(QDIR, item["cover"]) if item.get("cover") and os.path.exists(os.path.join(QDIR, item["cover"])) else None
    cap = build_caption(item, cfg)
    fc = first_comment(item, cfg)
    print(f"--> {item['file']}\n{cap}\nfirst comment: {fc}")
    if dry:
        return
    jobs = []
    if networks.get("ig") and not item.get("ig_id"):
        jobs.append(("ig", lambda: publish.ig_reel(mp4, cap, cover), publish.ig_comment))
    if networks.get("fb") and not item.get("fb_id"):
        jobs.append(("fb", lambda: publish.fb_reel(mp4, cap), publish.fb_comment))
    for net, fn, cm in jobs:
        for attempt in (1, 2):  # Meta geçici hata verebilir: bir kez daha dene
            try:
                item[net + "_id"] = fn()
                item.pop(net + "_error", None)
                break
            except Exception as e:
                traceback.print_exc()
                item[net + "_error"] = str(e)[:300]
                if attempt == 1:
                    time.sleep(30)
        else:
            item["tries"] = item.get("tries", 0) + 1
        if item.get(net + "_id"):
            time.sleep(5)
            try:
                cm(item[net + "_id"], fc)
            except Exception as e:
                print(net, "ilk yorum:", e)
    ok = [n for n in ("ig", "fb") if item.get(n + "_id")]
    lines = [("🎉 Paylaşıldı" if ok else "⚠️ Paylaşılamadı") + "\n" + item["hook"]]
    if item.get("ig_id"):
        lines.append(f"• ig_reel: {publish.ig_link(item['ig_id']) or item['ig_id']}")
    if item.get("fb_id"):
        lines.append(f"• fb_reel: {publish.fb_link(item['fb_id'])}")
    for net in ("ig", "fb"):
        if not item.get(net + "_id") and item.get(net + "_error"):
            lines.append(f"• {net}_reel: ❌ {item[net + '_error'][:160]}")
    notify.text("\n".join(lines))


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", choices=["ig", "fb"])
    ap.add_argument("--item")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    cfg = jload(os.path.join(ROOT, "config", "strategy.json"), {})
    networks = dict(cfg.get("networks", {"ig": True, "fb": True}))
    if a.only:
        networks = {n: n == a.only for n in ("ig", "fb")}
    q = jload(QFILE, [])
    posts = jload(POSTS, [])
    now = dt.datetime.now(dt.timezone.utc)
    pend = pending(q)
    if not pend:
        import notify
        print("kuyruk boş")
        if not a.dry_run and now.hour == 12 and now.minute < 30:
            notify.text("⚠️ Kuyruk boş: yeni video ekle (tools/enqueue.py).")
        return
    if a.preview:
        nxt = upcoming_slot(cfg, posts, now)
        if not nxt:
            sys.exit("yaklaşan slot yok")
        send_preview(pend[0], cfg, nxt)
        print("önizleme gönderildi:", pend[0]["id"], nxt[0])
        return
    # 1) yarım kalan (bir ağa gitmiş, diğerine gitmemiş) video: eksik ağı tamamla, slot harcama
    partial = [i for i in pend if i.get("ig_id") or i.get("fb_id")]
    if a.item:
        match = [i for i in pend if i["id"] == a.item]
        if not match:
            sys.exit("bekleyen öğe bulunamadı: " + a.item)
        item, slot = match[0], "force"
    elif partial:
        item, slot = partial[0], None
    else:
        item = pend[0]
        slot = "force" if a.force else due_slot(cfg, posts, now)
        if not slot:
            maybe_preview(cfg, item, posts, now, a.dry_run)
            print("slot vakti değil; sıradaki:", item["file"], "| bekleyen:", len(pend))
            return
        if not a.force and held_for_revision(item):
            print("revize bekleniyor, yayın askıda:", item["id"])
            return
    post_item(item, cfg, networks, a.dry_run)
    if a.dry_run:
        return
    if os.path.exists(PREVIEW):
        os.remove(PREVIEW)
    if item.get("ig_id") or item.get("fb_id"):
        item.setdefault("slot", slot if slot != "force" else now.strftime("%Y-%m-%d %H:%M"))
    done = all(item.get(n + "_id") for n, on in networks.items() if on)
    if done:
        rec = {k: v for k, v in item.items() if k not in ("file", "cover")}
        rec["posted_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        posts.append(rec)
        q.remove(item)
        for f in (item["file"], item.get("cover")):
            if f:
                try:
                    os.remove(os.path.join(QDIR, f))
                except OSError:
                    pass
    jsave(QFILE, q)
    jsave(POSTS, posts)
    if not any(i for i in pending(q)):
        import notify
        notify.text("⚠️ Kuyrukta bekleyen video kalmadı.")
    if not done and not any(item.get(n + "_id") for n in ("ig", "fb")):
        sys.exit("yayın başarısız")


if __name__ == "__main__":
    main()
