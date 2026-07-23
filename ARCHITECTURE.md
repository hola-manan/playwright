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
| Auth | **Firebase Auth** — email + Google + Apple |
| Database | **Firebase Data Connect / SQL Connect** → managed **PostgreSQL** (Cloud SQL) |
| AI compute / API | **Cloud Run** (containerized service) |
| LLM | **Vertex AI — Gemini 2.5 Flash** (volume) + **Gemini 2.5 Pro** (course outline only) |
| Code sandbox | **Constrained in-process execution** — JS (isolated engine) + Python (Pyodide/WASM) |
| Push notifications | **FCM** (Firebase Cloud Messaging) |
| Analytics | **PostHog** |
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

### AI compute — Cloud Run
- The AI pipeline (outline + lesson generation, streamed), the **conversational
  tutor**, and the **code-execution sandbox** run in a containerized **Cloud Run**
  service.
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
  └── HTTPS/SSE → Cloud Run service
                    ├── Vertex AI: Gemini 2.5 Flash (lessons, exercises, tutor)
                    ├── Vertex AI: Gemini 2.5 Pro   (course outline)
                    ├── Sandbox: isolated JS engine + Pyodide/WASM (answer-key verify)
                    └── writes → PostgreSQL (Data Connect / Cloud SQL)
```

---

## Still Open (not architecture-blocking)

- **CI/CD & release**: build/deploy pipeline for Flutter (e.g. Codemagic / Fastlane)
  and Cloud Run (Cloud Build). Decide before first release, not before first code.
- **Secrets/config management**: Google Secret Manager is the natural default.
- **Per-course generation cost budget**: concrete ceiling to tune Flash/Pro usage and
  free-tier generation limits. Needs a first real cost measurement to set.
- **App name & branding**: still open (product decision, tracked in the feature plan).
