---
name: feedback
description: Synthesize App Store reviews and player feedback for one or all Oneware games into themes, bugs and prioritized fixes, and draft developer responses. Use for /feedback [slug] or when asked what players are saying.
---

# Feedback

1. Pull reviews: `python3 tools/asc.py reviews <app_id> --limit 200` for
   the game (or every live game). Add any feedback emails/forms the owner
   pastes or saves under `data/feedback/`.
2. Cluster into themes: bugs, difficulty, ads, controls, content wanted,
   praise. Count, average rating per theme, 1–2 verbatim quotes each.
3. Map each theme to a pillar and a metric (e.g. "too many ads" →
   retention D1, monetization ad placement).
4. Prioritized fix list: severity × frequency ÷ effort.
5. Draft short, human developer responses for 1–3★ reviews that describe a
   fixable problem. **Owner approves before posting.**
6. Studio-wide run: note themes that recur across games — those are
   signals about our audience for the next wave of games.
7. Save to `reports/<date>-feedback[-slug].md`.
