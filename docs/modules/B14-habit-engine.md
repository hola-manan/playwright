# B14 — habit-engine

**Tier:** Backend (engine)
**Code location:** `services/api/app/habit/`
**Milestone:** 6
**Status:** not started

## Purpose

The retention engine, server side. It holds the authoritative XP ledger, evaluates
whether the daily goal was met, and derives the streak from daily activity
history. XP and the goal are one module because the goal *is* an XP target
internally — minutes are only the user-facing framing.

## Scope

**Owns**
- The authoritative XP total and award ledger
- Daily goal evaluation against the user's XP target
- `daily_activity` rows, one per user per local day
- Streak derivation from that history
- Local-midnight day boundaries computed against the user's stored timezone
- Serving streak, goal progress, and total XP to the home screen

**Does not own**
- The optimistic client ledger → `E05`
- The flame and ring visuals → `E04`, `C16`
- Notifications → `B18`
- Which actions earn XP → `E01` emits, this module records

## Source references

- `FEATURE_PLAN.md` § 4 "Daily goal" (lines 117–119)
- `FEATURE_PLAN.md` § 4 "XP" (lines 121–123)
- `FEATURE_PLAN.md` § 4 "Streak" (lines 125–128)
- `FEATURE_PLAN.md` § 7 "Data model → streak / daily_activity" (line 167)
- `FEATURE_PLAN.md` § 3 "Review mode" — review counts toward goal and streak
  (line 108)

## Depends on

`F01`, `B01` (timezone), `B12`

## Depended on by

`E05`, `C15`, `C16`, `B18`, `B15`

## State machine

```
award(xp) ──▶ add to today's daily_activity row (local date)
           └─▶ total >= user's xp_target ?
                  yes and not already met ──▶ mark goal_met ──▶ evaluate streak
                  no ──▶ hold

streak = count of consecutive prior local days with goal_met, ending today
```

## Invariants

1. The streak is **always derived** from `daily_activity`, never stored as an
   incrementing counter. This is what allows freezes to be added later without a
   migration (`FEATURE_PLAN.md:128`, `167`).
2. Day boundaries are the user's local midnight, computed from their stored
   timezone — never server time (`FEATURE_PLAN.md:119`).
3. The goal can be met only once per local day; re-crossing the threshold does not
   re-fire.
4. XP from review counts toward the goal and streak identically to XP from lessons
   (`FEATURE_PLAN.md:108`).
5. Award ingestion is idempotent — `E05` retries must not inflate the total.

## Failure modes

| Failure | Recovery |
|---------|----------|
| User changes timezone mid-streak | Recompute against the new timezone; never break a streak because someone flew |
| Offline awards arrive after local midnight | Attribute to the local date they were earned, not received — otherwise a genuine streak day is lost |
| Duplicate award submission | Idempotency key rejects it |
| Clock skew on the device | Server assigns the local date from server time plus stored timezone; the client does not decide the date |

## Decisions inherited

- **The daily goal is internally an XP target**; minutes are the user-facing
  framing, so review and lessons both contribute cleanly
  (`FEATURE_PLAN.md:118`).
- **XP values kept simple and legible** — correct exercise 10, lesson complete
  +20 as illustrative figures, with exact values a tuning detail rather than an
  architecture decision (`FEATURE_PLAN.md:122-123`).
- **No streak freezes or repair in v1**, explicitly deferred — but the history must
  be stored so freezes can be added later without migration pain
  (`FEATURE_PLAN.md:128`).
- **Deferred but data-model-relevant:** leagues, leaderboards, achievements
  (`FEATURE_PLAN.md:136`).

## Open questions

- Whether a partial-day timezone change can create two "local days" in 24 hours,
  and which one counts.
- Grace window for offline awards arriving well after the day ended — unbounded
  backdating is exploitable.
- Whether goal-met should be evaluated optimistically client-side by `E05`; a
  streak increment that later reverses would be a bad moment.

## Acceptance criteria

- [ ] Streak is computed purely from `daily_activity` with no stored counter
- [ ] A user in UTC+13 and one in UTC−8 both roll over at their own midnight
- [ ] Review-earned XP meets the goal identically to lesson-earned XP
- [ ] Replaying the award queue leaves the total unchanged
- [ ] Awards earned offline before midnight and synced after still count for that
      day
- [ ] A backdated freeze row can be inserted without a schema change
