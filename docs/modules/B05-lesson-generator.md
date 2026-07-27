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
- Lesson prompt and response schema for cards and exercises
- The four card types: concept, code, example, recap
- The four exercise types: MCQ, predict-output, fill-blank, order-steps
- Exercise interleave placement within the lesson
- Pre-generated right/wrong explanations
- Difficulty targeting from the `B13` signal
- Streaming cards and exercises as they complete

**Does not own**
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

`B03`, `B04` (outline), `B13` (difficulty signal), `F01`

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
  hard requirement, not an optimisation.
- **Fill-blank input adapts to difficulty** — token bank at easier levels, free
  typing at harder levels and in review, which means the generator must emit
  tokens *and* an answer tolerant of fuzzy matching (`FEATURE_PLAN.md:66`).

## Latency budget

First card within 3s of outline confirmation per `E06`. Cards stream individually;
the lesson is usable long before it is complete.

## Open questions

- Whether interleave placement is emitted by the model or computed
  deterministically after generation — the latter is more controllable and more
  cacheable.
- Synonym lists for fuzzy fill-blank matching: generated per exercise, or a
  shared normaliser in `C12`.
- How the `B13` difficulty signal is expressed in the prompt without producing
  patronising content at the easy end.

## Acceptance criteria

- [ ] All four card types and all four exercise types are generated and validate
- [ ] Every exercise has a pre-generated explanation for both correct and
      incorrect answers
- [ ] Every lesson ends with a recap card
- [ ] Card count varies with concept density rather than sitting at a constant
- [ ] The first card streams within the `E06` budget
- [ ] Fill-blank exercises emit both a token bank and a free-typing answer key
- [ ] No image or diagram content is ever produced
