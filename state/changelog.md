# Changelog

## 2026-10-17 12:39 UTC
- No changes made. Only 2 posts published so far (97/1 views and 0/1 views) — far below the ~6-post threshold needed to distinguish signal from noise.
- Both posts went out close together (11:41 and 12:23 UTC) outside the configured slots (12:30/17:00/21:00), likely initial backfill/catchup posts, so their timing isn't representative of the real slot performance yet.
- Kept slots_utc (12:30, 17:00, 21:00), tags, outro, and first_comment pool unchanged — no justified move yet.
- Next check: once ~6+ posts have accumulated per slot, compare views/avg watch time across 12:30 vs 17:00 vs 21:00 and shift slots toward the best-performing hour; also compare hook styles (question-based hooks on 01 and 02) against comment/engagement counts.

## 2026-10-17 18:36 UTC
- No changes made. Still only 4 posts total (234, 149, 113, 109 views; avg watch 6.6-12.6s) — below the ~6-post threshold, so the spread between posts is treated as noise rather than a real pattern.
- All 4 posts hit their 21:00 slot has zero data yet (no post has run there), and 12:30/17:00 each only have 1-2 data points, too thin to justify moving slots.
- Engagement is uniformly low (1 like, 1 comment, 0 shares on almost every post) and FB views are near-zero (0-1 each) — not yet a clear signal to change tags/outro/first_comment, just a sign the page is very new.
- No publish errors in posts.json; all 4 posts have valid ig_id/fb_id, so no KOD fix needed this cycle.
- Next check: wait for 21:00 slot data and at least 6-8 total posts, then compare views/avg-watch-time by slot (12:30 vs 17:00 vs 21:00) and by hook style before touching slots_utc or tags.

## 2026-10-18 00:47 UTC
- 8 posts now (just above the ~6 threshold), views 83-239, but comments are exactly 1 on every single post (that's just our own auto-posted first_comment — zero organic replies so far) and shares are 0 everywhere, so there's no real engagement signal yet to differentiate hook styles or hashtag topics; kept slots_utc/per_day untouched per owner's fixed schedule.
- Raised tags_per_post from 5 to 6 and added "#physicslessons" to tags_rotating — still within the 5-8 niche-relevant range, aimed at slightly wider discovery while FB is boosting the new page, low-risk since it doesn't touch content/timing.
- Added a 4th first_comment prompt ("Yes or no: did you already know this one?") — a binary-choice variant to test against the open-ended ones, since none of the 3 existing prompts have produced any organic replies yet (0 comments beyond our own seed comment across all 8 posts).
- Did not touch outro, tags_core, or slots — no post has enough individual-variant data (each hook/tag/comment variant has only 1 data point) to justify bigger moves; avg watch time (4.5-12.8s on ~60s videos) looks low across the board but that's a content/pacing issue, not something fixable via strategy.json.
- Next check: once each first_comment variant and the new #physicslessons tag have appeared on 2-3+ posts, compare organic comment counts and views between variants; also watch whether avg watch time improves or stays flat (would point to a content-level fix outside this config).

## 2026-10-18 06:40 UTC
- No changes made. Still the same 8 posts as the 00:47 UTC check (views just ticked up slightly, 105-247 vs 83-239, as IG counters continue accruing on existing posts) — no new post has published since the last slot, so there's no fresh data to evaluate the tags_per_post=6/#physicslessons/4th first_comment change made 6 hours ago.
- Next slot is 19:00 UTC; the 01:00 UTC slot already passed before this check ran. Kept caption.outro, tags_core, tags_rotating, tags_per_post, first_comment, and slots_utc/per_day untouched this cycle.
- No publish errors in posts.json (all 8 entries have valid ig_id/fb_id) — no KOD fix needed.
- Next check: after the 19:00 UTC post lands (post #9), compare its tags/first_comment variant performance against posts 1-8, and keep watching for the first organic (non-seed) comment as the real engagement signal.

## 2026-10-18 12:40 UTC
- No changes made. Still the exact same 8 posts as the 06:40 UTC check (views only ticked up slightly as IG counters keep accruing, e.g. 01_video2_projectile 247→253, 07_video8_electricity 183→189) — no new post has published since, so there's still zero fresh data to judge the tags_per_post=6/#physicslessons/4th first_comment change made at 00:47 UTC.
- The 19:00 UTC slot (today's second post) has not fired yet at 12:40 UTC check time, so post #9 is still pending.
- Comments remain exactly 1 on every post (our own seed first_comment) and shares are 0 across the board — no organic engagement signal yet to differentiate hook/tag/comment variants.
- No publish errors in posts.json; all 8 entries have valid ig_id/fb_id — no KOD fix needed.
- Kept caption.outro, tags_core, tags_rotating, tags_per_post, first_comment, and slots_utc/per_day unchanged this cycle. Next check: after post #9 (19:00 UTC) lands, compare it against posts 1-8 and look for the first organic comment/share.

## 2026-10-18 18:36 UTC
- No changes made. Still the exact same 8 posts as the 12:40 UTC check (views up only slightly, e.g. 07_video8_electricity 189→227, 06_video7_heat 154 stable) — the 19:00 UTC slot (post #9) has not fired yet at 18:36, so there's still zero new data to evaluate the tags_per_post=6/#physicslessons/4th first_comment change from 00:47 UTC.
- Comments remain exactly 1 on every post (our own seed first_comment) and shares are 0 across all 8 posts — no organic engagement signal yet, same pattern as every prior check.
- No publish errors in posts.json; all 8 entries have valid ig_id/fb_id — no KOD fix needed.
- Kept caption.outro, tags_core, tags_rotating, tags_per_post, first_comment, and slots_utc/per_day unchanged. Next check: after post #9 (19:00 UTC today) and ideally post #10 (01:00 UTC tomorrow) land, compare their performance and tag/comment variants against posts 1-8, and watch for the first organic (non-seed) comment or share as the real engagement signal.

## 2026-10-19 00:49 UTC
- No changes made. 9 posts total now (up from 8), views 108-258, still no organic engagement: comments are exactly 1 on every post (our own seed) and shares are 0 everywhere — 9 posts in, there's still zero real signal to differentiate hook/tag/first_comment variants, so per the rule to change little under ~6 posts (and no justified move even now), strategy.json is left untouched this cycle.
- Confirmed via src/run.py (build_caption/first_comment) that every queued video (03 onward, including all of queue/queue.json orders 10-22) carries its own hardcoded `tags` and `first_comment` — the config's `caption.first_comment` pool is only a fallback used when an item has none (true for posts 01-02 only). So tuning the first_comment pool in strategy.json has no effect on future posts; real first_comment A/B testing would need per-video variants in queue.json, not this config. Left the pool as-is (still a valid 4-entry fallback) — noting this for future cycles so effort isn't wasted tuning a field that mostly isn't read.
- Post #9 (09_video10_doppler) landed at 19:12 UTC, close to the configured 19:00 UTC slot — first real on-schedule data point: 152 views, 8.9s avg watch, 4 likes, 2 saves, still 0 organic comments/shares. Slots_utc/per_day left unchanged per owner's fixed schedule regardless.
- No publish errors in posts.json (all 9 entries have valid ig_id/fb_id) — no KOD fix needed.
- Next check: watch for post #10 (01:00 UTC slot) and the first organic (non-seed) comment/share; once ~15+ posts accumulate, compare avg watch time and views by hashtag topic cluster (e.g. waves/sound topics vs mechanics topics) since avg watch time is uniformly low (5.5-12.5s on ~60s videos) — likely a content/pacing issue rather than a strategy.json lever.
