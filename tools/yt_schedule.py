"""Video 2-23'ü YouTube'a yükler ve yayın saatlerini YouTube içinde zamanlar (gün 2 yayın).

python tools/yt_schedule.py --dry     # planı yazdırır
python tools/yt_schedule.py           # kota yettiği kadar yükler; kota bitince durur, yarın aynı komutla devam eder

Slotlar (Türkiye saati): 04:00 ve 22:40 = 01:00 ve 19:40 UTC. İlerleme state/yt_schedule.json'da tutulur (tekrar çalıştırmak güvenli).
Günlük API kotası 10.000 birim, bir yükleme ~1.700 birim: günde en fazla ~5 video yüklenir.
"""
import argparse
import datetime as dt
import json
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
FIRST_DAY = dt.date(2026, 10, 18)
SLOTS_UTC = ["01:00", "19:40"]  # 04:00 ve 22:40 TR
OLD = {  # kuyruktan çıkmış (IG/FB'de yayınlanmış) videolar: id -> (mp4, kapak)
    "01_video2_projectile": ("video2_projectile.mp4", "kapak_video2_aci.png"),
    "02_video3_inertia": ("video3_inertia.mp4", "kapak_video3_atalet.png"),
    "03_video4_second_law": ("video4_second_law.mp4", "kapak_video4_ikinci_yasa.png"),
    "04_video5_third_law": ("video5_third_law.mp4", "kapak_video5_ucuncu_yasa.png"),
}
TITLE = {"01_video2_projectile": "Which launch angle sends a ball the farthest? 🎯"}


def items():
    out = []
    posts = {p["id"]: p for p in run.jload(run.POSTS, [])}
    q = {i["id"]: i for i in run.jload(run.QFILE, [])}
    for iid, (mp4, cover) in OLD.items():
        it = dict(posts[iid])
        it["mp4"], it["cover"] = os.path.join(V, mp4), os.path.join(K, cover)
        out.append(it)
    for iid, it in sorted(q.items(), key=lambda kv: kv[1]["order"]):
        it = dict(it)
        it["mp4"], it["cover"] = os.path.join(run.QDIR, it["file"]), os.path.join(run.QDIR, it["cover"])
        out.append(it)
    for it in out:
        if it["id"] in TITLE:
            it["hook"] = TITLE[it["id"]]
    return out


def slot(i):
    day = FIRST_DAY + dt.timedelta(days=i // 2)
    return f"{day:%Y-%m-%d}T{SLOTS_UTC[i % 2]}:00Z"


def main():
    run.load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    cfg = run.jload(os.path.join(ROOT, "config", "strategy.json"), {})
    pl = cfg.get("yt", {}).get("playlist_id")
    state = run.jload(STATE, {})
    for i, it in enumerate(items()):
        st = state.setdefault(it["id"], {"publish_at": slot(i), "steps": []})
        title, desc, tags = run.yt_meta(it, cfg)
        tr = dt.datetime.strptime(st["publish_at"], "%Y-%m-%dT%H:%M:%SZ") + dt.timedelta(hours=3)
        print(f"{i + 1:2d}. {it['id']:28s} {tr:%d.%m %H:%M} TR  {'tamam' if st.get('done') else 'bekliyor'}  {title}")
        if a.dry or st.get("done"):
            continue
        try:
            if "video_id" not in st:
                st["video_id"] = publish.yt_short(it["mp4"], title, desc, tags, publish_at=st["publish_at"])
                run.jsave(STATE, state)
            vid = st["video_id"]
            for name, fn in (("thumb", lambda: publish.yt_thumbnail(vid, it["cover"])),
                             ("playlist", lambda: pl and publish.yt_playlist_add(vid, pl))):
                if name not in st["steps"]:
                    fn()
                    st["steps"].append(name)
                    run.jsave(STATE, state)
            st["done"] = True
            run.jsave(STATE, state)
            print("    yüklendi:", publish.yt_link(vid))
        except RuntimeError as e:
            run.jsave(STATE, state)
            print("    DURDU:", str(e)[:300])
            if "quota" in str(e).lower():
                print("Günlük kota doldu; yarın (TR 10:00'dan sonra) aynı komutla devam et.")
            return
    run.jsave(STATE, state)


if __name__ == "__main__":
    main()
