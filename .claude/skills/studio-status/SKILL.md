---
name: studio-status
description: Studio-wide dashboard for Oneware Games — installs, retention, revenue and ratings across every live game, with the top 3 actions. Use when the owner asks "how are we doing", for a status check, or runs /studio-status.
---

# Studio status

1. Read `games/catalog.csv` and each live game's `games/<slug>/game.md`.
2. If ASC credentials are set, pull fresh data:
   - `python3 tools/asc.py sales --frequency DAILY` for the last 7 days
     (loop `--date`), sum units and proceeds per app (match on Apple
     Identifier / SKU to `asc_app_id`).
   - `python3 tools/asc.py reviews <app_id> --limit 20` per live game.
   - Downloaded analytics reports in `data/` for retention and product page
     conversion, if present.
   If credentials are missing, say so and use the latest numbers recorded
   in the game sheets, stating their dates.
3. Produce one table: game | days live | installs 7d (Δ vs prior 7d) |
   PP→install | D1 | D7 | revenue 7d | rating | gate status (per
   `studio/strategy.md`).
4. Studio totals and the three north-star metrics from `studio/strategy.md`.
5. **Top 3 actions** this week, each naming the pillar, the metric it moves,
   and the effort (hours). Prefer actions on the biggest lever, not the
   easiest.
6. Save to `reports/<YYYY-MM-DD>-studio.md` and append new metrics rows to
   each game sheet. Keep the chat reply to the table + actions.
