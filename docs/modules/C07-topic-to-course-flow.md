# C07 — topic-to-course-flow

**Tier:** Client
**Code location:** `apps/mobile/lib/features/topic_to_course/`
**Milestone:** 2
**Status:** not started

## Purpose

Topic in, confirmed course out. Free-text entry with popular-topic chips, the one
scoping question for over-broad topics, the streamed outline reveal, outline
editing, the depth control, and confirmation. Deliberately **not** an onboarding
sub-step: this exact flow is reused every time a user taps "Start a new topic"
from home.

## Scope

**Owns**
- Topic entry: free-text box plus popular chips
- The scoping question when the topic is too broad
- Streamed outline reveal, consuming `E02`
- Outline editing: remove lessons, mark "I already know this", ask for more depth
- The depth control: Quick intro / Solid working knowledge / Deep
- Confirmation and handoff into lesson 1

**Does not own**
- Outline generation → `B04`
- Enrollment deltas from those edits → `B11`
- Streaming mechanics → `E02`
- First-run framing around this flow → `C06`

## Source references

- `FEATURE_PLAN.md` § 2 "Flow" (lines 47–50)
- `FEATURE_PLAN.md` § 1 "Topic pick" (line 34)
- `FEATURE_PLAN.md` § 1 "Generation with payoff" (line 36)
- `FEATURE_PLAN.md` § 5 "Start a new topic" — always-available entry back into
  the generation flow (line 146)

## Depends on

`E02`, `B04`, `B11`, `C02`, `E03`

## Depended on by

`C06`, `C16`

## Decisions inherited

- **The topic box plus chips is the hook**, and it comes before any account step
  (`FEATURE_PLAN.md:34`).
- **One scoping question maximum** for a broad topic, before anything is built
  (`FEATURE_PLAN.md:48`).
- **The outline is the main up-front personalisation lever** and is cheap to
  generate, which is why editing it is worth the screens
  (`FEATURE_PLAN.md:49`).
- **Depth control sets intent** across three levels and scales both coverage and
  granularity (`FEATURE_PLAN.md:49`).
- **The user can remove lessons, mark "I already know this", or ask for more depth
  on any part, then confirm** (`FEATURE_PLAN.md:49`).
- **This flow is reachable from home, not only from onboarding**
  (`FEATURE_PLAN.md:146`).

## Feel spec

The outline reveal is the product's first real magic moment, and it must read as
*writing*, not *loading*. Rows arrive one at a time with the `E03` stagger, so the
user watches a syllabus assemble itself. No spinner appears at any point.

Editing must feel cheap and non-destructive — removing a lesson is a tap with an
obvious undo, not a confirmation dialogue. The depth control shows its effect:
changing it visibly changes the outline rather than silently affecting a future
generation.

The confirm button is present and tappable from the moment enough of the outline
exists to judge it. An impatient user should not have to wait for row 20.

## Latency budget

First outline row within 3s per `E06`. This flow carries the largest share of the
60-second onboarding budget, which is why it streams.

## Degradation

- Timeout or failure → friendly retry plus a pre-cached starter topic
  (`FEATURE_PLAN.md:41`)
- Abandoned mid-generation → resume on next open (`FEATURE_PLAN.md:42`)
- Partial outline received then connection lost → show what arrived, offer to
  continue; never discard rows already paid for
- Topic blocked by `F08` → clear, non-alarming message with the box still editable

## Accessibility

Streaming rows are announced at a sane cadence, not per row for a long outline.
The depth control is a labelled three-option control, not an unlabelled slider.
Edit affordances are reachable by screen reader.

## Open questions

- Whether "ask for more depth on this part" regenerates immediately or is applied
  at confirmation — immediate is more satisfying but more expensive.
- How the chips are chosen: static list, popularity from `B10`, or both.
- Whether the depth control appears before generation or after the first outline,
  as a way to re-roll.

## Acceptance criteria

- [ ] The outline streams row by row, staggered, with no spinner
- [ ] Confirm is available before the outline finishes arriving
- [ ] All three edit actions work and produce `B11` deltas
- [ ] Depth control visibly changes the outline across all three settings
- [ ] A broad topic produces exactly one scoping question
- [ ] The flow is reachable identically from onboarding and from home
- [ ] First row arrives within the `E06` budget
