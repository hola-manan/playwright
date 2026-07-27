# P16 — quality-rubric

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/rubric/`
**Milestone:** 2 (drafted), 4 (enforced)
**Status:** not started

## Purpose

The standard a generated course is judged against, and the thresholds that decide
whether it ships. Every rule in `P01`–`P14` is an intention until something scores
against it; this is that something.

With **no human review gate in v1**, this rubric plus `P17` is the entire quality
apparatus. It is therefore written as a gate, not as a report.

## Scope

**Owns**
- The scoring dimensions and their behavioural anchors
- Which dimensions are hard gates versus tradeable
- Pass thresholds, per dimension and overall
- The lower ceiling applied to ungrounded courses
- Threshold revision policy

**Does not own**
- Running the evaluation → `P17`
- The rules being scored → `P01`–`P14`
- Deterministic checks → `P15`
- Pipeline gating mechanics → `B07`

## Source references

- `FEATURE_PLAN.md` § 2 "Depth / completeness" — equivalence to a good external
  source; the user shouldn't finish and feel they still need the real tutorial
  (line 59)
- `FEATURE_PLAN.md` § 2 "Answer-key verification (trust)" — wrong answer keys are
  fatal to trust (lines 69–71)
- `FEATURE_PLAN.md` § "Guiding principle" (line 22)
- `FEATURE_PLAN.md` § "Verification" — success criteria (lines 228–230)

## Depends on

`P01`–`P14`

## Depended on by

`P17`, `B06`, `B07`, `B10`

## Dimensions

Each scored 1–5 against written behavioural anchors — what a 2 looks like versus a
4, in concrete terms, not adjectives.

| # | Dimension | Scores | Gate |
|---|-----------|--------|------|
| 1 | **Coverage** | Completeness against the `P03` shape checklist at the chosen depth | Hard |
| 2 | **Accuracy** | Factual correctness; `P14` compliance; nothing from the never-invent list | **Hard, non-tradeable** |
| 3 | **Clarity** | `P01` one-idea compliance, `P05` length and caption rules, terminology | Soft |
| 4 | **Exercise quality** | `P06` novel-context rule, `P07` distractor quality, auto-checkability | Hard |
| 5 | **Explanation quality** | `P08` four-beat structure, per-distractor targeting, tone | Soft |
| 6 | **Progression** | `P01` scaffolding fade, mastery levels, `P04` prerequisite order | Soft |

## Gating

**Accuracy is non-tradeable.** A course scoring 5 on everything else and 2 on
accuracy does not ship. Wrong content in a learning app is not offset by being
well-organised — the source calls this fatal to trust (`:70`), and with no human
reviewer there is nothing downstream to catch it.

Proposed thresholds, to be calibrated in `P17`:

- **Accuracy ≥ 4** — hard floor, no exceptions
- **Coverage ≥ 3** and **Exercise quality ≥ 3** — hard floors
- **Overall mean ≥ 3.5**
- Any single soft dimension may sit at 2 if the mean holds

Below threshold routes back to `B07`'s `generating` state under bounded retry.

## The ungrounded ceiling

A course generated without retrieval (`P13` timeout, or no corpus coverage) is
capped at **4** on Accuracy — it can be good, but it cannot be certified as
verified. It still ships, because `P14`'s fallback constrains it to conceptual and
executable content and the never-a-dead-end rule holds. But it is visibly a
different tier of confidence, and `B10` should prefer a grounded course over an
ungrounded one when both exist for a topic.

## What the rubric does not measure

Stated so absence is not read as failure:

- **Synthesis and open-ended reasoning** — the four exercise types are all
  auto-checkable by design (`:63`), so a course cannot assess these. That is a
  format decision, not a quality gap, and the tutor covers the territory.
- **Engagement** — whether a course is enjoyable is measured by `F06` retention
  data, not by a judge.
- **Novelty** — a course covering standard material in a standard order is
  correct, not unoriginal.

## Open questions

- Whether thresholds are global or vary by topic shape. Some shapes are genuinely
  harder to score well on, and a global bar may block whole categories.
- Whether Accuracy ≥ 4 is achievable at acceptable regeneration cost. If most
  first attempts score 3, the gate becomes a cost problem — this needs measuring
  early, which is why the rubric is drafted at milestone 2.
- Whether the rubric should score the outline separately before lessons generate,
  catching structural problems before paying for content.
- How thresholds are revised without invalidating comparisons over time —
  versioning the rubric alongside `P10` prompts is the likely answer.

## Acceptance criteria

- [ ] Every dimension has written behavioural anchors for each score point
- [ ] Every anchor traces to a rule in `P01`–`P14`, with no orphan criteria
- [ ] Accuracy is enforced as non-tradeable in the gate logic
- [ ] Thresholds are calibrated against human-labelled examples in `P17` before
      enforcement
- [ ] An ungrounded course is capped and still ships
- [ ] Two independent judge runs on the same content agree within one point per
      dimension
- [ ] The rubric is versioned so score history stays comparable
