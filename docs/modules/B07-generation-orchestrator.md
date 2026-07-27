# B07 — generation-orchestrator

**Tier:** Backend (engine)
**Code location:** `services/api/app/generation/orchestrator/`
**Milestone:** 2
**Status:** not started

## Purpose

The pipeline state machine. It sequences outline → lesson → validation →
answer-key verification → persist, and it owns the just-in-time policy that keeps
a long course feeling fast: generate lesson N+1 in the background while the user
works through lesson N. Every `generation_status` transition on a lesson happens
here.

## Scope

**Owns**
- The generation pipeline and its ordering
- `lesson.generation_status` transitions
- Just-in-time scheduling of the next lesson
- Regeneration decisions from `B06` and `B09` failures
- Cache consultation before generating anything
- Failure and retry policy for the pipeline as a whole

**Does not own**
- Prompts and model calls → `B04`, `B05`
- Validation rules → `B06`
- Sandbox execution → `B08`, `B09`
- Cache storage → `B10`

## Source references

- `FEATURE_PLAN.md` § 7 "Services → Generation pipeline" (line 173)
- `FEATURE_PLAN.md` § 2 "Just-in-time generation" (line 50)
- `FEATURE_PLAN.md` § 2 "Depth / completeness" — why JIT matters more for long
  courses (line 60)
- `FEATURE_PLAN.md` § 7 "Data model → lesson" — generation status enum (line 161)

## Depends on

`B04`, `B05`, `B06`, `B09`, `B10`, `F07`, `P13` (retrieval), `P15` (coherence),
`P17` (the gate)

## Depended on by

`C07`, `E02`, `B11`

## State machine

Per lesson:

```
pending ──scheduled──▶ retrieving          (course-level, once — see below)
retrieving ──context | timeout──▶ generating
generating ──content ok──▶ validating
validating ──invalid──▶ generating        (bounded retries, per B06)
validating ──valid────▶ verifying          (only if the lesson has code exercises)
verifying  ──mismatch─▶ generating        (bounded retries, per B09)
verifying  ──ok───────▶ evaluating
evaluating ──below P16 threshold──▶ generating   (bounded retries, per P17)
evaluating ──passes───▶ ready
any state ──retries exhausted──▶ failed
```

`retrieving` and `evaluating` are the pedagogy tier's two insertions.

- **`retrieving`** (`P13`) runs **once per course at outline time**, not per
  lesson. Lesson generation reuses the stored context and pays no retrieval
  latency, which is what protects the `E06` first-card budget. A retrieval
  timeout is **not** a failure — it proceeds to `generating` ungrounded, with
  `P14` hedging applied.
- **`evaluating`** (`P17`) is a **blocking quality gate**. Because v1 ships no
  human review, a lesson below the `P16` threshold must not reach a learner. It
  regenerates, and on exhausting retries the lesson is marked `failed` — `E01`
  degrades gracefully around a missing lesson, which is a better outcome than a
  wrong one.

Cheap checks run before expensive ones: `B06` schema, then `B09` execution, then
`P15` deterministic coherence, then the `P17` judge call. Anything the earlier
stages reject never costs a judge call.

Course level: outline generated once → lesson 1 generated immediately → lesson
N+1 scheduled when the user enters lesson N.

## Invariants

1. A lesson reaches `ready` only after passing validation, answer-key
   verification where applicable, coherence checks, and the `P17` quality gate.
2. Retries are bounded at every stage; no state can loop indefinitely.
3. Only one generation runs per lesson at a time — concurrent requests for the
   same lesson join the in-flight generation rather than starting a second.
4. A cache hit in `B10` short-circuits before any model call is made.
5. Just-in-time generation never blocks the user's current lesson.
6. Retrieval runs once per course. No lesson generation performs retrieval.
7. Retrieval failure degrades grounding; it never fails a lesson.

## Failure modes

| Failure | Recovery |
|---------|----------|
| Model call fails | Retry per `B03` policy, then `failed` |
| Validation exhausts retries | Lesson marked `failed`; `E01` ends the lesson gracefully at the last complete item |
| Verification exhausts retries | Regenerate the exercise; if still failing, drop the exercise rather than failing the whole lesson |
| Retrieval times out or returns nothing | Proceed ungrounded per `P14`; mark the course ungrounded for `P16`'s lower ceiling. Never a failure |
| Quality gate exhausts retries | Lesson marked `failed`. Shipping a lesson known to be below threshold is not an option when nothing downstream reviews it |
| Coherence check fails | Targeted regeneration of the specific item `P15` identified, not the whole lesson |
| Background JIT generation fails | Silent to the user until they reach that lesson; retried on entry |
| Cloud Run instance dies mid-generation | Lesson stuck in `generating` — needs a stale-state sweep so it does not block forever |

## Decisions inherited

- **Just-in-time, not up-front.** Each subsequent lesson generates while the user
  works through the current one, so difficulty adaptation always uses the latest
  performance data (`FEATURE_PLAN.md:50`).
- **Long courses make JIT and the cache matter more, not less** — they keep a
  40-card course cheap and fast rather than generating everything up front
  (`FEATURE_PLAN.md:60`).
- **Answer-key verification ships in v1** because wrong answer keys are fatal to
  trust in a learning app (`FEATURE_PLAN.md:70`).

## Open questions

- Stale-`generating` sweep interval and whether it needs a lease/heartbeat.
- Whether JIT should generate one lesson ahead or two — two smooths bursty
  reading, but doubles wasted generation when a user abandons.
- Where the difficulty signal is sampled: at scheduling time or at generation
  time. Later sampling is more accurate but complicates caching.

## Acceptance criteria

- [ ] All seven invariants are covered by tests, including the concurrent-request
      join
- [ ] A lesson scoring below the `P16` threshold never reaches a learner
- [ ] Retrieval runs once per course, verified by `F07` records showing no
      retrieval spend on lesson generation
- [ ] A user working steadily never waits for lesson N+1
- [ ] A cache hit performs zero model calls, verified by `F07` records
- [ ] Every retry path is bounded and terminates in `ready` or `failed`
- [ ] A killed instance mid-generation does not leave a lesson permanently stuck
- [ ] A failed lesson degrades per `E01` rather than surfacing an error screen
