# B16 — tutor-service

**Tier:** Backend
**Code location:** `services/api/app/tutor/service/`
**Milestone:** 8
**Status:** not started

## Purpose

The conversational tutor: a persistent chat thread per course that the user can
open from any card or exercise. Its defining property is context-awareness — it
knows the current card, the user's answer, and where they are in the course — so
"why is my answer wrong?" works without the user re-explaining anything. This is
the largest single feature in v1 and is built after the core loop is solid so it
is additive.

## Scope

**Owns**
- Thread and message persistence per user per course
- Context injection: current card, the user's answer, position in the course
- Streamed replies over the `F02` envelope
- The preset quick actions that seed a thread
- Conversation history management within the model's context window

**Does not own**
- Metering, on-topic scoping, moderation → `B17`
- Chat UI → `C18`
- Model access → `B03`

## Source references

- `FEATURE_PLAN.md` § 2 "Explanations & tutor chat" (lines 78–81)
- `FEATURE_PLAN.md` § 7 "Services → Tutor service" (line 175)
- `FEATURE_PLAN.md` § 7 "Data model → tutor_thread / tutor_message" (line 168)
- `FEATURE_PLAN.md` § "v1 Build Milestones" — biggest single feature, build after
  the core loop (line 197)
- `ARCHITECTURE.md` § "LLM — tiered" — Flash for the tutor (lines 85–86)

## Depends on

`B03`, `B17`, `B11`, `F07`

## Depended on by

`C18`, `C14`

## Data touched

`tutor_thread`, `tutor_message` — read and write, including metering counters read
by `B17`.

## Decisions inherited

- **A full conversational tutor, not preset actions.** Preset quick actions
  ("explain differently", "give me an example", "why is this wrong?") seed the
  thread, but the user can free-type follow-ups (`FEATURE_PLAN.md:80`).
- **Context-aware by construction** — it knows the current card, the user's
  answer, and course position, so the user never re-explains
  (`FEATURE_PLAN.md:80`).
- **One persistent thread per course**, openable from any card or exercise
  (`FEATURE_PLAN.md:80`).
- **Gemini 2.5 Flash**, because cost is per message (`ARCHITECTURE.md:85-86`).
- **This is a meaningfully bigger surface than preset actions**, flagged in the
  source so implementation budgets for it (`FEATURE_PLAN.md:81`).

## Latency budget

First token within 2s per `E06`. Moderation on the input path (`F08`) sits inside
that budget.

## Open questions

- How much conversation history is carried as the thread grows, and what gets
  summarised or dropped — this is both a quality and a cost decision.
- Whether context injection includes the full current card text or a reference,
  given cost per message.
- Whether a thread is per course or per course-plus-lesson; the source says per
  course, but long courses may make threads unwieldy.

## Acceptance criteria

- [ ] Asking "why is my answer wrong?" with no other input produces a specific,
      correct answer about the actual exercise just attempted
- [ ] Quick actions seed the thread and free-typed follow-ups continue it
- [ ] Replies stream, with first token inside the `E06` budget
- [ ] Every message passes through `B17` before and after the model call
- [ ] Thread history persists across app restarts and is scoped to the course
- [ ] Every message produces an `F07` cost record attributed to the user
