# C05 — auth-ui

**Tier:** Client
**Code location:** `apps/mobile/lib/features/auth/`
**Milestone:** 1
**Status:** not started

## Purpose

Sign-in surfaces and client session state. Email, Google, and Apple, plus the
anonymous guest session that lets a new user reach their first card without an
account. Holds the token that `C03` injects and exposes the guest-versus-permanent
distinction the rest of the app branches on.

## Scope

**Owns**
- Sign-in screens for email, Google, and Apple
- Anonymous guest session creation at first launch
- Client-side session state and the current-user stream
- Triggering the `B02` upgrade when a guest signs up
- Sign-out

**Does not own**
- The soft account gate's placement and framing → `C06`
- Server-side migration → `B02`
- Account deletion UI → `C19`

## Source references

- `FEATURE_PLAN.md` § 1 "Soft account gate" — email + Google/Apple social login
  (line 37)
- `FEATURE_PLAN.md` § 7 "Services → Auth" (line 172)
- `ARCHITECTURE.md` § "Auth + Database" — guest → account migration (lines 57–59)
- `ARCHITECTURE.md` locked decisions — email + Google + Apple (line 22)

## Depends on

`B01`, `B02`, `C02`, `C04`

## Depended on by

`C01`, `C03`, `C06`, `C19`

## Feel spec

Sign-in is an interruption to something the user was enjoying, so it must be
short and obviously reversible. Social sign-in is the primary path and is
presented first; email is available but not the default. The screen never blocks
on a spinner — the OS sheets carry their own state.

## Latency budget

Guest session creation happens during launch and must not delay first interaction;
it can complete behind the value teaser in `C06`.

## Degradation

If sign-in fails, the user returns to exactly where they were with their guest
progress intact and a clear retry. A failed sign-up must never appear to have cost
them their lesson.

## Accessibility

Provider buttons carry proper labels, not icon-only affordances. Email fields use
correct input types and autofill hints.

## Open questions

- Apple sign-in is mandatory on iOS if Google is offered — confirm the
  presentation order satisfies review guidelines.
- Whether email sign-in is passwordless link or password; passwordless is fewer
  screens but adds an email round trip at the worst moment.
- What happens if a user signs in to an existing account while holding guest
  progress — merge, discard, or ask. The source only covers the new-account case.

## Acceptance criteria

- [ ] All three providers complete sign-in and produce a valid session
- [ ] A guest session exists from first launch without any user action
- [ ] Converting a guest triggers `B02` and preserves all progress
- [ ] A failed or cancelled sign-in returns the user to their prior state intact
- [ ] Sign-out clears local user data via `C04`
