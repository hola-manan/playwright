# P13 — retrieval-at-generation

**Tier:** Pedagogy
**Code location:** `services/api/app/knowledge/retrieval/`
**Milestone:** 4
**Status:** not started

## Purpose

Getting the right corpus passages into the generation prompt, fast enough not to
break the product's headline latency promise. This module sits directly in front
of generation, which makes it the one place where content quality and perceived
speed are in genuine tension — and it owns resolving that tension.

## Scope

**Owns**
- Query formulation from topic, shape, and concept
- Retrieval strategy: top-k, relevance thresholds, tier weighting, deduplication
- **The retrieval-once-per-course policy** and context reuse across lessons
- The retrieval latency budget and its timeout
- Degradation to ungrounded generation
- Retrieval provenance, passed to `P14` for citation

**Does not own**
- Corpus construction → `P12`
- Source policy → `P11`
- How retrieved claims are hedged or cited → `P14`
- Prompt assembly and the token budget → `P10`

## Source references

- `FEATURE_PLAN.md` § 1 — outline appears within seconds, streamed (line 36)
- `FEATURE_PLAN.md` § 2 "Just-in-time generation" — first card visible within
  seconds (line 50)
- `FEATURE_PLAN.md` § 1 — topic to first card in under 60 seconds (line 30)
- `FEATURE_PLAN.md` § 1 "Edge cases" — never a dead end (line 41)
- `ARCHITECTURE.md` § "Auth + Database" — vector search (lines 55–56)

## Depends on

`P11`, `P12`, `P03` (shape), `F01`

## Depended on by

`P14`, `P16`, `B04`, `B05`, `B07`, `B16`

## Decisions inherited

Carries the same `ARCHITECTURE.md:55-56` divergence recorded in `P12`: vector
search moves from "a bonus for later" to v1 scope. No second datastore is
introduced; what is added is this hop in front of generation and the latency
budget below.

## The latency problem

`E06` requires the first outline row within 3s and the first card within 3s,
inside a 60-second topic-to-first-card target. Retrieval now sits ahead of
generation on both paths. Naively — retrieve per lesson, block until done — this
breaks the budget.

Three mitigations, in priority order:

### 1. Retrieve once per course

Retrieval happens **once, at outline time**, against the topic and its `P03`
shape. The resulting context is persisted with the course and reused for every
lesson in it. Lesson generation therefore pays **zero** retrieval latency, which
protects the more frequently-hit "first card within seconds" target entirely.

Per-concept top-up retrieval for a specific lesson is possible later but is
explicitly not v1: it would reintroduce the latency on the hot path.

### 2. Overlap with generation

Outline generation begins streaming as soon as retrieval returns, and later
outline sections may generate while remaining passages are still being scored.
Retrieval and generation are not strictly sequential.

### 3. Hard timeout with graceful degradation

**Proposed budget: 800ms**, once per course. On timeout, generation proceeds
**ungrounded**, with `P14` hedging rules applied and the course marked ungrounded
for `P16`.

This is the never-a-dead-end rule (`FEATURE_PLAN.md:41`) applied to grounding:
retrieval failure degrades quality, never availability. A user waiting on a
knowledge base is a worse outcome than a slightly less certain course.

> **`E06` action:** the latency table needs a "topic submitted → retrieval
> complete" row at 800ms, and the "first outline row" budget must be shown as
> accommodating it. `P13` and `E06` must agree before either is implemented.

## Retrieval strategy

- **Query formulation** uses the normalised topic and shape from `P03` plus the
  outline's concept list — never the user's raw text, which is short, sometimes
  misspelled, and a poor embedding target
- **Tier weighting** — tier 1 and 2 passages from `P11` outrank tier 3 at equal
  similarity
- **Relevance threshold** — passages below it are dropped rather than padded to
  top-k. Returning weak matches to fill a quota is how irrelevant grounding gets
  in
- **Deduplication** across documents from the same source
- **Provenance** — every passage carries its metadata through to `P14`

Returning **nothing** is a valid, correct outcome, and better than returning
something irrelevant.

## Open questions

- Whether 800ms is achievable against Data Connect vector search at corpus scale,
  including embedding the query. Needs measurement before `E06` commits to it.
- Whether retrieval should run *before* the outline (grounding the syllabus) or
  *after* (grounding lessons against a known concept list). Before is better for
  coverage; after gives far better queries. A two-pass approach would do both and
  costs a second hop.
- Whether cached shared courses in `B10` reuse their stored retrieval context or
  re-retrieve on corpus change — the latter is more correct and more expensive.
- How much retrieved context to include, given `P10`'s stated trim order puts
  retrieval first on the chopping block.

## Acceptance criteria

- [ ] Retrieval runs once per course; lesson generation performs no retrieval
- [ ] The measured budget is met at realistic corpus size, or `E06` is amended
      with an agreed number
- [ ] Retrieval timeout degrades to ungrounded generation without user-visible
      failure
- [ ] Below-threshold passages are dropped rather than padding to top-k
- [ ] Tier 1 and 2 sources outrank tier 3 at comparable similarity
- [ ] Every returned passage carries provenance through to `P14`
- [ ] A topic with no corpus coverage generates successfully and is marked
      ungrounded
