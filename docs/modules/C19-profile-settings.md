# C19 — profile-settings

**Tier:** Client
**Code location:** `apps/mobile/lib/features/profile_settings/`
**Milestone:** 6
**Status:** not started

## Purpose

Profile stats, learning settings, account management, and the legal surfaces the
app stores require. Small in feature terms but non-negotiable in scope: account
deletion and the legal links are review-blocking.

## Scope

**Owns**
- Profile: display name, avatar, join date, headline stats — streak, total XP,
  courses completed, lessons done
- Learning settings: daily goal, reminder time, quiet hours, experience level
- Account: manage sign-in method, sign out, delete account
- Legal and support: privacy policy, terms, contact/feedback, app version
- The global sound and haptics toggles for `E04`

**Does not own**
- Server-side deletion → `B02`
- Stat computation → `B14`, `B11`, `B12`
- Notification scheduling → `B18`
- Sign-in mechanics → `C05`

## Source references

- `FEATURE_PLAN.md` § 6 "Profile & Settings" — entire section (lines 149–154)
- `FEATURE_PLAN.md` § 4 "Daily goal" — editable in settings (line 118)
- `FEATURE_PLAN.md` § 4 "Notifications" — quiet-hours setting (line 133)
- `FEATURE_PLAN.md` § 7 "Cross-cutting → Privacy" (line 182)

## Depends on

`B01`, `B02`, `B14`, `C05`, `C02`

## Depended on by

`C01`

## Decisions inherited

- **Delete account must actually purge user data** — it matters for app-store
  review and privacy law (`FEATURE_PLAN.md:153`).
- **Privacy policy, terms, contact, and app version are required by the stores**
  (`FEATURE_PLAN.md:154`).
- **Experience level is adjustable and feeds future difficulty**
  (`FEATURE_PLAN.md:152`).
- **The daily goal is editable after onboarding** (`FEATURE_PLAN.md:118`).

## Feel spec

Settings should be boring and fast — this is the one area of the app where
surprise is unwelcome. Changes apply immediately without a save button.

Deletion is the exception and needs friction: a clear explanation of what is
destroyed, an explicit confirmation, and no ambiguity that it is irreversible. It
must not be so buried that it looks like it is hiding, which reviewers notice.

Changing the daily goal or reminder time should show its effect — the goal ring
recalculates against the new target immediately rather than at the next midnight.

## Latency budget

Settings render from local state instantly. Writes are optimistic and reconcile in
the background.

## Degradation

Offline, settings display and can be changed locally, queued via `C04`. Account
deletion requires connectivity and says so plainly rather than appearing to
succeed.

## Accessibility

Every control is labelled and reachable. Time pickers work with a screen reader.
The destructive action is clearly marked as such beyond colour.

## Open questions

- Whether changing the daily goal mid-day can retroactively meet or unmeet
  today's goal — and therefore affect the streak. This needs a `B14` rule.
- Whether avatars are uploaded, which would make Firebase Storage a v1 dependency
  rather than the "if and when needed" it is in `ARCHITECTURE.md:31`.
- Where the sound and haptics toggles live — settings is correct, but they may
  also deserve a first-run mention.

## Acceptance criteria

- [ ] All headline stats are accurate and match the home screen
- [ ] Every learning setting persists and takes effect immediately
- [ ] Deleting an account completes the `B02` purge and signs the user out
- [ ] Privacy, terms, contact, and version are all present and reachable
- [ ] Sound and haptics toggles control `E04` globally
- [ ] Deletion is discoverable without being accidental
