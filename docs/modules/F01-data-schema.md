# F01 — data-schema

**Tier:** Foundation
**Code location:** `packages/schema/`
**Milestone:** 1
**Status:** not started

## Purpose

The single definition of the relational data model. Every table, column, enum,
index, and migration lives here, expressed as a Firebase Data Connect schema over
managed PostgreSQL (Cloud SQL). No other module defines storage; they reference
this one. Data Connect generates type-safe SDKs from this schema, so a change here
propagates to both the Flutter client and the Python service.

## Scope

**Owns**
- Table and enum definitions for the full v1 model
- Migrations, run in strict mode as a deploy step, staging first
- Generated SDK configuration for Dart and Python consumers
- Index and constraint design

**Does not own**
- Business rules over the data — each owning module (`B11`–`B15`) owns those
- Which fields the API exposes → `F02`
- Deletion semantics and cascade behaviour at the application level → `B02`

## Source references

- `FEATURE_PLAN.md` § 7 "Backend / Platform → Data model (sketch)" (lines 158–169)
- `ARCHITECTURE.md` § "Auth + Database — Firebase Auth + Data Connect (PostgreSQL)" (lines 48–59)
- `ARCHITECTURE.md` § "CI/CD → Backend" — migrations as a deploy step (lines 157–158)

## Depends on

`F03` (Cloud SQL instance and project layout)

## Depended on by

Every backend module (`B01`–`B19`), and `F02` for the shapes it serialises.

## Table inventory

| Table | Owning module | Notes |
|-------|---------------|-------|
| `user` | `B01` | Firebase UID, timezone, experience level, daily-goal XP target, reminder time, quiet hours, FCM token, `is_guest` |
| `course` | `B11` | topic, `normalized_topic` (cache key), outline JSONB, `source` enum, `visibility` enum, `author_ref` nullable, depth, level |
| `lesson` | `B05` | `course_id`, `order_index`, title, one-liner, estimated minutes, `generation_status` enum |
| `card` | `B05` | `lesson_id`, `order_index`, `type` enum, content JSONB |
| `exercise` | `B05` | `lesson_id`, `order_index`, `type` enum, prompt, options/tokens JSONB, answer key, `answer_key_verified`, pre-generated explanation, difficulty |
| `enrollment` | `B11` | `user_id` × `course_id`, personal deltas JSONB (skipped lessons, difficulty adjustment) |
| `progress` | `B12` | per user per lesson: status, started/completed timestamps |
| `exercise_result` | `B12` | per attempt: `exercise_id`, correct, `latency_ms`, `attempt_no`, answered at |
| `review_item` | `B15` | per user per exercise: box, interval, `next_due_on` |
| `daily_activity` | `B14` | per user per local date: XP earned, `goal_met` — streak is derived from this history |
| `tutor_thread` | `B16` | per user per course, with metering counters |
| `tutor_message` | `B16` | role, content, context ref, token count |
| `analytics_event` | `F06` | append-only |

## Decisions inherited

- **PostgreSQL, not NoSQL.** Data Connect gives a real relational database on Cloud
  SQL with joins and type-safe generated SDKs, so the model above maps directly
  with no NoSQL compromise (`ARCHITECTURE.md:49-54`).
- **`source` enum exists in v1 even though only `ai` is used.** Community content
  in v2 is then additive rather than a rewrite (`FEATURE_PLAN.md:160`).
- **A shared cached course is just a `course` row reused across users**, with
  per-user variation living in `enrollment` deltas (`FEATURE_PLAN.md:160,164`).
- **Streak is derived from `daily_activity`, never stored as a counter.** This is
  what lets streak freezes be added later without a migration
  (`FEATURE_PLAN.md:128,167`).
- **Vector search is available but unused in v1** — noted so no second datastore
  gets introduced for it later (`ARCHITECTURE.md:55-56`).

## Open questions

- Do `card` and `exercise` content payloads stay JSONB, or get promoted to typed
  columns once the generators stabilise? JSONB is the v1 default.
- Retention policy for `analytics_event` and `exercise_result` at volume.
- Whether `progress` and `exercise_result` need partitioning by user for the
  review query in `B15`.

## Acceptance criteria

- [ ] Every table in the inventory above exists with its enums and constraints
- [ ] Migrations run in strict mode against staging before prod, as a deploy step
      ordered ahead of the Cloud Run deploy that depends on them
- [ ] Dart and Python SDKs generate cleanly and are consumed by at least one
      module in each tier
- [ ] `daily_activity` shape supports inserting a backdated freeze row without
      schema change
- [ ] A full user delete can be expressed as a bounded set of statements — `B02`
      can purge without orphans
