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
