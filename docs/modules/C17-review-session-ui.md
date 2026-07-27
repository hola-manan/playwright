# C17 — review-session-ui

**Tier:** Client
**Code location:** `apps/mobile/lib/features/review/`
**Milestone:** 7
**Status:** not started

## Purpose

The daily review player. Works through the due set assembled by `B15`, drawn from
every course the user has touched. Deliberately built on the same surfaces as a
lesson — the exercise modules, `C14`'s feedback, and a win screen — so review
feels like the product rather than a separate mode.

## Scope

**Owns**
- The review session flow and its progress display
- Reusing the exercise modules with review-mode settings
- The review completion screen
- Cross-course context — showing which course an item came from
- Reporting review results to `B15` and `B12`

**Does not own**
- Scheduling and set assembly → `B15`
- Exercise rendering → `C10`–`C13`
- Feedback → `C14`
- XP → `E05`, `B14`

## Source references

- `FEATURE_PLAN.md` § 3 "Review mode (cross-session spaced repetition)"
  (lines 105–108)
- `FEATURE_PLAN.md` § 5 "Daily Review card" (line 144)
- `FEATURE_PLAN.md` § 2 "Exercise types" — free typing in review mode (line 66)
- `FEATURE_PLAN.md` § 3 "Session sizing" (lines 110–111)

## Depends on

`B15`, `C10`–`C14`, `E01`, `E04`, `E05`, `C02`

## Depended on by

`C16`

## Decisions inherited

- **Review counts toward the daily goal and streak**, so users have a fast option
  on busy days (`FEATURE_PLAN.md:108`).
- **The set spans all courses**, not just the active one
  (`FEATURE_PLAN.md:106`).
- **Fill-blank uses free typing in review mode** even where the original offered a
  token bank (`FEATURE_PLAN.md:66`).
- **The session targets the user's chosen daily minutes** with an honest time
  estimate before starting (`FEATURE_PLAN.md:111`).

## Feel spec

Review must feel like a fast win, not homework. It is the option a user picks when
they have five minutes and a streak to protect, so it should open immediately, show
a visibly finite set, and reach its completion screen quickly.

Because items come from different courses, each should carry a light course
attribution — enough for orientation, not enough to feel like a change of context
between every item.

The completion screen uses the same celebration vocabulary as `C15`, because
meeting the goal via review is exactly as legitimate as meeting it via a lesson.

## Latency budget

The session opens from the home screen within one frame of tap; the due set is
prefetched with the home screen's data. Per-item feedback is instant, as in a
lesson.

## Degradation

If the due set cannot be fetched, the home card should not have offered the
session. If connectivity drops mid-session, remaining items already fetched are
completed offline and results queue via `C04`.

## Accessibility

Identical to the exercise modules it reuses. Course attribution is announced once
per item, not repeated within it.

## Open questions

- Whether the re-queue mechanic from `E01` applies within a review session, or
  whether a missed review item simply reschedules via `B15`. The latter is more
  correct for spaced repetition.
- Whether the session shows a running count or a progress bar — a finite count is
  more motivating for a short set.
- Whether review can be started with fewer items than a full session.

## Acceptance criteria

- [ ] A session draws items from multiple courses in one sitting
- [ ] Fill-blank items use free typing regardless of their original mode
- [ ] Completing review meets the daily goal and increments the streak
- [ ] An honest time estimate is shown before starting
- [ ] Results reach both `B15` and `B12`
- [ ] The session completes offline once its items are fetched
