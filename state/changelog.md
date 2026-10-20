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

## 2026-10-19 06:50 UTC
- No changes made. 10 posts now (up from 9), views 108-258, comments still exactly 1 on every single post (our own seed first_comment, confirmed zero organic replies) and shares 0 everywhere — still no real engagement signal to differentiate any variant.
- Correction to the 00:49 UTC note: `tags_core`/`tags_rotating`/`tags_per_post` are NOT dead config — re-checked `build_caption()` in src/run.py: it always merges `tags_core + item["tags"] + picked-from-tags_rotating` up to `tags_per_post` total, for every post including hardcoded-tag items (03+). So the tags_per_post=6 / #physicslessons change from 2026-10-18 00:47 UTC is live and already affecting every post's hashtag set. Only `caption.first_comment` (the pool) is a dead fallback for items 03+, since those have their own hardcoded `first_comment` — that part of the earlier note was correct.
- Lower recent views (10_video11_light_sound 135, 09_video10_doppler 163) vs higher earlier posts (258, 242) look like normal view-count ramp-up for newer posts (older posts keep accruing views over days, per the 247→253 pattern seen in past checks), not a real quality signal — so not treating it as a hook-style difference.
- Kept caption.outro, tags_core, tags_rotating, tags_per_post, first_comment, and slots_utc/per_day unchanged this cycle — no justified move with zero organic engagement data to split variants on.
- No publish errors in posts.json; all 10 entries have valid ig_id/fb_id — no KOD fix needed.
- Next check: keep watching for the first organic (non-seed) comment/share and for FB followers to move off 0; once ~15+ posts accumulate, compare avg watch time/views by hashtag topic cluster (mechanics vs waves/sound vs electricity) since avg watch time is uniformly low (5.5-12.5s on ~60s videos) — likely content/pacing, not a strategy.json lever.

