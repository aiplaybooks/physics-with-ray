"""IG + FB metriklerini çeker, kısa bir state/summary.md yazar (tuner ve sen sadece bunu okursun)."""
import json
import os
import time

import requests

V = "v23.0"
IG = f"https://graph.instagram.com/{V}"
FB = f"https://graph.facebook.com/{V}"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get(url, **params):
    try:
        r = requests.get(url, params=params, timeout=30)
        return r.json() if r.status_code < 400 else {"error": r.text[:200]}
    except requests.RequestException as e:
        return {"error": str(e)}


def ig_metrics(mid, tok):
    out = {}
    for m in ("views", "reach", "likes", "comments", "shares", "saved", "ig_reels_avg_watch_time"):
        d = get(f"{IG}/{mid}/insights", metric=m, access_token=tok)
        if d.get("data"):
            out[m] = d["data"][0]["values"][0]["value"]
    return out


def fb_metrics(vid, tok):
    out = {}
    for row in get(f"{FB}/{vid}/video_insights", access_token=tok).get("data", []):
        if row["name"] in ("blue_reels_play_count", "post_video_avg_time_watched", "post_impressions_unique", "post_video_followers"):
            out[row["name"]] = row["values"][0]["value"]
    return out


def main():
    ig_tok, fb_tok = os.environ["IG_TOKEN"], os.environ["FB_PAGE_TOKEN"]
    path = os.path.join(ROOT, "state", "posts.json")
    posts = json.load(open(path, encoding="utf8")) if os.path.exists(path) else []
    acct = get(f"{IG}/me", fields="followers_count,media_count", access_token=ig_tok)
    page = get(f"{FB}/{os.environ['FB_PAGE_ID']}", fields="followers_count,fan_count", access_token=fb_tok)
    for p in posts:
        if p.get("ig_id"):
            p["ig"] = ig_metrics(p["ig_id"], ig_tok)
        if p.get("fb_id"):
            p["fb"] = fb_metrics(p["fb_id"], fb_tok)
    json.dump(posts, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=1)

    def views(p):
        return (p.get("ig", {}).get("views") or 0) + (p.get("fb", {}).get("blue_reels_play_count") or 0)

    igf, fbf = acct.get("followers_count", 0), page.get("followers_count", 0)
    lines = [f"# Summary {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
             f"Followers IG {igf} + FB {fbf} = {igf + fbf} | Views {sum(views(p) for p in posts)} | Posts {len(posts)}", "",
             "| id | hook | views IG/FB | avg watch s IG | likes | cmts | shares | saves |", "|---|---|---|---|---|---|---|---|"]
    for p in sorted(posts, key=views, reverse=True)[:15]:
        ig, fb = p.get("ig", {}), p.get("fb", {})
        aw = ig.get("ig_reels_avg_watch_time")
        lines.append(f"| {p.get('id')} | {p.get('hook', '')[:40]} | {ig.get('views', '-')}/{fb.get('blue_reels_play_count', '-')} | "
                     f"{round(aw / 1000, 1) if aw else '-'} | {ig.get('likes', '-')} | {ig.get('comments', '-')} | {ig.get('shares', '-')} | {ig.get('saved', '-')} |")
    errs = [f"{p.get('id')}: {p.get('ig_error') or p.get('fb_error')}" for p in posts[-6:] if p.get("ig_error") or p.get("fb_error")]
    if errs:
        lines += ["", "Recent publish errors:"] + [f"- {e[:160]}" for e in errs]
    with open(os.path.join(ROOT, "state", "summary.md"), "w", encoding="utf8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:2]))
    if time.gmtime().tm_hour == 6:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import notify
        notify.text("\n".join(lines))


if __name__ == "__main__":
    main()
