# B05 — lesson-generator

**Tier:** Backend
**Code location:** `services/api/app/generation/lesson/`
**Milestone:** 2
**Status:** not started

## Purpose

Turns one outline entry into a finished lesson: a run of cards followed by
interleaved and end-of-lesson exercises, with a pre-generated explanation attached
to every exercise. Streams so the first card is readable long before the lesson is
finished. Runs on Gemini 2.5 Flash, because this is the high-volume call and
courses are deliberately unbounded in length.

## Scope

**Owns**
- Executing lesson generation: the model call, streaming, and persistence
- Emitting all four card types and all four exercise types per their rules
- Applying the `P09` difficulty levers from the `B13` signal
- Attaching per-distractor explanations to every exercise
- Streaming cards and exercises as they complete

**Does not own**
- Prompt content and composition → `P10`
- What a good card contains → `P05`
- Exercise design, interleave placement, answer tolerance → `P06`
- Distractors and misconception labels → `P07`
- Explanation structure and tone → `P08`
- What "easier" and "harder" mean → `P09`
- Retrieved grounding context and hedging → `P13`, `P14`
- Schema validation and the regenerate loop → `B06`
- Answer-key execution → `B09`
- Which lesson to generate when → `B07`

## Source references

- `FEATURE_PLAN.md` § 2 "Lesson & card structure" (lines 52–56)
- `FEATURE_PLAN.md` § 2 "Exercise types" (lines 63–68)
- `FEATURE_PLAN.md` § 2 "Explanations & tutor chat" — explanations pre-generated
  with the lesson (line 79)
- `FEATURE_PLAN.md` § 2 "Just-in-time generation" (line 50)
- `ARCHITECTURE.md` § "LLM — tiered" — Flash for lessons, exercises, tutor
  (lines 85–86)

## Depends on

`B03`, `B04` (outline), `B13` (difficulty signal), `P05`–`P10`, `P13`, `P14`, `F01`

## Depended on by

`B06`, `B07`, `B09`, `E02`, `C08`

## Data touched

Writes `lesson`, `card`, `exercise`.

## Decisions inherited

- **No fixed card or lesson count.** The constraint is *one idea per card*, so a
  dense lesson simply has more cards. Lessons stay finishable in a sitting; a
  longer topic means more lessons, not longer cards (`FEATURE_PLAN.md:53`).
- **Exercises interleave at a healthy cadence** — roughly every few concept cards,
  plus an end-of-lesson set — so practice tracks the volume of new material rather
  than a fixed quota (`FEATURE_PLAN.md:55`).
- **A recap card ends every lesson** (`FEATURE_PLAN.md:54`).
- **No AI-generated diagrams or images in v1** — quality is too unreliable for
  teaching material (`FEATURE_PLAN.md:56`).
- **Every exercise carries its explanation, generated with the lesson.** This is
  what makes post-answer feedback zero-latency (`FEATURE_PLAN.md:79`) and is a
  hard requirement, not an optimisation. Per `P08`, explanations are
  **per-distractor** — an MCQ with three wrong options needs three of them, which
  is the main generation-cost consequence of the pedagogy tier.
- **Fill-blank input adapts to difficulty** — token bank at easier levels, free
  typing at harder levels and in review, which means the generator must emit
  tokens *and* an answer tolerant of fuzzy matching (`FEATURE_PLAN.md:66`).

## Latency budget

First card within 3s of outline confirmation per `E06`. Cards stream individually;
the lesson is usable long before it is complete.

## Open questions

- Whether interleave placement is emitted by the model or computed
  deterministically after generation from `P06`'s cadence rules — the latter is
  more controllable and more cacheable.
- Whether per-distractor explanations are generated in the same call as the
  exercise or a follow-up call. One call is cheaper; two give better targeting.
- How the `P09` levers are expressed — in the prompt, in the schema, or both.
  `P09` requires they be unambiguous rather than left to model interpretation.

## Acceptance criteria

- [ ] All four card types and all four exercise types are generated and validate
- [ ] Every exercise has a pre-generated correct-path explanation and one
      explanation per distractor, each targeting its labelled misconception
- [ ] Every lesson ends with a recap card
- [ ] Card count varies with concept density rather than sitting at a constant
- [ ] The first card streams within the `E06` budget
- [ ] Fill-blank exercises emit both a token bank and a free-typing answer key
- [ ] No image or diagram content is ever produced
