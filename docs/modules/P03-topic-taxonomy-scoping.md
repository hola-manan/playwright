# P03 — topic-taxonomy-scoping

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/taxonomy/`
**Milestone:** 2
**Status:** not started

## Purpose

Turns a free-text topic into a **course shape**. "Git basics", "How DNS works",
and "Python decorators" are all valid inputs and all need structurally different
courses — a tool course is workflow-shaped, a concept course is
mental-model-shaped, a language-feature course is syntax-and-semantics-shaped.
Without this classification the generator produces the same generic course
skeleton for everything, which is the most visible failure mode in AI-generated
curricula.

Also owns the operational definition of "comprehensive", which the source states
only as an aspiration.

## Scope

**Owns**
- Topic shape classification
- The coverage checklist per shape — what "comprehensive" means concretely
- Over-broad detection and the single scoping question
- Topic normalisation feeding the `B10` cache key
- Mapping a shape to its source domains for `P11`

**Does not own**
- Asking the question in the UI → `C07`
- Executing classification at request time → `B04`
- Ordering the resulting lessons → `P04`
- Cache storage → `B10`

## Source references

- `FEATURE_PLAN.md` § 2 "Flow" — if the topic is too broad the AI asks one quick
  scoping question before building anything (line 48)
- `FEATURE_PLAN.md` § 2 "Outline confirmation" — lesson count driven by the
  topic's actual scope (line 49)
- `FEATURE_PLAN.md` § 2 "Depth / completeness" — coverage target is equivalence to
  a good external source (line 59)
- `FEATURE_PLAN.md` § 1 "Topic pick" — free text plus popular chips (line 34)
- `FEATURE_PLAN.md` § 2 "Cost control & reuse" — cache keyed by normalised topic
  (line 84)

## Depends on

`P01`, `P02`

## Depended on by

`P04`, `P06`, `P11`, `B04`, `B10`

## Topic shapes

The launch set, from the tech pack in `P02`:

| Shape | Examples | Course is organised by |
|-------|----------|----------------------|
| **Tool / CLI** | Git, Docker, curl | Mental model, then workflows, then recovery from mistakes |
| **Language feature** | Python decorators, JS closures | Syntax → semantics → when to use → when not to |
| **Concept / protocol** | How DNS works, HTTP caching | Layered mental model; may need no code at all |
| **Library / framework** | React basics, pandas | Setup → core API → idioms → ecosystem boundaries |
| **Practice / methodology** | Unit testing, code review | Principles → applied examples → tradeoffs |
| **Language** | Python, Go | Composite: usually over-broad, needs scoping |

Shape drives outline structure in `P04`, exercise-type mix in `P06`, and source
selection in `P11`.

## What "comprehensive" means

The source sets the bar as *equivalence to a good external source* — the learner
should not finish and still feel they need to go read the real tutorial
(`FEATURE_PLAN.md:59`). This module makes that checkable by giving each shape a
**coverage checklist**. A course is comprehensive when every checklist item is
addressed at the chosen depth.

For a Tool/CLI shape, for example, the checklist covers: what problem the tool
solves, its core mental model, the everyday command set, the two or three
workflows people actually use it for, how to recover from the common destructive
mistakes, and where to go next. A course that teaches commands without the mental
model is incomplete regardless of length.

Each shape's checklist is the concrete artefact this module delivers, and `P16`
scores coverage against it.

## Over-broad detection

A topic is over-broad when either:

1. Its shape is **ambiguous** — "Python" could be language, library ecosystem, or
   practice, or
2. Comprehensive coverage at the chosen depth would exceed a course a learner
   could plausibly finish

The response is **exactly one** scoping question, asked before anything is built
(`FEATURE_PLAN.md:48`). The question resolves shape or sub-domain — "for web,
data, or general?" — and never asks about preferences the depth control already
covers. One question, then build.

## Normalisation

The cache key for `B10` is `shape + canonical topic + depth + level`. Canonical
topic collapses phrasing — "learn git", "Git Basics", "git for beginners" — but
**must not** collapse genuinely different scopes. Over-collapsing serves a user a
course they did not ask for, which is worse than a cache miss.

## Open questions

- Whether shape classification is a model call, a heuristic over a curated topic
  list, or a model call constrained to the enumerated shapes. The last is
  probably right, and is cheap at outline time.
- How aggressive normalisation should be. This trades cache hit rate directly
  against relevance, and needs a measured answer from `B10`.
- What happens to a topic that fits no shape — refuse, or fall back to a generic
  concept shape with a lower quality ceiling.
- Whether the popular-topic chips in `C07` are drawn from shapes with the best
  coverage checklists, which would bias first impressions favourably.

## Acceptance criteria

- [ ] Every launch shape has a written coverage checklist that `P16` can score
- [ ] Three topics of different shapes produce structurally different outlines,
      not one skeleton with different words
- [ ] An over-broad topic triggers exactly one scoping question, and a
      well-scoped one triggers none
- [ ] Normalisation collapses phrasing variants and is verified not to collapse
      distinct scopes, on a test set
- [ ] Shape is carried through to `P04`, `P06`, and `P11` rather than being
      recomputed
- [ ] A topic with no matching shape has a defined, tested behaviour
