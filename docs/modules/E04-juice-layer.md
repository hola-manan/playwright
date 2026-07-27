# E04 — juice-layer

**Tier:** Engine
**Code location:** `apps/mobile/lib/engine/juice/`
**Milestone:** 3
**Status:** not started

## Purpose

The reward layer: haptics, sound, the XP tick, and celebration choreography. The
feature plan specifies feel directly — "correct → satisfying confirmation + XP
tick" (`FEATURE_PLAN.md:97`) and the win screen as "the dopamine beat — keep it
snappy and celebratory" (`:102`) — and those sentences are the entire difference
between this app and a quiz form. This module makes them concrete, budgeted, and
consistent, so the reward is designed once rather than improvised per screen.

## Scope

**Owns**
- The haptic map, one entry per meaningful event
- Sound stings and the global sound toggle
- The XP tick: counter animation and the `+N` flyup
- Correct and incorrect answer feedback choreography
- The win-screen staged reveal
- Streak flame states and the goal ring sweep
- The particle budget

**Does not own**
- Durations and curves → `E03`
- When a reward fires → `E01`
- The XP number itself → `E05`
- Screen layout → `C14`, `C15`, `C16`

## Source references

- `FEATURE_PLAN.md` § 3 "Exercise flow" — satisfying confirmation + XP tick
  (lines 95–99)
- `FEATURE_PLAN.md` § 3 "Lesson completion" — the dopamine beat, snappy and
  celebratory (lines 101–103)
- `FEATURE_PLAN.md` § 4 "Streak" — prominent flame + count (lines 125–128)
- `FEATURE_PLAN.md` § 5 — goal progress ring (line 142)
- `ARCHITECTURE.md` § "Mobile client — Flutter" — micro-interaction-heavy
  (lines 37–41)

## Depends on

`E03` (durations, curves), `E05` (XP values), `C02` (colour tokens)

## Depended on by

`C14`, `C15`, `C16`, `C17`, `C10`–`C13`

## Interface

### Haptic map

| Event | Pattern |
|-------|---------|
| Card advance | Selection / light impact |
| Token selected (fill-blank) | Selection |
| Correct answer | Success notification |
| Incorrect answer | **Warning**, not error |
| Lesson complete | Success, heavier |
| Streak increment | Heavy impact, fired on the flame ignite frame |
| Goal met | Success |

The incorrect-answer choice is deliberate: an error haptic reads as punishment,
and the product's stated position is that a wrong answer costs nothing
(`FEATURE_PLAN.md:98`).

### Sound

On by default, respecting the OS silent switch, with one global toggle in `C19`.
Stings for correct, incorrect, and lesson complete. Short — under 400ms. Nothing
loops.

### XP tick

- Counter animates to the new total over `standard` with the standard curve.
- A `+N` label flies from the answer control to the XP total on an arc, `400ms`,
  fading at the end.
- The tick starts **on tap**, driven by `E05`'s optimistic value. It never waits
  for a server response (`FEATURE_PLAN.md:97` reads as instant, and `E06`
  requires it).

### Correct / incorrect

- **Correct** — checkmark draws on over 200ms, control scale-pops 1.0 → 1.12 → 1.0
  on the interactive spring, colour washes to the success token.
- **Incorrect** — damped horizontal shake: 3 oscillations, 300ms, 8px amplitude,
  decaying. The control alone shakes. **No full-screen red flash** — the screen is
  not angry at the user.

### Win-screen staged reveal

Sequenced, total under 1.5s so "snappy" survives contact with "celebratory":

```
0ms     XP counts up                      (celebratory, 700ms)
+150ms  accuracy figure fades in
+250ms  streak flame ignites  ── heavy haptic fires here
+400ms  continue CTA fades in and becomes tappable
```

The CTA is tappable from the first frame it exists — an impatient user is never
held hostage by the celebration.

### Streak flame and goal ring

- Flame: gentle idle flicker (cheap — not a per-frame shader), ignite burst on
  increment, desaturated slow pulse when the streak is at risk.
- Goal ring: sweeps to the new value over `standard`; on reaching the goal it
  overshoots slightly, settles, and fires a single burst.

### Particle budget

Particles fire at **lesson completion** and **streak milestones only** — never on
an individual correct answer. Rewarding every correct answer at maximum intensity
makes the reward meaningless by card six. This budget is the module's most
important constraint and the easiest one to erode.

## Invariants

1. No reward effect waits on a network response.
2. Every effect has a reduced-motion and a muted equivalent.
3. Particle effects fire only at the two sanctioned moments.
4. Nothing in this module blocks input — the user can always tap through a
   celebration.

## Failure modes

| Failure | Recovery |
|---------|----------|
| Haptics unavailable or disabled at OS level | Silently skip; never fall back to sound as a substitute |
| Sound asset missing | Skip the sting, keep the visual |
| Optimistic XP is later corrected downward by `E05` | Animate the correction; never snap, never re-celebrate |
| Frame budget exceeded during particles | Reduce particle count rather than dropping frames |

## Feel spec

The governing rule: **intensity must be earned**. A correct answer gets a
confirmation; a finished lesson gets a celebration; a streak milestone gets the
full treatment. If everything celebrates, nothing does.

Second rule: **feedback is instant, always**. Every effect here is driven by local
state and fires on the same frame as the user's action.

## Latency budget

Cites `E06`. Reward begins within one frame of touch-up. The win screen's full
sequence completes in under 1.5s. No effect may extend the time to the next
interactive state.

## Degradation

With sound off, haptics off, and reduced motion on, the app must still clearly
communicate correct, incorrect, XP change, and lesson completion — through colour,
icon, and static state. The reward layer is enhancement; the information it
carries is not.

## Accessibility

Reduced motion disables particles, converts shake to a static error state, and
snaps counters instead of animating them. The silent switch is respected. Colour
is never the only signal for correct versus incorrect — an icon always accompanies
it.

## Open questions

- Sound on or off by default. On matches the category norm; off is safer for a
  learning app used in public. Needs a product call.
- Whether the win-screen sequence is skippable by tapping, and whether skipping
  should feel rewarded rather than punished.
- Streak milestone thresholds that trigger the fuller celebration.

## Acceptance criteria

- [ ] Every event in the haptic map fires the specified pattern, verified on both
      platforms
- [ ] Incorrect answers use warning, never error, and never flash the screen
- [ ] The XP tick begins on tap with no network dependency
- [ ] The win-screen sequence completes under 1.5s with the CTA tappable from its
      first frame
- [ ] Particles appear at exactly two moments in the entire app
- [ ] With sound, haptics, and motion all disabled, all four states remain
      unambiguous
