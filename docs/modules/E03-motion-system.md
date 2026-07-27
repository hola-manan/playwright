# E03 — motion-system

**Tier:** Engine
**Code location:** `apps/mobile/lib/engine/motion/`
**Milestone:** 1
**Status:** not started

## Purpose

The app's animation vocabulary, defined once. Flutter was chosen over React Native
*specifically* for animation quality — Impeller rendering to its own canvas for
pixel-identical, high-framerate custom animation in a "gamified, card-swipe,
micro-interaction-heavy learning app" (`ARCHITECTURE.md:38-41`). That advantage is
only realised if motion is a designed system rather than per-screen improvisation.
This module supplies the durations, curves, gesture physics, and transition
grammar every other client module composes.

## Scope

**Owns**
- Duration scale and curve set
- Card-advance choreography: tap, swipe physics, thresholds, rubber-banding
- Screen-transition grammar, including the shared-element hero into a lesson
- Staggered entrance used by streaming content
- Reduced-motion substitutions for every primitive
- The frame budget and the Impeller-safe patterns that protect it

**Does not own**
- Haptics, sound, particles, celebration → `E04`
- Colour, type, spacing, static components → `C02`
- What triggers a transition → the consuming module
- Gesture *meaning* (what a swipe does) → `E01`

## Source references

- `ARCHITECTURE.md` § "Mobile client — Flutter" (lines 37–46) — the entire
  rationale for the client stack
- `FEATURE_PLAN.md` § 3 "Card reader" — advance by tap or swipe, back allowed
  (lines 89–93)
- `FEATURE_PLAN.md` § 5 — the continue card as the hero of the home screen
  (line 143)

## Depends on

`C02` (tokens it animates between)

## Depended on by

Every `C` module, plus `E02` (stagger) and `E04` (shared curves).

## Interface

### Duration scale

| Token | Duration | Use |
|-------|----------|-----|
| `instant` | 90ms | State flips that should feel like no animation at all |
| `quick` | 160ms | Back navigation, dismissals, token selection |
| `standard` | 240ms | Card advance, most transitions, counters |
| `expressive` | 400ms | Screen transitions, hero |
| `celebratory` | 700ms | Win-screen beats (used by `E04`) |

### Curves

- **Standard** — `easeOutCubic`. Default for anything moving into place.
- **Entrance** — emphasized decelerate. Content arriving from a stream.
- **Interactive** — spring, tuned so a flung card settles without visible
  oscillation. Gesture-driven motion must track the finger, then spring.
- **Exit** — `easeInCubic`. Faster than its entrance; leaving should not linger.

### Card advance

- **Tap (right side)** — slide + fade at `standard`, motion begins on touch-down.
- **Swipe** — 1:1 finger tracking, then commit or return. Commit threshold: 35%
  of card width **or** velocity above 600 px/s, whichever fires first, so a fast
  flick works without a long drag.
- **Rubber-band** — resistance at the first card and at the unseen boundary. The
  "you cannot skip ahead" rule from `E01` is communicated by resistance, not by an
  error message.
- **Back** — the same transition reversed at `quick`. Going back should feel
  cheaper than going forward.

### Transitions

- Screens: push/pop at `expressive`.
- Tutor: modal sheet, so the card stays visible behind it — the tutor is
  context-aware and the UI should say so (`FEATURE_PLAN.md:80`).
- Lesson entry: shared-element hero from the home continue-card into the lesson
  header.
- Streaming items: staggered entrance, 40ms apart, total stagger capped at 400ms
  so a long outline does not crawl in.

## Invariants

1. No module defines its own duration or curve. If something needs a value not in
   the scale, the scale changes here.
2. Every primitive has a defined reduced-motion substitution.
3. Gesture-driven motion tracks the finger 1:1 before any easing applies.

## Failure modes

| Failure | Recovery |
|---------|----------|
| Frame drops on a low-end device | Motion degrades to the reduced-motion path automatically rather than stuttering |
| An animation is interrupted mid-flight | It must be interruptible from any point and settle correctly, never snap |
| Hero source widget unmounts mid-transition | Fall back to a plain push |

## Feel spec

The whole module is a feel spec. The governing principle: **motion carries
meaning**. Every animation answers "where did this come from, where did it go, and
can I still get back". Motion that only demonstrates capability is removed.

## Latency budget

60fps minimum, 120fps on capable displays — 16.6ms and 8.3ms frame budgets.
Impeller-safe patterns are mandatory: prefer transform and opacity, avoid
`saveLayer`, avoid unbounded blur, avoid rebuilding subtrees inside animation
ticks. Motion begins on touch-down, never after an async gap.

## Accessibility

`MediaQuery.disableAnimations` and the OS reduced-motion flag are honoured
globally:

- Translate and scale become cross-fades at `quick`
- Hero becomes a fade
- Stagger collapses to zero
- Spring physics become linear settles

Reduced motion must never remove information — if an animation was the only cue
that something moved, the reduced path needs a static equivalent.

## Open questions

- Exact spring constants for the card flick; needs tuning on a real device, not
  in a simulator.
- Whether the 120Hz path is enabled at launch or after profiling on target
  hardware.
- Whether golden tests can meaningfully cover motion, or whether this needs
  recorded frame-timing tests in `F05`.

## Acceptance criteria

- [ ] Every duration and curve used anywhere in the app resolves to a token here
- [ ] A card flick commits on velocity alone, without a 35% drag
- [ ] Rubber-band resistance is the only feedback when a user tries to skip ahead
- [ ] Reduced motion is honoured app-wide with no information lost
- [ ] Frame timing holds the budget on the lowest target device during a card
      swipe and the win screen
- [ ] Interrupting any animation mid-flight settles correctly
