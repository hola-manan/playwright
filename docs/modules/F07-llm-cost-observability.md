# F07 — llm-cost-observability

**Tier:** Foundation
**Code location:** `services/api/app/shared/cost/`
**Milestone:** 9 (instrumented from milestone 2)
**Status:** not started

## Purpose

Token and cost accounting on every Vertex AI call, attributed per user and per
topic. Courses have no card limit and the tutor is billed per message, so the two
headline features are also the two unbounded cost surfaces. This module makes that
spend visible early enough to inform generation limits and monetization rather
than discovering it from a bill.

## Scope

**Owns**
- Per-call recording: model, input/output tokens, latency, cost, caller module
- Attribution to user, course, and topic
- Aggregation and reporting: cost per user, per topic, per generated course, per
  tutor thread
- Budget alerting thresholds

**Does not own**
- Enforcement of per-user limits → `B17` for the tutor, `B10` for generation reuse
- The Vertex AI call itself → `B03`
- Product analytics → `F06`

## Source references

- `FEATURE_PLAN.md` § 7 "Cross-cutting" — cost observability on every LLM call
  (line 180)
- `FEATURE_PLAN.md` § 2 "Cost control & reuse" (lines 83–85)
- `FEATURE_PLAN.md` § 2 — tutor cost per message, cap/meter free-tier usage
  (line 81)
- `ARCHITECTURE.md` § "LLM — Gemini via Vertex AI, tiered" (lines 84–92)

## Depends on

`B03` (the call site it instruments), `F01` (storage for records)

## Depended on by

`B03`, `B04`, `B05`, `B07`, `B10`, `B16`, `B17`

## Interface

A wrapper or hook applied at the `B03` boundary so no generator has to remember to
report, plus a query surface for the aggregations above.

## Decisions inherited

- **Tiered models are the primary cost lever.** Gemini 2.5 Flash for the
  high-volume calls — lesson content, exercises, tutor — and 2.5 Pro reserved for
  the course outline only, where volume is low and quality sets up everything
  downstream (`ARCHITECTURE.md:85-90`). Cost reporting must break down by tier or
  it cannot show whether the tiering is working.
- **Courses are deliberately unbounded in length** (`FEATURE_PLAN.md:22,53`),
  which is exactly why the shared-course cache in `B10` matters more, not less
  (`FEATURE_PLAN.md:60`). Cost per generated course is the metric that proves it.
- **The tutor is a per-message cost** and was flagged as a meaningfully bigger
  surface than preset actions (`FEATURE_PLAN.md:81`).

## Open questions

- Whether cost data lives in Postgres, PostHog, or both.
- Alert thresholds — per user per day, and global daily spend.
- Whether cached-course reuse is credited back so the cache's saving is visible.

## Acceptance criteria

- [ ] No Vertex AI call can be made without a cost record being written
- [ ] Cost is attributable per user, per topic, and per model tier
- [ ] Cost per generated course and cost per tutor thread are directly queryable
- [ ] The saving from a `B10` cache hit is measurable
- [ ] A runaway user or topic triggers an alert before it becomes a bill
