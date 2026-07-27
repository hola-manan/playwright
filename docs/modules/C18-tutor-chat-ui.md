# C18 — tutor-chat-ui

**Tier:** Client
**Code location:** `apps/mobile/lib/features/tutor/`
**Milestone:** 8
**Status:** not started

## Purpose

The tutor's surface: a persistent thread per course, openable from any card or
exercise, with preset quick actions and free-typed follow-ups. Its defining
requirement is that the user never re-explains context — they tap the icon on the
card they are confused by and ask "why?".

## Scope

**Owns**
- The chat thread UI and message rendering, including code blocks
- Preset quick actions: "explain differently", "give me an example", "why is this
  wrong?"
- The composer for free-typed follow-ups
- Streamed reply rendering via `E02`
- Passing the current context — card, answer, position — into the request
- The cap-reached and blocked-content states from `B17`

**Does not own**
- Context injection into the prompt → `B16`
- Metering, moderation, on-topic scoping → `B17`
- Streaming mechanics → `E02`
- The entry point on the card and in feedback → `C08`, `C14`

## Source references

- `FEATURE_PLAN.md` § 2 "Explanations & tutor chat" (lines 78–81)
- `FEATURE_PLAN.md` § 3 "Card reader" — tutor entry point on every card (line 93)
- `FEATURE_PLAN.md` § 3 "Exercise flow" — "still confused? ask the tutor"
  (line 97)
- `FEATURE_PLAN.md` § "v1 Build Milestones" — the biggest single feature, built
  after the core loop (line 197)

## Depends on

`B16`, `B17`, `E02`, `E03`, `C09` (code rendering), `C02`

## Depended on by

`C08`, `C14`

## Decisions inherited

- **A persistent thread per course**, openable from any card or exercise
  (`FEATURE_PLAN.md:80`).
- **Preset quick actions seed the thread; the user can free-type follow-ups**
  (`FEATURE_PLAN.md:80`).
- **Context-aware, so "why is my answer wrong?" works without re-explaining**
  (`FEATURE_PLAN.md:80`).
- **This is a meaningfully bigger surface than preset actions**, flagged so
  implementation budgets for it (`FEATURE_PLAN.md:81`).

## Feel spec

The tutor opens as a modal sheet over the card, not as a full-screen navigation —
the card stays visible behind it, so the UI physically demonstrates that the tutor
knows what you are looking at (`E03` owns the transition).

Quick actions are the primary affordance on an empty thread, because the hardest
part of asking for help is composing the question. The composer is present but
secondary until the thread has started.

Replies stream at a readable cadence via `E02`, never flashing a wall of text.
Code in replies uses the same rendering as `C09`, so a snippet in the tutor looks
identical to a snippet in a lesson.

## Latency budget

First token within 2s per `E06`. Moderation on the input path sits inside that
budget. The sheet itself opens within one frame — it must never wait on the thread
to load.

## Degradation

Offline, the sheet opens and explains that the tutor needs a connection, with the
pre-generated explanation from `C14` still available behind it — the user is never
left with nothing. A blocked message or a reached cap shows a clear, non-punitive
state with a next step, per `B17`.

## Accessibility

Streamed replies are announced at a sane cadence, not per token. Quick actions are
labelled buttons. Code blocks follow `C09`'s accessibility rules. The sheet is
dismissible by gesture and by an explicit control.

## Open questions

- Whether opening from a specific exercise pre-fills "why is my answer wrong?" or
  merely offers it as the first quick action.
- How much thread history is shown on reopen for a long-running course thread.
- Whether the sheet is dismissible to a minimised state so a user can consult the
  card mid-conversation.

## Acceptance criteria

- [ ] The tutor opens from any card and from exercise feedback, within one frame
- [ ] The card remains visible behind the sheet
- [ ] All three quick actions produce contextually correct responses with no extra
      user input
- [ ] Replies stream with first token inside the `E06` budget
- [ ] Code in replies renders identically to `C09`
- [ ] Cap-reached and blocked states are clear and offer a next step
- [ ] Offline, the pre-generated explanation remains reachable