## 2026-10-19 12:47 UTC
- No changes made. Still the exact same 10 posts as the 06:50 UTC check (views ticked up only slightly, e.g. 10_video11_light_sound 135→140, 09_video10_doppler 163→171) — today's 19:00 UTC slot hasn't fired yet, so there's zero fresh data since the last cycle 6 hours ago.
- Comments remain exactly 1 on every post (our own seed first_comment, zero organic replies) and shares are 0 across all 10 posts; FB followers still 0 — no engagement signal has appeared in 5+ consecutive checks now, so there's nothing to split hashtag/comment variants on.
- Views still range 108-258 with no clear hook/topic pattern distinguishing them from pure accrual-over-time noise (e.g. oldest post 02_video3_inertia still has only 114 views despite being first published) — not treating this as a content signal.
- Kept caption.outro, tags_core, tags_rotating, tags_per_post, first_comment, and slots_utc/per_day unchanged this cycle — no justified move with no new data and no organic engagement.
- No publish errors in posts.json; all 10 entries have valid ig_id/fb_id — no KOD fix needed.
- Next check: after the 19:00 UTC post (#11) lands, compare it against posts 1-10 and keep watching for the first organic comment/share or any FB follower movement; if organic engagement stays at zero past ~15-20 posts, consider that avg watch time (consistently 5.5-12.5s on ~60s videos) is the real bottleneck and flag it as a content/pacing issue outside strategy.json's scope.

## 2026-10-19 18:45 UTC
- No changes made. Still the exact same 10 posts as the 12:47 UTC check (no new post since then) — the owner just switched the schedule to 1 post every 2 days at 12:00 UTC (every_days=2, slots_utc=["12:00"], committed today), so the next post won't land until roughly 2026-10-21 12:00 UTC and there is zero fresh data to react to this cycle.
- Engagement rate (likes+saves)/views is notably uneven across the 10 posts even though all get the same tag/comment-pool treatment: 07_video8_electricity leads at 6.2% (10 likes+5 saves / 243 views) and 09_video10_doppler is second at 4.0%, vs 0% on 08_waves, 04_third_law, 05_energy. The pattern favors "how does X actually work" curiosity hooks (electricity, doppler, heat) over abstract law-statement hooks (third law, energy) — but this is a content/hook signal, not something tunable via strategy.json (no reordering lever available here), so no caption/hashtag change was made on this basis alone.
- Comments remain exactly 1 on every post (our own seed first_comment, zero organic replies) and shares are 0 across all 10 posts — still no organic engagement signal to split hashtag or first_comment variants on.
- No publish errors in posts.json; all 10 entries have valid ig_id/fb_id — no KOD fix needed.
- Next check: after the first post under the new 2-day cadence lands (~2026-10-21 12:00 UTC), compare its views/watch-time/engagement against this 10-post baseline to see if the slower cadence changes per-post reach (e.g. less FB "new page boost" competition for attention), and keep watching for the first organic comment/share.

## 2026-10-20 00:49 UTC
- No changes made. Still the exact same 10 posts as the 18:45 UTC check (posted_utc for all 10 unchanged, views essentially flat — e.g. 07_video8_electricity 243, 09_video10_doppler 177, matching prior cycle) — no new post has published since the schedule switched to every_days=2/slots_utc=["12:00"] on 2026-10-19, so there is zero fresh data this cycle. Next post is expected ~2026-10-21 12:00 UTC.
- Comments remain exactly 1 on every post (our own seed first_comment, zero organic replies), shares are 0 on all 10 posts, and FB followers are still 0 — 3+ consecutive checks with no organic engagement signal, so there is nothing to split hashtag/comment variants on yet.
- Kept caption.outro, tags_core, tags_rotating, tags_per_post (6), first_comment pool, and slots_utc/per_day/every_days unchanged — no justified move with no new data.
- No publish errors in posts.json; all 10 entries have valid ig_id/fb_id — no KOD fix needed.
- Next check: after the first 12:00 UTC-cadence post (#11, ~2026-10-21) lands, compare its views/avg-watch-time/engagement against this 10-post baseline under the old denser schedule, and keep watching for the first organic comment/share or FB follower movement.

## 2026-10-20 06:44 UTC
- No changes made. Still the exact same 10 posts as the 00:49 UTC check, views byte-for-byte identical (e.g. 01_video2_projectile 258, 07_video8_electricity 243, 09_video10_doppler 177) — zero fresh data since last cycle, confirming no new post has landed yet under the every_days=2/12:00 UTC cadence. Next post still expected ~2026-10-21 12:00 UTC.
- Comments remain exactly 1 on every post (our own seed) and shares 0 on all 10 posts; FB followers still 0 — 4+ consecutive checks now with zero organic engagement signal, so there is still nothing to split hashtag/first_comment variants on.
- Kept caption.outro, tags_core, tags_rotating, tags_per_post (6), first_comment pool, and slots_utc/per_day/every_days unchanged — no justified move with identical data to the last check.
- No publish errors in posts.json; all 10 entries have valid ig_id/fb_id — no KOD fix needed.
- Next check: after post #11 (~2026-10-21 12:00 UTC, first post under the new 2-day cadence) lands, compare its views/avg-watch-time/engagement against this 10-post baseline, and keep watching for the first organic comment/share or FB follower movement.

## 2026-10-20 12:47 UTC
- Still the exact same 10 posts as the 06:44 UTC check, views unchanged (e.g. 01_video2_projectile 258, 07_video8_electricity 243, 09_video10_doppler 177) — no new post has landed yet, next one expected ~2026-10-21 12:00 UTC under the every_days=2 cadence. No engagement signal change (comments still 1/post seed-only, shares 0, FB followers 0), so no data-driven move this cycle.
- One non-data-driven fix: caption.outro said "follow for a new physics lesson every day 🚀", but the schedule is now 1 post every 2 days (owner decision, 2026-10-19) — the daily promise was stale and misleading to new followers, so reworded to "follow for a new physics lesson every few days 🚀". Low-risk, doesn't touch tags/timing/content.
- Left tags_core, tags_rotating, tags_per_post (6), first_comment pool, and slots_utc/per_day/every_days unchanged — no fresh data to justify any variant split.
- No publish errors in posts.json; all 10 entries have valid ig_id/fb_id — no KOD fix needed.
- Next check: after post #11 (first under the 2-day cadence) lands, compare it to this 10-post baseline and watch for the first organic comment/share, FB follower movement, and whether the reworded outro affects follow-through rate.
