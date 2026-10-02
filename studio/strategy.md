# Strategy — Months 1–2: "Release, measure, double down"

_Last updated: 2026-10-02_

## The bet

We can ship good small games in days. Paid user acquisition is out of
budget, so the edge has to come from **volume of experiments** plus **free
distribution we own**. The bank of finished games is our test budget: each
release is an experiment that teaches us what our players want.

## What changes from the original plan

The core plan (release the bank one at a time, learn, build the next wave
for the players we find) is sound. Four adjustments:

1. **Instrument before releasing, not after.** App Store Connect analytics
   only counts players who opted into sharing data, lags 1–2 days, and has
   no in-game funnel. Without our own events we can't tell *why* a game
   loses players. Every game ships with the same small event set
   (`studio/analytics-spec.md`) so games can be compared like-for-like.

2. **Every game advertises every other game.** A cross-promo slot (a
   "More from Oneware" button plus an occasional interstitial card) turns
   game #1's players into game #5's first downloads. That's the only free
   outreach that grows with the catalog. Build it once as a shared module.

3. **Watch out for Apple's spam rule (Guideline 4.3).** Apple rejects
   accounts that ship many similar or template-based apps, and repeat
   rejections can threaten the developer account itself. Every release must be
   clearly distinct in mechanic and art, with a real store listing.
   Never ship reskins back to back.

4. **Pick the release order for marketability, not just polish.** Our main
   free channel is short-form video (TikTok, YouTube Shorts, Reels). Rank
   the bank on "does a 7-second silent vertical clip make someone want to
   play?" A game that looks satisfying in a clip goes first.

## The "AI-run studio" angle is itself marketing

A studio run as a public experiment with an AI manager makes a story
people follow. Build-in-public posts (weekly numbers, what we changed, what
happened) can reach r/gamedev, r/iosgaming, IndieHackers, X and TikTok
#gamedev audiences that a single casual game never would. Use it.

## Cadence

- **1 release per week** (not faster: each launch needs a content week,
  and it keeps us clear of 4.3).
- **Launch week per game:** day 0 release + build-in-public post; days 1–7
  one gameplay clip per day across TikTok/Shorts/Reels; one Reddit post in
  the right sub (follow sub rules, no spam).
- **Weekly review every Monday** (`/weekly-review`).

## Release gates (per game, judged 14 days after launch)

Rough casual-mobile ranges; we replace them with our own medians once
we have 4+ live games.

| Metric | Kill / park | Iterate | Double down |
|---|---|---|---|
| D1 retention | < 25% | 25–35% | > 35% |
| D7 retention | < 6% | 6–12% | > 12% |
| Product page → install | < 15% | 15–30% | > 30% |
| Avg session length | < 3 min | 3–6 min | > 6 min |

- **Double down** → micro-influencer campaign, update with more content,
  feature it first in cross-promo.
- **Iterate** → one targeted update aimed at the weakest metric, re-judge.
- **Kill / park** → stop promoting; keep it live as a cross-promo source
  unless reviews are hurting the studio's rating.

**No money is spent on a game that hasn't reached "double down."**

## Monetization stance

IAP alone rarely carries a casual game. Standard lean setup:
rewarded ads (player chooses to watch for a reward) + a "Remove ads" IAP
+ an optional small IAP pack. Keep interstitials light until D1 is proven.
Requires an active **Paid Apps Agreement** (App Store Connect → Business).

## Weeks 1–8

| Week | Focus |
|---|---|
| 0 (setup) | Catalog the bank + score it; ASC API key; analytics + cross-promo + review prompt module; studio socials (one handle everywhere); privacy policy page |
| 1 | Release game #1; first build-in-public post |
| 2 | Release #2; first data from #1 |
| 3 | Release #3; first `/game-report` on #1 |
| 4 | Release #4; first gate decision on #1–2; first micro-influencer test if a game qualifies |
| 5–6 | Continue releases; update the strongest game; compare genres |
| 7–8 | Write the "player profile" from data; brief the first purpose-built game for it |

## North-star metrics for this phase

1. Total weekly installs across the catalog (outreach).
2. Best D1 retention of any game (have we found something players like?).
3. Cross-promo installs as a share of total (is the network compounding?).
