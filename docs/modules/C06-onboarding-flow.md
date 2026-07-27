# C06 — onboarding-flow

**Tier:** Client
**Code location:** `apps/mobile/lib/features/onboarding/`
**Milestone:** 1 (tuned at 10)
**Status:** not started

## Purpose

The most important screen sequence in the app — it decides whether a new install
becomes a day-2 user. This module owns the genuinely first-run parts of that
sequence and the ordering discipline behind it: let the user taste the product
before asking for anything, and get from topic to first card in under 60 seconds.

The topic entry and outline steps sit in `C07` because they are reused every time
a user starts a new course; everything else in the first-run sequence is here.

## Scope

**Owns**
- Value teaser: one line, one button, no sign-up wall
- Quick calibration: experience level and daily goal, two taps, skippable with
  defaults
- The soft account gate after the first lesson's win screen
- Guest-progress migration UI and its reassurance
- Notification permission, framed around the streak
- Abandon and resume across the whole sequence
- Sequencing and the 60-second budget

**Does not own**
- Topic entry and outline confirmation → `C07`
- The first lesson itself → `C08`, `E01`
- Sign-in mechanics → `C05`
- Server-side migration → `B02`

## Source references

- `FEATURE_PLAN.md` § 1 "Onboarding & First Run" — entire section (lines 28–43)
- `FEATURE_PLAN.md` § 1 "Sequence" steps 1, 3, 5, 6 (lines 33, 35, 37, 38)
- `FEATURE_PLAN.md` § 1 "Edge cases" (lines 40–43)
- `FEATURE_PLAN.md` § "v1 Build Milestones" — polish and onboarding tuning
  (line 199)

## Depends on

`C05`, `C07`, `C04`, `B02`, `E06`

## Depended on by

`C01` (launch routing)

## Sequence

```
1. Value teaser          ── one line, "Start learning". No account wall
2. Topic pick            ── C07
3. Quick calibration     ── level + daily goal, skippable (defaults: Some / Regular)
4. Generation + payoff   ── C07, then first lesson as a GUEST
5. Soft account gate     ── after the win screen: "keep your streak"
6. Notification permission ── framed by streak, with the chosen reminder time
```

## Decisions inherited

- **The topic pick comes before any account step** — it is the hook
  (`FEATURE_PLAN.md:34`).
- **The user completes their entire first lesson as a guest**, full card and
  exercise experience, no account required (`FEATURE_PLAN.md:36`).
- **The account gate arrives after the win screen**, framed as saving progress and
  keeping the streak — not before the payoff (`FEATURE_PLAN.md:37`).
- **Notification permission is requested here, framed around the streak with the
  user's chosen reminder time — not a cold OS prompt on launch**
  (`FEATURE_PLAN.md:38`).
- **Calibration is skippable with sensible defaults** (Some / Regular)
  (`FEATURE_PLAN.md:35`).
- **A guest who never signs up keeps local progress; re-prompt gently, do not
  nag** (`FEATURE_PLAN.md:43`).

## Feel spec

Every screen here is a toll on the way to the product, so each must justify
itself in one glance. The calibration step is two taps and visibly skippable. The
account gate arrives at the emotional peak — immediately after the win screen's
celebration, while the user is holding something they do not want to lose — and
its copy must reference what they just earned, not what the app wants.

The notification prompt is the same pattern: it follows a moment of success and
names the specific benefit and time, so the OS dialogue that follows is a
formality rather than a surprise.

## Latency budget

**Topic to first card in under 60 seconds, end to end** (`E06`,
`FEATURE_PLAN.md:30`). This is the module's headline number and the reason `C07`
streams rather than waits. Calibration must not sit on the critical path — it can
be answered while generation runs behind it.

## Degradation

- Generation fails or times out → friendly retry plus a pre-cached starter topic,
  so the first run is never a dead end (`FEATURE_PLAN.md:41`)
- User abandons mid-generation → resume state on next open
  (`FEATURE_PLAN.md:42`)
- Sign-up fails at the gate → progress is visibly retained, retry offered
- Notification permission denied → the flow continues without complaint and never
  re-prompts aggressively

## Accessibility

The sequence is completable with a screen reader and at the largest type setting.
Skip affordances are reachable without scrolling. No step is time-limited.

## Open questions

- Whether calibration runs *during* generation to save wall-clock time against the
  60-second budget, at the cost of a busier moment.
- Exact re-prompt cadence for a guest who declines the account gate — "gently"
  needs a number.
- Whether the value teaser is skippable for a returning install.

## Acceptance criteria

- [ ] Topic to first card measured under 60s on a mid-tier device and a typical
      connection
- [ ] A user reaches their first card with no account and no permission prompts
- [ ] The account gate appears only after the first win screen
- [ ] Notification permission is requested with the user's chosen time in the copy
- [ ] Calibration is skippable and defaults are applied
- [ ] Killing the app at any onboarding step resumes correctly
- [ ] A forced generation failure lands on the starter topic, never a dead end
