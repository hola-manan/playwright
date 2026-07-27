# C12 — exercise-fill-blank

**Tier:** Client
**Code location:** `apps/mobile/lib/features/learn/exercises/fill_blank/`
**Milestone:** 3
**Status:** not started

## Purpose

Fill in the blank — the only exercise type whose **input mode changes with
difficulty**. Easier levels offer a bank of three to five tokens to tap; harder
levels and review mode require free typing, which in turn requires fuzzy answer
matching. That dual mode is the whole complexity of this module.

## Scope

**Owns**
- Token-bank mode: 3–5 provided tokens, tap to place, tap to remove
- Free-typing mode: text input with appropriate keyboard
- Mode selection from the exercise's difficulty
- **Fuzzy answer matching**: trimmed whitespace, case-insensitive where
  appropriate, accepted synonyms
- Blank presentation within prose or code

**Does not own**
- Which mode a given exercise uses → `P09` defines the lever, `B05` applies it
- The tolerance rules being implemented — what counts as a synonym, when case
  matters → `P06`. This module implements the spec it is handed
- Synonym lists → generated with the exercise by `B05`
- Feedback → `C14`

## Source references

- `FEATURE_PLAN.md` § 2 "Exercise types" — fill in the blank, input adapts to
  difficulty; tap-to-choose from 3–5 provided tokens at easier levels, free typing
  at harder levels and in review mode, needing fuzzy/normalized answer matching
  (line 66)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — token bank + blanks (line 96)
- `FEATURE_PLAN.md` § 3 "Review mode" (lines 105–108)

## Depends on

`C14`, `E04`, `E03` (token placement motion), `C02`

## Depended on by

`C08`, `C17`

## Interface

Implements the shared exercise contract from `C14`, plus a documented matching
function so the same normalisation can be unit-tested independently of the widget.

## Decisions inherited

- **Input adapts to difficulty**: token bank at easier levels, free typing at
  harder levels (`FEATURE_PLAN.md:66`).
- **Review mode always uses free typing**, even where the original presentation
  offered tokens — review is meant to be harder recall
  (`FEATURE_PLAN.md:66`, `B15`).
- **Matching normalises**: trim whitespace, case-insensitive where appropriate,
  accept known synonyms (`FEATURE_PLAN.md:66`). "Where appropriate" is doing real
  work — case matters in code and not in prose.

## Feel spec

Token placement should feel like snapping into place: the token animates from the
bank into the blank on the interactive spring, with a selection haptic. Removing
it reverses cheaply.

Free typing must not fight the user. The keyboard type matches the content, and
the blank stays visible above the keyboard — a blank hidden behind the keyboard is
the most common way this exercise type fails.

A near-miss that the fuzzy matcher accepts should be marked correct without
comment. A near-miss it rejects must show the expected answer prominently, because
that is the case where the user most suspects the app is wrong.

## Latency budget

Matching is local and instantaneous. Result within one frame per `E06`.

## Degradation

Fully offline. If synonyms are missing from the payload, matching falls back to
normalised exact comparison rather than failing.

## Accessibility

Tokens are labelled buttons, not drag-only affordances. Free typing works with
autocorrect disabled where the answer is code. The blank's position is announced
so a screen-reader user knows where their answer lands.

## Open questions

- Whether case sensitivity is decided per exercise by `B05` or inferred from
  whether the blank sits in code or prose.
- Whether tokens support drag as well as tap — tap alone is more accessible and
  simpler.
- Multiple blanks per exercise: supported in v1 or not.

## Acceptance criteria

- [ ] Both input modes work and are selected by difficulty
- [ ] Review mode forces free typing
- [ ] The matching function is unit-tested against whitespace, case, and synonym
      cases independently of the widget
- [ ] The blank remains visible above the keyboard on the smallest target screen
- [ ] Tokens are operable by screen reader without dragging
- [ ] Works fully offline
