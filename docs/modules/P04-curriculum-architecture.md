# P04 — curriculum-architecture

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/curriculum/`
**Milestone:** 2
**Status:** not started

## Purpose

Outline-level design: how a topic's concepts are decomposed, ordered, and packed
into lessons. This is where the source's two structural commitments are enforced —
that lesson count follows the topic's actual scope rather than a fixed range, and
that a lesson stays finishable in a sitting. It is also where depth control does
its work.

The outline is the single highest-leverage artefact in the product: everything
downstream inherits its structure, and it is the one thing the user reviews before
committing.

## Scope

**Owns**
- Concept decomposition into a prerequisite graph
- Lesson ordering, and the no-forward-reference guarantee
- Lesson sizing against the user's session length
- How the three depth settings scale coverage and granularity
- Placement of the course arc phases
- Where a review card opens a lesson after a hard one

**Does not own**
- What "comprehensive" covers → `P03`
- Card and exercise content → `P05`, `P06`
- Checking coherence after generation → `P15`
- Executing outline generation → `B04`

## Source references

- `FEATURE_PLAN.md` § 2 "Outline confirmation" — full syllabus end to end; lesson
  count driven by scope, not a fixed range; depth control scales coverage and
  granularity (line 49)
- `FEATURE_PLAN.md` § 2 "Lesson & card structure" — lessons sized to stay
  finishable in a sitting; a longer topic means more lessons, not longer cards
  (line 53)
- `FEATURE_PLAN.md` § 2 "Depth / completeness" — the course arc (line 59)
- `FEATURE_PLAN.md` § 3 "Session sizing" — a session targets the user's chosen
  daily minutes, with an honest estimate before starting (lines 110–111)
- `FEATURE_PLAN.md` § 2 "Difficulty adaptation" — next lesson opens with a review
  card after a hard one (line 75)

## Depends on

`P01`, `P02`, `P03`

## Depended on by

`P09`, `P15`, `P16`, `B04`, `B05`

## Concept graph and ordering

Outline generation is a two-step process, not one:

1. **Decompose** the topic into concepts, with prerequisite edges between them.
2. **Order** them by topological sort, then pack into lessons.

Doing it in one step is how forward references appear — the model writes a
plausible-sounding lesson list without ever checking that lesson 4 does not rely
on something taught in lesson 6. Making the graph explicit makes the guarantee
checkable, and `P15` verifies it after generation.

**No forward references** is absolute: no lesson may use a term or construct
introduced later. Where a genuine cycle exists in the subject, it is broken by
teaching a simplified form first and refining it later — and the refinement is
declared, not silent.

## Arc placement

The course arc from `P01` maps onto lesson ranges:

```
fundamentals ──▶ practical application ──▶ common pitfalls ──▶ next steps
```

A pitfall cannot precede the thing it is a pitfall of, so the ordering is a
constraint on the sort, not a suggestion. "Next steps" is always the final lesson
and is the one place the course may reference material it does not teach.

## Lesson sizing

A lesson targets the user's chosen daily minutes — Casual 5, Regular 10, Serious
15 (`FEATURE_PLAN.md:35`) — and the outline carries an honest estimate the UI
shows before the user starts (`:111`).

Sizing works in one direction only: **a longer topic produces more lessons, never
longer lessons** (`:53`). When a concept group exceeds the sitting budget it
splits, and the split happens at a prerequisite boundary so neither half has a
forward reference.

## Depth control

The source says depth "scales how much the outline covers and how granular each
lesson gets" (`:49`) — two axes, and conflating them is a common mistake:

| Depth | Coverage (breadth of the graph) | Granularity (cards per concept) |
|-------|--------------------------------|--------------------------------|
| **Quick intro** | Core path only; optional branches pruned | Coarser — one card per concept |
| **Solid working knowledge** | Full checklist from `P03` | Default |
| **Deep / comprehensive** | Full checklist plus edge cases and adjacent concepts | Finer — concepts split into sub-claims |

Quick intro **prunes branches**; it does not compress the cards on the path it
keeps. That distinction preserves the `P01` rule that coverage is never traded for
ease — a shallower course teaches less *ground*, but what it teaches, it teaches
properly.

## Difficulty interaction

When `B13` reports a hard lesson, the next lesson opens with a **review card**
(`:75`). That card restates the prior lesson's claims in new words — it is not a
repeat, and it does not count against the new-concept budget. `P09` owns the rest
of the difficulty response; this module owns only where the review card sits.

## Open questions

- Whether the concept graph is persisted or discarded after ordering. Persisting
  it would let `P15` check forward references mechanically and let `B11` handle
  "I already know this" by pruning the graph rather than just hiding a lesson —
  but it widens the `F01` schema.
- How "I already know this" interacts with prerequisites: skipping a lesson whose
  concepts a later lesson depends on needs either a warning or a graph re-sort.
- Whether the estimate shown to the user is derived from card and exercise counts
  or generated as a judgement, and how it is calibrated against real completion
  times from `B12`.
- Whether Deep should raise the new-concept budget per lesson or only add lessons.

## Acceptance criteria

- [ ] Outline generation produces an explicit concept graph before a lesson list
- [ ] No generated course contains a forward reference, verified by `P15` on the
      golden set
- [ ] A narrow and a broad topic at the same depth produce visibly different
      lesson counts
- [ ] The same topic at all three depths differs in both coverage and granularity,
      not just length
- [ ] Quick intro prunes branches without compressing the cards it keeps
- [ ] Lesson estimates are within a defined tolerance of real completion times
      once `B12` data exists
- [ ] A hard lesson is followed by one opening with a review card
