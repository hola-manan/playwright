# B15 — review-scheduler

**Tier:** Backend (engine)
**Code location:** `services/api/app/review/`
**Milestone:** 7
**Status:** not started

## Purpose

Cross-session spaced repetition. It decides which previously-missed or
long-unseen exercises come back, and when, assembling a daily review set drawn
from every course the user has touched. Review is also the fast path to the daily
goal on a busy day, which makes it a retention feature as much as a learning one.

## Scope

**Owns**
- `review_item` state: box, interval, next-due date
- The scheduling algorithm and its promotion/demotion rules
- Assembling the daily review set across all of a user's courses
- Ingesting review results and rescheduling
- The due count shown on the home screen

**Does not own**
- The review player UI → `C17`
- XP awards for review answers → `B14`
- In-lesson re-queue, which is a different mechanism entirely → `E01`

## Source references

- `FEATURE_PLAN.md` § 3 "Review mode (cross-session spaced repetition)"
  (lines 105–108)
- `FEATURE_PLAN.md` § 7 "Data model → review_item" (line 166)
- `FEATURE_PLAN.md` § 5 "Daily Review card" (line 144)
- `FEATURE_PLAN.md` § 2 "Exercise types" — free typing in review mode (line 66)

## Depends on

`B12` (results), `F01`

## Depended on by

`C16`, `C17`, `B14`

## State machine

```
exercise missed ──▶ review_item created in box 1, due tomorrow
review answered correct ──▶ promote a box, interval stretches, next_due extends
review answered wrong   ──▶ demote to box 1, due tomorrow
long-unseen item ──▶ surfaced regardless of box
```

## Invariants

1. An item missed today comes back tomorrow (`FEATURE_PLAN.md:107`).
2. An item answered correctly repeatedly stretches out — intervals grow
   monotonically within a box progression.
3. The daily set spans all of the user's courses, not just the active one
   (`FEATURE_PLAN.md:106`).
4. Review results are recorded through `B12` like any other attempt, so they feed
   the same history.

## Failure modes

| Failure | Recovery |
|---------|----------|
| Due set is enormous after a long absence | Cap the daily set at a session-sized number and prioritise most-missed and most-overdue |
| An exercise's course was deleted | Drop the review item rather than serving a dangling reference |
| Timezone change shifts due dates | Due dates are local dates, computed as in `B14` |

## Decisions inherited

- **A simple, well-understood algorithm — Leitner boxes or SM-2-lite. Full FSRS is
  overkill for v1** (`FEATURE_PLAN.md:107`).
- **Review counts toward the daily goal and streak**, giving users a fast option on
  busy days (`FEATURE_PLAN.md:108`).
- **Built from exercises previously missed or not seen in a while, across all
  courses** (`FEATURE_PLAN.md:106`).
- **Fill-blank uses free typing in review mode** even where the original
  presentation offered a token bank (`FEATURE_PLAN.md:66`) — review is meant to be
  harder recall.

## Open questions

- Leitner versus SM-2-lite. Leitner is simpler to reason about and explain; SM-2
  gives smoother intervals. Either satisfies the source.
- Daily set cap, and whether it is fixed or scaled to the user's daily goal.
- Whether items from a completed course keep surfacing indefinitely.

## Acceptance criteria

- [ ] An item missed today is due tomorrow
- [ ] Repeated correct answers produce visibly stretching intervals
- [ ] The daily set draws from multiple courses in one session
- [ ] The due count on the home screen matches the set actually served
- [ ] A user returning after a month gets a session-sized set, not a backlog
- [ ] Review answers grant XP and can meet the daily goal on their own
