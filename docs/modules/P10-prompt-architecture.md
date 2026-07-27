# P10 — prompt-architecture

**Tier:** Pedagogy
**Code location:** `services/api/app/generation/prompts/`
**Milestone:** 2
**Status:** not started

## Purpose

The machinery that turns pedagogy rules into actual prompts. Each `P01`–`P09`
module owns a rule *and* the fragment expressing it; this module owns the
registry, the composition, and — critically — the **versioning** that lets a
prompt change be cached against, regression-tested, and rolled back.

The separation matters: change what the AI teaches by editing a pedagogy module's
fragment; change how prompts are assembled by editing this one.

## Scope

**Owns**
- The fragment registry and its ownership map
- Prompt composition per task: outline, lesson, tutor, judge
- Few-shot exemplars, versioned alongside fragments
- **Prompt versioning** — a content hash over the composed prompt
- Declaring the **response-schema requirements** each prompt implies, which `B06`
  implements and enforces
- The prompt token budget and how fragments compete for it

**Does not own**
- What any rule says → `P01`–`P09`
- Retrieved context selection → `P13`
- Model invocation → `B03`
- Response validation → `B06`

## Source references

- `ARCHITECTURE.md` § "LLM — tiered" — structured output via response schema
  (lines 91–92)
- `ARCHITECTURE.md` § "Backend language — Python" — Pydantic validates structured
  output (lines 61–65)
- `FEATURE_PLAN.md` § 2 "Cost control & reuse" (lines 83–85)
- `FEATURE_PLAN.md` § 2 "Answer-key verification" — malformed output regenerated
  (line 71)

## Depends on

`P01`–`P09` (fragments)

## Depended on by

`B04`, `B05`, `B10`, `B16`, `P17`

## Schema coupling

A prompt and its response schema must agree, but the dependency runs downstream,
not up: this module **declares** what shape the output must take, and `B06`
implements the Pydantic model and enforces it. `B06`'s acceptance criteria carry
the obligation that the two cannot drift apart when a fragment version changes.

## Composition

A prompt is assembled, never written whole:

```
system  = P01 spine
        + P02 vertical pack
        + P03 shape rules for this topic's shape
        + P09 difficulty settings

task    = outline:  P04 curriculum rules
        | lesson:   P05 cards + P06 exercises + P07 distractors + P08 explanations
        | tutor:    P08 tutor standard + P14 grounding
        | judge:    P16 rubric

context = P13 retrieved passages (when available)
schema  = B06 response schema for the task
```

Only fragments relevant to the task are included — a lesson prompt does not carry
outline rules. Composition is deterministic, so the same inputs always produce the
same prompt, which is what makes versioning and caching sound.

## Versioning

Every fragment is independently versioned, and the composed prompt carries a
**content hash** over the fragments that went into it. That hash is what:

- `B10` includes in the cache key, so improving a fragment invalidates exactly the
  cached courses that used it, rather than everything or nothing
- `P17` watches, so any change triggers a regression run against the golden set
- Rollback targets, when a prompt change scores worse

Without this, prompt improvement is unsafe: you cannot tell whether generated
content came from the current rules or a superseded version.

## Few-shot exemplars

Some rules are far easier to show than to state — caption-versus-narration in
`P05`, a distractor that encodes a misconception in `P07`, the four-beat structure
in `P08`. Exemplars live here, versioned with the fragments they illustrate, and
are drawn from content that scored well in `P17`. Good generated output becomes the
next version's exemplar.

## The token budget

Every fragment and every retrieved passage competes for the same context window,
and the tension is real: the full pedagogy stack plus retrieval could crowd out
the material being taught. This module owns the budget and the priority order when
it is exceeded — with a stated default that **retrieved context is trimmed before
pedagogy rules are**, because ungrounded-but-well-taught degrades more gracefully
than grounded-but-badly-taught, and `P14` has an explicit hedging path for thin
grounding.

## Open questions

- Whether prompts are stored as files, database rows, or code. Files version
  naturally with git and review well in a PR, which argues for files.
- Whether fragment changes need a promotion workflow — staging first, gated on
  `P17` — or whether a regression run on the PR is enough.
- Whether the judge prompt (`P16`) should share the spine fragments. Sharing risks
  a judge that agrees with the generator's blind spots; not sharing risks the
  judge scoring against a different standard.
- How much of the difficulty setting belongs in the system prompt versus the
  schema, given `P09` wants unambiguous levers rather than model interpretation.

## Acceptance criteria

- [ ] Every `P01`–`P09` rule set has exactly one fragment, and no rule text lives
      outside its owning module
- [ ] Composition is deterministic — identical inputs produce an identical prompt
      and hash
- [ ] Changing one fragment changes the hash and invalidates only the affected
      `B10` cache entries
- [ ] A fragment change triggers a `P17` regression run before it can ship
- [ ] Rollback to a prior prompt version is a single operation
- [ ] The assembled prompt stays inside the token budget with retrieval context
      attached, with a tested trim order
