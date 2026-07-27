# B13 — difficulty-adaptation

**Tier:** Backend (engine)
**Code location:** `services/api/app/difficulty/`
**Milestone:** 3
**Status:** not started

## Purpose

Keeps the course at the right level. It reads the learner's onboarding experience
level and their per-lesson miss rate, and emits a difficulty signal that `B05`
uses when generating the next lesson. Because generation is just-in-time, this
signal is always computed from the most recent performance data.

## Scope

**Owns**
- Per-lesson miss-rate computation
- The difficulty signal handed to `B05`
- The "open with a review card" instruction after a hard lesson
- Detecting two aced lessons in a row and raising the faster-pace offer
- Recording the resulting adjustment on the enrollment

**Does not own**
- **What "easier" and "harder" mean in content terms → `P09`.** This module
  computes *when* to adapt; `P09` defines *what changes*
- Generating easier or harder content → `B05`
- Presenting the pace toggle → `C15` or `C16`
- Spaced repetition, which is cross-session → `B15`

## Source references

- `FEATURE_PLAN.md` § 2 "Difficulty adaptation" (lines 73–76)
- `FEATURE_PLAN.md` § 2 "Just-in-time generation" — so adaptation always uses the
  latest performance data (line 50)
- `FEATURE_PLAN.md` § 1 "Quick calibration" — experience level feeds difficulty
  (line 35)

## Depends on

`B12` (results), `B11` (enrollment), `P09` (lever semantics), `F01`

## Depended on by

`B05`, `B07`, `C15`

## State machine

```
lesson completed ──▶ compute miss rate
   miss rate > ~40%  ──▶ signal: easier + open next lesson with a review card
   aced && previous aced ──▶ signal: offer faster/harder pace
   otherwise ──▶ signal: hold
```

## Invariants

1. The signal is computed after lesson completion and before `B07` schedules the
   next lesson — a late signal is a wasted signal.
2. Difficulty moves one step at a time; no lesson jumps two levels.
5. **Coverage is never reduced.** Per `P09`, an easier lesson has more
   scaffolding, not less material — the signal must never be interpretable as
   "teach less".
3. The faster-pace change is an **offer**, never automatic — the user opts in
   (`FEATURE_PLAN.md:76`).
4. Adaptation never rewrites an already-generated lesson.

## Failure modes

| Failure | Recovery |
|---------|----------|
| Lesson has too few exercises for a meaningful rate | Hold; do not adapt on noise |
| Results arrive late from an offline buffer | Recompute; if the next lesson is already generated, apply from the following one |
| Signal unavailable at generation time | `B05` falls back to the onboarding experience level |

## Decisions inherited

- **Inputs are experience level from onboarding plus per-lesson miss rate**
  (`FEATURE_PLAN.md:74`).
- **Miss more than roughly 40% of a lesson's exercises → next lesson is generated
  easier and opens with a review card** (`FEATURE_PLAN.md:75`).
- **Ace two lessons in a row → offer a faster or harder pace toggle**
  (`FEATURE_PLAN.md:76`). Offer, not impose.
- The 40% figure is a starting threshold, not a locked constant — it lives in
  config alongside the XP values.

## Open questions

- Whether first attempts or all attempts count toward the miss rate. First
  attempts match the intent of "miss rate"; all attempts punishes the re-queue
  mechanic.
- Minimum exercise count before the rate is trusted.
- Whether the signal should decay — one bad lesson after five good ones probably
  should not drop difficulty.

## Acceptance criteria

- [ ] A lesson missed above threshold produces an easier next lesson that opens
      with a review card
- [ ] Two aced lessons produce an offer, and declining it changes nothing
- [ ] The signal is available to `B07` before it schedules lesson N+1
- [ ] Difficulty never moves more than one step per lesson
- [ ] Late-arriving offline results do not corrupt an already-generated lesson
