"""Telegram chat agent: runs Claude Code on the owner's message with a narrow toolset.

Claude may only read config/, state/, queue/queue.json, edit config/strategy.json and queue/queue.json
(captions/order) and request actions via state/tg_action.json. No shell, no web, no code edits, no Meta tokens.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import notify  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT = os.path.join(ROOT, "state", "tg_chat.json")
ACTION = os.path.join(ROOT, "state", "tg_action.json")
STRATEGY = os.path.join(ROOT, "config", "strategy.json")
PREVIEW = os.path.join(ROOT, "state", "preview.json")
QUEUE = os.path.join(ROOT, "queue", "queue.json")

SYSTEM = """You are Claude, the operator of "Physics with Ray" (Facebook Page "Vector Physics Lab" + Instagram @vectorphysicslab): an automated channel posting ~1 minute English voice-over animated physics lesson Reels starring the robot mascot Ray. Videos are rendered by the owner locally (desktop Claude Code session) and put into queue/queue.json; GitHub Actions posts the next queued video at the daily slots in config/strategy.json (at least 3 per day, UTC), adds a first comment, and runs analytics + an autonomous tuner every 6h. Goal: grow views and followers fast while Facebook boosts new pages. $0 budget.

You are chatting with the owner on Telegram. Reply in Turkish and always give clock times in Turkey time (UTC+3; the config slots are UTC, e.g. 12:30 UTC = 15:30), never in UTC. Warm and natural like a teammate, short (plain text, no markdown tables, max ~12 lines).

What you can do:
- Read config/strategy.json, state/summary.md (latest metrics), state/changelog.md, state/posts.json (posted items), queue/queue.json (pending items).
- Edit config/strategy.json (keep valid JSON and the exact schema): per_day, slots_utc (HH:MM UTC, keep per_day equal to number of slots, minimum 3), catchup_hours, networks.{ig,fb}, caption.{outro,tags_core,tags_rotating,tags_per_post}, first_comment (list).
- Edit queue/queue.json: change hook/body/tags/first_comment of pending items or reorder ("order" field). Never touch file/cover names, never delete items.
- Previews: about 1 hour before each slot the system automatically sends the owner a Telegram preview (cover, video, caption, first comment, time) with buttons Yayınla/Revize/Reddet; without a reaction the autopilot posts at the slot. You do not need to handle those buttons.
- Trigger actions by writing state/tg_action.json: {"actions":[{"type":"post"|"dry_run","only":"ig|fb or empty"}]}. "post" publishes the next queued video now to IG+FB (ignoring slots); "dry_run" only shows what would be posted.

