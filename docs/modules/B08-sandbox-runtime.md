# B08 — sandbox-runtime

**Tier:** Backend (engine)
**Code location:** `services/api/app/sandbox/`
**Milestone:** 4
**Status:** not started

## Purpose

Constrained code execution for JavaScript and Python, in-process inside the Cloud
Run container. Two engines behind one harness that enforces no network, capped
CPU, capped memory, and a hard time limit. In v1 its only consumer is answer-key
verification, but the same runtimes are what make the deferred on-device "run your
code" feature possible later.

## Scope

**Owns**
- The JS engine integration (isolated engine — `isolated-vm` or QuickJS)
- The Python engine integration (Pyodide / WASM)
- The shared harness: timeouts, memory and CPU caps, network denial, output
  capture
- Normalising results and errors across both engines

**Does not own**
- Comparing output to an answer key → `B09`
- Deciding what to run → `B09`, `B07`
- Any user-submitted code execution — that is explicitly deferred (`FEATURE_PLAN.md:218`)

## Source references

- `ARCHITECTURE.md` § "Code sandbox — constrained in-process execution (the
  Grasshopper lesson)" (lines 94–108)
- `FEATURE_PLAN.md` § 7 "Services → Sandbox" (line 174)
- `FEATURE_PLAN.md` § 2 "Answer-key verification (trust)" (lines 69–72)

## Depends on

`F03` (container runtime)

## Depended on by

`B09`

## State machine

```
idle ──run(lang, source)──▶ preparing ──▶ executing
executing ──completes──▶ captured(stdout, stderr, value)
executing ──exceeds time/memory/CPU cap──▶ terminated(reason)
executing ──attempts network──▶ denied
```

## Invariants

1. No execution can reach the network.
2. Every execution terminates — the time cap is enforced by the harness, never by
   the guest code.
3. A runaway execution cannot degrade the serving container for other requests.
4. Both engines return the same normalised result shape, so `B09` has one code
   path.

## Failure modes

| Failure | Recovery |
|---------|----------|
| Guest code infinite-loops | Hard-killed at the time cap, reported as `terminated` |
| Guest code exhausts memory | Killed at the memory cap |
| Engine fails to initialise | Verification is skipped and the exercise is flagged rather than silently trusted |
| Guest code produces enormous output | Output truncated at a cap; treated as a mismatch by `B09` |

## Decisions inherited

- **Constrain the language, not the infrastructure — the Grasshopper lesson.**
  Google's Grasshopper taught JavaScript only and ran code client-side in a JS
  engine, so it never needed VM or container infrastructure. The same principle
  applies here (`ARCHITECTURE.md:95-97`).
- **JS and Python only in v1** (`ARCHITECTURE.md:98-102`).
- **In-process inside the Cloud Run container**, which is one of the reasons Cloud
  Run was chosen over Cloud Functions (`ARCHITECTURE.md:78-80`).
- **Deliberately not a paid execution service (E2B) or self-managed containers** —
  unnecessary given the constrained language set, and avoids that infrastructure
  and cost (`ARCHITECTURE.md:107-108`).
- **The sandbox is polyglot regardless of backend language**, so it was never a
  reason to pick Python over Node (`ARCHITECTURE.md:70-72`).
- **These same runtimes can run on the client**, which is what sets up the
  deferred "run your code" feature (`ARCHITECTURE.md:105-106`). Keep the harness
  portable in spirit even though v1 runs it server-side.

## Open questions

- `isolated-vm` versus QuickJS: `isolated-vm` is a Node addon and this is a Python
  service, so QuickJS via bindings may be the more natural fit. Needs a decision
  before implementation.
- Pyodide startup cost per execution, and whether a warm pool is needed to stay
  inside generation latency budgets.
- Exact cap values for time, memory, and output size.

## Acceptance criteria

- [ ] Network access from guest code is impossible, verified by an explicit test
      that attempts it
- [ ] An infinite loop in each language is terminated at the cap
- [ ] Concurrent executions cannot starve the serving container
- [ ] Both engines return one normalised result shape
- [ ] Engine initialisation failure results in a flagged exercise, never an
      unverified one silently marked verified
