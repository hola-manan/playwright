# F03 — infra-gcp

**Tier:** Foundation
**Code location:** `infra/gcp/`
**Milestone:** 1
**Status:** not started

## Purpose

The Google Cloud footprint the rest of the system runs on: projects, the Cloud Run
service, Artifact Registry, Cloud SQL, Secret Manager, and the IAM / Workload
Identity Federation wiring that lets CI deploy without long-lived keys. Staging
and production are separate Firebase projects, so this module defines the shape
once and instantiates it twice.

## Scope

**Owns**
- Project layout: separate Firebase projects for staging and prod
- Cloud Run service definition (region, concurrency, scale-to-zero, min instances)
- Artifact Registry repository
- Cloud SQL instance backing Data Connect
- Secret Manager secrets and the runtime service account's access to them
- Workload Identity Federation pool and provider, scoped per repo and per
  environment
- IAM roles for the Cloud Run runtime identity (Vertex AI, Cloud SQL, Secret
  Manager, FCM)

**Does not own**
- The pipelines that consume WIF → `F04`
- Schema and migrations on the Cloud SQL instance → `F01`
- Application configuration values → the consuming module

## Source references

- `ARCHITECTURE.md` § "AI compute — Cloud Run" (lines 74–82)
- `ARCHITECTURE.md` § "CI/CD" table — environments, secrets (lines 144–150)
- `ARCHITECTURE.md` § "Backend — GitHub Actions + WIF" (lines 152–158)
- `ARCHITECTURE.md` § "Auth + Database" (lines 48–59)

## Depends on

Nothing — this is the root of the dependency graph.

## Depended on by

`F01`, `F04`, `F07`, and every backend module at runtime.

## Interface

Infrastructure-as-code definitions plus a documented set of outputs other modules
consume: project ids, service URLs per environment, the runtime service account
email, secret names, and the WIF provider resource path.

## Decisions inherited

- **Cloud Run over Cloud Functions** — no hard execution-timeout ceiling so long
  streamed course generation is fine, the sandbox runs in-process inside the
  container, and it scales to zero when idle (`ARCHITECTURE.md:78-80`).
- **Staging + prod as separate Firebase projects**, with separate Cloud Run
  services and PostHog environments (`ARCHITECTURE.md:148`).
- **No long-lived keys anywhere.** Google Secret Manager for backend runtime
  secrets, GitHub OIDC for deploy auth (`ARCHITECTURE.md:150`, `155-156`).
- **Firebase Storage is provisioned only if and when needed** — not part of the v1
  critical path (`ARCHITECTURE.md:31`).

## Open questions

- Region choice, and whether Cloud SQL and Cloud Run must be co-located for the
  latency budget in `E06`.
- Whether a warm min-instance is needed to protect the "outline within seconds"
  target against cold starts — cost versus `E06` compliance.
- Cloud SQL sizing and connection pooling strategy from a scale-to-zero service.

## Acceptance criteria

- [ ] Staging and prod are fully separate and neither can reach the other's data
- [ ] CI can deploy to Cloud Run with no long-lived service-account key in
      existence
- [ ] The runtime identity has least-privilege access to Vertex AI, Cloud SQL,
      Secret Manager, and FCM — and nothing else
- [ ] Cold-start latency is measured and recorded against the `E06` budget
- [ ] Tearing down and recreating an environment from this definition is
      reproducible
