# C01 — app-shell

**Tier:** Client
**Code location:** `apps/mobile/lib/core/shell/`
**Milestone:** 1
**Status:** not started

## Purpose

The container everything else lives in: app entry, routing, environment
configuration, session bootstrap, and the launch path. It decides what the user
sees on open — onboarding, home, or a resumed lesson — and it owns the cold-start
budget.

## Scope

**Owns**
- App entry, Firebase initialisation, dependency wiring
- Routing and deep-link handling, including notification deep links
- Environment configuration (staging vs prod)
- Launch routing: first run, returning user, or mid-lesson resume
- Splash and the first-frame path
- App lifecycle: backgrounding, resume, and telling `E02`/`E01` about it

**Does not own**
- Any screen's content
- Transition animations → `E03`
- Session state and identity → `C05`

## Source references

- `FEATURE_PLAN.md` § 1 "Edge cases" — user abandons mid-generation, resume state
  on next open (line 42)
- `FEATURE_PLAN.md` § 5 — the home screen as the daily landing screen (lines 138–140)
- `ARCHITECTURE.md` § "Stack at a Glance" (lines 125–138)

## Depends on

`C02`, `C03`, `C04`, `E03`, `F03`

## Depended on by

Every `C` module.

## Interface

The route table, and a documented launch-decision function taking session and
resume state and returning the initial route.

## Feel spec

Launch should feel like resuming, not starting. A returning mid-lesson user lands
back on their card, not on home with a "continue" button they must press. The
splash exists to cover initialisation, not to be seen — if it is noticeable, it is
too long.

## Latency budget

App launch to interactive under 1.5s per `E06`. Nothing on the launch path awaits
the network; the launch decision is made from local state and corrected afterwards
if the server disagrees.

## Degradation

Cold start with no connectivity still reaches a usable screen: home with cached
courses, or the resumed lesson from local state. The app is never a blank screen
waiting on a request.

## Accessibility

Respects OS text scaling from the first frame; no layout in the shell breaks at
the largest dynamic type setting.

## Open questions

- Whether resume goes straight into the lesson or to home with the lesson
  pre-opened — straight in is better for habit, worse for orientation after a long
  gap. Possibly time-dependent.
- State management choice, which this module effectively fixes for the whole app.
- Whether staging and prod are separate installable builds or one build with a
  switch.

## Acceptance criteria

- [ ] Launch reaches interactive within the `E06` budget on the lowest target
      device
- [ ] A user killed mid-lesson relaunches into that lesson at the exact position
- [ ] Notification deep links land on the correct screen from a cold start
- [ ] The app opens to a usable screen with no network
- [ ] Staging and prod cannot be confused at runtime
