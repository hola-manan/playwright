# F04 — ci-backend

**Tier:** Foundation
**Code location:** `infra/ci/backend/`
**Milestone:** 1
**Status:** not started

## Purpose

The GitHub Actions pipeline for the Python service: lint and test on pull request,
and on merge to `main` build a container, push it to Artifact Registry, run
schema migrations, deploy to Cloud Run staging, and gate production behind manual
approval. Authentication to GCP is via Workload Identity Federation, so no
service-account key exists to leak or rotate.

## Scope

**Owns**
- PR workflow: backend lint, type check, unit tests
- Merge workflow: container build → Artifact Registry → migrate → deploy staging
- Manual approval gate and the promotion to prod
- Ordering guarantee between migrations and the deploy that depends on them
- OIDC token exchange configuration on the CI side

**Does not own**
- The WIF pool/provider and IAM bindings → `F03`
- Migration content → `F01`
- Mobile builds → `F05`

## Source references

- `ARCHITECTURE.md` § "CI/CD" table (lines 144–150)
- `ARCHITECTURE.md` § "Backend — GitHub Actions + WIF" (lines 152–158)
- `ARCHITECTURE.md` § "Not yet scaffolded" (lines 172–174)

## Depends on

`F03` (WIF provider, Artifact Registry, Cloud Run services), `F01` (migrations)

## Depended on by

Every backend module, as the path to a deployed environment.

## Interface

Workflow files plus documented required checks for branch protection, and the
environment names used by the approval gate.

## Decisions inherited

- **Workload Identity Federation, not keys.** Access is scoped per repo and per
  environment (`ARCHITECTURE.md:155-156`).
- **Migrations run as a deploy step in strict mode, staging first, before the
  Cloud Run deploy that depends on them** (`ARCHITECTURE.md:157-158`). This
  ordering is the pipeline's core correctness property.
- **Auto-deploy to staging, manual promotion to prod** (`ARCHITECTURE.md:149`,
  `153-154`).
- **Two CI tools is an accepted tradeoff**, this one plus Codemagic; overridable
  to a single GitHub Actions + Fastlane setup if unified tooling is later
  preferred (`ARCHITECTURE.md:168-170`).

## Open questions

- Rollback procedure when a migration succeeds but the deploy fails — forward-fix
  only, or a tested down-migration path?
- Whether integration tests requiring a live database run in CI against an
  ephemeral instance or against staging post-deploy.
- Test coverage threshold, if any, as a required check.

## Acceptance criteria

- [ ] A PR runs lint, type check, and unit tests, and these are required checks
- [ ] Merge to `main` produces a deployed staging revision with no manual steps
- [ ] No long-lived GCP credential exists in GitHub secrets
- [ ] A migration failure blocks the dependent deploy rather than leaving schema
      and code mismatched
- [ ] Production deploy cannot happen without explicit human approval
