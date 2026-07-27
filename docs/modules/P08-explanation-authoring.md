# P08 — explanation-authoring

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/explanations/`
**Milestone:** 3
**Status:** not started

## Purpose

The highest-leverage text in the product. It is what a learner reads at the exact
moment they were wrong and are paying full attention — the point of maximum
teaching opportunity in the whole experience. The source requires it to be
pre-generated with the lesson so it appears with zero latency, but says nothing
about what it should contain.

Also sets the standard for the **tutor**, whose job is the same job in
conversational form.

## Scope

**Owns**
- Structure and content of the incorrect-answer explanation
- Structure of the correct-answer confirmation
- The requirement that explanations are **per-distractor**, not per-exercise
- Tone rules
- Length ceilings
- The explanatory standard the tutor works to, including what "explain
  differently" means

**Does not own**
- Misconception labelling → `P07`
- When and how the explanation is displayed → `C14`
- Tutor mechanics, context injection, guardrails → `B16`, `B17`
- Factual accuracy of the explanation → `P14`, `P16`

## Source references

- `FEATURE_PLAN.md` § 2 "Explanations & tutor chat" — every exercise's right/wrong
  explanation pre-generated with the lesson, zero latency after answering; preset
  quick actions "explain differently", "give me an example", "why is this wrong?"
  (lines 78–81)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — wrong gets the pre-generated explanation
  of *why*, plus the correct answer, plus a route to the tutor (line 97)
- `FEATURE_PLAN.md` § 3 — no hard fail (line 98)

## Depends on

`P01`, `P06`, `P07`

## Depended on by

`P16`, `B05`, `B16`, `C14`

## Per-distractor, not per-exercise

The structural requirement that everything else follows from:

> An MCQ with three distractors needs **three** incorrect-answer explanations, one
> per option — not one generic explanation shown regardless of what the learner
> chose.

A learner who picked option B because they confused mutation with copying needs to
read about mutation versus copying. Showing them a restatement of why option A is
correct does not address the thing that went wrong. `P07` labels each distractor
with its misconception; this module explains *that* misconception.

This widens the `exercise` payload in `F01` and the structural rules in `B06`, and
it multiplies explanation generation cost in `B05` — worth stating plainly, since
it is the main cost consequence of this tier.

## Structure of an incorrect explanation

Four beats, in order, and short:

1. **Name the likely thinking** — "You may have expected the list to be unchanged
   here." Naming it makes the learner feel understood rather than corrected.
2. **Say why it does not hold** — the specific mechanism, not a restatement of the
   rule.
3. **State what is actually true** — the correct model, briefly.
4. **Optionally, a handle** — a way to remember or a check to apply next time.

**Ceiling: 60 words.** It is read on a phone, immediately after a mistake, by
someone who wants to continue. An explanation that needs more belongs in the
tutor.

## Correct-answer confirmation

Brief and *out of the way* — one line confirming why it is right, matching the
`C14` feel rule that a correct answer should barely interrupt momentum. Where the
learner might have been right for the wrong reason, one clause naming the actual
reason is worth the interruption; otherwise nothing beyond the confirmation.

## Tone

Follows directly from the no-hard-fail decision (`FEATURE_PLAN.md:98`). A wrong
answer costs nothing mechanically, and the writing must not reimpose a cost the
mechanics removed:

- Never "obviously", "simply", "just", or "as you should know"
- Never blame — the misconception is a reasonable thing to have believed, and the
  text says so
- Second person, present tense, active voice
- No exclamation marks on the failure path
- The correct answer is stated plainly, never withheld to make a point

## The tutor standard

The tutor is explanation in conversational form (`FEATURE_PLAN.md:80`), so the
same four beats, tone, and honesty rules apply. Two additions specific to it:

- **"Explain differently" means a different representation** — an analogy, a
  concrete example, a counter-example, a decomposition into smaller steps. It does
  not mean the same explanation reworded, which is what a model does by default if
  not told otherwise.
- **The tutor may say it does not know.** Pre-generated explanations are checked
  by `P16` before shipping; tutor replies are not, so admitting uncertainty is the
  correct behaviour where `P14` grounding is thin.

## Open questions

- Whether per-distractor explanations are affordable at generation time for every
  MCQ, or whether they generate lazily on first miss — lazy would break the
  zero-latency promise the source is explicit about (`:79`), so probably not.
- Whether the 60-word ceiling holds for predict-output explanations, which often
  need to walk through evaluation step by step.
- Whether a re-queued exercise (`E01`) shows the same explanation on the second
  miss, or escalates to a different representation as the tutor would.
- Whether explanations should ever include a code snippet, given the card-reader
  layout constraints in `C14`.

## Acceptance criteria

- [ ] Every MCQ distractor has its own explanation addressing its labelled
      misconception
- [ ] Explanations follow the four-beat structure and respect the word ceiling
- [ ] No explanation contains blaming or minimising language, checked as a `P16`
      dimension across the golden set
- [ ] The correct answer is always stated explicitly on the incorrect path
- [ ] All explanations are pre-generated, so `C14` renders within one frame
- [ ] "Explain differently" in the tutor produces a genuinely different
      representation, not a rewording — verified by sampling
- [ ] The tutor declines rather than invents when grounding is absent
