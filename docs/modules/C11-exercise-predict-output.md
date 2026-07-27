# C11 — exercise-predict-output

**Tier:** Client
**Code location:** `apps/mobile/lib/features/learn/exercises/predict_output/`
**Milestone:** 3
**Status:** not started

## Purpose

"What does this print?" — the exercise type that best fits the tech vertical, and
the one most dependent on `B09` having verified its answer key. Presents a code
snippet and collects the user's prediction of its output.

## Scope

**Owns**
- Snippet presentation within an exercise context
- The prediction input control
- Comparing the shown expected output against the user's answer for display
  purposes

**Does not own**
- Snippet rendering internals → reuses `C09`'s code renderer
- Answer-key correctness → `B09` guarantees it before this ever ships
- Feedback and re-queue → `C14`, `E01`

## Source references

- `FEATURE_PLAN.md` § 2 "Exercise types" — predict the output of a code snippet
  (line 65)
- `FEATURE_PLAN.md` § 2 "Answer-key verification" — code-based exercises executed
  in a sandbox at generation time (line 70)
- `FEATURE_PLAN.md` § 3 "Exercise flow" (lines 95–99)

## Depends on

`C14`, `C09` (code rendering), `E04`, `C02`

## Depended on by

`C08`, `C17`

## Interface

Implements the shared exercise contract from `C14`.

## Feel spec

The snippet and the answer control must be visible together — scrolling between
the code and the answer to compare them breaks the exercise. On a small screen
with a long snippet, the code area scrolls independently while the control stays
anchored.

On reveal, the real output is shown alongside the user's answer so the difference
is legible at a glance. This is the type where the explanation matters most, and
it must sit immediately under the comparison.

## Latency budget

Result within one frame per `E06`. No execution happens on device — the expected
output was verified server-side at generation time.

## Degradation

Fully offline-capable; the expected output ships with the exercise.

## Accessibility

Code respects dynamic type and scrolls rather than reflowing, matching `C09`.
Expected versus actual is distinguishable without colour.

## Open questions

- Whether the answer is multiple choice over candidate outputs or free text. Free
  text is a truer test; MCQ is far more forgiving to grade and matches the
  "auto-checkable" requirement more safely.
- Whitespace and formatting tolerance if free text is used — the same
  normalisation problem `B09` solves server-side.

## Acceptance criteria

- [ ] Snippet and answer control are usable together without scrolling between them
- [ ] The reveal shows expected and actual side by side
- [ ] Renders correctly for the launch language set
- [ ] Implements the `C14` contract
- [ ] Works fully offline
