# B06 — content-validation

**Tier:** Backend
**Code location:** `services/api/app/generation/validation/`
**Milestone:** 4
**Status:** not started

## Purpose

The schema gate between the model and the database. Every generated card and
exercise is validated against a Pydantic model before it can be persisted, and
malformed output is regenerated automatically. Nothing invalid reaches a learner.

## Scope

**Owns**
- Pydantic schemas for every card type and every exercise type
- Structural rules beyond types: an MCQ has exactly one correct option, an
  order-steps exercise has at least three steps, a fill-blank has a token bank
  when required and an explicit tolerance spec, a lesson ends with a recap card
- Structural enforcement of the pedagogy payload: every distractor carries a
  misconception label and its own explanation (`P07`, `P08`); every fill-blank
  declares its case policy (`P06`)
- The regenerate-on-malformed loop and its retry ceiling
- The response schemas `B03` sends to Gemini

**Does not own**
- Whether an answer key is factually correct → `B09`
- Whether content is factually true beyond executable claims → `P14`
- Whether content is pedagogically any good → `P16`, `P17`
- Cross-lesson coherence → `P15`
- Generation itself → `B04`, `B05`
- Pipeline orchestration → `B07`

## Source references

- `FEATURE_PLAN.md` § 2 "Answer-key verification (trust)" — all generated lessons
  must pass schema validation; malformed output is regenerated automatically
  (line 71)
- `FEATURE_PLAN.md` § 7 "Services → Generation pipeline" — per-exercise schema
  validation (line 173)
- `ARCHITECTURE.md` § "Backend language — Python" — Pydantic as the cleanest way
  to validate Gemini's structured output (lines 61–65)

## Depends on

`B03` (response schemas), `F01` (target shapes), `P06`, `P07`, `P08` (the payload
shapes those rules require)

## Depended on by

`B07`, `B05`, `P17`

## Where this sits

Validation is the **first and cheapest** gate in a four-stage sequence, and
rejecting here means the later, costlier stages never run:

```
B06 schema  ──▶ B09 answer keys ──▶ P15 coherence ──▶ P17 judge
(free)          (sandbox)           (deterministic)   (model call)
```

## Decisions inherited

- **Malformed output is regenerated automatically**, not surfaced as an error
  (`FEATURE_PLAN.md:71`).
- **Pydantic is the validation layer**, and the same models drive Gemini's
  structured-output schema so validation failures should be rare by construction
  (`ARCHITECTURE.md:63-65`).
- **Validation is per-exercise**, so one bad exercise costs one regeneration
  rather than a whole lesson (`FEATURE_PLAN.md:173`).

## Open questions

- Retry ceiling before a lesson is marked `failed` — and whether the ceiling is
  per-exercise or per-lesson.
- Whether structural rules live in Pydantic validators or as a separate rule pass;
  the former keeps one source, the latter reads better.
- Whether a persistently invalid exercise can be dropped rather than failing the
  lesson, given `E01` handles a missing exercise gracefully.

## Acceptance criteria

- [ ] No card or exercise reaches the database without passing validation
- [ ] Every structural rule listed above is enforced and unit-tested
- [ ] An MCQ missing a misconception label or a per-distractor explanation is
      rejected structurally, before `P17` ever sees it
- [ ] A deliberately malformed model response triggers regeneration, not an error
      to the client
- [ ] The retry ceiling is bounded and a lesson that exceeds it transitions to
      `failed` rather than looping
- [ ] Validation models and Gemini response schemas cannot drift apart
- [ ] Schemas satisfy every output-shape requirement `P10` declares, checked
      whenever a prompt fragment version changes
