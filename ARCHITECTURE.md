# Architecture Decisions — Bite-Sized Learning App (v1)

Companion to `FEATURE_PLAN.md`. This records the **locked** technical stack for v1.
Feature scope and product decisions live in the feature plan; this document is
the "how we build it" layer. Each decision below is settled unless explicitly
revisited.

The through-line: a **coherent, mostly all-Google stack** (Flutter + Firebase +
Vertex AI) chosen for UI quality, minimal backend boilerplate, and tight
integration, with two deliberate outside-Google picks (PostHog for analytics, a
constrained in-process sandbox for code execution) where the Google-native option
was the weaker fit.

---

## Locked Decisions

| Area | Decision |
|------|----------|
| Mobile client | **Flutter** (Dart) |
| Backend language | **Python** — FastAPI + Pydantic |
| Auth | **Firebase Auth** — email + Google + Apple |
| Database | **Firebase Data Connect / SQL Connect** → managed **PostgreSQL** (Cloud SQL) |
| AI compute / API | **Cloud Run** (containerized Python service) |
| LLM | **Vertex AI — Gemini 2.5 Flash** (volume) + **Gemini 2.5 Pro** (course outline only) |
| Code sandbox | **Constrained execution** — JS (isolated engine) + Python (Pyodide/WASM) |
| Push notifications | **FCM** (Firebase Cloud Messaging) |
| Analytics | **PostHog** |
| CI/CD — mobile | **Codemagic** (build + store submission) |
| CI/CD — backend | **GitHub Actions + Workload Identity Federation** (keyless deploy to Cloud Run) |
| File/asset storage | **Firebase Storage** (if/when needed) |

---

## Rationale & Notes

### Mobile client — Flutter
- Chosen over React Native specifically for **UI/animation quality**. Flutter renders
  on its own canvas (Impeller), giving pixel-identical, high-framerate custom
  animations across iOS/Android — the right fit for a gamified, card-swipe,
  micro-interaction-heavy learning app.
- First-class **Firebase Data Connect Flutter SDK** and **Vertex AI access via
  Firebase AI Logic**, so the client integrates natively with the rest of the stack.
- Accepted tradeoff: Dart isn't shared with backend logic. Mitigated by Firebase
  doing most of the "backend" (auth, DB access, generated type-safe SDKs), leaving
  only the AI orchestration as custom code (on Cloud Run).

### Auth + Database — Firebase Auth + Data Connect (PostgreSQL)
- Firebase **Data Connect / SQL Connect** provides a fully-managed **PostgreSQL**
  database on Cloud SQL with Firebase Auth integration, relational joins, type-safe
  generated SDKs, and vector search. This means the relational data model in
  `FEATURE_PLAN.md` (`user` / `course` / `lesson` / `card` / `exercise` /
  `enrollment` / `progress` / `review_item` / `daily_activity` / `tutor_thread` …)
  maps directly onto a real SQL schema — **no NoSQL compromise**.
- Vector search availability is a bonus for later (semantic review, RAG over course
  content) without adding another datastore.
- Firebase Auth covers the email + Google + Apple sign-in required by onboarding,
  including the **guest → account migration** flow (anonymous auth upgraded to a
  permanent account, preserving first-lesson progress).

### Backend language — Python (FastAPI + Pydantic)
- The backend's core job is the **AI generation pipeline + tutor**, which is Python's
  home turf: the **Vertex AI Python SDK** is first-class, most Gemini docs/examples are
  Python, and **Pydantic** is the cleanest way to validate Gemini's structured
  (JSON-schema) lesson output before it's persisted. FastAPI covers streaming/SSE.
- Considered and rejected: **Node/TS** (great at streaming and runs the JS sandbox
  in-process, but thinner AI ecosystem) and **Dart** (would share language with the
  Flutter client, but the weakest server-side Gemini tooling — a poor fit exactly where
  the product is hardest).
- Note: the code sandbox is **polyglot regardless of backend language** (it must run
  both JS and Python exercises), so it's a small separate execution component either
  way — not a reason to pick one backend language over another.

### AI compute — Cloud Run
- The AI pipeline (outline + lesson generation, streamed), the **conversational
  tutor**, and the **code-execution sandbox** run in a containerized **Python** service
  on **Cloud Run**.
- Chosen over Cloud Functions because: no hard execution-timeout ceiling (long,
  streamed course generation is fine), the JS/WASM sandbox runs **in-process**
  inside the container, and it scales to zero when idle.
- Talks to Vertex AI (Gemini), writes results to Postgres via Data Connect, and
  streams tokens to the Flutter client (SSE / streaming HTTP).

