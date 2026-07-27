# P11 — source-curation

**Tier:** Pedagogy
**Code location:** `services/api/app/knowledge/sources/`
**Milestone:** 4
**Status:** not started

## Purpose

Which sources the system is allowed to learn from. Retrieval only improves
accuracy if what is retrieved is authoritative — grounding against a low-quality
blog post is worse than not grounding at all, because it launders a wrong claim
into a cited one. This module is the editorial policy: a **curated allowlist**,
not an open-web crawl.

## Scope

**Owns**
- The source allowlist and its trust tiers
- Mapping topic shapes and domains to their sources
- Licensing and terms-of-use assessment per source
- Freshness policy and version pinning per source
- The process for adding, demoting, and removing a source
- What happens when a topic has no curated source

**Does not own**
- Fetching, chunking, embedding → `P12`
- Retrieval at generation time → `P13`
- How retrieved claims are used or hedged → `P14`

## Source references

- `FEATURE_PLAN.md` § "Decisions made" — tech/coding chosen partly for lowest
  AI-accuracy risk (line 8)
- `FEATURE_PLAN.md` § 2 "Answer-key verification (trust)" — wrong answer keys are
  fatal to trust in a learning app (line 70)
- `FEATURE_PLAN.md` § 2 "Depth / completeness" — equivalence to a good external
  source (line 59)
- `ARCHITECTURE.md` § "Auth + Database" — vector search available (lines 55–56)

## Depends on

`P02` (which source domains count as authoritative), `P03` (topic shapes)

## Depended on by

`P12`, `P13`, `P14`, `P16`

## Curated, not crawled

The defining decision. Sources are added deliberately, one at a time, with a
recorded rationale. There is no open-web ingestion and no automatic discovery.

The reasoning: the whole point of grounding is to raise the floor on factual
accuracy. An uncurated corpus lowers it, because retrieval will confidently
surface the most textually similar passage regardless of whether its source is
right. A small, high-quality corpus beats a large, mixed one for this purpose.

## Trust tiers

| Tier | Kind | Treatment |
|------|------|-----------|
| **1 — Canonical** | Official documentation, language and tool specifications | Cited directly; claims may be stated flatly |
| **2 — Reference** | Established references (MDN-class), standards bodies | Cited; claims stated flatly |
| **3 — Instructional** | Reputable books, official tutorials | Used for pedagogy and framing more than for facts |
| **4 — Community** | Q&A sites, blogs | **Excluded from v1** |

Tier 4 is excluded deliberately. It is where most of the internet's practical
knowledge lives, and also where most of its confidently-wrong knowledge lives —
and this system has no human reviewer to tell them apart.

## Licensing

Every source carries a recorded assessment before ingestion:

- Whether its terms permit retrieval-time use
- Whether verbatim quotation is permitted, and at what length
- Attribution requirements
- Whether the crawl itself is permitted

This is a real constraint, not a formality: content is being ingested, stored,
embedded, and used to produce a product. A source whose licensing is unclear is
not ingested.

## Freshness

Each source declares a re-check cadence and, where relevant, a pinned version.
Tech content decays (`P02`), so a stale corpus grounds claims in last year's
truth — which is worse than no grounding because it carries a citation. `P12`
enforces the cadence; this module sets it.

## Coverage gaps

A user can type any topic; the corpus covers a curated subset. When a topic has no
adequate source, generation proceeds **ungrounded with hedging** per `P14`, and
`P16` applies a lower quality ceiling. The system never refuses a topic for lack of
sources — that would break the "never a dead end" rule — but it does know, and
record, that it is on thinner ice.

## Open questions

- Who curates. This is ongoing editorial work with no owner in the current plan,
  and it is the module's largest unresolved dependency.
- Whether the allowlist ships with enough coverage for the popular-topic chips in
  `C07` at minimum, which would at least guarantee grounding for first impressions.
- Whether tier 3 instructional sources risk teaching the model someone else's
  course structure closely enough to be a derivation concern.
- How coverage gaps are surfaced — silently lower-confidence, or visible to the
  user.

## Acceptance criteria

- [ ] Every source in the allowlist has a recorded trust tier, licensing
      assessment, and freshness cadence
- [ ] No content is ingested from a source without a completed licensing
      assessment
- [ ] Tier 4 sources are excluded, enforced rather than merely intended
- [ ] Every popular-topic chip in `C07` maps to at least one tier 1 or 2 source
- [ ] A topic with no curated source generates successfully and is marked
      ungrounded for `P16`
- [ ] Adding a source is a reviewable change with a recorded rationale
