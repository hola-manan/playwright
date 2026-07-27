# C04 — local-persistence

**Tier:** Client
**Code location:** `apps/mobile/lib/core/storage/`
**Milestone:** 1
**Status:** not started

## Purpose

On-device state. Three things depend on it existing: a guest can complete a full
lesson before any account exists and must not lose it; a user who abandons
mid-generation must be able to resume; and `E06` requires that nothing blocks on
the network, which means results and XP awards need somewhere local to live until
they sync.

## Scope

**Owns**
- Guest progress storage before an account exists
- The outbound queue for answer results and XP awards
- Resume state: mid-lesson position, re-queue contents, mid-generation state
- Cached course and lesson content for offline reading
- Clearing local state on sign-out and on account deletion

**Does not own**
- What to sync and when → `E05`, `E01`
- Server persistence → `B12`, `B14`
- Migration of guest data server-side → `B02`

## Source references

- `FEATURE_PLAN.md` § 1 — user completes their first lesson as a guest, no account
  required (line 36)
- `FEATURE_PLAN.md` § 1 "Edge cases" — abandons mid-generation, resume on next
  open; guest who never signs up keeps local progress (lines 42–43)
- `FEATURE_PLAN.md` § 1 "Soft account gate" — guest progress migrates on sign-up
  (line 37)

## Depends on

`C02` (nothing visual), `F01` (shapes it mirrors)

## Depended on by

`E01`, `E02`, `E05`, `C01`, `C06`

## Feel spec

Invisible when working. Its whole job is that the user never learns which parts of
the app needed a network. A lesson read on a train should be indistinguishable
from one read on wifi.

## Latency budget

Reads on the launch path and the answer path must be synchronous-fast — no
awaiting a slow store before showing a card or ticking XP.

## Degradation

If local storage is unavailable or corrupt, the app must still run in a degraded
online-only mode rather than failing to launch. Corrupt resume state is discarded
rather than crashing on restore.

## Accessibility

No direct surface.

## Open questions

- Storage mechanism, and whether cached lesson content warrants a different store
  from small queues.
- Retention policy for cached courses — unbounded caching of long courses will
  grow.
- Whether guest progress that is never converted is eventually purged, and after
  how long (`FEATURE_PLAN.md:43` says keep it and re-prompt gently).

## Acceptance criteria

- [ ] A guest completes a full lesson with the network disabled and loses nothing
- [ ] Queued results and awards survive an app kill and replay correctly
- [ ] Resume state restores `E01` position including the re-queue
- [ ] Corrupt local state is discarded without preventing launch
- [ ] Sign-out and account deletion leave no residual user data on device
