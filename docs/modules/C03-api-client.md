# C03 — api-client

**Tier:** Client
**Code location:** `apps/mobile/lib/core/api_client/`
**Milestone:** 1
**Status:** not started

## Purpose

Request/response transport against the `F02` contract: base configuration, auth
header injection, typed serialisation, error mapping, and retry. Streaming is
explicitly **not** here — `E02` owns SSE — so this module stays a simple, boring,
well-tested HTTP layer.

## Scope

**Owns**
- HTTP client configuration and base URLs per environment
- Firebase ID token injection and refresh on 401
- Typed request/response serialisation from `F02`
- Mapping backend error codes to client-facing failure types
- Retry and backoff for idempotent requests
- Connectivity detection feeding the offline paths in `C04` and `E05`

**Does not own**
- SSE and progressive rendering → `E02`
- The contract itself → `F02`
- Local persistence → `C04`
- Any UI

## Source references

- `ARCHITECTURE.md` § "Stack at a Glance" — HTTPS/SSE to the Cloud Run service
  (lines 125–138)
- `ARCHITECTURE.md` § "Auth + Database" — Firebase Auth integration (lines 48–59)
- `FEATURE_PLAN.md` § 7 "Services" (lines 171–177)

## Depends on

`F02`, `C05` (token source)

## Depended on by

Every `C` module that talks to the backend, plus `E02` (base config and auth) and
`E05` (award sync).

## Interface

One typed method per `F02` endpoint, plus a documented failure type per error
class so callers can choose a degradation path without string-matching.

## Feel spec

This module's contribution to feel is negative space: it must never be on the path
of an interaction that should feel instant. Anything user-visible that waits on
this layer is a design error somewhere else.

## Latency budget

Token refresh must not add a round trip to every request — tokens are cached and
refreshed proactively. Retries use backoff and never block the UI thread.

## Degradation

Offline is a normal state, not an error. Requests that can be deferred are handed
to `C04`'s queue; requests that cannot return a typed failure the caller can
render as a real state rather than a generic error dialogue.

## Accessibility

No direct surface. Error types must carry text suitable for screen readers rather
than codes.

## Open questions

- Whether generated client types come from `F02` at build time or are checked in.
- Which requests are safe to auto-retry given `E05` and `B12` handle idempotency
  independently.
- Connectivity detection strategy — OS reachability lies often enough that
  request outcomes may be the better signal.

## Acceptance criteria

- [ ] Every `F02` endpoint has a typed method and a typed failure
- [ ] A 401 triggers exactly one refresh and one retry, never a loop
- [ ] No SSE code exists in this module
- [ ] Offline produces typed failures, never unhandled exceptions
- [ ] No request blocks the UI thread
