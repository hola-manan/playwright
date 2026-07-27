# E02 — streaming-engine

**Tier:** Engine
**Code location:** `apps/mobile/lib/engine/streaming/`
**Milestone:** 2
**Status:** not started

## Purpose

Progressive rendering. Three things in this app stream — the course outline, each
lesson, and tutor replies — and in all three the product promise is that content
appears *while it is being generated*, not after. This module consumes the `F02`
SSE envelope, surfaces partial results the instant they are usable, and owns every
path by which a slow or failed generation still ends somewhere useful.

Without this module the app is a loading spinner in front of an LLM. With it,
generation feels like the product working.

## Scope

**Owns**
- SSE connection lifecycle for all three streams
- Partial-payload handling: emit an outline row or a finished card as soon as it
  is complete, without waiting for the stream to end
- Reconnect and resume-from-offset
- Cancellation and backpressure when the user navigates away
- The timeout ladder and the never-a-dead-end fallback
- Stream-level analytics: time to first item, time to done, failure rate

**Does not own**
- Non-streaming requests → `C03`
- The envelope definition → `F02`
- What gets rendered from each item → `C07`, `C08`, `C18`
- Entrance animation for arriving items → `E03`

## Source references

- `FEATURE_PLAN.md` § 1 "Generation with payoff" — outline appears within seconds,
  streamed (line 36)
- `FEATURE_PLAN.md` § 2 "Just-in-time generation" — first card visible within
  seconds (line 50)
- `FEATURE_PLAN.md` § 1 "Edge cases" — generation fails or times out, abandon
  mid-generation (lines 40–43)
- `ARCHITECTURE.md` § "AI compute — Cloud Run" — streams tokens to the Flutter
  client (lines 74–82)

## Depends on

`F02` (envelope), `C03` (auth and base transport), `C04` (resume state)

## Depended on by

`C07` (outline), `E01` and `C08` (lesson content), `C18` (tutor)

## State machine

```
idle ──open──▶ connecting ──▶ streaming ──▶ done
                    │             │
                    │             ├─ item ──▶ (emit to consumer immediately)
                    │             ├─ chunk ─▶ (accumulate)
                    │             └─ drop ──▶ reconnecting ──resume(idx)──▶ streaming
                    │
                    └─ timeout / error ──▶ failed ──▶ fallback
user leaves ──▶ cancelled (connection released, partial work preserved)
```

## Invariants

1. An `item` event is surfaced to its consumer in the same frame it is parsed —
   buffering items until `done` defeats the module's entire purpose.
2. A reconnect resumes from the last received index and never restarts generation
   already paid for.
3. `cancelled` releases the connection but never discards content already
   persisted locally.
4. No stream can end in a state with no available user action.

## Failure modes

| Failure | Recovery |
|---------|----------|
| Connection drops mid-stream | Reconnect and resume from last index, transparently. No user-visible interruption if it succeeds within the budget |
| Timeout before first item | Escalate through the `E06` degradation ladder, then offer the pre-cached starter topic (`FEATURE_PLAN.md:41`) |
| Terminal `error` event | Friendly retry, plus the pre-cached starter topic so the first run is never a dead end |
| Malformed partial payload | Discard the fragment, keep the stream open, log. One bad card must not kill a lesson |
| App backgrounded mid-generation | Persist resume state; on next open, resume rather than restart (`FEATURE_PLAN.md:42`) |
| Output moderation blocks a tutor completion | Stop rendering, replace partial text — never leave blocked content on screen (`F08`) |

## Feel spec

- **Items arrive staggered, not in bursts.** If ten outline rows parse in one
  frame, they still enter at the `E03` stagger interval. A block that pops in
  reads as a page load; rows that arrive in sequence read as something being
  written for you.
- **No spinners on the generation path.** A spinner communicates "waiting"; a
  streaming outline communicates "working". Skeletons and progressive content
  only.
- **The first item is the moment that matters.** Time-to-first-item is the metric
  this module is judged on, not total generation time.
- **Tutor tokens** render at a readable cadence rather than instantly on arrival,
  so a fast burst does not flash a wall of text.

## Latency budget

Cites `E06`. Time to first outline row under 3s; time to first card under 3s after
outline confirmation; tutor first token under 2s. These are the module's own
acceptance thresholds, measured and reported to `F06`.

## Degradation

The ladder, owned by `E06` and implemented here:

| Elapsed | What the user sees |
|---------|--------------------|
| 0–1s | Skeleton, no spinner |
| 1–5s | Items appearing progressively as they arrive |
| 5–15s | Reassuring copy naming the work: "Building your Git course…" |
| >15s | Continue waiting, or take the pre-cached starter topic — both offered |
| failure | Friendly retry plus the starter topic. Never a dead end |

## Accessibility

Progressive arrival must be announced to screen readers at a sane cadence, not
per token. With reduced motion, the stagger collapses to zero and items appear
without transform.

## Open questions

- Buffer size and cadence for tutor token rendering — too smooth feels laggy, too
  raw flashes.
- Whether resume-from-offset needs server support beyond the monotonic index in
  `F02`, particularly for tutor streams.
- What the pre-cached starter topics are, and who generates them (likely `B10`).

## Acceptance criteria

- [ ] A lesson's first card renders before its stream completes, demonstrably
- [ ] Killing the network mid-stream and restoring it resumes without regenerating
- [ ] Every failure path terminates at a screen with an available action
- [ ] Time-to-first-item is instrumented and reported for all three streams
- [ ] Navigating away releases the connection and does not leak it
- [ ] No spinner appears anywhere on the generation path
