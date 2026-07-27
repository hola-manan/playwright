# F05 — ci-mobile

**Tier:** Foundation
**Code location:** `infra/ci/mobile/`
**Milestone:** 1
**Status:** not started

## Purpose

The Codemagic pipeline for the Flutter app: analyze, test, and format checks on
pull request; on merge to `main`, build both platforms and publish to the test
tracks. Codemagic is chosen specifically because it owns iOS code signing and
store submission — the biggest time sink in mobile CI.

## Scope

**Owns**
- PR workflow: `flutter analyze`, `flutter test`, `dart format --set-exit-if-changed`
- Merge workflow: build iOS and Android, auto-publish to TestFlight and Play
  internal
- iOS code signing and certificate/profile management
- Store submission configuration and encrypted signing/store credentials
- Golden-test execution for the modules that have them (`E03`, `E04`, `C09`)

**Does not own**
- Backend pipelines → `F04`
- Runtime app configuration → `C01`
- Manual promotion to public release, which stays a human decision

## Source references

- `ARCHITECTURE.md` § "CI/CD" table (lines 144–150)
- `ARCHITECTURE.md` § "Mobile — Codemagic" (lines 160–170)
- `ARCHITECTURE.md` § "Not yet scaffolded" (lines 172–174)

## Depends on

`F03` (Firebase project config per environment)

## Depended on by

Every `C` and `E` module, as the path to a testable build.

## Interface

Codemagic workflow definitions plus the documented required checks for branch
protection and the environment variable groups holding signing material.

## Decisions inherited

- **Codemagic for ergonomics, not price.** Free tier is 500 macOS-M2 minutes per
  month; pay-as-you-go roughly $0.095/min after. The flat team plan only wins past
  roughly 3,500 build-minutes per month, so solo and pre-launch usage is
  effectively free (`ARCHITECTURE.md:165-167`).
- **Auto-publish to test tracks, manual promotion to public**
  (`ARCHITECTURE.md:149`, `163-164`).
- **Signing and store keys live in Codemagic encrypted env**, never in the repo
  (`ARCHITECTURE.md:150`).
- **Two CI tools is an accepted tradeoff**; a single-tool GitHub Actions +
  Fastlane setup is the documented override if unified tooling is preferred over
  mobile ergonomics (`ARCHITECTURE.md:168-170`).

## Open questions

- Whether golden tests for `E03`/`E04` run on every PR or nightly — they are the
  slowest check and the most prone to platform rendering drift.
- Build-minute budget alerting before the free tier is exhausted.
- Whether generated Dart types from `F02` are produced in this pipeline or
  checked in.

## Acceptance criteria

- [ ] A PR runs analyze, test, and format, and these are required checks
- [ ] Merge to `main` produces builds on TestFlight and Play internal with no
      manual steps
- [ ] iOS signing works without a developer running anything locally
- [ ] No signing material is present in the repository
- [ ] Public release requires an explicit human promotion step
