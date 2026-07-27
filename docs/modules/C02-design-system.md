# C02 — design-system

**Tier:** Client
**Code location:** `apps/mobile/lib/core/design_system/`
**Milestone:** 1
**Status:** not started

## Purpose

The static visual language: colour, typography, spacing, elevation, iconography,
and the shared components built from them. Deliberately **motionless** — every
animated or reward behaviour belongs to `E03` and `E04`, so this module stays a
predictable, testable foundation rather than absorbing the app's dynamics.

## Scope

**Owns**
- Colour tokens including semantic roles (success, warning, code surface)
- Type scale and the monospace family used by code cards
- Spacing and radius scales, elevation
- Icon set
- Shared static components: buttons, cards, sheets, chips, progress bar chrome,
  skeletons
- Light and dark theming

**Does not own**
- Motion → `E03`
- Haptics, sound, celebration → `E04`
- Screen composition → the feature modules

## Source references

- `ARCHITECTURE.md` § "Mobile client — Flutter" — gamified, micro-interaction-heavy
  (lines 37–41)
- `FEATURE_PLAN.md` § 3 "Card reader" — code cards monospaced and syntax
  highlighted, inline code styled distinctly (line 92)
- `FEATURE_PLAN.md` § 5 "Top bar" — streak, goal ring, XP (line 142)

## Depends on

Nothing within the app.

## Depended on by

Every `C` module, plus `E03` and `E04` for the tokens they animate between.

## Interface

Theme extensions and a component library. Every token is named by role, not by
appearance, so a palette change does not require a rename.

## Feel spec

The visual language must carry the reward tone without motion: success and error
states must be unambiguous as static frames, because that is exactly what a
reduced-motion user sees. Skeletons are a first-class component here, since `E06`
forbids spinners on the generation path.

## Latency budget

Components must not rebuild expensively inside animation ticks driven by `E03`.
Theme lookup is constant-time.

## Degradation

Every semantic state has a static, colour-independent representation — an icon or
a shape — so nothing depends on colour alone.

## Accessibility

Contrast meets WCAG AA across light and dark. Dynamic type is supported
throughout; components reflow rather than clip. Minimum tap target 44pt is
enforced at the component level so feature modules inherit it.

## Open questions

- Syntax-highlighting theme and library, and whether it is shared with the code
  card renderer in `C09` or owned there.
- Whether dark mode ships in v1 — it affects every token decision, so it should be
  decided before tokens are written rather than retrofitted.
- Brand direction is blocked on the app name, which both source documents leave
  open (`ARCHITECTURE.md:180`).

## Acceptance criteria

- [ ] No hard-coded colour, size, or font exists outside this module
- [ ] Contrast passes AA in both themes
- [ ] Every component is usable at the largest dynamic type setting
- [ ] Success and error are distinguishable without colour and without motion
- [ ] Skeleton components exist for every streaming surface
- [ ] The module contains no animation code
