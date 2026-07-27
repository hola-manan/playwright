# P14 — grounding-attribution

**Tier:** Pedagogy
**Code location:** `services/api/app/generation/grounding/`
**Milestone:** 4
**Status:** not started

## Purpose

The rules governing what the model may assert. `B09` verifies executable claims by
running them; everything else — API signatures, defaults, version behaviour,
historical facts, best-practice claims — has no such check. This module covers
that gap with three mechanisms: things that may never be invented, things that
must be hedged, and claims bound to a retrieved source.

Applies to the tutor as well as to generated content, where the risk is higher
because tutor replies are never reviewed before a learner reads them.

## Scope

**Owns**
- The never-invent list
- Hedging rules: what may be stated flatly versus qualified
- Claim-to-source binding and the `grounding_citation` record
- The ungrounded-generation fallback and its constraints
- Confidence marking passed to `P16`
- The tutor's grounding standard

**Does not own**
- Retrieval → `P13`
- Executable verification → `B09`
- Source policy → `P11`
- Scoring accuracy → `P16`

## Source references

- `FEATURE_PLAN.md` § 2 "Answer-key verification (trust)" — wrong answer keys are
  fatal to trust (lines 69–71)
- `FEATURE_PLAN.md` § 2 "Explanations & tutor chat" — tutor build considerations
  (lines 78–81)
- `FEATURE_PLAN.md` § "Decisions made" — tech chosen for lowest AI-accuracy risk
  (line 8)
- `ARCHITECTURE.md` § "Code sandbox" — verification at generation time
  (lines 102–104)

## Depends on

`P02` (version sensitivity), `P11`, `P13`

## Depended on by

`P16`, `B05`, `B09`, `B16`, `F01`

## The never-invent list

Categories the model may **never** produce from parametric knowledge. Each must
come from a retrieved passage or be omitted:

- Version numbers, release dates, deprecation timelines
- Benchmark figures, performance numbers, percentages
- Direct quotations and attributions to named people
- Exact API signatures, parameter names, and defaults
- Command flags and their exact behaviour
- URLs and file paths presented as real
- Standards and RFC numbers

These are the highest-confidence hallucinations a model produces — fluent,
specific, and wrong — and they are exactly what a learner will copy and run.

## Hedging rules

| Claim type | Grounded | Ungrounded |
|-----------|----------|-----------|
| Executable behaviour | State flatly — `B09` verified it | State flatly if verified |
| Documented API behaviour | State flatly, cite | **Omit or hedge** |
| Version-bound behaviour | State with version | **Omit** |
| Conceptual explanation | State flatly | State flatly — stable, low risk |
| Best practice, idiom | Attribute to the source | Hedge: "commonly", "many teams" |
| Historical or ecosystem claims | Cite | **Omit** |

Conceptual explanation is deliberately permitted ungrounded: how DNS resolution
works or what a closure is does not change, and requiring a citation for it would
gut the product's coverage for no accuracy gain.

Hedging must be **honest, not decorative**. Hedging every sentence teaches nothing
and signals nothing; the point is that a hedge marks genuine uncertainty and its
absence marks confidence.

## Claim-to-source binding

Where a claim comes from a retrieved passage, the binding is recorded in
`grounding_citation` (`F01`), linking the generated card or exercise to the chunk
it drew on. This gives:

- An audit path when a learner reports something wrong — the only such path v1 has
- `P16` a way to score whether grounded claims actually used their grounding
- `P12` a way to find affected content when a source changes

Whether citations are ever shown to the learner is an open question below.

## Ungrounded fallback

When `P13` returns nothing — timeout, no coverage, everything below threshold —
generation proceeds under tightened constraints:

1. The never-invent list becomes absolute; omit rather than approximate
2. Version-bound and ecosystem claims are dropped entirely
3. Conceptual and executable content carries the course
4. The course is marked **ungrounded**, and `P16` applies a lower quality ceiling

An ungrounded course is a legitimate product outcome, not an error. It teaches
concepts and verified code, and stays quiet about the things it cannot check.

## The tutor

The highest-risk surface. Tutor replies are generated live, are never scored by
`P16` before display, and arrive when the learner is confused and least able to
detect an error.

- The never-invent list applies unchanged
- **"I'm not certain" is a correct answer**, and `P08` requires the tutor be
  willing to give it
- Where a question needs a fact the tutor cannot ground, it should say so and
  point at the source rather than construct something plausible

## Open questions

- Whether citations are surfaced to the learner. Showing them builds trust and
  fits the "equivalence to a good external source" framing; hiding them keeps
  cards clean and short, which `P05` wants.
- Whether an ungrounded course should be visibly marked to the user, or only
  internally for `P16`.
- Whether the tutor gets retrieval of its own. It is the highest-risk surface and
  currently the least grounded, but adding retrieval to a per-message path
  reintroduces the `P13` latency problem against a 2s first-token budget.
- How to detect that a model has invented something from the never-invent list.
  Pattern-matching version strings and numerals is feasible; catching a fabricated
  parameter name is much harder.

## Acceptance criteria

- [ ] No generated content contains a version number, benchmark, or API signature
      absent from a retrieved passage — checked mechanically where possible
- [ ] Hedging appears where grounding is thin and is absent where content is
      verified
- [ ] Every grounded claim has a `grounding_citation` row linking it to its chunk
- [ ] A course generated with retrieval disabled is coherent, teaches its
      concepts, and omits rather than invents
- [ ] Ungrounded courses are marked and scored under a lower ceiling by `P16`
- [ ] The tutor declines to assert facts it cannot ground, verified by adversarial
      questioning on the golden set
