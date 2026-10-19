"""Otomatik ayar: analytics'ten sonra Claude state/summary.md'yi okuyup config/strategy.json'u (caption/hashtag/yorum/slot) günceller."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import notify  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRATEGY = os.path.join(ROOT, "config", "strategy.json")

PROMPT = """You are the autonomous growth operator of "Physics with Ray": an Instagram + Facebook Page channel posting ~1 minute animated physics lesson Reels (English voice-over, robot mascot Ray), 1 post every 2 days (15:00 Turkey time = 12:00 UTC, set by the owner). Goal: grow views and followers fast while Facebook boosts new pages. The owner does not intervene: you decide.

Now is {now}. Do this:
1. Read state/summary.md (metrics), state/changelog.md (past changes, may not exist yet), config/strategy.json.
2. Decide the few changes most likely to raise views, watch time, comments and follows. You may edit: caption.outro, caption.tags_core, caption.tags_rotating, caption.tags_per_post, first_comment (keep 3-6 comment-provoking entries), slots_utc, per_day and every_days (the owner fixed 1 post every 2 days, so leave them unchanged). Rules:
   - Judge with data. With fewer than ~6 posts treat differences as noise and change little.
   - Slots: the owner fixed 12:00 UTC every 2 days; do not change slots_utc, per_day or every_days.
   - Hashtags: 5-8 per post, niche-relevant (physics, science education), no banned/spammy tags.
   - Change a few things at a time so effects stay measurable. If nothing is justified, change nothing.
3. Edit config/strategy.json only (valid JSON, same schema, keep all keys).
4. Append to state/changelog.md a section "## {now}" with 2-5 bullets: what you changed and why (cite numbers), plus what to check next time.
5. Your final reply must be ONLY a short Turkish message for the owner (max 6 lines, plain text): what you changed and why, or that you kept the strategy. If summary.md shows publish errors that need code fixes, add one line starting with "KOD:".
"""


def main():
    before = open(STRATEGY, encoding="utf8").read()
    env = {k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN", "TELEGRAM_TOKEN")}
    cmd = ["claude", "-p", PROMPT.format(now=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())),
           "--output-format", "json", "--model", "sonnet", "--max-turns", "15",
           "--allowedTools", "Read(./config/**)", "Read(./state/**)", "Edit(./config/strategy.json)",
           "Edit(./state/changelog.md)", "Write(./state/changelog.md)",
           "--disallowedTools", "Bash", "WebFetch", "WebSearch", "Task", "NotebookEdit"]
    report = ""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600, cwd=ROOT)
        print(r.stdout[-2000:], r.stderr[-1000:])
        report = json.loads(r.stdout)["result"].strip()
    except (subprocess.TimeoutExpired, ValueError, KeyError) as e:
        print("tuner:", e)
    try:
        cfg = json.load(open(STRATEGY, encoding="utf8"))
        assert len(cfg["slots_utc"]) >= 1
    except (ValueError, AssertionError, KeyError):
        open(STRATEGY, "w", encoding="utf8").write(before)
        report += "\n⚠️ strategy.json bozuldu, değişiklik geri alındı."
    changed = open(STRATEGY, encoding="utf8").read() != before
    if report and (changed or "KOD:" in report or "⚠️" in report):
        notify.text("🧠 Otomatik ayar\n" + report)


if __name__ == "__main__":
    main()
