# B12 — progress-service

**Tier:** Backend
**Code location:** `services/api/app/progress/`
**Milestone:** 5
**Status:** not started

## Purpose

The record of what a learner did. Per-lesson status, and per-exercise results with
correctness and latency. This log is the input to three other systems — difficulty
adaptation, spaced repetition, and the habit loop — so its completeness matters
beyond simply resuming a lesson.

## Scope

**Owns**
- `progress` rows: lesson status, started and completed timestamps
- `exercise_result` rows: correctness, latency, attempt number
- Ingesting result batches from `E01` (which may arrive late, after buffering)
- Idempotent writes so a replayed offline queue does not duplicate
- Serving resume state for an interrupted lesson

**Does not own**
- XP arithmetic and goal evaluation → `B14`
- Difficulty computation → `B13`
- Review scheduling → `B15`
- Client-side buffering → `C04`

## Source references

- `FEATURE_PLAN.md` § 7 "Data model → progress" (line 165)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — every answer result is logged (exercise
  id, correct/incorrect, latency), feeding both difficulty adaptation and
  cross-session review (line 99)
- `FEATURE_PLAN.md` § 3 "Lesson completion" (lines 101–103)

## Depends on

`F01`, `B11`

## Depended on by

`B13`, `B14`, `B15`, `C15`, `C16`, `E01`

## Data touched

`progress`, `exercise_result` — read and write.

## Decisions inherited

- **Latency is logged alongside correctness** (`FEATURE_PLAN.md:99`). It is not
  decoration: it is a difficulty signal and a review-quality signal.
- **Results feed both difficulty adaptation and cross-session review**
  (`FEATURE_PLAN.md:99`), so the log must be complete rather than sampled.
- **Re-queued attempts within a lesson are still attempts.** `E01` re-presents a
  missed exercise, and each presentation is its own result row with an incrementing
  attempt number — otherwise `B15` cannot tell a first-time miss from a
  eventually-cleared one.

## Open questions

- Whether the first attempt or the final attempt drives `B13`'s miss rate. The
  source says "per-lesson miss rate" (`:74`), which reads as first attempts.
- Retention and aggregation policy for `exercise_result` at volume.
- Whether lesson completion is written here or derived from the exercise log.

## Acceptance criteria

- [ ] Every exercise presentation produces exactly one result row
- [ ] Replaying a buffered offline batch produces no duplicates
- [ ] Latency is stored per attempt and is measured client-side from first paint
- [ ] Resume state is sufficient for `E01` to restore position and re-queue
- [ ] Attempt numbers distinguish a first-time miss from a cleared re-queue
