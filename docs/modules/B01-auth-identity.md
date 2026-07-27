# B01 — auth-identity

**Tier:** Backend
**Code location:** `services/api/app/identity/`
**Milestone:** 1
**Status:** not started

## Purpose

Identity at the API boundary. Verifies Firebase ID tokens, provisions the `user`
row on first contact, exposes the current user to every other module, and
represents guest sessions as first-class authenticated identities so a signed-out
learner can still complete a full lesson.

## Scope

**Owns**
- Firebase ID token verification middleware
- `user` row provisioning and the profile fields on it
- The "authenticated but guest" distinction
- Settings reads/writes on `user`: timezone, experience level, daily-goal XP
  target, reminder time, quiet hours

**Does not own**
- Guest → account migration and deletion → `B02`
- Sign-in UI → `C05`
- FCM token storage → `B19`

## Source references

- `FEATURE_PLAN.md` § 7 "Services → Auth" (line 172)
- `FEATURE_PLAN.md` § 7 "Data model → user" (line 159)
- `FEATURE_PLAN.md` § 6 "Learning settings" (line 152)
- `ARCHITECTURE.md` § "Auth + Database" (lines 48–59)

## Depends on

`F01`, `F02`, `F03`

## Depended on by

Every authenticated endpoint — effectively all of Tier B.

## Interface

Request-scoped current-user dependency for FastAPI, plus `/account` settings
endpoints per `F02`.

## Data touched

`user` — read and write. Reads only, elsewhere.

## Decisions inherited

- **Firebase Auth covers email, Google, and Apple sign-in**, including anonymous
  auth for guests (`ARCHITECTURE.md:57-59`, locked decisions table line 22).
- **Guest sessions are real authenticated sessions**, not an unauthenticated
  mode — anonymous auth is later upgraded in place (`ARCHITECTURE.md:57-59`).
- **Timezone is stored on the user** and is the basis for day boundaries in `B14`
  (`FEATURE_PLAN.md:119,159`).

## Open questions

- Token verification caching, so every request does not pay a verification cost
  against the `E06` budget.
- Whether experience level lives here or moves to `enrollment` once per-course
  difficulty diverges.

## Acceptance criteria

- [ ] An invalid, expired, or absent token is rejected consistently with the `F02`
      error envelope
- [ ] First contact from a new Firebase UID provisions exactly one `user` row,
      with no duplicate under concurrent requests
- [ ] Guest identity is distinguishable from a permanent account at every endpoint
- [ ] Timezone is captured before `B14` needs it
