# C10 — exercise-mcq

**Tier:** Client
**Code location:** `apps/mobile/lib/features/learn/exercises/mcq/`
**Milestone:** 2
**Status:** not started

## Purpose

Multiple choice — the first exercise type built, and the reference implementation
of the shared exercise interface defined by `C14`. Every other exercise type
follows the contract this one establishes.

## Scope

**Owns**
- Option list presentation and selection
- Submission of the chosen option
- Its own correct and incorrect visual states, driven by `E04`

**Does not own**
- Feedback, explanation, re-queue → `C14`, `E01`
- Reward choreography → `E04`
- Content → `B05`

## Source references

- `FEATURE_PLAN.md` § 2 "Exercise types" — multiple choice (line 64)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — exercise fills the screen, answer
  control matches the type, MCQ buttons (line 96)

## Depends on

`C14` (interface), `E04`, `C02`

## Depended on by

`C08`, `C17`

## Interface

Implements the shared exercise contract from `C14`: receives an exercise payload,
emits an answer, and renders a result state on command. It does not decide
correctness and does not know what happens next.

## Feel spec

Options are large, unambiguous tap targets. Selection is immediate and visible
before submission resolves. On answer, only the chosen option and the correct one
change state — the rest stay quiet, so the eye goes to the two that matter.

Correct fires the `E04` confirmation and `E01` auto-advances. Incorrect shakes the
chosen option only, and waits for the user to read.

## Latency budget

Result state renders within one frame of tap per `E06` — correctness is known
locally and the explanation was pre-generated.

## Degradation

Submission is optimistic; a network failure never delays the result. The answer is
queued through `C04`.

## Accessibility

Options are a labelled radio group. Correct and incorrect are conveyed by icon and
text, never by colour alone. Every option meets the 44pt minimum even with four
long options on a small screen.

## Open questions

- Whether selection auto-submits or requires a confirm tap. Auto-submit is faster
  and matches the category; confirm prevents mis-taps.
- Option count range the renderer must handle gracefully.

## Acceptance criteria

- [ ] Renders and answers correctly from real generated content
- [ ] Result state appears within one frame of tap, offline included
- [ ] Only the chosen and correct options change state on reveal
- [ ] Implements the `C14` contract with no correctness logic of its own
- [ ] Meets tap-target and contrast requirements at four long options
