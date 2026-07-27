# B04 — outline-generator

**Tier:** Backend
**Code location:** `services/api/app/generation/outline/`
**Milestone:** 2
**Status:** not started

## Purpose

Turns a topic into a full syllabus. This is the highest-leverage generation step
in the product: it decides coverage, and everything downstream inherits its
structure. It is also the only step that uses Gemini 2.5 Pro, because volume is
one call per course and quality here sets up every lesson that follows.

## Scope

**Owns**
- Executing outline generation: the model call, streaming, and persistence
- Applying the `P03` shape classification and its scoping decision
- Applying `P04` curriculum rules and depth scaling
- Computing the normalised topic for the `B10` cache key, per `P03` rules
- Streaming outline rows as they are produced

**Does not own**
- Prompt content and composition → `P10`
- Topic shapes, coverage checklists, over-broad criteria, normalisation rules → `P03`
- Concept decomposition, ordering, lesson sizing, depth semantics → `P04`
- Retrieved grounding context → `P13`
- Lesson content → `B05`
- Outline editing by the user → `C07`, `B11`
- Cache storage and lookup → `B10`

## Source references

- `FEATURE_PLAN.md` § 2 "Flow" — topic entry, scoping question, outline
  confirmation (lines 47–49)
- `FEATURE_PLAN.md` § 2 "Depth / completeness" (lines 58–61)
- `FEATURE_PLAN.md` § "Guiding principle: completeness, delivered short-form"
  (line 22)
- `ARCHITECTURE.md` § "LLM — tiered" — Pro reserved for the outline (lines 87–90)

## Depends on

`B03`, `P03`, `P04`, `P10`, `P13`, `F08` (topic moderation), `F01`

## Depended on by

`B07`, `B10`, `C07`

## Data touched

Writes `course` (topic, `normalized_topic`, outline JSONB, depth, level).

## Interface

Streams outline rows over the `F02` envelope: each `item` is one lesson title,
one-liner, and estimated minutes. `done` carries the persisted `course` id.

## Decisions inherited

- **Lesson count is driven by the topic's actual scope, not a fixed range.** A
  narrow topic is a handful of lessons; a broad one is many
  (`FEATURE_PLAN.md:49`).
- **The coverage target is equivalence to a good external source** — the user
  should not finish and still feel they need to go read the real tutorial. The
  arc is fundamentals → practical application → common pitfalls → next steps,
  scaled by the chosen depth (`FEATURE_PLAN.md:59`). `P03` defines what that
  covers per topic shape; `P04` orders it.
- **Short-form is the format, not a limit on coverage** (`FEATURE_PLAN.md:22`).
  The prompt must not be tuned toward brevity.
- **Gemini 2.5 Pro, outline only** (`ARCHITECTURE.md:87-90`).
- **One scoping question maximum** for a broad topic, asked before anything is
  built (`FEATURE_PLAN.md:48`).

## Latency budget

First outline row within 3s per `E06`. This is the user's first evidence that the
product works, and it arrives before the outline is complete because rows stream.

## Open questions

- Whether depth control changes the prompt, the schema, or both. `P04` defines the
  two axes it must move along; the mechanism is this module's call.
- Whether retrieval (`P13`) runs before the outline or after it — see that
  module's open questions, since it changes what this one calls and when.

## Acceptance criteria

- [ ] A narrow and a broad topic produce visibly different lesson counts, without
      any fixed range in the prompt
- [ ] Depth control measurably changes coverage across all three settings
- [ ] An over-broad topic triggers exactly one scoping question, never a
      back-and-forth
- [ ] First row streams within the `E06` budget
- [ ] Topic text passes `F08` moderation before any generation cost is incurred
- [ ] The outline validates against its response schema every time