### LLM — Gemini via Vertex AI, tiered
- **Gemini 2.5 Flash** for the high-volume calls: lesson content, exercises, and the
  tutor. Cheap and fast, which matters because courses can be long (see the
  no-card-limit decision) and the tutor is per-message.
- **Gemini 2.5 Pro** reserved for the **course outline** only — the one step where
  structure and coverage quality set up everything downstream, and volume is low
  (one outline per course, cached and shared).
- Structured lesson output uses Gemini **structured output / response schema** so the
  pipeline gets valid JSON to schema-validate.

### Code sandbox — constrained in-process execution (the Grasshopper lesson)
- Google's Grasshopper taught **JavaScript only** and ran code **client-side in a JS
  engine** — it never needed VM/container infrastructure because it constrained the
  language. We apply the same principle.
- v1 supports **JavaScript + Python** for generated code exercises:
  - **JS** → an isolated JS engine (e.g. `isolated-vm` or QuickJS) — no network, CPU/
    memory/time capped.
  - **Python** → **Pyodide / WASM** — sandboxed by the WASM runtime.
- Used at **generation time** for **answer-key verification**: run the snippet, compare
  real output to the AI's claimed answer, regenerate on mismatch (per the trust
  decision in the feature plan).
- Same runtimes set up the **deferred on-device "run your code" feature** (the
  Grasshopper signature) later, since Pyodide/QuickJS can also run on the client.
- Deliberately **not** using a paid execution service (E2B) or self-managed containers
  in v1 — unnecessary given the constrained language set, and avoids that infra/cost.

### Notifications — FCM
- Firebase Cloud Messaging for the daily reminder and streak-at-risk nudges. Native to
  the stack; scheduling is server-driven from Cloud Run (personalized copy), delivered
  via FCM, timezone-aware, respecting OS permission + quiet hours.

### Analytics — PostHog
- The one deliberate step outside Google. Retention curves, funnels, and cohort
  analysis (D1/D7, streak survival, onboarding drop-off) are the metrics this product
  is judged on, and PostHog is purpose-built for them with a generous free tier and a
  Flutter SDK.
- Firebase Analytics + BigQuery could do this but would require building the analysis
  layer ourselves; not worth it for v1.

---

## Stack at a Glance

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

---

## CI/CD

| Area | Decision |
|------|----------|
| Mobile (Flutter) | **Codemagic** — build iOS+Android, code signing, store submission |
| Backend (Cloud Run) | **GitHub Actions + Workload Identity Federation** (keyless) |
| Environments | **Staging + Prod** — separate Firebase projects, Cloud Run services, PostHog envs |
| Release cadence | Auto → test track (TestFlight / Play internal); **manual** promotion to public |
| Secrets | **Google Secret Manager** (backend runtime) + **GitHub OIDC** (deploy auth) + **Codemagic encrypted env** (signing/store keys) — no long-lived keys |

### Backend — GitHub Actions + WIF
- On PR: backend lint + unit tests. On merge to `main`: build container → push to
  **Artifact Registry** → deploy to Cloud Run **staging**; **manual approval** → prod.
- **Workload Identity Federation** (OIDC) means no long-lived GCP service-account keys
  to leak or rotate; access is scoped per-repo and per-environment.
- **Data Connect schema migrations** run as a deploy step (strict mode), **staging
  first**, before the Cloud Run deploy that depends on them.

### Mobile — Codemagic
- Purpose-built for Flutter: it owns **iOS code signing** and **TestFlight / Play
  Console submission** — the biggest mobile-CI time sink — on fast M-series runners.
- On PR: `flutter analyze`, `flutter test`, `dart format --set-exit-if-changed`. On
  merge to `main`: build both platforms → auto-publish to the test tracks.
- **Cost:** free tier is 500 macOS-M2 min/month (personal account); pay-as-you-go
  ~$0.095/min after. Solo/pre-launch usage is effectively free; the $3,990/yr flat
  team plan only wins past ~3,500 build-min/month. Chosen for ergonomics, not price.
- Accepted tradeoff: **two CI tools** (Codemagic + GitHub Actions). Overridable to a
  single-tool GitHub Actions + Fastlane setup if unified tooling is preferred over
  mobile ergonomics.

**Not yet scaffolded:** no pipeline YAML exists — there's no Flutter project or Cloud
Run service to build yet. The config files land with that first code; this section is
the decided approach so that work is turn-key.

---

## Still Open (not architecture-blocking)

- **App name & branding**: product decision, tracked separately.
