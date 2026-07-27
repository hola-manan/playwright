# P17 — content-eval-harness

**Tier:** Pedagogy
**Code location:** `tools/content_eval/`
**Milestone:** 4
**Status:** not started

## Purpose

The machinery that applies `P16` — and, because v1 ships **no human review gate**,
the only thing standing between a badly generated course and a learner. It scores
generated content, blocks what falls below threshold, and re-runs the golden set
whenever a `P10` prompt version changes so that improving one thing cannot quietly
break another.

Without this, every pedagogy rule in Tier P is an unenforced intention.

## Scope

**Owns**
- The LLM-as-judge implementation
- The golden topic set
- The **blocking gate** in `B07`'s `evaluating` state
- Regression runs triggered by `P10` version changes
- Judge calibration against human-labelled examples
- Score tracking over time
- The sampling policy that keeps gating affordable

**Does not own**
- The rubric → `P16`
- Deterministic checks → `P15`
- Pipeline state machine → `B07`
- Prompt versioning → `P10`

## Source references

- `FEATURE_PLAN.md` § 2 "Answer-key verification (trust)" — malformed output
  regenerated automatically (lines 69–71)
- `FEATURE_PLAN.md` § 2 "Depth / completeness" (lines 58–61)
- `FEATURE_PLAN.md` § "v1 Build Milestones" — milestone 4, make generated content
  trustworthy (line 193)
- `FEATURE_PLAN.md` § "Verification" (lines 228–230)

## Depends on

`P15`, `P16`, `P10`, `B03`

*(Offline tooling: this module drives the generation pipeline to evaluate it, so
it is the documented exception to the rule that Tier P does not depend on Tier B.)*

## Depended on by

`B07` (the gate), `P10` (regression signal)

## The gate

In `B07`'s pipeline, `evaluating` sits between `verifying` and `ready`:

```
verifying ──▶ evaluating ──▶ ready
                  │
                  └── below P16 threshold ──▶ generating   (bounded retry)
```

It **blocks**. A lesson scoring below the `P16` floor does not reach a learner; it
regenerates. On exhausting retries, the lesson is marked `failed` and `E01`
degrades gracefully — a missing lesson is a better outcome than a wrong one.

## Order of operations

Cheap and certain before expensive and probabilistic:

```
B06 schema  ──▶ B09 answer keys ──▶ P15 coherence ──▶ P17 judge
(free)          (sandbox)           (deterministic)   (model call)
```

Anything the earlier stages can reject never reaches the judge, which is what
makes gating every lesson affordable.

## Cost, and why the cache saves it

Judging every lesson adds a model call per lesson — real money on a product whose
courses are deliberately unbounded in length (`:22`). Three things contain it:

1. **The `B10` shared cache.** A cached course is generated and judged **once** and
   served to many users. The cache's cost argument (`:84`) applies to evaluation
   as much as to generation, and the more popular a topic, the cheaper its
   quality assurance becomes per learner.
2. **Judge on Flash**, per the `B03` tiering rationale — judging is a
   high-volume call.
3. **Earlier stages reject first**, so the judge sees only structurally sound,
   key-verified, coherent content.

Judge spend is its own `F07` category, so the gate's cost is visible rather than
buried in generation.

## The golden set

A fixed set of topics that exercises the system's range, regenerated and scored on
every `P10` version change:

- One topic per `P03` shape
- The same topic at all three depths, to verify the `P04` coverage-versus-
  granularity distinction
- The same topic at easiest and hardest difficulty, to verify the `P09` rule that
  **coverage does not change**
- A deliberately spatial topic, to test `P05`'s no-diagram substitutions
- A topic with no corpus coverage, to test the `P14` ungrounded path
- A topic in an unsupported language, to test the `P02` fallback

A change that improves the average while regressing any golden topic below its
floor is not shipped.

## Judge calibration

The judge must itself be validated, and this is where humans enter a system with
no human gate: a one-off human-labelled calibration set, scored independently, and
compared to judge output. If judge and human disagree beyond tolerance, the judge
prompt or `P16`'s anchors are wrong — and every downstream score is untrustworthy.

Recalibration is required whenever `P16` anchors change. Skipping this makes the
entire gate theatre.

## Open questions

- **No learner-side reporting path exists.** With content shipping unreviewed, a
  wrong card has no route back — the source only covers reporting for v2 community
  content (`:210`). A "report this card" affordance in `C14` would be cheap and is
  the natural counterweight to shipping unreviewed. This is a product decision, so
  it is flagged rather than assumed.
- Whether the gate scores per lesson or per course. Per lesson fits just-in-time
  generation; per course catches structural problems a single lesson cannot show.
- Whether a judge sharing `P10`'s spine fragments inherits the generator's blind
  spots — the same question `P10` raises from the other side.
- Whether to sample rather than gate every lesson once volume grows, and what
  evidence would justify relaxing a gate that is currently the only one.
- How judge scores relate to `F06` retention data. Agreement would validate the
  rubric; sustained disagreement would mean it measures the wrong thing.

## Acceptance criteria

- [ ] The gate blocks below-threshold lessons and triggers bounded regeneration
- [ ] Judge scores agree with human labels within tolerance on the calibration set
      before the gate is enabled
- [ ] Two judge runs on identical content agree within one point per dimension
- [ ] A `P10` fragment change triggers a full golden-set regression automatically
- [ ] A regression below any golden topic's floor blocks the prompt change
- [ ] Cheap checks run before the judge, verified by cost records showing no judge
      call on content that failed `B06`, `B09`, or `P15`
- [ ] Judge spend is separately visible in `F07`
- [ ] Score history is retained and comparable across rubric versions
