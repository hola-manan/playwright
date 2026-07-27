# P09 — difficulty-semantics

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/difficulty/`
**Milestone:** 3
**Status:** not started

## Purpose

What "easier" and "harder" actually mean in content. `B13` computes a difficulty
signal from miss rate and hands it to `B05` — but nothing currently defines what
the generator should *do* differently on receiving it. Without this module,
"easier" collapses into "shorter and vaguer", which is the failure mode where an
adaptive course quietly stops teaching the learner who most needs it to.

## Scope

**Owns**
- The ranked levers that make content easier or harder
- The rule that coverage is never a lever
- Mapping onboarding experience levels to starting positions
- Mapping the `B13` signal to a lever delta
- The one-step-at-a-time constraint

**Does not own**
- Computing the signal → `B13`
- Applying it during generation → `B05`
- The levers' own definitions — scaffolding is `P01`, distractor subtlety is
  `P07`, token bank versus free typing is `P06`
- Presenting the pace toggle → `C15`

## Source references

- `FEATURE_PLAN.md` § 2 "Difficulty adaptation" — inputs are experience level plus
  per-lesson miss rate; miss above roughly 40% means the next lesson is generated
  easier and opens with a review card; ace two in a row offers a faster pace
  (lines 73–76)
- `FEATURE_PLAN.md` § 1 "Quick calibration" — New / Some / Confident (line 35)
- `FEATURE_PLAN.md` § 2 — fill-blank input adapts to difficulty; free typing at
  harder levels and in review (line 66)
- `FEATURE_PLAN.md` § "Guiding principle" (line 22)

## Depends on

`P01`, `P04`, `P06`, `P07`

## Depended on by

`P16`, `B05`, `B13`

## The binding constraint

> **Coverage is never a difficulty lever.**

An easier course teaches the same material with more support. It does not skip
concepts, shorten the outline, or soften claims. This follows directly from the
guiding principle that short-form is the format and not a limit on coverage
(`FEATURE_PLAN.md:22`), and it is what separates adaptation from giving up on a
learner.

Anything that reduces what is taught is a `P04` depth decision the **user** makes,
never an adaptation the system makes on their behalf.

## The levers, ranked

Applied in this order as difficulty decreases:

| # | Lever | Easier | Harder |
|---|-------|--------|--------|
| 1 | **Scaffolding** | More worked examples before practice; support fades later | Support fades immediately |
| 2 | **Concept density** | Fewer new concepts per lesson — more lessons, same coverage | Toward the top of the `P01` budget |
| 3 | **Exercise input** | Token bank | Free typing |
| 4 | **Distractor subtlety** | Greater conceptual distance | Close, plausible distractors |
| 5 | **Snippet complexity** | Shorter, single-construct | Longer, composed |
| 6 | **Mastery level** | Recall and apply | Apply and analyse |
| 7 | **Worked-example fading** | Slower fade across the lesson | Faster fade |

Levers 1 and 2 do the most work and are reached for first. Note that **lever 2
increases lesson count** — the same ground taught in smaller steps — which is
consistent with "a longer topic means more lessons, not longer cards"
(`FEATURE_PLAN.md:53`) applied to difficulty rather than scope.

## Starting positions

Onboarding calibration (`FEATURE_PLAN.md:35`) sets where a course begins:

| Level | Starting position |
|-------|------------------|
| **New** | Levers at their easier settings; fundamentals assumed unknown |
| **Some** | Default. The skippable-default value (`:35`) |
| **Confident** | Levers toward harder; fundamentals covered briskly but **still covered** |

Confident does not mean skipping fundamentals — it means teaching them quickly.
Skipping is the user's explicit "I already know this" (`:49`), handled by `B11`.

## Signal mapping

From `B13` (`FEATURE_PLAN.md:75-76`):

| Signal | Response |
|--------|----------|
| Miss rate above threshold | One step easier; next lesson opens with a review card (`P04`) |
| Two lessons aced | **Offer** a faster pace — never applied automatically (`:76`) |
| Otherwise | Hold |

**One step at a time.** No lesson moves two levels, in either direction — a single
bad lesson after a run of good ones should not restructure the course, and the
adaptation should be invisible rather than jarring.

## Open questions

- Whether the levers move together as a single scalar or independently. A scalar
  is far simpler to generate against and to cache in `B10`; independent levers are
  more precise but multiply cache keys.
- Whether difficulty is per course or per concept. A learner may be confident
  about syntax and lost on semantics, which a single course-level scalar cannot
  express.
- How lever 2 interacts with an already-confirmed outline: adding lessons
  mid-course changes the syllabus the user agreed to, which may need surfacing.
- Whether "harder" should ever be applied without the user accepting the offer,
  given the source says offer (`:76`) but says nothing about a user who ignores it
  repeatedly.

## Acceptance criteria

- [ ] The same topic generated at the easiest and hardest settings covers an
      identical concept set, verified on the golden set — this is the coverage
      constraint made testable
- [ ] Each lever is individually demonstrable in generated output
- [ ] A course generated for New shows more worked examples and lower concept
      density than one for Confident, on the same topic
- [ ] Confident courses still teach fundamentals
- [ ] No adaptation moves more than one step per lesson
- [ ] The faster-pace change never applies without the user accepting it
- [ ] `B05` receives a signal it can act on unambiguously — no lever is left to
      the model's interpretation
