# E06 — experience-spec

**Tier:** Engine (specification only — no code)
**Code location:** this document
**Milestone:** 1
**Status:** not started

## Purpose

The app's feel contract. `ARCHITECTURE.md:38-41` justifies the entire client stack
on animation quality and micro-interaction density, and `FEATURE_PLAN.md` states
timing promises in prose scattered across seven sections. This document collects
them into principles, a measurable latency budget, a degradation ladder, and an
accessibility floor — so "does it feel right" becomes a check rather than an
opinion.

Every Tier C and Tier E spec cites this file. It is the one place a timing target
can be changed.

## Scope

**Owns**
- The feel principles
- The latency budget table and its measurement points
- The degradation ladder for slow and failed generation
- The accessibility floor

**Does not own**
- Any implementation → `E01`–`E05` and Tier C
- Visual design tokens → `C02`

## Source references

- `FEATURE_PLAN.md` § 1 — topic to first card in under 60 seconds (line 30)
- `FEATURE_PLAN.md` § 1 — outline within seconds, streamed (line 36)
- `FEATURE_PLAN.md` § 2 — first card visible within seconds (line 50)
- `FEATURE_PLAN.md` § 2 — explanations pre-generated, zero latency after answering
  (line 79)
- `FEATURE_PLAN.md` § 3 — satisfying confirmation + XP tick, no hard fail
  (lines 95–99)
- `FEATURE_PLAN.md` § 3 — the dopamine beat, snappy and celebratory (line 102)
- `FEATURE_PLAN.md` § 1 — edge cases, never a dead end (lines 40–43)
- `ARCHITECTURE.md` § "Mobile client — Flutter" (lines 37–46)

## Depended on by

`E01`–`E05`, and all of `C01`–`C19`.

## Principles

1. **Instant feedback.** The user never waits for a server to learn whether they
   were right. Explanations are pre-generated with the lesson precisely so this
   holds (`FEATURE_PLAN.md:79`).
2. **Never a dead end.** Every failure state offers a next action. A failed
   generation offers retry and a pre-cached starter topic; a stalled lesson banks
   progress and offers "continue later".
3. **Never block on the network.** Local optimistic state first, reconcile after.
   This applies to XP, progress, and navigation.
4. **No punishment.** A wrong answer costs nothing but a re-queue. No lives, no
   score loss, no red screen, no error haptic.
5. **One dopamine beat per lesson.** Confirmation on every correct answer;
   celebration at completion. Intensity is earned, not sprayed.
6. **Motion carries meaning.** Every animation answers where something came from
   and where it went. Motion that only demonstrates capability is removed.
7. **Progress over spinners.** On any wait longer than a moment, show the work
   happening — streaming content, skeletons — never an indeterminate spinner.

## Latency budget

| Moment | Target | Owner | Source |
|--------|--------|-------|--------|
| App launch → interactive | < 1.5s | `C01` | derived |
| Topic submitted → first outline row | < 3s | `E02`, `B04` | `:36` "within seconds" |
| Outline confirmed → first card rendered | < 3s | `E02`, `B05` | `:50` "within seconds" |
| **Topic → first card, end to end** | **< 60s** | `C06`, `C07` | `:30` |
| Answer submitted → feedback visible | < 1 frame | `E01`, `C14` | `:79` pre-generated |
| Answer → XP tick begins | < 1 frame | `E04`, `E05` | `:97` |
| Card advance → motion begins | on touch-down | `E03` | derived |
| Tutor message → first token | < 2s | `E02`, `B16` | derived |
| Win-screen full sequence | < 1.5s | `E04` | `:102` "snappy" |
| Frame budget | 16.6ms / 8.3ms at 120Hz | `E03` | `ARCHITECTURE.md:38-41` |

Measurement points are instrumented in `F06` so these are reported, not assumed.
The 60-second target is the single most important number in the table: it is the
stated design goal of the most important screen sequence in the app
(`FEATURE_PLAN.md:30`).

## Degradation ladder

Applied to any generation wait, implemented in `E02`:

| Elapsed | What the user sees |
|---------|--------------------|
| 0–1s | Skeleton. No spinner |
| 1–5s | Content appearing progressively as it streams |
| 5–15s | Reassuring copy naming the work: "Building your Git course…" |
| > 15s | Keep waiting, or take a pre-cached starter topic — both offered |
| failure | Friendly retry plus the starter topic |

The rule underneath: **the user's first run is never a dead end**
(`FEATURE_PLAN.md:41`).

## Accessibility floor

- OS reduced-motion honoured app-wide, with no information conveyed by motion
  alone (`E03`)
- Silent switch respected; sound never required to understand state (`E04`)
- Dynamic type supported; code cards may scroll horizontally rather than reflow
- Contrast meets WCAG AA
- Minimum 44pt tap targets, which the exercise controls in `C10`–`C13` must
  respect even at their densest
- Correct/incorrect never signalled by colour alone
- Screen reader labels on every exercise control, and sane announcement cadence
  for streaming content

## Open questions

- Whether the 60-second target is measured from app open or from topic submission
  — the source says "topic → first card" but the sequence begins earlier.
- Whether the > 15s starter-topic offer is a hard cut or user-dismissible.
- Whether frame budget is enforced in CI (`F05`) or profiled manually per release.

## Acceptance criteria

- [ ] Every row in the latency budget is instrumented and reported to `F06`
- [ ] The 60-second target is measured end to end on a mid-tier device on a
      typical connection, and met
- [ ] Every principle maps to at least one enforced acceptance criterion in
      another module
- [ ] The degradation ladder is implemented and reachable in testing by throttling
- [ ] The accessibility floor is verified with OS settings at their most
      restrictive, and the app remains fully usable
