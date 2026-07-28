# Build order

How to actually build the 69 modules in [`docs/modules/`](modules/README.md).

Written for a **solo builder** whose immediate goal is proving the concept works.

---

## The shape of the work

69 specs with acceptance criteria look like 69 sequential tasks. They are not.

> A module's acceptance criteria describe its **v1-launch** state, not the scope
> of one sitting. Most modules are visited two or three times. Build the thin
> version of many modules rather than the complete version of few.

`C09 card-renderers` shows the pattern:

| Phase | What exists |
|-------|-------------|
| 1 | A concept card renders as plain text |
| 2 | A code card renders in monospace |
| 3 | Syntax highlighting, all four types, copy-to-clipboard |

Only phase 3 satisfies the spec. The spec was never one task.

### Why not sequential completion in dependency order

- **The specs are hypotheses.** They were written from planning documents with no
  code in existence. Working through them in order means discovering a wrong
  assumption at module 40 that invalidates modules 5 through 39.
- **Schema-first is a trap.** You cannot design a good content schema before
  seeing what generated content actually looks like — which is precisely why
  `card` and `exercise` payloads are JSONB in `F01` today.
- **Nothing works until the end.** Building tier by tier leaves the integration
  seams — Flutter ↔ FastAPI ↔ Vertex ↔ Postgres — untested until last, and that
  is where greenfield projects die.

Specs are living documents. Revising them is scheduled work below, not an
afterthought.

---

## Phase 0 — Does the AI teach?

**The current goal.** A Python script calling Vertex AI directly. No schema, no
service, no app, no auth, no streaming, no retrieval. Output to local JSON and
markdown you read yourself. Days, not weeks.

The deliverable is not code. It is **evidence** — and that evidence is what turns
`P01`–`P09` from theory into observation.

### 0.1 Outline quality (Gemini 2.5 Pro)

Six topics spanning the `P03` shapes: *Git basics* (tool), *Python decorators*
(language feature), *How DNS works* (concept), *React basics* (library), *Unit
testing* (practice), and *Python* (deliberately over-broad).

- Does lesson count **actually** follow scope, or default to roughly eight
  regardless of topic? This is the most likely failure.
- Do the three depth settings produce genuinely different outlines, or just
  different word counts?
- Is the over-broad topic detected without being told to look for it?
- **Test `P04`'s central hypothesis directly:** does asking for a concept graph
  and then topologically sorting beat asking for a lesson list in one step? That
  two-step design is an assumption today, and a lot depends on it.

### 0.2 Lesson quality (Gemini 2.5 Flash)

Full lessons from two or three of those outlines.

- Does *one idea per card* hold, or do cards drift into paragraphs?
- **Are exercises answerable by pattern-matching the preceding card?** `P06`'s
  novel-context rule exists because this is expected to fail badly by default.
- Are MCQ distractors plausible, or obvious filler? (`P07`)
- Do explanations explain, or restate the answer? (`P08`)

### 0.3 The trust check

Generate ~20 predict-output exercises, execute the snippets with a subprocess,
and compare real output to the claimed answer keys.

The cheapest high-information experiment available. **If the error rate is 2%,
`B09` is a safety net. If it is 25%, it is load-bearing** and the pipeline design
changes.

### 0.4 Cost and latency reality

Measure tokens, cost, time-to-first-token, and total time for one outline, one
lesson, and one full course at each depth.

- Does the 60-second topic-to-first-card target survive contact with reality?
- What does a *Deep* course on a broad topic actually cost? That decides whether
  `B10`'s cache is an optimisation or a survival requirement.

### 0.5 Write the rubric from evidence

With three to five generated courses in hand, score them by hand and write down
what made the bad ones bad.

This is the only way `P16` gets real behavioural anchors — "what a 2 looks like
versus a 4" cannot be written in the abstract. It also produces the human-labelled
calibration set `P17` needs before its judge can be trusted.

### Kill and pivot criteria

Decide these before running, not after.

