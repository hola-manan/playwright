# C13 — exercise-order-steps

**Tier:** Client
**Code location:** `apps/mobile/lib/features/learn/exercises/order_steps/`
**Milestone:** 3
**Status:** not started

## Purpose

Arrange the steps, or order the lines — the most physically interactive exercise
type and the one most dependent on `E03`'s gesture physics. A draggable list where
the user reconstructs a correct sequence.

## Scope

**Owns**
- The draggable step list and reordering interaction
- Submission of the resulting order
- Per-position correct/incorrect reveal

**Does not own**
- Drag physics, spring behaviour, reorder animation → `E03`
- Feedback and explanation → `C14`
- Reward → `E04`

## Source references

- `FEATURE_PLAN.md` § 2 "Exercise types" — arrange the steps / order the lines
  (line 68)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — draggable step list (line 96)

## Depends on

`C14`, `E03` (drag physics), `E04`, `C02`

## Depended on by

`C08`, `C17`

## Interface

Implements the shared exercise contract from `C14`.

## Feel spec

This is the exercise type where feel *is* the exercise. Dragging must track the
finger 1:1 with no lag, the displaced item must move out of the way with
anticipation rather than snapping after the drop, and the dropped item must settle
on the interactive spring. A selection haptic fires on pick-up and on each
reorder.

On reveal, correct positions confirm in place and incorrect ones shake — showing
*which* steps were misplaced, not merely that the sequence was wrong. Partial
correctness is visible even though scoring is binary.

## Latency budget

Drag tracks at the full frame budget per `E06` — this interaction exposes dropped
frames more than any other in the app. Result within one frame of submission.

## Degradation

If drag is unavailable or the user cannot perform it, the accessible reorder
controls below are a complete alternative, not a lesser one.

## Accessibility

Drag-and-drop is not accessible on its own. This module must ship explicit
move-up / move-down controls, or a screen-reader reorder mode, that can complete
the exercise without any drag gesture. Reduced motion removes the displacement
animation but keeps the positional information.

## Open questions

- Step count range the layout must handle — long lists on small screens will need
  scrolling while dragging, which is the hardest case.
- Whether scoring is all-or-nothing or per-position. The source implies binary,
  but the reveal shows per-position information regardless.
- Whether items can be code lines with horizontal overflow, which conflicts with
  horizontal drag.

## Acceptance criteria

- [ ] Drag tracks the finger 1:1 and holds the frame budget while scrolling
- [ ] The reveal shows which specific positions were wrong
- [ ] The exercise is fully completable without any drag gesture
- [ ] Reduced motion preserves all positional information
- [ ] Haptics fire on pick-up and reorder
- [ ] Implements the `C14` contract
