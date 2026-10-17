"""Facebook Business Suite için elle planlama listesi (FB_PLAN.md). IG ile aynı caption + ilk yorum."""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import run
import week_copy as wc

cfg = json.load(open(os.path.join(ROOT, "config", "strategy.json"), encoding="utf8"))
q = {int(i["id"].split("_video")[1].split("_")[0]): i for i in json.load(open(os.path.join(ROOT, "queue", "queue.json"), encoding="utf8"))}
out = ["# Facebook planlama listesi (Meta Business Suite, saatler TR = UTC+3)", "",
       "Her satır: video dosyası, yayın saati, caption (kopyala-yapıştır), ilk yorum. IG ile aynı metin.", ""]
for no, t in wc.plan():
    it = q[no]
    tr = t + dt.timedelta(hours=3)
    out += [f"## Video {no} — {tr:%d.%m.%Y %H:%M} (TR) · {t:%H:%M} UTC", f"Dosya: `queue/{it['file']}`  |  Kapak: `queue/{it['cover']}`", "",
            "```", run.build_caption(it, cfg), "```", f"İlk yorum: {run.first_comment(it, cfg)}", ""]
open(os.path.join(ROOT, "FB_PLAN.md"), "w", encoding="utf8").write("\n".join(out))
print("FB_PLAN.md yazıldı")
