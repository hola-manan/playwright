# F02 — api-contract

**Tier:** Foundation
**Code location:** `packages/contracts/`
**Milestone:** 1
**Status:** not started

## Purpose

The negotiated boundary between the Flutter client and the FastAPI service. Every
request shape, response shape, streaming envelope, error format, and auth
convention is defined here once. Client and backend modules both cite this file
rather than agreeing bilaterally, so a change to the boundary is a change to one
document with two reviewers.

## Scope

**Owns**
- REST endpoint inventory, request/response Pydantic models, and the generated
  Dart equivalents
- The **SSE envelope**: event names, partial-payload framing, completion and error
  events, resume-from-offset semantics
- Auth convention — Firebase ID token as bearer, and how guest sessions are
  represented
- The error envelope, and the mapping from backend failure to client-visible state
- Versioning policy for breaking changes

**Does not own**
- Transport implementation on the client → `C03` (REST) and `E02` (SSE)
- Business behaviour behind any endpoint → the owning `B` module
- Storage shapes → `F01`

## Source references

- `ARCHITECTURE.md` § "AI compute — Cloud Run" — streams tokens to the Flutter
  client over SSE / streaming HTTP (lines 74–82)
- `ARCHITECTURE.md` § "Backend language — Python" — FastAPI covers streaming/SSE,
  Pydantic validates structured output (lines 61–65)
- `ARCHITECTURE.md` § "Stack at a Glance" (lines 125–138)
- `FEATURE_PLAN.md` § 7 "Services" (lines 171–177)

## Depends on

`F01` (the shapes being serialised)

## Depended on by

`C03`, `E02`, and every `B` module that exposes an endpoint.

## Interface

Endpoint groups, each owned by the module named:

| Group | Owner | Streaming |
|-------|-------|-----------|
| `/auth/*` — session exchange, guest upgrade | `B01`, `B02` | no |
| `/courses/outline` — topic → syllabus | `B04` | **yes** |
| `/courses/{id}/lessons/{n}` — lesson content | `B05`, `B07` | **yes** |
| `/courses/*` — enrollment, deltas, listing | `B11` | no |
| `/progress/*` — answer results, lesson completion | `B12` | no |
| `/habit/*` — XP total, goal, streak, daily activity | `B14` | no |
| `/review/*` — due set, review results | `B15` | no |
| `/tutor/threads/*` — messages | `B16` | **yes** |
| `/notifications/token` — FCM registration | `B19` | no |
| `/account` — settings, delete | `B01`, `B02` | no |

## SSE envelope

Three streams exist (outline, lesson, tutor) and they share one framing so `E02`
implements the consumer once:

- `event: chunk` — an incremental payload fragment
- `event: item` — a completed sub-unit (an outline row, a finished card)
- `event: done` — terminal success, carries the persisted entity id
- `event: error` — terminal failure, carries an error code `E02` can map to a
  retry or fallback path

`item` is what makes progressive rendering possible: the client can show outline
row 1 or card 1 without waiting for the stream to finish
(`FEATURE_PLAN.md:36,50`). Streams carry a monotonic index so a reconnect can
resume rather than restart.

## Decisions inherited

- **FastAPI + Pydantic on the backend**, so request/response models are Pydantic
  and are the source for generated client types (`ARCHITECTURE.md:61-65`).
- **Firebase Auth** issues the identity token; guest sessions are anonymous auth
  upgraded in place, so the contract must express "authenticated but guest"
  (`ARCHITECTURE.md:57-59`).
- **Cloud Run has no hard execution-timeout ceiling**, so long streamed generation
  is legitimate and the contract does not need a chunked-polling fallback
  (`ARCHITECTURE.md:78-80`).

## Open questions

- Whether generated Dart types are checked in or generated at build time in `F05`.
- Error-code taxonomy granularity: enough for `E02` to choose a degradation path
  without leaking backend internals.
- Whether `/habit` and `/progress` merge into one write endpoint to cut round
  trips on the answer path.

## Acceptance criteria

- [ ] Every endpoint in the inventory has a request model, response model, and
      error case defined
- [ ] The three streams use one shared envelope, consumable by a single `E02`
      implementation
- [ ] The envelope supports resume-from-offset without restarting generation
- [ ] A breaking change procedure is written down and references the two-tier
      review requirement
- [ ] Guest vs. authenticated is representable and testable at the contract level
