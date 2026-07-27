# E05 — xp-scoring-engine

**Tier:** Engine
**Code location:** `apps/mobile/lib/engine/scoring/`
**Milestone:** 5
**Status:** not started

## Purpose

The client-side XP ledger. XP is the app's unit of progress — the daily goal is
internally an XP target (`FEATURE_PLAN.md:118`) — and the XP tick is the most
frequent reward moment in the product, firing on every correct answer. It
therefore cannot wait for a server round trip. This module keeps an optimistic
local total that updates instantly, then reconciles against `B14`'s authoritative
figure without the user ever seeing a number jump.

## Scope

**Owns**
- The optimistic local XP ledger and its award rules
- Reconciliation with the server total, including how a divergence is animated
- Guest XP accrual while offline, and the handoff at sign-up
- Idempotency keys so a retried award is never counted twice
- The values feeding the tick, the goal ring, and the win screen

**Does not own**
- The authoritative total, goal evaluation, or streak → `B14`
- Rendering the tick or ring → `E04`, `C16`
- When XP is earned → `E01`
- Persisting locally → `C04`

## Source references

- `FEATURE_PLAN.md` § 4 "XP" (lines 121–123)
- `FEATURE_PLAN.md` § 4 "Daily goal" — represented internally as an XP target
  (lines 117–119)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — XP tick on correct (line 97)
- `FEATURE_PLAN.md` § 1 — guest completes a full first lesson before any account
  exists (lines 36–37)

## Depends on

`C04` (local persistence), `B14` (server truth), `F02` (award shapes)

## Depended on by

`E04` (tick values), `C15` (win screen), `C16` (goal ring), `C17`

## Award rules

Per `FEATURE_PLAN.md:121-123`, kept deliberately simple and legible:

| Action | XP |
|--------|-----|
| Correct exercise | base award (e.g. 10) |
| Card completed | small award |
| Lesson completed | bonus (e.g. +20) |
| Correct review item | base award |

Exact values are a tuning detail, not an architecture decision
(`FEATURE_PLAN.md:123`) — they live in config, not in code.

## State machine

```
local_total ──award(id, amount)──▶ optimistic_total   (immediate, same frame)
                                        │
                                   queued for sync
                                        ▼
                        ┌── ack ──▶ confirmed, queue entry dropped
sync ──────────────────▶┤
                        └── server_total differs ──▶ reconcile(delta)
                                                        └─▶ animate to server value
```

## Invariants

1. An award updates the visible total in the same frame as the user's action.
   Nothing in the award path awaits I/O.
2. Every award carries an idempotency key; replaying the queue can never
   double-count.
3. The server total always wins on conflict.
4. A downward correction is animated, never snapped, and never re-triggers
   celebration in `E04`.
5. Guest XP accrued offline survives sign-up — a converting user does not lose the
   XP from their first lesson (`FEATURE_PLAN.md:37`).

## Failure modes

| Failure | Recovery |
|---------|----------|
| Award sync fails | Stays queued in `C04`, retried with backoff. The user sees their XP regardless |
| Queue replayed after a crash | Idempotency keys make it safe |
| Server total lower than local | Animate down over `standard`; do not celebrate; log the divergence — it means an award was rejected |
| Server total higher than local | Animate up; this is the normal case after a review on another device |
| Guest converts with a pending queue | `B02` migration must complete before the queue flushes, or awards attach to a dead identity |

## Feel spec

The tick is the product's heartbeat. It must feel like the app is *counting with
you*, which means it starts on your tap and never stutters. A number that hesitates
before moving reads as the app checking whether you deserved it.

Reconciliation is the subtle part: if the server disagrees, the number moves to
the truth smoothly enough that the user reads it as continued counting rather than
a correction.

## Latency budget

Cites `E06`. Award to visible change: same frame, zero network. Reconciliation
happens off the interaction path and never interrupts an in-flight tick.

## Degradation

Fully functional offline. XP accrues locally, the goal ring moves, the win screen
is accurate. Sync catches up when connectivity returns. The user should not be
able to tell they were offline during a lesson.

## Accessibility

With reduced motion, totals snap rather than count. Screen readers announce the
new total once per award, not per animation frame.

## Open questions

- Whether the local ledger evaluates goal-met optimistically too, or defers that
  to `B14` — an optimistic streak increment that later reverses would be a bad
  moment.
- Cap on queue size before forcing a sync or dropping to server-authoritative.
- Whether card-completion XP is awarded per card or batched at lesson end; batching
  is cheaper but weakens the per-card feedback loop.

## Acceptance criteria

- [ ] XP is visible within one frame of a correct answer, with the network
      disabled
- [ ] Replaying the full award queue produces an identical total
- [ ] A forced server/client divergence animates smoothly and does not re-celebrate
- [ ] A guest completing a lesson offline, then signing up, retains every point
- [ ] Award values are configurable without a code change
