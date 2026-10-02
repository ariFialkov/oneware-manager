---
name: release
description: Take a game from the bank to "Submitted for Review" on the App Store — readiness checks, store listing, privacy, IAPs, build status and launch-week plan. Use for /release <slug> or when the owner wants to ship a game.
---

# Release a game

Argument: game slug. Work through the checklist, mark each item done or
blocked, and stop at blockers with a precise ask for the owner.

## 1. Readiness
- Distinct from every live game in mechanic and look (Guideline 4.3).
  If it's close to a recent release, recommend a different game this week.
- Analytics events, cross-promo, review prompt and feedback wired
  (`studio/analytics-spec.md`). Missing → blocker.
- No placeholder art, debug menus, crashes on launch, or dead buttons
  (Guideline 2.1 / 4.2).

## 2. Store listing (draft with `/aso` logic)
Name (30), subtitle (30), keywords (100, comma-separated, no spaces, no
words already in name), promo text (170), description, 5 screenshots
following the hook → loop → progression → variety → reward story, age
rating answers, category, privacy policy URL, support URL. Write the
drafts into the game sheet.

## 3. Privacy and monetization
- App Privacy answers matching the analytics/ads SDKs; ATT if tracking.
- IAPs created and in "Ready to Submit" (`tools/asc.py iaps <app>`).
- Paid Apps Agreement active (owner checks App Store Connect → Business).

## 4. Build
- `tools/asc.py builds <app>`: newest build `processingState` = VALID.
- Uploads happen on macOS (Xcode Organizer, Transporter, or
  `fastlane pilot upload`). If no build is there, give the owner the
  exact steps.

## 5. Submit — CONFIRM FIRST
Show the full listing and checklist. Only after an explicit yes, submit
(App Store Connect or API) with release type "manual" so launch-day content
lines up. Record `in_review` in `games/catalog.csv`.

## 6. Launch week plan
Produce: day-0 build-in-public post, 7 daily clip ideas (use `/social`),
the Reddit sub to post in and its rules, and the cross-promo JSON entry to
add. Add these to `marketing/content-calendar.md`.
