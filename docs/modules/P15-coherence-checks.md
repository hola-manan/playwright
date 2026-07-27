# P15 — coherence-checks

**Tier:** Pedagogy
**Code location:** `services/api/app/generation/coherence/`
**Milestone:** 4
**Status:** not started

## Purpose

Deterministic checks across a whole course, catching the defects a program can
catch without asking a model. Because lessons generate just-in-time and
independently (`FEATURE_PLAN.md:50`), nothing otherwise guarantees that lesson 6
uses the same term as lesson 2, or that lesson 4 does not rely on something taught
in lesson 7.

Deliberately separate from `P16`/`P17`: these checks are cheap, fast, and
reproducible, so they run first and catch what judgement should never be spent on.

## Scope

**Owns**
- Terminology stability across a course
- Forward-reference detection
- Recap-card verification — no new information
- Duplicate coverage detection
- Orphan concept detection — outlined but never taught
- Feeding failures back to `B07` for targeted regeneration

**Does not own**
- Judged quality → `P16`, `P17`
- Structural schema validation of a single item → `B06`
- The rules being checked — terminology is `P05`, ordering is `P04`
- Factual accuracy → `P14`

## Source references

- `FEATURE_PLAN.md` § 2 "Just-in-time generation" — lessons generate independently
  as the user progresses (line 50)
- `FEATURE_PLAN.md` § 2 "Lesson & card structure" — recap card ends every lesson
  (line 54)
- `FEATURE_PLAN.md` § 2 "Outline confirmation" — the outline is a full syllabus the
  user confirms (line 49)

## Depends on

`P04` (concept graph), `P05` (terminology rules)

## Depended on by

`P17`, `B06`, `B07`

## The checks

| Check | Detects | Method |
|-------|---------|--------|
| **Terminology stability** | The same concept called different things across lessons | Concept-to-term map built at outline time; flag any card using an alias for a mapped concept |
| **Forward reference** | A term or construct used before the card that introduces it | Walk the ordered course, maintain an introduced set, flag first-use violations against the `P04` graph |
| **Recap integrity** | A recap card teaching something new | Every claim in a recap must match a claim already made in that lesson |
| **Duplicate coverage** | Two lessons teaching the same claim | Claim similarity across lessons above threshold |
| **Orphan concept** | The outline promises a concept no lesson delivers | Diff the `P04` concept graph against claims actually generated |
| **Broken progression** | Independent practice before any worked example for a concept | Check exercise scaffolding level against concept introduction order |

## Why deterministic first

A judge call costs money and latency and returns a probability. These checks cost
neither and return a fact. Anything mechanically decidable should be decided
mechanically — which also means `P17`'s judge budget goes entirely on things that
genuinely need judgement, like whether a caption teaches or narrates.

The `P04` concept graph is what makes most of this possible, which is the strongest
argument for persisting it rather than discarding it after ordering — noted as an
open question in `P04`.

## Feeding back

A failure identifies the **specific** card, exercise, or lesson at fault, so `B07`
regenerates that item rather than the whole lesson. A forward reference in lesson
6 is a lesson-6 problem; regenerating the course would be both expensive and
likely to reintroduce it.

Where a check fails repeatedly on the same item, `B07`'s bounded-retry rules apply
and the item is dropped or the lesson marked `failed` — `E01` already degrades
gracefully around a missing exercise.

## Open questions

- Whether these run per lesson as it generates, or once when a course completes.
  Per lesson catches problems earlier but cannot see forward; a hybrid — per
  lesson for local checks, whole-course for cross-lesson ones — is likely right.
- How claim similarity is computed for duplicate detection. Embeddings would reuse
  `P12` infrastructure but blur genuinely distinct-but-related claims.
- Whether terminology aliasing needs a per-topic dictionary from `P02`, since
  "function" and "method" are synonyms in some contexts and a meaningful
  distinction in others.
- Whether a course that a user has partly completed can be corrected mid-flight,
  or whether fixes apply only to future generations.

## Acceptance criteria

- [ ] All six checks run and produce item-level failures, not course-level verdicts
- [ ] A deliberately injected forward reference is caught
- [ ] A recap card containing new information is caught
- [ ] No check requires a model call
- [ ] Failures trigger targeted regeneration in `B07`, not whole-course
      regeneration
- [ ] Checks complete fast enough not to add a user-visible delay to the
      just-in-time pipeline
- [ ] Repeated failure on one item terminates per `B07` retry bounds rather than
      looping
