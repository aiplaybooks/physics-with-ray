"""YouTube zamanlayıcı: Video 2-23'ü yükler, yayın saatlerini YouTube içinde zamanlar (günde 2: 04:00 ve 22:00 TR) ve yayına
giren videolara ilk yorumu atar. GitHub Actions her 30 dk çalıştırır (.github/workflows/yt.yml); elle de çalışır.

python tools/yt_schedule.py --dry    # planı yazdırır
python tools/yt_schedule.py          # yüklenebilenleri yükler, yayına girenlere yorum atar

YouTube günlük yükleme limiti ya da API kotası dolarsa yüklemeler durur, birkaç saat sonra otomatik denenir.
Slot geçmişte kalan video, bir sonraki boş slota (04:00/22:40 TR) kaydırılır. İlerleme state/yt_schedule.json'da.
"""
import argparse
import datetime as dt
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import publish  # noqa: E402
import run  # noqa: E402

STATE = os.path.join(ROOT, "state", "yt_schedule.json")
V = os.path.join(ROOT, "vector", "cikti")
K = os.path.join(V, "kapak")
SLOTS_UTC = [(1, 0), (19, 0)]  # 04:00 ve 22:00 TR
FMT = "%Y-%m-%dT%H:%M:%SZ"
RETRY_HOURS = 6
MIN_LEAD = dt.timedelta(minutes=20)
OLD = {  # IG/FB'ye yayınlanıp kuyruktan çıkmış videolar: id -> (mp4, kapak), yerel dosyalar
    "01_video2_projectile": ("video2_projectile.mp4", "kapak_video2_aci.png"),
    "02_video3_inertia": ("video3_inertia.mp4", "kapak_video3_atalet.png"),
    "03_video4_second_law": ("video4_second_law.mp4", "kapak_video4_ikinci_yasa.png"),
    "04_video5_third_law": ("video5_third_law.mp4", "kapak_video5_ucuncu_yasa.png"),
}
TITLE = {"01_video2_projectile": "Which launch angle sends a ball the farthest? 🎯"}


def now_utc():
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


def items():
    """Zamanlanacak tüm videolar, video numarası sırasıyla."""
    posts = {p["id"]: p for p in run.jload(run.POSTS, [])}
    q = {i["id"]: i for i in run.jload(run.QFILE, [])}
    out = []
    for iid, it in {**posts, **q}.items():
        it = dict(it)
        if iid in OLD:
            it["mp4"], it["cover"] = os.path.join(V, OLD[iid][0]), os.path.join(K, OLD[iid][1])
        else:
            it["mp4"] = os.path.join(run.QDIR, f"{iid}.mp4")
            it["cover"] = os.path.join(run.QDIR, f"{iid}.png")
        if iid in TITLE:
            it["hook"] = TITLE[iid]
        out.append(it)
    return sorted(out, key=lambda x: x["order"])


def next_slot(after):
    day = after.date()
    while True:
        for h, m in SLOTS_UTC:
            t = dt.datetime(day.year, day.month, day.day, h, m)
            if t > after:
                return t
        day += dt.timedelta(days=1)


def upload_all(its, st, cfg, dry):
    pl = cfg.get("yt", {}).get("playlist_id")
    meta = st.setdefault("_meta", {})
    last = max([dt.datetime.strptime(v["publish_at"], FMT) for k, v in st.items() if k != "_meta" and v.get("video_id")],
               default=dt.datetime(2000, 1, 1))
    blocked = meta.get("upload_after") and dt.datetime.strptime(meta["upload_after"], FMT) > now_utc()
    for n, it in enumerate(its, 1):
        e = st.get(it["id"], {})
        if e.get("done"):
            continue
        title, desc, tags = run.yt_meta(it, cfg)
        if blocked or dry or not os.path.exists(it["mp4"]):
            why = "bloklu" if blocked else "dosya yok" if not os.path.exists(it["mp4"]) else "bekliyor"
            print(f"{n:2d}. {it['id']:28s} {why}  {title}")
            continue
        if "video_id" not in e:
            e = st[it["id"]] = {"publish_at": next_slot(max(last, now_utc() + MIN_LEAD) if last > now_utc() else now_utc() + MIN_LEAD).strftime(FMT), "steps": []}
        try:
            if "video_id" not in e:
                e["video_id"] = publish.yt_short(it["mp4"], title, desc, tags, publish_at=e["publish_at"])
                run.jsave(STATE, st)
            last = max(last, dt.datetime.strptime(e["publish_at"], FMT))
            vid = e["video_id"]
            for name, fn in (("thumb", lambda: publish.yt_thumbnail(vid, it["cover"])),
                             ("playlist", lambda: pl and publish.yt_playlist_add(vid, pl))):
                if name not in e["steps"]:
                    fn()
                    e["steps"].append(name)
                    run.jsave(STATE, st)
            e["done"] = True
            run.jsave(STATE, st)
            print(f"{n:2d}. yüklendi {publish.yt_link(vid)}  yayın {e['publish_at']} UTC")
            if it["id"] not in {i["id"] for i in run.jload(run.QFILE, [])}:  # IG/FB'de de bitmiş: artık gereksiz dosyalar
                for f in (it["mp4"], it["cover"]):
                    if os.path.exists(f) and os.path.dirname(f) == run.QDIR:
                        os.remove(f)
        except RuntimeError as ex:
            msg = str(ex)
            print(f"{n:2d}. DURDU: {msg[:200]}")
            if "uploadLimitExceeded" in msg or "quota" in msg.lower():
                meta["upload_after"] = (now_utc() + dt.timedelta(hours=RETRY_HOURS)).strftime(FMT)
                print(f"    {RETRY_HOURS} saat sonra tekrar denenecek")
            run.jsave(STATE, st)
            return


def comment_all(its, st, cfg, dry):
    import requests
    for it in its:
        e = st.get(it["id"], {})
        if not e.get("done") or e.get("commented") or e.get("comment_tries", 0) >= 3:
            continue
        if dt.datetime.strptime(e["publish_at"], FMT) + dt.timedelta(minutes=2) > now_utc():
            continue
        r = requests.get(f"{publish.YT}/videos", params={"part": "status", "id": e["video_id"]},
                         headers={"Authorization": f"Bearer {publish._yt_token()}"})
        its_ = r.json().get("items", []) if r.status_code < 400 else []
        if not its_ or its_[0]["status"]["privacyStatus"] != "public":
            print("henüz yayında değil:", it["id"])
            continue
        if dry:
            print("yorum atılacak:", it["id"])
            continue
        try:
            publish.yt_comment(e["video_id"], run.comment_text(run.first_comment(it, cfg), cfg, "yt"))
            e["commented"] = True
            print("yorum atıldı:", it["id"])
        except RuntimeError as ex:
            e["comment_tries"] = e.get("comment_tries", 0) + 1
            print("yorum hatası:", it["id"], str(ex)[:200])
        run.jsave(STATE, st)


def main():
    run.load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    cfg = run.jload(os.path.join(ROOT, "config", "strategy.json"), {})
    st = run.jload(STATE, {})
    its = [i for i in items() if i["id"] in st or i["id"] in OLD or i["order"] <= cfg.get("yt", {}).get("backfill_max_order", 0)]
    upload_all(its, st, cfg, a.dry)
    comment_all(its, st, cfg, a.dry)
    if not a.dry:
        run.jsave(STATE, st)


if __name__ == "__main__":
    main()
