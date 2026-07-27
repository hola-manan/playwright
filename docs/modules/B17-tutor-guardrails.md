# B17 — tutor-guardrails

**Tier:** Backend
**Code location:** `services/api/app/tutor/guardrails/`
**Milestone:** 8
**Status:** not started

## Purpose

The tutor's risk surface, separated from its conversation logic. Three concerns
live here: metering usage so an unbounded per-message cost stays bounded, keeping
the tutor on-topic so it stays a learning tool, and routing every message through
moderation in both directions. The source flags all three explicitly as the reason
a full chat is a bigger surface than preset actions.

## Scope

**Owns**
- Per-user usage metering and caps
- The cap-reached response and how it degrades
- The on-topic guardrail: scoped to learning, declines off-topic requests
- Wiring `F08` moderation into both the input and output paths
- Metering counters on `tutor_thread`

**Does not own**
- The moderation classifier itself → `F08`
- Conversation and context → `B16`
- Cost recording → `F07` (this module enforces; that module observes)

## Source references

- `FEATURE_PLAN.md` § 2 "Tutor build considerations" — cost per message
  (cap/meter free-tier usage), content moderation on both user input and model
  output, keeping the tutor on-topic (line 81)
- `FEATURE_PLAN.md` § 7 "Services → Tutor service" — per-user usage metering,
  moderation on input and output, on-topic guardrail (line 175)
- `FEATURE_PLAN.md` § 7 "Data model → tutor_thread" — usage metering counters
  (line 168)
- `FEATURE_PLAN.md` § 2 "Cost control & reuse" — per-user generation limits tie
  into monetization later (line 85)

## Depends on

`F08`, `F07`, `F01`

## Depended on by

`B16`

## Decisions inherited

- **Moderation runs on both user input and model output** — not input only
  (`FEATURE_PLAN.md:81`).
- **The tutor is scoped to learning and declines off-topic requests**
  (`FEATURE_PLAN.md:81`).
- **Usage is metered and capped per user**, tying into monetization later
  (`FEATURE_PLAN.md:81`, `85`).
- **On-topic scoping is a product guardrail, not a safety mechanism.** It is kept
  separate from `F08` deliberately so that loosening the topic scope can never
  weaken content safety.

## Open questions

- Cap values, and whether they are per day, per course, or per thread.
- Whether the on-topic check is a system-prompt instruction, a pre-classifier, or
  both. A prompt instruction is cheaper; a classifier is enforceable.
- What the user sees at the cap — a hard stop, or degraded service such as
  preset actions only. A hard stop on a learning question is a bad moment.

## Acceptance criteria

- [ ] No tutor message reaches the model without passing input moderation
- [ ] No model reply reaches the user without passing output moderation, including
      mid-stream
- [ ] An off-topic request is declined in a way that redirects to learning rather
      than simply refusing
- [ ] Usage counters are accurate under concurrent messages
- [ ] Reaching the cap produces a clear, non-punitive message with a next step
- [ ] Loosening the on-topic scope cannot weaken `F08` moderation
