# B19 — fcm-delivery

**Tier:** Backend
**Code location:** `services/api/app/notifications/fcm/`
**Milestone:** 6
**Status:** not started

## Purpose

The delivery mechanism. Registers and maintains FCM tokens, sends the messages
`B18` decides on, and handles the token lifecycle — refreshes, invalidations, and
multi-device. Kept separate from scheduling so that delivery problems and policy
problems stay distinguishable.

## Scope

**Owns**
- FCM token registration, refresh, and removal
- Multi-device token sets per user
- The send call and its retry policy
- Handling delivery failures and pruning dead tokens
- Deep-link payloads so a tap lands on the right screen

**Does not own**
- Who and when → `B18`
- Copy → `B18`
- Client-side permission handling and token acquisition → `C06`, `C01`

## Source references

- `ARCHITECTURE.md` § "Notifications — FCM" (lines 110–113)
- `ARCHITECTURE.md` locked decisions table — push notifications: FCM (line 27)
- `FEATURE_PLAN.md` § 7 "Data model → user" — notification token (line 159)
- `FEATURE_PLAN.md` § 4 "Notifications" (lines 130–134)

## Depends on

`F03` (Firebase project), `F01` (token storage)

## Depended on by

`B18`, `B02` (deletion must remove tokens)

## Data touched

Notification token(s) on `user`.

## Decisions inherited

- **FCM, native to the stack** (`ARCHITECTURE.md:110-111`,
  locked decisions line 27).
- **Delivery is timezone-aware and respects OS permission plus quiet hours** — the
  policy is `B18`'s, but this module must not deliver anything that policy
  suppressed (`ARCHITECTURE.md:112-113`).
- **Account deletion must remove tokens** so no notification can reach a deleted
  user (`FEATURE_PLAN.md:153`, enforced with `B02`).

## Open questions

- Whether multiple devices per user are supported in v1 or whether the newest
  token wins. Multi-device is more correct but multiplies sends.
- Deep-link targets: home, the active lesson, or the review session, depending on
  which notification.
- Retry policy for transient FCM failures, and when a token is considered dead.

## Acceptance criteria

- [ ] A token registered at onboarding receives a notification
- [ ] A refreshed token replaces the old one without producing duplicate sends
- [ ] Invalid tokens are pruned rather than retried indefinitely
- [ ] Tapping a notification deep-links to the intended screen
- [ ] Deleting an account removes every token, verified by attempting a send
