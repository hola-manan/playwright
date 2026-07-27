# C16 — home-screen

**Tier:** Client
**Code location:** `apps/mobile/lib/features/home/`
**Milestone:** 6
**Status:** not started

## Purpose

The daily landing screen. Its job is to make "what do I do right now" a one-tap
answer. It carries the streak and goal state that the whole habit loop is built
around, and it is where a returning user lands every day after the first.

## Scope

**Owns**
- Top bar: streak flame and count, today's goal progress ring, total XP
- The continue card — the active course, hero-sized, with "Continue — Lesson N"
- The daily review card, shown when items are due, with the count
- My courses list, in-progress and completed, each with progress
- "Start a new topic" entry into `C07`
- The empty state for an account with no second course yet

**Does not own**
- Flame and ring animation → `E04`
- XP and streak values → `E05`, `B14`
- Review scheduling and the due count → `B15`
- The generation flow → `C07`

## Source references

- `FEATURE_PLAN.md` § 5 "Home / My Courses" — entire section (lines 138–147)
- `FEATURE_PLAN.md` § 4 "Streak" — prominent flame + count on the home screen
  (line 126)
- `FEATURE_PLAN.md` § 3 "Review mode" — a separate daily review session surfaced
  on the home screen (line 106)

## Depends on

`B11`, `B14`, `B15`, `E04`, `E05`, `E03`, `C02`

## Depended on by

`C01`

## Decisions inherited

- **The continue card is the hero and the default action every day**
  (`FEATURE_PLAN.md:143`).
- **The review card appears only when items are due**, showing the count — for
  example "12 items to review" — and is the fast path to hitting the goal
  (`FEATURE_PLAN.md:144`).
- **"Start a new topic" is always available** (`FEATURE_PLAN.md:146`).
- **The streak flame and count are prominent** (`FEATURE_PLAN.md:126`).
- **The empty state guides toward starting a second topic or reviewing**
  (`FEATURE_PLAN.md:147`).

## Feel spec

The top bar is the app's status line and the most-looked-at pixels in the product.
The goal ring must animate on arrival if XP changed since last view — a user
returning after finishing a lesson on another device should see the ring sweep,
not find it already full.

The continue card is the hero in both hierarchy and motion: tapping it plays the
`E03` shared-element transition into the lesson, so the card the user pressed
becomes the lesson they are reading.

The flame carries state: idle flicker when safe, desaturated slow pulse when the
streak is at risk. That pulse is the screen's one piece of urgency and it must not
be used for anything else.

## Latency budget

Renders from local state within the launch budget in `E06` — never a loading
screen. Server values arrive afterwards and reconcile via `E05` without visible
jumps.

## Degradation

Fully usable offline from cached state: streak, XP, course list, and the continue
card all render. The review count may be stale, which is acceptable; the review
session itself needs `B15`.

## Accessibility

The goal ring's value is available as text, not only as a shape. The flame's
at-risk state is conveyed by label as well as by pulse. The continue card is the
first focusable element after the top bar.

## Open questions

- Ordering of the courses list — recency, progress, or manual.
- Whether completed courses stay in the main list or move to a separate section.
- What the continue card shows when the active course's next lesson is still
  generating.
- Whether the review card competes with or complements the continue card when both
  are available; the source implies review is the fast path, not the default.

## Acceptance criteria

- [ ] The continue card resumes the correct lesson in one tap
- [ ] The review card appears only when items are due and shows an accurate count
- [ ] The goal ring animates from its previous value rather than appearing full
- [ ] Streak flame reflects safe, at-risk, and incremented states
- [ ] The screen renders fully offline from cached state
- [ ] The empty state offers a clear next action
