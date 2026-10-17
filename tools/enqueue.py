"""Hazır bir videoyu (+kapak) paylaşım kuyruğuna ekler.

python tools/enqueue.py --video vector/cikti/video3_inertia.mp4 --cover vector/cikti/kapak/kapak_video3_atalet.png \
    --hook "Why do you lurch forward when a bus brakes?" --body "..." [--tags "#bus #inertia"] [--first-comment "..."]
Sıra numarası otomatik devam eder (queue.json + state/posts.json'daki en büyük sıradan sonra).
"""
import argparse
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, "queue")
QFILE = os.path.join(QDIR, "queue.json")
POSTS = os.path.join(ROOT, "state", "posts.json")


def jload(p):
    return json.load(open(p, encoding="utf8")) if os.path.exists(p) else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--cover")
    ap.add_argument("--hook", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--first-comment", default="")
    ap.add_argument("--slug")
    a = ap.parse_args()
    q, posts = jload(QFILE), jload(POSTS)
    order = max([i["order"] for i in q] + [p.get("order", 0) for p in posts] + [0]) + 1
    slug = a.slug or re.sub(r"[^a-z0-9]+", "_", os.path.splitext(os.path.basename(a.video))[0].lower()).strip("_")
    name = f"{order:02d}_{slug}"
    os.makedirs(QDIR, exist_ok=True)
    shutil.copyfile(a.video, os.path.join(QDIR, name + ".mp4"))
    item = {"order": order, "id": name, "file": name + ".mp4", "hook": a.hook, "body": a.body}
    if a.cover:
        shutil.copyfile(a.cover, os.path.join(QDIR, name + ".png"))
        item["cover"] = name + ".png"
    if a.tags:
        item["tags"] = a.tags.split()
    if a.first_comment:
        item["first_comment"] = a.first_comment
    q.append(item)
    with open(QFILE, "w", encoding="utf8") as f:
        json.dump(q, f, ensure_ascii=False, indent=1)
    print("kuyruğa eklendi:", name, "| bekleyen:", len(q))


if __name__ == "__main__":
    main()
