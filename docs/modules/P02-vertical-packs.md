# P02 — vertical-packs

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/verticals/`
**Milestone:** 2
**Status:** not started

## Purpose

The seam between the general instructional model and a specific subject area.
`P01` holds what is true of teaching anything; this module holds what is true of
teaching **tech**, behind an interface a future vertical can implement without
touching the spine. The source commits to exactly this shape: tech at launch, with
"architecture stays topic-agnostic so other verticals can be added later"
(`FEATURE_PLAN.md:8`).

## Scope

**Owns**
- The pack interface — what any vertical must supply
- The **tech pack**: the launch vertical's rules
- Snippet conventions, which are what make automated verification possible
- Version-sensitivity policy
- Which claims in this vertical are machine-verifiable
- The vertical's terminology authority and source domains for `P11`

**Does not own**
- The general model → `P01`
- Topic shapes within the vertical → `P03`
- Execution of snippets → `B08`, `B09`

## Source references

- `FEATURE_PLAN.md` § "Decisions made" — tech/coding at launch: best fit for card
  + checkable-exercise format, lowest AI-accuracy risk; architecture stays
  topic-agnostic (line 8)
- `FEATURE_PLAN.md` § 2 "Answer-key verification (trust)" (lines 69–72)
- `FEATURE_PLAN.md` § 3 "Card reader" — code cards, syntax highlighting,
  horizontal scroll (line 92)
- `ARCHITECTURE.md` § "Code sandbox" — JS and Python in v1 (lines 94–108)

## Depends on

`P01`

## Depended on by

`P03`, `P05`, `P06`, `P07`, `P09`, `P11`, `P16`

## The pack interface

Any vertical must supply:

| Contract | What it defines |
|----------|----------------|
| Topic shapes | The structural kinds of topic in this subject, for `P03` |
| Verifiable claims | Which assertions can be checked automatically, and how |
| Artefact conventions | Rules for the vertical's primary artefact — code here, but a formula, a case, or a phrase elsewhere |
| Recency policy | Whether and how fast the subject's truth changes |
| Terminology authority | Which naming to prefer when a concept has several names |
| Source domains | Which kinds of source count as authoritative, feeding `P11` |
| Exercise suitability | Which of the four exercise types fit which topic shapes |

## The tech pack

### Snippet conventions

These are the highest-leverage rules in the module, because they are what make
`B09`'s trust guarantee achievable. Every generated snippet intended as an answer
key must be:

- **Self-contained** — runs with no project setup
- **Deterministic** — no randomness, no clock, no network, no filesystem, no
  environment dependence
- **Minimal** — the fewest lines that demonstrate the idea, one new construct
- **Output-bearing** — produces something observable when the exercise depends on
  output
- **Import-light** — standard library only unless the topic *is* a library

A snippet that violates these cannot be verified, and an unverifiable answer key
is exactly the failure the source calls fatal to trust
(`FEATURE_PLAN.md:70`).

### Version sensitivity

Tech content decays. Every claim is one of:

| Class | Handling |
|-------|----------|
| **Version-neutral** | Stated plainly |
| **Version-bound** | Must state the version it holds for |
| **Volatile** | Avoid, or hedge explicitly per `P14` |

The generator may **never invent** a version number, release date, or benchmark
figure — enforced in `P14` and checked by `P16`.

### Verifiable claims

| Claim type | Verifiable | By |
|-----------|-----------|-----|
| What a snippet outputs | **Yes** | `B09` via `B08` |
| Whether code runs | **Yes** | `B09` |
| Syntax and semantics | **Yes** | Execution |
| API surface and signatures | Partially | Retrieval (`P13`) |
| Best practice, idiom, tradeoff | No | Rubric judgement (`P16`) |
| Historical or version claims | No | Retrieval, or avoid |

### Languages at launch

JavaScript and Python, matching the sandbox (`ARCHITECTURE.md:98-102`). Topics in
other languages are still teachable, but their code exercises cannot be
answer-key verified — so the pack must either restrict such exercises to
non-executable types or mark them unverified for `P16` to weigh.

### No diagrams

The product ships no generated images (`FEATURE_PLAN.md:56`), so this vertical
must teach inherently spatial ideas — network topology, tree structures, memory
layout — through prose, analogy, and code alone. The pack owns the substitution
strategies, since this is where a tech course most wants a picture.

## Open questions

- Whether a topic in an unsupported language should be refused, degraded to
  non-executable exercise types, or generated with unverified keys and a lower
  quality ceiling.
- Whether "idiomatic" is a claim worth making at all, given it cannot be verified
  and dates quickly.
- How the pack expresses topics that span languages, such as "REST API design".

## Acceptance criteria

- [ ] The interface is documented well enough that a second vertical could be
      written against it without changing `P01`
- [ ] Every snippet convention is enforced in a `P10` fragment and checked by
      `P16`
- [ ] A generated snippet that is non-deterministic is caught before it becomes an
      answer key
- [ ] No generated content states a version number that was not retrieved
- [ ] Unsupported-language topics have a defined, tested behaviour
- [ ] The pack contains no rule that belongs in `P01`
