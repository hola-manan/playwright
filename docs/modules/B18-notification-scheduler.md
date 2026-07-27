# B18 — notification-scheduler

**Tier:** Backend
**Code location:** `services/api/app/notifications/scheduler/`
**Milestone:** 6
**Status:** not started

## Purpose

Decides who gets notified, when, and with what copy. Two notifications exist: the
daily reminder at the user's chosen time, and an evening streak-at-risk nudge if
the goal is not yet met. Scheduling is server-driven precisely so the copy can be
personalised to the user's active course.

## Scope

**Owns**
- The scheduled job that computes each day's sends
- Timezone-aware send-time computation
- Quiet-hours and OS-permission-state enforcement
- Personalised copy generation referencing the user's active course
- The two-per-day cap
- Streak-at-risk evaluation against the daily goal

**Does not own**
- Delivery and tokens → `B19`
- Permission request UX → `C06`
- Reminder-time and quiet-hours settings storage → `B01`
- Goal and streak state → `B14`

## Source references

- `FEATURE_PLAN.md` § 4 "Notifications" (lines 130–134)
- `FEATURE_PLAN.md` § 7 "Services → Notification service" (line 176)
- `FEATURE_PLAN.md` § 1 "Notification permission" (line 38)
- `ARCHITECTURE.md` § "Notifications — FCM" (lines 110–113)

## Depends on

`B14` (goal state), `B11` (active course), `B01` (settings), `B19`

## Depended on by

`B19`, `F06`

## Decisions inherited

- **Daily reminder at the user-chosen time, with copy referencing their active
  course** — the source's own example is "Your Python course is waiting — 8 min to
  keep your streak" (`FEATURE_PLAN.md:131`).
- **Streak-at-risk evening nudge** if the goal is not met by a few hours before
  local midnight (`FEATURE_PLAN.md:132`).
- **Cap at these two per day — no spam** (`FEATURE_PLAN.md:133`).
- **Respect OS permission state and a quiet-hours setting**
  (`FEATURE_PLAN.md:133`).
- **Server-driven so copy can be personalised**, with local fallbacks
  (`FEATURE_PLAN.md:134`, `ARCHITECTURE.md:112-113`).

## Open questions

- What runs the schedule on a scale-to-zero Cloud Run service — Cloud Scheduler
  hitting an endpoint is the obvious fit but is not yet a locked decision.
- How many hours before local midnight the streak-at-risk nudge fires.
- What the local fallback notification says, given it cannot be personalised.
- Whether a user who has already met their goal still gets the daily reminder.

## Acceptance criteria

- [ ] Both notifications fire at the correct local time across several timezones
- [ ] Quiet hours suppress sends, and suppressed sends are not queued up to
      deliver later in a burst
- [ ] No user receives more than two per day under any circumstance
- [ ] Copy names the user's actual active course
- [ ] A user who has met their goal does not receive a streak-at-risk nudge
- [ ] Users with OS permission denied are never scheduled
