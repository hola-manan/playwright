# P05 — card-authoring-rules

**Tier:** Pedagogy
**Code location:** `packages/pedagogy/cards/`
**Milestone:** 2
**Status:** not started

## Purpose

What a good card contains, per type. The source fixes the four types and the
one-idea constraint but says nothing about what fills them — and cards are the
majority of what a learner reads. This module makes the difference between a card
that teaches and a card that merely states.

## Scope

**Owns**
- Rules for concept, code, example, and recap cards
- Length ceilings and the one-idea test applied per type
- Caption conventions for code cards
- Inline code usage in prose
- Terminology stability within and across lessons
- Substitution strategies where a diagram would normally be used

**Does not own**
- The one-idea principle itself → `P01`
- Snippet determinism and version rules → `P02`
- Rendering → `C09`
- Whether a card is factually correct → `P14`, `P16`

## Source references

- `FEATURE_PLAN.md` § 2 "Lesson & card structure" — card types; one idea per card;
  a dense lesson simply has more of them (lines 53–54)
- `FEATURE_PLAN.md` § 2 — no AI-generated diagrams or images in v1 (line 56)
- `FEATURE_PLAN.md` § 3 "Card reader" — code cards monospaced and syntax
  highlighted, horizontal scroll, copy; inline code styled distinctly (line 92)

## Depends on

`P01`, `P02`

## Depended on by

`P06`, `P08`, `P15`, `P16`, `B05`, `C09`

## Rules by type

### Concept card

- Exactly one claim, passing the `P01` one-idea test
- **Target ≤ 50 words, hard ceiling 80.** A concept needing more is two concepts
- At most one new term, defined at first use
- States the idea, then why it matters. A card that only defines is a glossary
  entry, not a lesson
- No forward references

### Code card

The substantive type, and the one that makes or breaks credibility in the tech
vertical.

- Snippet plus caption, both required
- **Target ≤ 8 lines, hard ceiling 12.** Longer means the idea is not yet
  decomposed
- One new construct per card
- Obeys every `P02` snippet convention — self-contained, deterministic, minimal
- **The caption says what to notice, not what the code says.** Restating the code
  in prose teaches nothing; pointing at the line that matters teaches
- Comments inside the snippet only where they carry the idea, never as narration

### Example card

- Applies a concept **already taught** — never introduces one
- Concrete and specific: a real situation, real values, a plausible outcome
- Follows the concept it illustrates, before the exercise that tests it — this is
  the worked-example stage of the `P01` progression

### Recap card

- Ends every lesson (`FEATURE_PLAN.md:54`)
- Restates the lesson's claims in **different words** than the cards used
- **Never contains new information.** A recap that teaches something is a defect,
  and `P15` checks for it
- One line per claim, in the order taught

## Terminology stability

One concept, one term, chosen once and used everywhere — including in exercises,
explanations, and the tutor. Where the subject has competing names, the `P02`
terminology authority picks, the alternatives are acknowledged once at first use,
and the chosen term is used thereafter. `P15` enforces this across a whole course.

## Teaching without diagrams

No images ship in v1 (`FEATURE_PLAN.md:56`), which bites hardest on spatial ideas
— network paths, tree structures, memory layout, request lifecycles. Permitted
substitutions:

- **Sequential decomposition** — walk the structure one step per card rather than
  showing it at once
- **Concrete analogy** — one, named as an analogy, and never stretched past the
  point it holds
- **Structured text** — indentation, ordered lists, and code-formatted trees where
  the shape is genuinely textual
- **Order-steps exercises** (`C13`) to make the learner reconstruct a sequence,
  which teaches structure better than a picture would

## Open questions

- Whether length ceilings are enforced in the schema (`B06`) or scored by the
  rubric (`P16`). Schema enforcement is absolute but causes regeneration churn on
  a near-miss; rubric scoring is softer but lets long cards through.
- Whether the caption-versus-narration rule is machine-checkable at all, or
  whether it is inherently a judge-scored dimension.
- How the recap card scales for a long lesson — one line per claim may itself
  exceed a card.
- Whether analogies should be allowed at all, given they are the most common
  source of subtly wrong mental models.

## Acceptance criteria

- [ ] Every type has written rules expressed as a `P10` fragment
- [ ] Generated cards respect length ceilings, measured across the golden set
- [ ] No code card introduces more than one new construct
- [ ] Captions point at what to notice rather than restating the snippet, scored
      by `P16`
- [ ] No recap card contains information not present earlier in its lesson
- [ ] Terminology is stable across a full generated course, verified by `P15`
- [ ] A spatial topic generated without diagrams is still comprehensible, checked
      on a golden topic chosen for exactly this
