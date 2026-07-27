# E01 — session-engine

**Tier:** Engine
**Code location:** `apps/mobile/lib/engine/session/`
**Milestone:** 2
**Status:** not started

## Purpose

The state machine that runs a lesson. It sequences cards and interleaved
exercises, decides what a wrong answer does, tracks what the user has seen, drives
the segmented progress bar, and decides when a lesson is finished. This is the
module that encodes the learning experience's rules — no-hard-fail, re-queue on
miss, no skipping ahead — as testable logic rather than as behaviour scattered
across widgets.

Pure Dart, no widgets. `C08` renders whatever state this engine is in.

## Scope

**Owns**
- The lesson state machine and all transitions
- Exercise interleave scheduling within a lesson
- The re-queue policy for missed exercises
- Seen/unseen tracking and the back-navigation rule
- Segmented progress computation
- Session sizing and the pre-start time estimate
- Mid-lesson resume state
- Emitting answer results, XP events, and analytics events

**Does not own**
- Rendering anything → `C08`, `C09`, `C10`–`C14`
- Animation and gesture physics → `E03`
- Reward feedback → `E04`
- Fetching or streaming content → `E02`
- Persisting results server-side → `B12`
- The XP arithmetic → `E05`

## Source references

- `FEATURE_PLAN.md` § 3 "Card reader" (lines 89–93)
- `FEATURE_PLAN.md` § 3 "Exercise flow" (lines 95–99)
- `FEATURE_PLAN.md` § 3 "Lesson completion" (lines 101–103)
- `FEATURE_PLAN.md` § 3 "Session sizing" (lines 110–111)
- `FEATURE_PLAN.md` § 2 "Lesson & card structure" — interleave cadence (lines 52–56)

## Depends on

`E02` (content arrival), `E05` (XP events), `C04` (resume persistence), `F02` (result shapes)

## Depended on by

`C08`, `C14`, `C15`, `C17`

## State machine

```
idle
 └─ start(lesson) ──▶ preparing
                       └─ first item available ──▶ card(0)

card(i) ──advance──▶ card(i+1) | exercise(j)      (per interleave schedule)
card(i) ──back─────▶ card(i-1)                    (only if already seen)

exercise(j) ──answer──▶ feedback(j, correct|incorrect)
feedback(j, correct)   ──▶ next item
feedback(j, incorrect) ──▶ append j to requeue ──▶ next item

last item ──▶ requeue empty?  ──yes──▶ complete
                              ──no───▶ requeue_drain

requeue_drain: present head
   correct   ──▶ remove from queue ──▶ queue empty? complete : requeue_drain
   incorrect ──▶ move to back of queue ──▶ requeue_drain
```

`complete` hands off to `C15`.

## Invariants

1. The user can never reach an item with index greater than
   `max_seen_index + 1`. Skipping ahead past unseen content is impossible
   (`FEATURE_PLAN.md:90`).
2. Back navigation is permitted only within the current lesson, and only to
   already-seen cards (`FEATURE_PLAN.md:90`).
3. `complete` is unreachable while the re-queue is non-empty — a missed exercise
   must be cleared to finish the lesson (`FEATURE_PLAN.md:98`).
4. Every exercise presentation emits exactly one result event, with latency
   measured from the exercise's **first paint** to answer submission — not from
   state entry (`FEATURE_PLAN.md:99`).
5. A wrong answer never blocks progress, never removes XP, and never ends the
   session. There is no fail state (`FEATURE_PLAN.md:98`).
6. Resume restores the exact position, the seen set, and the re-queue contents.

## Failure modes

| Failure | Recovery |
|---------|----------|
| Content stream stalls mid-lesson | Hold at the last available card; `E02` retries. If unrecoverable, offer "continue later" with progress preserved — never discard the session |
| Answer submission fails (network) | Buffer the result locally via `C04` and advance immediately. The user must never wait on the network to learn they were right |
| App killed mid-lesson | Resume from persisted position, including re-queue |
| A re-queued exercise's content is missing or corrupt | Drop it from the queue with a logged warning. Invariant 3 must never trap a user in an uncompletable lesson |
| Interleave schedule references an exercise that failed generation | Skip it and continue; `B07` regenerates out of band |

## Feel spec

The engine owns pacing, which is a feel decision even though it renders nothing:

- **Correct answer** → confirmation plays (`E04`), then auto-advance after a short
  beat. The user should not have to tap to acknowledge being right; that tax is
  paid dozens of times per lesson. Proposed default: auto-advance once the `E04`
  confirmation completes, roughly 600ms.
- **Wrong answer** → never auto-advances. The explanation needs reading, so the
  user taps to continue. This asymmetry is deliberate.
- **Card advance** → immediate. The transition begins on touch-down, not on
  response from anything.
- **Re-queue presentation** → a missed exercise reappearing at the end is framed
  as a second chance, not a penalty, and is visually identical to a first
  presentation.

## Latency budget

Cites `E06`. No transition in this engine may await a network call. Answer →
feedback is a single frame because the explanation was pre-generated with the
lesson (`FEATURE_PLAN.md:79`). Progress recomputation on every transition must
stay off the critical frame path.

## Degradation

If a lesson is only partially generated, the engine runs what exists and waits at
the boundary rather than showing an error — the user reads card 3 while card 4 is
still being written. If generation ultimately fails, the lesson ends gracefully at
the last complete item with progress banked.

## Accessibility

Auto-advance timing must respect the OS reduced-motion and any "increase time
limits" preference; when set, correct answers also require a tap. Progress state
must be exposed to screen readers as position and total.

## Open questions

- Auto-advance on correct: fixed delay, or tied to the `E04` animation's
  completion? The latter is more coherent but couples the modules.
- Where the interleave schedule is computed — here from the lesson payload, or
  server-side in `B05` and carried as data. Server-side is more cacheable.
- Whether re-queued items that are missed twice get a third presentation or are
  deferred to `B15` review instead.

## Acceptance criteria

- [ ] All six invariants are covered by unit tests, including the trap-prevention
      case in failure mode 4
- [ ] The engine runs a full lesson with no widget layer attached
- [ ] Killing the app at any state and relaunching resumes exactly, re-queue
      included
- [ ] No transition path performs or awaits I/O
- [ ] Answer latency is measured from first paint, verified against a rendered
      frame timestamp
