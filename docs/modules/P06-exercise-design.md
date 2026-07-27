# P06 — exercise-design

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/exercises/`
**Milestone:** 2
**Status:** not started

## Purpose

What makes an exercise worth answering. The source fixes four auto-checkable types
and an interleave cadence, but the difference between an exercise that builds
memory and one the learner can answer by glancing at the previous card is entirely
in the design. This module owns that difference.

Also owns the answer-tolerance design behind fill-blank matching — the rules the
generator must emit alongside an answer so `C12` can grade fairly.

## Scope

**Owns**
- Which exercise type suits which concept and topic shape
- The novel-context rule that separates understanding from lookup
- Interleave placement and end-of-lesson set composition
- Scaffolding level per position in a lesson
- Answer-tolerance specification for fill-blank
- The auto-checkability constraint and what it rules out

**Does not own**
- Distractors → `P07`
- Explanations → `P08`
- Difficulty adjustment of these levers → `P09`
- Input controls and matching implementation → `C10`–`C13`
- Answer-key execution → `B09`

## Source references

- `FEATURE_PLAN.md` § 2 "Exercise types (all auto-checkable)" (lines 63–68)
- `FEATURE_PLAN.md` § 2 — fill in the blank, input adapts to difficulty; fuzzy /
  normalised answer matching, trim whitespace, case-insensitive where appropriate,
  accept known synonyms (line 66)
- `FEATURE_PLAN.md` § 2 "Lesson & card structure" — exercises interleaved at a
  healthy cadence, roughly every few concept cards plus an end-of-lesson set, so
  practice tracks the volume of new material (line 55)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — no hard fail; missed exercises re-queued
  (line 98)

## Depends on

`P01`, `P02`, `P03`

## Depended on by

`P07`, `P08`, `P09`, `P16`, `B05`, `C12`

## Type suitability

| Type | Tests | Best for |
|------|-------|----------|
| **Multiple choice** | Conceptual discrimination | Distinguishing similar ideas, surfacing misconceptions, "which is true here" |
| **Predict the output** | Semantics | Evaluation order, mutation, scope, gotchas — the tech vertical's sharpest tool |
| **Fill in the blank** | Precise recall | Syntax, API surface, exact terminology |
| **Order the steps** | Procedural knowledge | Workflows, algorithms, lifecycles — and structure, where a diagram would otherwise be needed |

Topic shape from `P03` biases the mix: a Tool/CLI course leans on order-steps and
fill-blank; a Concept/protocol course leans on MCQ and order-steps and may use no
code at all.

## The novel-context rule

The single most important rule here:

> An exercise must not be answerable by pattern-matching the card that precedes
> it. It must require applying the idea to a situation the learner has not
> already been shown.

An exercise whose answer is a phrase from the previous card tests scrolling, not
understanding. In practice: change the values, change the framing, or change the
direction of the question. This is scored as its own `P16` dimension because it is
the most common weakness in generated exercise sets.

## Interleave and scaffolding

Cadence tracks new material rather than a fixed quota (`FEATURE_PLAN.md:55`):

- **In-lesson**: an exercise after every 2–4 concept cards, checking material from
  those cards
- **End-of-lesson set**: covers every claim in the lesson at least once

Scaffolding follows the `P01` progression by position:

| Position | Stage | Support |
|----------|-------|---------|
| Immediately after a new concept | Scaffolded practice | Token bank, narrowed choices, partial answer |
| Later in the lesson | Independent practice | Support faded |
| End-of-lesson set | Independent | None |
| Review, cross-session (`B15`) | Independent, hardest | Free typing always |

## Auto-checkability

Every exercise must have a **decidable** answer (`FEATURE_PLAN.md:63`). This rules
out the open-ended questions that would otherwise be the natural way to test
understanding — "explain why this fails", "when would you use this instead". Those
are not lost; they are the **tutor's** territory (`:80`), and the exercise set
should hand off to it rather than approximate it badly.

A consequence worth stating: a course cannot assess synthesis. `P16` scores what
the exercise set *does* cover and does not penalise the absence of what the format
cannot support.

## Fill-blank answer tolerance

The generator must emit a **tolerance specification** alongside the answer, not
just the answer, so `C12` grades correctly (`FEATURE_PLAN.md:66`):

- **Whitespace** — always trimmed
- **Case** — insensitive in prose, **sensitive in code**, where case is meaning.
  The generator declares which applies; it is never inferred at grading time
- **Synonyms** — an explicit accepted list, generated with the exercise
- **Near-miss policy** — a genuinely equivalent answer is accepted silently; a
  rejected near-miss must show the expected answer prominently, because that is
  where the learner most suspects the app is wrong

A blank must have **one** defensible answer. If several are equally correct, it is
the wrong exercise type — use MCQ.

## Open questions

- Whether the novel-context rule can be checked mechanically — for example by
  n-gram overlap between an exercise and its preceding cards — or whether it is
  purely judge-scored.
- Whether the end-of-lesson set should have a size cap, given a dense lesson could
  otherwise produce a long tail before the win screen.
- Whether re-queued exercises (`E01`) should be re-presented identically or with
  values varied, which would test the concept rather than the memory of the miss.
- Whether predict-output should be MCQ-style or free text; free text is a truer
  test but reintroduces the tolerance problem in a harder form.

## Acceptance criteria

- [ ] Type selection is justified per exercise against the suitability table
- [ ] No generated exercise is answerable by copying from its preceding card,
      scored across the golden set
- [ ] Interleave cadence scales with concept density rather than sitting at a
      constant
- [ ] Scaffolding visibly fades within a lesson, and review is always unsupported
- [ ] Every fill-blank carries an explicit tolerance spec including case policy
- [ ] Every exercise has exactly one defensible answer
- [ ] The end-of-lesson set covers every claim in the lesson
