# Shared analytics spec (every game ships with this)

One event schema across all games so `/studio-status` can compare them.
Any free SDK works (Firebase Analytics, GameAnalytics, TelemetryDeck);
pick one and use it everywhere. Record the choice in `studio/profile.md`.

## Required events

| Event | Params | Answers |
|---|---|---|
| `session_start` | `session_number` | Retention, sessions/day |
| `tutorial_step` | `step` (int), `completed` (bool) | Where new players quit (FTUE funnel) |
| `level_start` | `level`, `attempt` | Progression depth |
| `level_end` | `level`, `result` (win/lose/quit), `duration_s` | Difficulty spikes |
| `ad_offer` | `placement` | Ad opportunity count |
| `ad_watched` | `placement`, `reward` | Rewarded-ad engagement |
| `iap_view` | `product_id` | Store funnel |
| `iap_purchase` | `product_id`, `price_usd` | Revenue per product |
| `crosspromo_click` | `target_game` | Is the network working? |
| `feedback_opened` | — | Feedback reach |
| `review_prompt` | `trigger` | When we ask for ratings |

## Required in-game modules

1. **Cross-promo**: "More games" button + a card after a win (not after a
   loss). Reads a remote JSON list so new games appear without an update.
2. **Review prompt**: `SKStoreReviewController.requestReview` after a
   positive moment (e.g. 3rd win, session ≥ 3). Never after a loss.
3. **Feedback**: one-tap "Tell us what you think" → email or form link.

## Privacy

Fill in the App Privacy "nutrition label" to match the SDK. If any SDK
tracks across apps (most ad SDKs), show the ATT prompt.
