# B03 — vertex-client

**Tier:** Backend
**Code location:** `services/api/app/llm/`
**Milestone:** 2
**Status:** not started

## Purpose

The single path to Vertex AI. Wraps the Gemini SDK with model tiering, structured
output configuration, streaming primitives, retries, and mandatory cost
instrumentation. Every generator and the tutor call through here, so tier policy
and cost accounting are enforced rather than remembered.

## Scope

**Owns**
- Vertex AI client configuration and credentials via the Cloud Run runtime identity
- Model tier selection: Flash versus Pro
- Structured output / response-schema configuration
- Streaming primitives the generators build on
- Retry, timeout, and backoff policy
- The mandatory `F07` cost hook

**Does not own**
- Prompts → `B04`, `B05`, `B16`
- Validation of returned content → `B06`
- What to do on invalid output → `B07`

## Source references

- `ARCHITECTURE.md` § "LLM — Gemini via Vertex AI, tiered" (lines 84–92)
- `ARCHITECTURE.md` § "Backend language — Python" — first-class Vertex AI Python
  SDK (lines 61–65)
- `ARCHITECTURE.md` § "AI compute — Cloud Run" (lines 74–82)
- `FEATURE_PLAN.md` § 7 "Cross-cutting" — cost observability on every LLM call
  (line 180)

## Depends on

`F03` (runtime identity, secrets), `F07` (cost hook)

## Depended on by

`B04`, `B05`, `B16`, `F08`

## Interface

A typed call surface taking a prompt, a response schema, and a tier, returning
either a complete validated object or a stream of fragments. Callers name the tier
by intent, not by model string, so a model upgrade is a change here alone.

## Decisions inherited

- **Two tiers, by design.** Gemini 2.5 Flash for high-volume calls — lesson
  content, exercises, tutor — because courses can be long and the tutor is billed
  per message. Gemini 2.5 Pro **only** for the course outline, where structure and
  coverage set up everything downstream and volume is one call per course
  (`ARCHITECTURE.md:85-90`).
- **Structured output via response schema** so the pipeline receives valid JSON to
  schema-validate rather than parsing prose (`ARCHITECTURE.md:91-92`).
- **Python because the Vertex AI Python SDK is first-class** and Pydantic is the
  cleanest way to validate Gemini's structured output (`ARCHITECTURE.md:61-65`).
- **No hard timeout ceiling on Cloud Run**, so long streamed generations are
  legitimate (`ARCHITECTURE.md:78-80`).

## Open questions

- Retry policy for a stream that fails partway — resume is not generally possible,
  so this likely means restart with the already-emitted prefix discarded.
- Whether tier selection should ever be dynamic (fall back to Flash for outlines
  under cost pressure), or stay a fixed policy.
- Concurrency limits per Cloud Run instance against Vertex AI quota.

## Acceptance criteria

- [ ] No module calls Vertex AI except through this one
- [ ] Tier is selected by intent, and a model version change touches only this
      module
- [ ] Every call produces a `F07` cost record, with no path that bypasses it
- [ ] Structured output is requested with an explicit schema on every generation
      call
- [ ] Streaming and non-streaming share one retry and timeout policy
