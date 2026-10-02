---
name: weekly-review
description: The Monday operating cycle for Oneware Games — pull data, update every game, apply release gates, pick next week's release and content, and log decisions. Use for /weekly-review or "plan the week".
---

# Weekly review

1. Run the `/studio-status` steps (data pull + table).
2. For each game 14+ days live without a verdict, apply the gates in
   `studio/strategy.md` and record kill / iterate / double down.
3. Look across games for patterns: which genres, session lengths, art
   styles and clip hooks beat the studio median? Update the
   "What we're learning" section at the bottom of `studio/strategy.md`
   (create it if missing). Claims need ≥ 2 games behind them.
4. Marketing check: last week's content calendar rows. Which hooks got
   views, which clips drove installs? Influencer tracker status.
5. **Pick next week's release** from the bank: score each `bank` game on
   clip_score, distinctness from the last 2 releases, and fit with what
   we're learning. Recommend one plus a backup, with reasons.
6. Plan the week: release day, 7 content slots, 1 iteration update (for
   the strongest "iterate" game), any influencer outreach for "double
   down" games.
7. Write `reports/<date>-weekly.md`, update `games/catalog.csv`, append
   decisions to `studio/log.md`. Reply with a short summary and the
   week's to-do list, owner tasks marked.
