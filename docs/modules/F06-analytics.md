# F06 — analytics

**Tier:** Foundation
**Code location:** `packages/analytics/`
**Milestone:** 10 (taxonomy defined at milestone 1)
**Status:** not started

## Purpose

The event taxonomy and the SDK wiring that emits it, on both client and server.
This product is judged on retention curves — D1/D7, streak survival, onboarding
drop-off — so the events that feed those funnels must exist from the first build,
not be retrofitted before launch. PostHog is the deliberate step outside the
Google stack because it is purpose-built for exactly these questions.

## Scope

**Owns**
- The event taxonomy: names, properties, and which module emits each
- PostHog Flutter SDK wiring and the server-side emission path
- Identity handling across the guest → account transition, so a converted user's
  pre-signup events stay attached to them
- The `analytics_event` append-only log and its relationship to PostHog
- Funnel and cohort definitions for the metrics below

**Does not own**
- LLM cost and token accounting → `F07`
- Any product decision made from the data

## Source references

- `FEATURE_PLAN.md` § 7 "Services → Analytics" (line 177)
- `FEATURE_PLAN.md` § 7 "Data model" — `analytics_event` (line 169)
- `ARCHITECTURE.md` § "Analytics — PostHog" (lines 115–121)
- `FEATURE_PLAN.md` § "Verification" — success criteria (lines 228–230)

## Depends on

`F01` (`analytics_event`), `F03` (per-environment PostHog projects)

## Depended on by

Every `C`, `E`, and `B` module that emits an event.

## Event taxonomy (initial)

| Event | Emitted by | Why it exists |
|-------|-----------|---------------|
| `onboarding_step_viewed` / `_completed` | `C06` | Onboarding drop-off funnel — the single most important funnel in the app |
| `topic_submitted` | `C07` | Top of the activation funnel |
| `outline_shown` / `outline_confirmed` | `C07` | Where users abandon before first lesson |
| `generation_started` / `_succeeded` / `_failed` | `B07` | Success rate and latency against the `E06` budget |
| `first_card_rendered` | `E02` | The 60-second activation target |
| `exercise_answered` | `E01` | Correct/incorrect, latency — feeds difficulty and review |
| `lesson_completed` | `E01` | Core progression metric |
| `guest_converted` | `B02` | Soft-gate conversion rate |
| `goal_met` / `streak_incremented` / `streak_broken` | `B14` | Streak survival curves |
| `notification_sent` / `_opened` | `B18` | Whether the retention loop actually works |
| `review_session_completed` | `C17` | Review's contribution to the daily goal |
| `tutor_message_sent` | `B16` | Engagement and cost per user |
| `session_started` / `_finished` | `C01` | D1/D7 retention base |

## Decisions inherited

- **PostHog over Firebase Analytics + BigQuery.** Both could answer these
  questions, but the Google path requires building the analysis layer ourselves
  and that is not worth it for v1 (`ARCHITECTURE.md:120-121`).
- **Needed from day one** to tune difficulty and retention, not added at the end
  (`FEATURE_PLAN.md:177`).
- **Separate PostHog environments for staging and prod**
  (`ARCHITECTURE.md:148`).

## Open questions

- Client-side versus server-side emission for events that both could send —
  server is more reliable, client is closer to the user's actual experience.
- Whether `analytics_event` in Postgres duplicates PostHog or serves only as a
  replay buffer.
- PII minimisation: which properties are safe to send given the deletion
  obligation in `B02`.

## Acceptance criteria

- [ ] Every event in the taxonomy has exactly one documented emitter
- [ ] A guest who converts retains their pre-signup event history under one
      identity
- [ ] D1/D7 retention, onboarding drop-off, and streak survival are answerable
      from the events defined here without adding new ones
- [ ] Staging events never land in the production project
- [ ] Account deletion in `B02` removes or anonymises this user's analytics data
