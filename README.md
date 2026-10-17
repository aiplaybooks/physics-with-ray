# Physics with Ray – autopilot

Videolar yerelde üretilir (`vector/`), `tools/enqueue.py` ile `queue/`'ya eklenir, GitHub Actions (`post.yml`, 30 dk'da bir) `config/strategy.json`'daki slotlarda (günde 3) sıradakini IG Reels + FB Reels olarak yayınlar, ilk yorumu atar. `analytics.yml` 6 saatte bir metrikleri `state/summary.md`'ye yazar, `src/tuner.py` caption/hashtag/slotları ayarlar.

Kurulum: `.env` doldur -> `python tools/set_secrets.py` -> Actions'tan `post` (dry_run) çalıştır. Token izinleri: `docs/TOKEN_REHBERI.md`.
Yeni video: `python tools/enqueue.py --video ... --cover ... --hook "..." --body "..."` -> commit & push.
Yerel test: `python src/run.py --dry-run`
