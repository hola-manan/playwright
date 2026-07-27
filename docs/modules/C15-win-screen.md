# C15 — win-screen

**Tier:** Client
**Code location:** `apps/mobile/lib/features/learn/win_screen/`
**Milestone:** 5
**Status:** not started

## Purpose

The dopamine beat. XP earned, accuracy, streak status, and the continue CTA,
delivered as a staged celebration that stays snappy. It is also the hinge of
onboarding — the soft account gate in `C06` fires immediately after this screen,
while the user is holding something they do not want to lose.

## Scope

**Owns**
- The end-of-lesson summary layout
- Sequencing the `E04` staged reveal
- The continue-to-next-lesson CTA
- The goal-met moment when this lesson crossed the daily target
- Handoff to `C06`'s account gate on the first lesson

**Does not own**
- The celebration choreography → `E04`
- XP and streak values → `E05`, `B14`
- The account gate itself → `C06`

## Source references

- `FEATURE_PLAN.md` § 3 "Lesson completion" (lines 101–103)
- `FEATURE_PLAN.md` § 4 "Daily goal" — the day counts when the XP target is hit
  (lines 117–119)
- `FEATURE_PLAN.md` § 1 "Soft account gate" — after the first lesson's win screen,
  "You earned 40 XP, day-1 streak started!" (line 37)

## Depends on

`E04`, `E05`, `B14`, `C02`

## Depended on by

`E01`, `C06`, `C17`

## Decisions inherited

- **This is the dopamine beat — keep it snappy and celebratory**
  (`FEATURE_PLAN.md:102`).
- **Shows XP earned, accuracy, streak status, and a continue CTA**
  (`FEATURE_PLAN.md:102`).
- **If the daily goal was hit, this screen doubles as the goal-met moment**
  (`FEATURE_PLAN.md:103`).
- **On the first lesson it is immediately followed by the account gate**, and the
  gate's copy references what was just earned (`FEATURE_PLAN.md:37`).

## Feel spec

Sequenced by `E04`, under 1.5s total:

```
XP counts up → accuracy appears → streak flame ignites (heavy haptic) → CTA
```

Two rules govern it. First, **snappy beats grand**: the whole sequence is over
before an impatient user gets bored, and the CTA is tappable from its first frame
so nobody is held hostage by the animation. Second, **the streak is the emotional
payload** — the XP number is information, but the flame igniting is what the
account gate is about to ask the user to protect.

When this lesson met the daily goal, the goal-met beat is folded into the same
sequence rather than shown as a second screen.

## Latency budget

Appears within one frame of lesson completion — every value is already local via
`E05`. The full sequence completes under 1.5s per `E06`.

## Degradation

Offline, every figure is available from `E05`'s optimistic ledger. If the server
later corrects a value, `E05` animates the correction on the home screen rather
than re-showing this screen.

## Accessibility

The full summary is available as static text immediately, independent of the
animation sequence. Reduced motion snaps every value and removes particles while
keeping the information. The CTA is the first focusable element.

## Open questions

- Whether the sequence is skippable by tapping, and whether skipping should still
  award the full celebration on the home screen.
- What the screen shows when a lesson is completed with a low accuracy — the
  source is silent, and "celebratory" needs a floor.
- Whether streak status appears on every lesson or only when it changes.

## Acceptance criteria

- [ ] The full sequence completes under 1.5s with the CTA tappable from frame one
- [ ] XP, accuracy, and streak are all correct and available offline
- [ ] Goal-met folds into this screen rather than adding another
- [ ] On the first lesson, the account gate follows immediately and references the
      earned XP and streak
- [ ] Reduced motion preserves every piece of information
