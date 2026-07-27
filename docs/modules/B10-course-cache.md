# B10 — course-cache

**Tier:** Backend
**Code location:** `services/api/app/generation/cache/`
**Milestone:** 9
**Status:** not started

## Purpose

Shared base courses. A popular topic maps to one cached course reused across many
users, with personalisation layered on top per user. One generation serves many
learners, which is the difference between an unbounded per-user LLM bill and a
sustainable one — and the best cached courses become the seed for the v2 community
catalog.

## Scope

**Owns**
- The cache key: normalised topic + depth + experience level
- Lookup before generation and promotion of a generated course to shared
- Which courses qualify for sharing
- The pre-cached starter topics that back the never-a-dead-end path in `E02`
- Cache invalidation and versioning when generation prompts change

**Does not own**
- Per-user variation → `B11` enrollment deltas
- Generation → `B04`, `B05`
- Cost reporting → `F07`

## Source references

- `FEATURE_PLAN.md` § 2 "Cost control & reuse" (lines 83–85)
- `FEATURE_PLAN.md` § 2 "Depth / completeness" — the cache matters more for long
  courses (line 60)
- `FEATURE_PLAN.md` § 7 "Data model → course" — visibility, shared/cached
  (line 160)
- `FEATURE_PLAN.md` § 7 "Services" — shared-course cache keyed by normalized topic
  + level (line 173)
- `FEATURE_PLAN.md` § 1 "Edge cases" — pre-cached starter topic (line 41)

## Depends on

`F01`, `B04` (normalisation)

## Depended on by

`B07`, `B11`, `E02`

## Data touched

`course` — `normalized_topic`, `visibility`, `source`.

## Decisions inherited

- **A shared cached course is just a `course` row reused across users** — no
  separate cache store (`FEATURE_PLAN.md:160`).
- **Personalisation is applied per user on top** via enrollment deltas, so sharing
  never means identical experiences (`FEATURE_PLAN.md:84`).
- **The best cached courses seed the v2 community catalog**, which is why the
  `source` enum already exists (`FEATURE_PLAN.md:84`, `160`).
- **Per-user generation limits tie into monetization later**
  (`FEATURE_PLAN.md:85`) — the cache is what makes a generous free tier viable.

## Open questions

- Normalisation aggressiveness: how many phrasings collapse to one key before
  users start receiving a course that does not match what they asked for.
- Whether experience level belongs in the key at all, or whether one course plus
  difficulty deltas covers it — including it multiplies cache entries by three.
- Cache invalidation when prompts change: version the key, or accept drift.
- Which topics are pre-cached as starters, and who curates that list.

## Acceptance criteria

- [ ] A second user requesting an already-cached topic triggers zero model calls,
      verified via `F07`
- [ ] Two users on the same cached course can have different skipped lessons and
      difficulty without affecting each other
- [ ] Pre-cached starter topics exist and are reachable by `E02`'s fallback path
- [ ] A prompt change can invalidate cached content without manual database work
- [ ] Cache hit rate and the cost saved by it are reportable
