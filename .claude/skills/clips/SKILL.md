---
name: clips
description: Run the clip network — ingest the owner's raw gameplay clips, render vertical variants, plan the posting schedule across Oneware's TikTok/YouTube/Instagram accounts, and learn from views. Use for /clips, "new clips", "plan this week's posts", or clip performance questions.
---

# Clip network manager

Read `marketing/clip-network.md` first; its rules on branded accounts and
no fake engagement are non-negotiable. If a request would cross them,
say why and offer the compliant version.

State: `marketing/clips/{bank,variants,accounts,hooks,posts}.csv`.
Media: `clips/raw/`, `clips/out/<game>/` (gitignored, so the cloud
container loses it when the session ends; send outputs to the owner or
run the tool on their Mac).

## Weekly cycle (default when run with no argument)

1. **Results**: for posts ≥ 48 h old without views, ask the owner to fill
   them in (or read them via API if tokens exist). Run
   `python3 tools/clips.py report`. Summarize: top 3 hooks, worst 3,
   best platform, best game, best moment tags.
2. **Hooks**: retire hooks that are below median after 3+ posts. Write
   5–10 new hooks in `marketing/clips/hooks.csv` modeled on the winners.
   Max ~6 words, specific, curiosity or challenge. No false claims (don't
   say "#1 game", don't show features the game doesn't have).
3. **Ingest**: for new files the owner provides,
   `python3 tools/clips.py add <files> --game <slug> --tags <moments>`,
   then `python3 tools/clips.py variants <clip ids> --count 4`.
4. **Plan**: `python3 tools/clips.py plan --days 7` (dry run), check
   for shortages, then rerun with `--commit`. Report how many raw clips
   are needed to cover any shortage.
5. **Hand-off**: give the owner the schedule CSV and the variant files
   (SendUserFile). Owner uploads to the scheduler. **Nothing is published
   without the owner's go-ahead.**
6. **Scale decision**: when an account averages > 1k views/post for two
   weeks, raise its `posts_per_day` by 1. When a platform averages < 200
   after 30 posts, lower its volume and move the effort elsewhere. Log
   changes in `studio/log.md`.

## Adding an account

Append to `accounts.csv` with `active=no` until the owner confirms it
exists, is branded, and has finished warm-up. `scope` is `studio` (all
games) or a game slug.
