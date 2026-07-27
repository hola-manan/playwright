# C08 — card-reader

**Tier:** Client
**Code location:** `apps/mobile/lib/features/learn/card_reader/`
**Milestone:** 2
**Status:** not started

## Purpose

The surface a lesson is read on. One card per screen, advanced by tap or swipe,
with a persistent segmented progress bar and a tutor entry point on every card.
This module is deliberately thin: `E01` decides what should be shown and what a
gesture is allowed to do, `E03` supplies the physics, and this module renders the
result and wires the gestures.

## Scope

**Owns**
- The card surface and its layout
- Gesture wiring: tap-right to advance, swipe, back
- The segmented progress bar
- The tutor entry point present on every card
- Hosting `C09` renderers and the exercise modules

**Does not own**
- Sequencing, seen-tracking, the back rule, progress computation → `E01`
- Swipe physics, thresholds, rubber-banding, transitions → `E03`
- Card content rendering → `C09`
- Exercise presentation → `C10`–`C14`

## Source references

- `FEATURE_PLAN.md` § 3 "Card reader" (lines 89–93)
- `FEATURE_PLAN.md` § 2 "Lesson & card structure" (lines 52–56)
- `FEATURE_PLAN.md` § 2 "Explanations & tutor chat" — tutor openable from any card
  (line 80)

## Depends on

`E01`, `E02`, `E03`, `C09`, `C02`

## Depended on by

`C17` (the review player reuses the surface)

## Decisions inherited

- **One card per screen; advance by tap on the right side or by swipe**
  (`FEATURE_PLAN.md:90`).
- **Back is allowed within a lesson to re-read a card, but you cannot skip ahead
  past unseen content** (`FEATURE_PLAN.md:90`). The rule lives in `E01`; this
  module must not implement its own version.
- **A persistent segmented progress bar** shows position within the lesson, so the
  user sees "3 of 7 cards, then exercises" (`FEATURE_PLAN.md:91`).
- **The tutor chat icon is available on every card** (`FEATURE_PLAN.md:93`).

## Feel spec

Advancing must feel weightless — it happens dozens of times per lesson, so any
friction compounds. Motion begins on touch-down, not on touch-up, so the card
tracks the finger from the first moment.

The progress bar is the reader's sense of pace. Segmenting it so cards and
exercises are visually distinct is what makes a long lesson feel finishable: the
user can see the exercises coming.

Attempting to skip ahead is answered by rubber-band resistance from `E03` — a
physical "not yet", never a message.

## Latency budget

Card advance begins within one frame of touch-down per `E06`. Rendering the next
card must not wait on anything, including image decode — there are no images
(`FEATURE_PLAN.md:56`).

## Degradation

When the next card has not streamed in yet, the reader holds at the current card
with a subtle indication that more is coming — not a spinner, not an error. If
generation ultimately fails, the lesson ends gracefully with progress banked, per
`E01`.

## Accessibility

Tap-to-advance must have a screen-reader-accessible equivalent that does not
depend on hitting the right-hand region. Progress is announced as position and
total. Reduced motion replaces slide transitions with cross-fades via `E03`.

## Open questions

- Whether the tutor icon is always visible or appears on scroll/idle — always
  visible is more discoverable, but it competes with the content on a small card.
- Whether the progress bar shows re-queued exercises, which would reveal how many
  the user missed. Probably not.
- Left-edge swipe conflicting with the OS back gesture on iOS.

## Acceptance criteria

- [ ] Tap and swipe both advance; back returns within the lesson only
- [ ] Skipping ahead is prevented by resistance, with no error message
- [ ] The progress bar segments cards and exercises distinctly
- [ ] The tutor is reachable from every card
- [ ] Advance begins on touch-down within one frame
- [ ] The reader contains no sequencing logic of its own
