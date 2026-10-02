# Clip network initiative

_Started 2026-10-02. Run with `/clips`. Review after 4 weeks._

**Goal:** get the studio and its games in front of strangers on TikTok,
YouTube Shorts and Instagram Reels at high volume, before and between
launches, so each release starts with an audience.

**Success at week 4:** 150+ posts published, at least one clip over 10k
views, a ranked list of hooks that work, and measurable profile → App
Store clicks.

## The line we don't cross

Every account is **openly Oneware's**: the studio or game name is in the
handle or bio ("by Oneware Games"). We don't run:

- accounts posing as independent fans, reviewers or clip pages,
- accounts that like, comment, share or follow each other to fake traction,
- bought followers, views or engagement,
- automated sign-ups, or new accounts to dodge a ban.

All three platforms ban coordinated inauthentic behavior. A takedown
usually hits the whole linked set of accounts, including the main studio
account, and posing as independent fans is a deceptive endorsement under
FTC rules. Branded accounts posting at high volume keep most of the
upside without that risk.

## Account structure (grow in stages)

| Stage | Accounts | When |
|---|---|---|
| 1 | `@onewaregames` on TikTok, YouTube, Instagram | Now |
| 2 | + one account per live game per platform (`@stackly.game`, bio "by Oneware Games") | When the game's pre-order page is live |
| 3 | + 1–2 themed showcase accounts ("Oneware Arcade: satisfying levels from Oneware games") | When there are 3+ games to rotate |

Add accounts slowly (a couple per week). Warm each one up: the first few
days, browse and watch the niche like a normal user before posting. Use
a professional/creator account type on Instagram and TikTok so analytics
are available.

## Volume math

| | Stage 1 | Stage 2 (3 games) |
|---|---|---|
| Accounts | 3 | 12 |
| Posts/day | 5 | ~15 |
| Variants/week | ~35 | ~105 |
| Raw clips/week from owner (4 variants each) | ~9 | ~26 |

A variant is posted **at most once per platform**. Posting the same
upload twice on one platform gets flagged as unoriginal content and
suppressed. Different hook text, different start point and a different
cut make each variant a distinct video.

## Pipeline

```
owner records raw clips ──► tools/clips.py add      (bank)
                            tools/clips.py variants (4 cuts per clip, hook + end card)
                            tools/clips.py plan     (schedule CSV across accounts)
            owner or scheduler publishes from the schedule
owner logs views/links ───► tools/clips.py report   (hook/game/platform/account ranking)
                            /clips adjusts hooks, mix and volume
```

**Who presses "post":** Claude can't log in to social accounts. Two options:
1. **Scheduler (recommended to start):** a multi-platform scheduler with
   bulk CSV upload (e.g. Metricool, Buffer, Later; check current plan
   limits on account count and bulk upload). Owner time is ~20 min/week
   to upload the week's videos and CSV.
2. **Official APIs (later):** YouTube Data API, Instagram Graph API
   (professional accounts), TikTok Content Posting API (requires app
   review before public posts). Tokens go in environment secrets and
   Claude posts directly. Worth it once volume is proven.

## What makes a clip work (owner's recording guide)

- Record at full resolution, 60 fps, portrait if possible. 20–60 s raw,
  with no UI overlays from the recorder.
- Capture **moments**: near-misses, big combos, the satisfying finish,
  a fail, a level that looks impossible, the first 10 s of a fresh run.
- The first second must already be moving. No logos or menus at the start.
- Game audio on. Platforms favor trending sounds, which the owner adds
  in-app when posting where possible.
- Tag clips when adding (`--tags near-miss,satisfying`) so the report
  can tell which kinds of moments work.

## Measurement

Fill `views` (and `likes`, `shares`, `profile_visits`, `url`) in
`marketing/clips/posts.csv` for posts 48 h old. Weekly, `/clips` ranks
hooks and moments, retires losing hooks, writes new ones in the style of
the winners, and shifts volume to the best platform. Profile visits and
App Store link clicks (bio link with an App Store campaign token,
`ct=tiktok-studio`) tie views to installs.
