# P07 — distractor-design

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/distractors/`
**Milestone:** 3
**Status:** not started

## Purpose

The wrong answers. Separated into its own module because bad distractors are the
single most common way a generated multiple-choice question becomes worthless —
and because good ones do something no other part of the system can: they tell you
*what* a learner misunderstands, not merely that they were wrong.

`B06` currently checks that an MCQ has exactly one correct option. Nothing checks
whether the other three are plausible, diagnostic, or accidentally give the answer
away. This module is that standard.

## Scope

**Owns**
- The requirement that each distractor encodes a **named misconception**
- Anti-tell rules — no giveaways through length, specificity, or grammar
- Option count and composition
- The misconception label carried on the exercise payload
- Distractor rules for predict-output and, where applicable, fill-blank
- Distractor subtlety as a difficulty lever, for `P09`

**Does not own**
- Explaining the misconception after a miss → `P08`
- Which exercises are MCQ at all → `P06`
- Option rendering → `C10`
- Schema enforcement of option count → `B06`

## Source references

- `FEATURE_PLAN.md` § 2 "Exercise types" — multiple choice; all auto-checkable
  (lines 63–64)
- `FEATURE_PLAN.md` § 2 "Explanations & tutor chat" — every exercise's right/wrong
  explanation pre-generated with the lesson (line 79)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — wrong answers get the pre-generated
  explanation of *why* (line 97)
- `FEATURE_PLAN.md` § 2 "Difficulty adaptation" (lines 73–76)

## Depends on

`P01`, `P02`, `P06`

## Depended on by

`P08`, `P09`, `P16`, `B05`, `B06`

## The core requirement

> Every distractor encodes a **specific, named misconception** that a learner of
> this topic plausibly holds. It is carried on the exercise payload as a label.

This is the module's whole argument. A distractor generated to be merely *not the
answer* wastes the slot. A distractor generated from a real misconception turns
every wrong answer into a diagnosis — which `P08` then explains directly, and
which downstream could inform `B13` difficulty and `B15` review selection far more
precisely than a boolean.

The payload consequence: an MCQ option is not a string, it is a string plus a
misconception label plus its own explanation. That flows into `F01`'s `exercise`
schema, `B06`'s structural validation, and `P08`'s explanation structure.

## Anti-tell rules

Generated MCQs leak the answer in predictable ways. All of these are defects:

| Tell | Rule |
|------|------|
| Correct answer is longest | All options within a similar length band |
| Correct answer is most qualified or hedged | Consistent register across options |
| Distractors are grammatically inconsistent with the stem | All options parse identically against the stem |
| Absurd filler options | Every distractor must be genuinely tempting |
| "All of the above" / "None of the above" | **Never generated** — they test test-taking, not the subject |
| Correct answer is the most technically precise | Precision distributed across options |

## Composition

- **Three or four options total** — one correct, two or three distractors
- Every distractor is **wrong**, not merely worse. No defensible-alternative
  options: if a learner can argue an option is correct, the exercise is broken
- Distractors are **mutually distinct** misconceptions, not variations of one
- Option order is randomised, with no positional bias across a lesson

## Misconception sources for the tech vertical

Supplied by the `P02` pack, since these are vertical-specific. Recurring families:

- Off-by-one and boundary errors
- Confusing similar commands or functions (`git reset` vs `git revert`)
- Wrong mental model of state — mutation versus copy, reference versus value
- Order of evaluation and short-circuiting
- Scope and shadowing
- Synchronous versus asynchronous execution
- Confusing a tool's *default* with its only behaviour

A distractor drawn from one of these families is nearly always more useful than
one invented fresh.

## Difficulty interaction

Distractor **subtlety** is one of `P09`'s difficulty levers. Easier means greater
conceptual distance between the correct answer and the distractors; harder means
distractors that are close, plausible, and require precise understanding to
reject. Note that this changes difficulty **without changing coverage**, which is
exactly what the `P01` rule requires.

## Open questions

- Whether anti-tell rules can be checked mechanically. Length banding and
  grammatical parallelism probably can; genuine temptingness probably cannot and
  falls to `P16`.
- Whether the misconception label should be a free string or drawn from a
  controlled vocabulary per topic shape. Controlled would let `B15` schedule review
  by misconception, which is a strong future capability but real scope now.
- Whether three or four options is the default. Four gives more diagnostic
  surface; three is faster on a phone and easier to generate well.
- Whether predict-output distractors deserve their own rules — plausible-wrong
  outputs are a different generation problem from plausible-wrong claims.

## Acceptance criteria

- [ ] Every generated MCQ distractor carries a misconception label
- [ ] No distractor is a defensible alternative answer, verified by review of the
      golden set
- [ ] Correct answers show no length, specificity, or grammatical tell, measured
      statistically across generated exercises
- [ ] "All of the above" and "none of the above" never appear
- [ ] Option position of the correct answer is uniformly distributed
- [ ] Distractor subtlety demonstrably changes between difficulty levels while
      coverage stays identical
- [ ] `P08` explanations reference the labelled misconception rather than
      restating the correct answer