| Finding | Consequence |
|---------|-------------|
| Answer-key error rate high and prompt-resistant | Verification becomes blocking earlier; possibly restrict or drop exercise types |
| Outlines generic regardless of topic shape | `P03`/`P04` become the first real investment, before any app work |
| Deep courses prohibitively expensive | Revisit the no-card-limit principle — a product decision touching `FEATURE_PLAN.md:22`, so surface it rather than absorb it |
| Quality already good with naive prompting | Tier P is lighter than specced. Equally valuable to learn |

### Output

A go / adjust / rethink decision. Revised `P01`–`P09`. `P16` with real anchors. A
labelled example set seeding `P17`'s golden and calibration sets. Real cost and
latency numbers feeding `E06` and `F07`.

---

## Phases 1–6

Sketched deliberately lightly — Phase 0 may change them.

### Phase 1 — Walking skeleton

*Unlocks: the seams exist. Topic → one card on a real device.*

`F01`(thin) `F02`(thin) `F03` `F06`(generation events) `F07` `E06` `B03`
`B04`(thin) `B05`(thin) `C01` `C02`(thin) `C03`

Hardcoded user, no auth, no streaming, one card type, no exercises. The point is
that every integration boundary exists and works.

`E06` is written here rather than guessed, using Phase 0's measured numbers.

### Phase 2 — Generation loop

*Unlocks: a demo that feels real.*

`P01` `P02` `P03` `P04` `P05` `P06` `P10` `P16`(draft) `B07` `E01` `E02` `E03`
`C07` `C08` `C10`

Depth on `B04`/`B05`. Streaming arrives, so the outline and first card appear
progressively rather than after a wait.

### Phase 3 — A full session

*Unlocks: someone can finish a lesson.*

`P07` `P08` `P09` `B06` `B08` `B09` `B12` `B13` `E04` `E05` `C09` `C11` `C12`
`C13` `C14` `C15`

All card and exercise types, feedback, the win screen, progress persistence — and
answer-key verification, which lands here because it is cheap and directly
protects trust.

### Phase 4 — A product

*Unlocks: someone comes back tomorrow.*

`F04` `F05` `F06`(full) `B01` `B02` `B11` `B14` `B18` `B19` `C04` `C05` `C06`
`C16` `C19`

Auth, the habit loop, home, settings. CI lands here — a solo builder does not
need it for a skeleton, but does need repeatable builds once real people are
involved.

### Phase 5 — Trustworthy

*Gate: **nothing external happens before this.***

`F08` `P11` `P12` `P13` `P14` `P15` `P16`(enforced) `P17`

Retrieval grounding, coherence checks, and the blocking quality gate. v1 ships AI
content with **no human review**, so `P17` must exist before content reaches
anyone other than you.

### Phase 6 — Sustainable

*Unlocks: cost control and depth.*

`B10` `B15` `B16` `B17` `C17` `C18`

Shared-course cache, review mode, the tutor.

---

## Two departures from the milestone table

[`docs/modules/README.md`](modules/README.md) maps modules onto the ten milestones
in `FEATURE_PLAN.md:186-201`. That mapping is still useful for *what belongs
with what*. Where execution order differs:

**`F07` and `F06` move to Phase 1.** The milestone table places cost at 9 and
analytics at 10. Neither can be reconstructed retroactively, and the entire
model-tiering and caching strategy depends on knowing real numbers from the first
call.

**Trust splits in two.** Milestone 4 lumps answer-key verification together with
retrieval and the quality gate. They should not move together: `B08`/`B09` is
cheap and protective, so it lands in Phase 3; `P11`–`P17` is a large build whose
value begins the moment content reaches someone other than the author, so it
lands in Phase 5 as a hard gate on external exposure.

---

## A note on where this repo is

69 specs, a scaffold, two verification scripts, and no code. That was the right
work — the failure mode from here is writing another planning document instead of
running an experiment.

This file should be the last document written before the Phase 0 spike runs.

The most valuable thing available right now is not a better plan. It is knowing
whether Gemini can teach Git well, and that is a few days of throwaway Python
away.
