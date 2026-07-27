# B11 — enrollment-service

**Tier:** Backend
**Code location:** `services/api/app/enrollment/`
**Milestone:** 1
**Status:** not started

## Purpose

The link between a user and a course, and the home of everything that makes a
shared course personal. Skipped lessons, difficulty adjustments, and position in
the course live on the enrollment, layered over a `course` row that may be shared
with many other learners.

## Scope

**Owns**
- Creating and reading enrollments
- Personal deltas: skipped lessons, "I already know this" marks, difficulty
  adjustment
- Resolving a shared course plus deltas into the effective course for one user
- The user's course list and per-course progress percentage
- Course completion state

**Does not own**
- Course content → `B04`, `B05`
- Cache and sharing decisions → `B10`
- Per-lesson progress and results → `B12`

## Source references

- `FEATURE_PLAN.md` § 7 "Data model → enrollment" (line 164)
- `FEATURE_PLAN.md` § 2 "Cost control & reuse" — personalisation applied per user
  on top of a shared course (line 84)
- `FEATURE_PLAN.md` § 2 "Outline confirmation" — remove lessons, mark "I already
  know this", ask for more depth (line 49)
- `FEATURE_PLAN.md` § 5 "My courses list" (line 145)

## Depends on

`F01`, `B10`

## Depended on by

`C07`, `C16`, `B07`, `B12`

## Data touched

`enrollment` — read and write. `course` — read.

## Interface

Endpoints for enroll, list my courses, read effective course, and apply a delta.
The **effective course** resolution is this module's central function: given a
shared `course` and an `enrollment`, produce the lesson sequence this particular
user should see.

## Decisions inherited

- **A shared cached course is reused across users**, with variation living here
  rather than in duplicated content (`FEATURE_PLAN.md:160`, `164`).
- **The user can remove lessons, mark "I already know this", or ask for more depth
  on any part** before confirming (`FEATURE_PLAN.md:49`). Those edits are deltas,
  not edits to the shared course.
- **Progress percentage is per course** and shown in the course list
  (`FEATURE_PLAN.md:145`).

## Open questions

- Whether "ask for more depth on this part" produces a delta or triggers a fresh
  partial generation — the latter creates a course that is no longer purely
  shared.
- How a delta behaves when the underlying shared course is regenerated or
  versioned by `B10`.
- Whether completion is derived from `B12` progress or stored explicitly.

## Acceptance criteria

- [ ] Two users enrolled in the same shared course can hold different deltas with
      no interference
- [ ] Effective-course resolution is deterministic and unit-tested against a
      shared course with every delta type applied
- [ ] The course list returns accurate progress for in-progress and completed
      courses
- [ ] Removing a lesson at outline time is reflected everywhere the course is
      consumed, including `B07` scheduling
