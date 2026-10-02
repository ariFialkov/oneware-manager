---
name: game-report
description: Deep-dive analysis of one Oneware game across outreach, retention and monetization, with specific improvements. Use for /game-report <slug> or when asked how a particular game is doing or how to improve it.
---

# Game report

Argument: a game slug from `games/catalog.csv`.

1. Load `games/<slug>/game.md`, its catalog row, and any `data/` files for
   its app id. Pull fresh sales, reviews, builds via `tools/asc.py` when
   credentials are available.
2. **Outreach** — impressions, product page views, PP→install, sources
   (search / browse / referrer / cross-promo), install trend since launch.
   Diagnose: low impressions = discovery (ASO, content); low PP→install =
   listing (icon, first two screenshots, subtitle).
3. **Retention** — D1/D7/D30, session length, sessions per day, FTUE funnel
   (`tutorial_step`), level funnel (`level_end` quit/lose spikes). Name the
   exact step or level where players leave.
4. **Monetization** — ARPDAU, rewarded-ad watch rate per placement,
   `iap_view`→`iap_purchase` conversion, revenue per product.
5. **Player voice** — themes from reviews and feedback, with quotes.
6. Compare every metric to the studio median of other live games and to
   the gates in `studio/strategy.md`.
7. **Recommendations**: at most 5, ranked by expected impact ÷ effort.
   Each: change, pillar, target metric with a numeric goal, how to measure,
   and build effort. Mark which could ship as one update.
8. Gate verdict if the game is ≥ 14 days live.
9. Save to `reports/<date>-<slug>.md`; append metrics + verdict to the game
   sheet; log any decision in `studio/log.md`.

Never invent numbers. When data is missing, say which data and how to get it.