You cannot make new videos, change code, visuals or run commands. If a request needs that, say so briefly and tell the owner to ask the desktop Claude Code session; offer the closest thing you can do via config. When the owner asks to post now, do it immediately by writing the action file; never ask for confirmation. Never invent numbers: quote state/summary.md. After changes, say exactly what you changed."""


def load(path, default):
    try:
        with open(path, encoding="utf8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def commit(paths, msg):
    git("add", *paths)
    if git("diff", "--cached", "--quiet").returncode:
        git("commit", "-qm", msg)
        git("pull", "-q", "--rebase")
        git("push", "-q")


def callback(cb, mid):
    """Önizleme düğmeleri: ok (yayınla) / rv (revize) / no (reddet). Claude gerekmez."""
    import run
    act, _, iid = cb.partition(":")
    notify.remove_buttons(mid)
    q = load(QUEUE, [])
    item = next((i for i in q if i["id"] == iid), None)
    if not item or item.get("ig_id") or item.get("fb_id") or item.get("skipped"):
        notify.text("Bu önizleme artık geçerli değil (video yayınlanmış, reddedilmiş ya da kuyrukta yok).")
        return
    cfg = load(STRATEGY, {})
    if act == "ok":
        if os.path.exists(PREVIEW):
            os.remove(PREVIEW)
        commit(["state"], "telegram: onay")
        ok = subprocess.run(["gh", "workflow", "run", "post", "-f", "dry_run=false", "-f", "force=true", "-f", f"item={iid}"], cwd=ROOT).returncode == 0
        notify.text("▶️ Yayınlanıyor (~2 dk), rapor gelecek." if ok else "⚠️ Yayın başlatılamadı.")
    elif act == "no":
        item["skipped"] = True
        json.dump(q, open(QUEUE, "w", encoding="utf8"), ensure_ascii=False, indent=1)
        if os.path.exists(PREVIEW):
            os.remove(PREVIEW)
        commit(["queue/queue.json", "state"], f"telegram: reddet {iid}")
        notify.text("❌ Reddedildi, kuyruktan çıkardım (dosya silinmedi).")
        pend = run.pending(q)
        nxt = run.upcoming_slot(cfg, load(run.POSTS, []), run.dt.datetime.now(run.dt.timezone.utc))
        if pend and nxt:
            run.send_preview(pend[0], cfg, nxt)
            commit(["state"], "telegram: yeni önizleme")
    elif act == "rv":
        cur = load(PREVIEW, {})
        json.dump({"item": iid, "slot": cur.get("slot"), "status": "revise"}, open(PREVIEW, "w", encoding="utf8"))
        commit(["state"], "telegram: revize")
        notify.text("✏️ Neyi değiştirelim? Hook, açıklama, hashtag, ilk yorum... yaz, düzenleyip yeni önizleme göndereyim. (Bu video o zamana kadar yayınlanmaz.)")


def main():
    if os.environ.get("CB", "").strip():
        return callback(os.environ["CB"].strip(), os.environ.get("MID"))
    msg = os.environ["MSG"].strip()
    hist = load(CHAT, [])
    if msg.lower() in ("/reset", "/start"):
        json.dump([], open(CHAT, "w", encoding="utf8"))
        notify.text("Sohbet geçmişini sıfırladım. Merhaba! Durumu sorabilir, strateji/caption değişikliği isteyebilir ya da \"şimdi paylaş\" diyebilirsin.")
        return
    convo = "\n".join(f"Owner: {h['u']}\nYou: {h['a']}" for h in hist[-8:])
    prompt = f"{SYSTEM}\n\n## Recent conversation\n{convo or '(none)'}\n\n## New message from owner\n{msg}"
    if os.path.exists(ACTION):
        os.remove(ACTION)
    before_s = open(STRATEGY, encoding="utf8").read()
    before_q = open(QUEUE, encoding="utf8").read() if os.path.exists(QUEUE) else "[]"
    env = {k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN", "TELEGRAM_TOKEN")}
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--model", "sonnet", "--max-turns", "12",
           "--allowedTools", "Read(./config/**)", "Read(./state/**)", "Read(./queue/queue.json)",
           "Edit(./config/strategy.json)", "Edit(./queue/queue.json)", "Write(./state/tg_action.json)",
           "--disallowedTools", "Bash", "WebFetch", "WebSearch", "Task", "NotebookEdit"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600, cwd=ROOT)
        out = json.loads(r.stdout)
        reply = out["result"]
        if out.get("permission_denials"):
            print("permission_denials:", json.dumps(out["permission_denials"])[:800])
    except Exception as e:
        tail = locals().get("r")
        reply = f"⚠️ Claude çalışırken hata oldu: {(tail.stderr or tail.stdout)[-400:] if tail else e}"
    try:
        cfg = json.load(open(STRATEGY, encoding="utf8"))
        assert len(cfg["slots_utc"]) >= 3
    except (ValueError, AssertionError, KeyError):
        open(STRATEGY, "w", encoding="utf8").write(before_s)
        reply += "\n\n⚠️ strategy.json geçersiz hale geldi, değişikliği geri aldım."
    try:
        q = json.load(open(QUEUE, encoding="utf8"))
        assert [i["file"] for i in q] == [i["file"] for i in json.loads(before_q)] or len(q) == len(json.loads(before_q))
    except (OSError, ValueError, AssertionError, KeyError):
        open(QUEUE, "w", encoding="utf8").write(before_q)
        reply += "\n\n⚠️ queue.json geçersiz hale geldi, değişikliği geri aldım."
    hist.append({"t": time.strftime("%Y-%m-%d %H:%M"), "u": msg[:1500], "a": reply[:1500]})
    json.dump(hist[-20:], open(CHAT, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    # commit before triggering posts so they check out the new config
    git("add", "config/strategy.json", "queue/queue.json", "state/tg_chat.json")
    if git("diff", "--cached", "--quiet").returncode:
        git("commit", "-qm", f"telegram: {msg[:60]}")
        git("pull", "-q", "--rebase")
        git("push", "-q")
    acts = load(ACTION, {}).get("actions", [])
    notes = []
    if revising and not any(a.get("type") == "post" for a in acts):
        import run
        cfg = load(STRATEGY, {})
        q = load(QUEUE, [])
        it = next((i for i in q if i["id"] == rev.get("item")), None)
        if it and rev.get("slot"):
            notify.text(reply)
            reply = ""
            run.send_preview(it, cfg, (rev["slot"], run.slot_dt(rev["slot"])))
            commit(["state"], "telegram: yeni önizleme")
    elif revising and os.path.exists(PREVIEW):
        os.remove(PREVIEW)
        commit(["state"], "telegram: revize bitti")
    for a in acts[:2]:
        typ = a.get("type")
        if typ not in ("post", "dry_run"):
            continue
        args = ["gh", "workflow", "run", "post", "-f", f"dry_run={'false' if typ == 'post' else 'true'}", "-f", "force=true"]
        if a.get("only") in ("ig", "fb"):
            args += ["-f", f"only={a['only']}"]
        ok = subprocess.run(args, cwd=ROOT).returncode == 0
        notes.append(f"{'▶️' if ok else '⚠️'} {typ} {'başlatıldı (~2 dk)' if ok else 'başlatılamadı'}")
    if os.path.exists(ACTION):
        os.remove(ACTION)
    notify.text(reply + ("\n\n" + "\n".join(notes) if notes else ""))


if __name__ == "__main__":
    main()
