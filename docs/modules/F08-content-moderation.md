# F08 — content-moderation

**Tier:** Foundation
**Code location:** `services/api/app/shared/moderation/`
**Milestone:** 8 (topic entry covered from milestone 2)
**Status:** not started

## Purpose

One moderation utility used everywhere free text crosses the boundary: the topic
the user types, their tutor messages, and the model's replies. Centralised because
the policy should be identical at every surface and because the tutor — the
largest surface — needs both input and output checked.

## Scope

**Owns**
- The moderation check itself and its policy configuration
- Input moderation for user-entered free text (topic entry, tutor messages)
- Output moderation for model-generated text
- The blocked-content response shape and how it degrades on the client

**Does not own**
- On-topic scoping of the tutor, which is a product guardrail not a safety one →
  `B17`
- Usage metering → `B17`
- Generated lesson content validity, which is a schema and correctness concern →
  `B06`, `B09`

## Source references

- `FEATURE_PLAN.md` § 2 "Tutor build considerations" — moderation on both user
  input and model output (line 81)
- `FEATURE_PLAN.md` § 7 "Cross-cutting" — moderation applies to tutor I/O and any
  user-entered free text (line 181)

## Depends on

`B03` (if a model-based classifier is used)

## Depended on by

`B04` (topic entry), `B16` and `B17` (tutor input and output)

## Interface

A single check function taking text plus a surface identifier, returning allow /
block with a reason code that `F02` can carry to the client.

## Decisions inherited

- **Both directions are moderated on the tutor**, not just user input
  (`FEATURE_PLAN.md:81`).
- **Any user-entered free text is in scope**, which in v1 means the topic box in
  `C07` as well as the tutor (`FEATURE_PLAN.md:181`).
- Moderation is distinct from the **on-topic guardrail** — declining to discuss
  something off-topic is a product decision owned by `B17`, while blocking harmful
  content is this module. Keeping them separate stops a scoping tweak from
  weakening safety.

## Open questions

- Which classifier: a Vertex AI safety setting, a dedicated moderation model, or
  a hybrid with a fast local pre-filter.
- Latency budget — this sits on the tutor's response path, which `E06` requires to
  feel immediate.
- Whether blocked content is logged for review, and how that squares with the PII
  minimisation commitment.

## Acceptance criteria

- [ ] One implementation is used by topic entry, tutor input, and tutor output
- [ ] A blocked input produces a clear, non-alarming client message rather than a
      generic error
- [ ] Output moderation cannot be bypassed by streaming — a blocked completion
      does not leave partial harmful text rendered on screen
- [ ] The check's added latency is measured against the `E06` tutor budget
- [ ] Policy changes are made in one place and take effect at every surface
