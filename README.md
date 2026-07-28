# Bite-Sized Learning App

A mobile learning app in the spirit of Google's retired Grasshopper, combined with
Duolingo's daily-habit mechanics. You type a tech topic, an AI generates a full
course sized to that topic, and you learn it as short swipeable cards followed by
auto-checkable exercises — with a streak, a daily goal, and a reminder bringing
you back tomorrow.

**Status: planning complete, implementation not started.** No application code
exists yet. This repository currently holds the product and architecture
decisions, and the module breakdown for building them.

---

## Where things are

| Path | What it is |
|------|-----------|
| **[`docs/BUILD_ORDER.md`](docs/BUILD_ORDER.md)** | **Start here.** What to build first, and why it starts with a throwaway spike rather than infrastructure |
| [`docs/modules/`](docs/modules/README.md) | 69 module specs and the index that organises them |
| [`FEATURE_PLAN.md`](FEATURE_PLAN.md) | The frozen v1 vision: feature set, milestones, v2 scope |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | The locked technical stack and the reasoning behind each choice |
| `apps/mobile/` | Flutter client (scaffold only) |
| `services/api/` | Python / FastAPI service on Cloud Run (scaffold only) |
| `packages/` | Schema, API contract, analytics taxonomy, **pedagogy rules** (scaffold only) |
| `infra/` | GCP footprint and CI pipelines (scaffold only) |
| `tools/` | Module verification, and the content eval harness (scaffold only) |

Every folder under `apps/`, `services/`, `packages/`, and `infra/` contains a
README stub naming its module and linking to that module's spec.

---

## The stack

Locked. Full reasoning in [`ARCHITECTURE.md`](ARCHITECTURE.md).

```
Flutter app (Dart)
  ├── Firebase Auth ....................... sign-in, guest→account
  ├── Firebase Data Connect SDK ........... reads/writes → PostgreSQL (Cloud SQL)
  ├── FCM ................................. push notifications
  ├── PostHog SDK ......................... product analytics
  └── HTTPS/SSE → Cloud Run service (Python / FastAPI)
                    ├── Vertex AI: Gemini 2.5 Flash (lessons, exercises, tutor)
                    ├── Vertex AI: Gemini 2.5 Pro   (course outline)
                    ├── Sandbox: isolated JS engine + Pyodide/WASM (answer-key verify)
                    └── writes → PostgreSQL (Data Connect / Cloud SQL)
```

CI/CD: Codemagic for the mobile builds, GitHub Actions with Workload Identity
Federation for the backend. Staging and prod are separate Firebase projects.

---

## How the work is organised

The project is split into **69 modules** across five tiers, each sized so a single
session can own it end to end.

| Tier | What it is | Count |
|------|-----------|-------|
| **F** — Foundation | Schema, API contract, infrastructure, CI, cross-cutting concerns | 8 |
| **P** — Pedagogy & content intelligence | What the AI teaches, how it grounds it, and what gates it | 17 |
| **E** — Engines & experience | The runtime that makes the app *feel* like the product | 6 |
| **B** — Backend | Python / FastAPI services | 19 |
| **C** — Client | Flutter screens and features | 19 |

Two tiers exist because the product would be hollow without them.

**Tier P** is the core product. Tiers B and C move a course around; Tier P decides
whether it is worth learning from — concept granularity, prerequisite ordering,
what makes a distractor diagnostic rather than filler, what "easier" means without
teaching less, and the rubric that blocks a bad lesson from reaching anyone. v1
ships AI content with no human review gate, so that gate is automated and
blocking.

**Tier E** exists because the stack was chosen for it. `ARCHITECTURE.md` picks
Flutter specifically for animation quality in a "gamified, card-swipe,
micro-interaction-heavy" app, and the feature plan specifies feel directly —
"satisfying confirmation + XP tick", "the dopamine beat — keep it snappy and
celebratory", "first card visible within seconds". Those promises get owning
modules with measurable acceptance criteria rather than being left as residue in
a design system.

**To pick up work:** read [`docs/BUILD_ORDER.md`](docs/BUILD_ORDER.md) first — it
says which module to start on and why the answer is "none of them yet". Then open
[`docs/modules/README.md`](docs/modules/README.md) and follow the chosen module's
spec. Each stands alone: interface, dependencies, inherited decisions, open
questions, and the acceptance criteria that define done at v1 launch.

---

## Document conventions

`FEATURE_PLAN.md` and `ARCHITECTURE.md` are the **frozen** v1 vision and decision
record; they are not updated as work proceeds. **Module specs are the living
working documents.** Where they disagree, the module spec wins.

Every section of both source documents is cited by at least one module spec — the
[coverage map](docs/modules/README.md#coverage-map) records where, so the split
can be verified as lossless.
