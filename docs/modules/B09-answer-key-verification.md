# B09 — answer-key-verification

**Tier:** Backend
**Code location:** `services/api/app/verification/`
**Milestone:** 4
**Status:** not started

## Purpose

Trust. Code-based exercises are executed at generation time and the real output is
compared to the answer key the model claimed; on mismatch, the exercise is
regenerated. Wrong answer keys are fatal to a learning app — a user who is marked
wrong while being right stops believing the product — which is why this ships in
v1 rather than later.

## Scope

**Owns**
- Deciding which exercises are verifiable
- Extracting the snippet and the claimed answer from an exercise
- Running it via `B08` and comparing real output to the claim
- Output normalisation before comparison (whitespace, trailing newline, numeric
  formatting)
- Raising the regenerate signal to `B07`
- Marking `exercise.answer_key_verified`

**Does not own**
- Execution → `B08`
- Regeneration → `B07`, `B05`
- Non-code exercise correctness, which has no automated check

## Source references

- `FEATURE_PLAN.md` § 2 "Answer-key verification (trust)" (lines 69–72)
- `FEATURE_PLAN.md` § 7 "Services → Generation pipeline" (line 173)
- `FEATURE_PLAN.md` § 7 "Services → Sandbox" — used only for answer-key
  verification in v1 (line 174)
- `ARCHITECTURE.md` § "Code sandbox" — used at generation time for answer-key
  verification (lines 102–104)

## Depends on

`B08`, `B05`

## Depended on by

`B07`

## Data touched

Reads `exercise`; writes `exercise.answer_key_verified`.

## Verifiable exercise types

| Type | Verifiable | How |
|------|-----------|-----|
| Predict the output | **Yes** | Run the snippet, compare to the claimed output |
| Fill in the blank (code) | **Yes** | Substitute the answer, run, check it executes and produces the stated result |
| MCQ over code behaviour | **Partially** | Only when the correct option is an output claim |
| Order the steps | No | No executable claim |
| MCQ over prose | No | No executable claim |

## Decisions inherited

- **Executed at generation time, not at answer time** (`FEATURE_PLAN.md:70`) —
  which is what keeps the learner's feedback instant per `E06`.
- **Mismatch means regenerate**, not "flag and ship" (`FEATURE_PLAN.md:70`).
- **v1 verifies only; it does not run user-submitted code**
  (`FEATURE_PLAN.md:174`).

## Open questions

- How strict output comparison should be. Too strict regenerates good exercises
  and burns cost; too loose lets a wrong key through, which defeats the module.
  Normalisation rules need to be explicit and tested.
- What happens to an exercise that fails verification repeatedly — drop it, or
  fail the lesson? `E01` tolerates a missing exercise, which argues for dropping.
- Whether non-verifiable exercise types deserve any secondary check, such as a
  second-model review.

## Acceptance criteria

- [ ] Every verifiable exercise is executed before its lesson reaches `ready`
- [ ] A deliberately wrong answer key is detected and triggers regeneration
- [ ] Normalisation rules are explicit and unit-tested against realistic output
      differences
- [ ] An exercise that cannot be verified is recorded as unverified, never
      silently marked verified
- [ ] Verification cost and duration are visible in `F07` and do not breach the
      generation latency budget
