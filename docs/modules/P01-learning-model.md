# P01 — learning-model

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/`
**Milestone:** 2
**Status:** not started

## Purpose

The instructional spine. Every other pedagogy module is an application of the
rules defined here, and every generation prompt ultimately expresses them. The
source states its teaching intent as principles — "one idea per card",
"completeness, delivered short-form", coverage equivalent to a good external
source — but never operationalises them. This module makes them into rules a
generator can follow and a rubric can score.

Deliberately **vertical-neutral**: the launch vertical is tech, but the model
holds for any subject. Vertical specifics live in `P02`.

## Scope

**Owns**
- Concept granularity — what "one idea" means operationally
- The practice progression: worked example → scaffolded practice → independent
  practice
- Cognitive load ceilings per card and per lesson
- The course arc: fundamentals → application → pitfalls → next steps
- Mastery levels (recall / apply / analyse) and where each belongs
- Prerequisite discipline
- The principle that coverage is never traded for ease

**Does not own**
- Vertical-specific rules → `P02`
- Outline structure → `P04`
- Card and exercise specifics → `P05`, `P06`
- How rules become prompt text → `P10`
- Scoring against these rules → `P16`

## Source references

- `FEATURE_PLAN.md` § "Guiding principle: completeness, delivered short-form"
  (line 22)
- `FEATURE_PLAN.md` § 2 "Lesson & card structure" — one idea per card (line 53)
- `FEATURE_PLAN.md` § 2 "Depth / completeness" — equivalence to a good external
  source; fundamentals → practical application → common pitfalls → next steps
  (line 59)
- `FEATURE_PLAN.md` § 2 "Exercise types" — all auto-checkable (line 63)
- `FEATURE_PLAN.md` § 3 "Review mode" — spaced repetition (lines 105–108)

## Depends on

Nothing. This is the root of the pedagogy graph.

## Depended on by

`P02`–`P09`, `P16`, and through `P10` every generation prompt.

## The rules

### 1. Concept granularity — the one-idea test

A card teaches exactly one **claim**: a single statement the learner could be
tested on. The operational test:

> Can you write **one** exercise that checks exactly this card, no more and no
> less? If checking it properly needs two exercises, it is two cards.

This is what keeps cards short without capping depth. A dense lesson has more
cards, not longer ones (`FEATURE_PLAN.md:53`).

### 2. The practice progression

New material moves through three stages, and the generator must not skip ahead:

| Stage | What the learner sees |
|-------|----------------------|
| **Worked example** | The idea demonstrated fully, nothing withheld |
| **Scaffolded practice** | An exercise with support — a token bank, a narrowed choice, a partial answer |
| **Independent practice** | The same skill with the support removed |

Support is **faded**, not dropped. Exercises immediately after a new concept are
scaffolded; the end-of-lesson set is independent. This is the mechanism `P09`
adjusts when difficulty changes.

### 3. Cognitive load ceilings

- **One new thing per card.** A card may introduce a new term or a new
  construct, never both.
- **A term is defined before it is used.** No exceptions, and `P15` checks it.
- **New-concept budget per lesson:** 3–5 at the default depth. Exceeding it means
  splitting the lesson, not compressing the cards.
- Presentation must never add difficulty the subject does not have. If a learner
  struggles with how something is written rather than what it says, that is a
  defect.

### 4. The course arc

Every course covers, in order (`FEATURE_PLAN.md:59`):

```
fundamentals ──▶ practical application ──▶ common pitfalls ──▶ next steps
```

Ordering is not cosmetic: a pitfall cannot be taught before the thing it is a
pitfall *of*. `P04` enforces this at outline level.

### 5. Mastery levels

| Level | Where it belongs |
|-------|-----------------|
| **Recall** | Immediately after introduction; scaffolded |
| **Apply** | End-of-lesson sets; the default level for most exercises |
| **Analyse** | Later lessons, pitfalls sections, and review |

A course that never leaves recall has not taught the topic, however complete its
coverage. This is a rubric dimension in `P16`.

### 6. Retrieval practice and spacing

Exercises are **retrieval practice**, not assessment — their purpose is to
strengthen memory, which is why they interleave through a lesson rather than
sitting at the end (`FEATURE_PLAN.md:55`) and why review exists across sessions
(`:106`). Two consequences the generator must respect:

- Interleave cadence tracks the volume of new material, not a fixed quota
- A missed exercise is a learning event, not a failure — consistent with the
  no-hard-fail rule (`:98`)

### 7. Coverage is never traded for ease

The most important rule in this module, and it falls directly out of the guiding
principle (`FEATURE_PLAN.md:22`):

> The short-form is the **format**, not a limit on coverage. Making a course
> easier means **more scaffolding**, not less material.

An easier course has more worked examples, smaller steps, and more support — and
covers exactly the same ground. `P09` is bound by this.

## Interface

A rule document plus the prompt fragment expressing it, consumed by `P10` and
included in every generation prompt. Also the shared vocabulary — claim, stage,
level, arc phase — that `P16` scores against and that appears in the content
schema so `P15` and `P17` can check structural conformance.

## Open questions

- Whether the new-concept budget scales with the user's daily-goal minutes, or
  stays fixed with lesson count absorbing the difference.
- Whether "claim" should be an explicit field on the card schema in `F01`. It
  would make the one-idea test machine-checkable, at the cost of a wider schema.
- Whether analyse-level exercises are reachable with only the four auto-checkable
  types (`:63`), or whether analysis is inherently the tutor's territory.

## Acceptance criteria

- [ ] Every rule here is expressed in a `P10` prompt fragment and cited by at
      least one `P16` rubric dimension
- [ ] The one-idea test is applied in review of generated cards and catches
      multi-claim cards
- [ ] Generated lessons show the three-stage progression, verifiably: scaffolded
      exercises near new concepts, independent ones at the end
- [ ] No generated card introduces a term and a construct together
- [ ] An easier-difficulty course covers the same outline as the standard one,
      demonstrated on a golden topic in `P17`
- [ ] The model is stated without vertical-specific assumptions — a non-tech
      vertical could adopt it by writing only a `P02` pack
