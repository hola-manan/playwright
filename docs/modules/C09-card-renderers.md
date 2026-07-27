# C09 — card-renderers

**Tier:** Client
**Code location:** `apps/mobile/lib/features/learn/card_renderers/`
**Milestone:** 3
**Status:** not started

## Purpose

Rendering for the four card types. Concept, example, and recap are thin text
renderers; the **code card** is the substantive work — monospaced, syntax
highlighted, horizontally scrollable for long lines, and copyable — and it is the
card type the tech vertical lives or dies on.

## Scope

**Owns**
- Concept card: short text, one idea
- Code card: snippet plus caption, syntax highlighting, horizontal scroll,
  copy-to-clipboard
- Example card
- Recap card, which ends every lesson
- Inline code styling within prose cards

**Does not own**
- Card sequencing and the surface → `C08`, `E01`
- Type tokens and the monospace family → `C02`
- Content → `B05`

## Source references

- `FEATURE_PLAN.md` § 2 "Lesson & card structure" — card types (line 54)
- `FEATURE_PLAN.md` § 3 "Card reader" — code cards monospaced, syntax highlighted,
  horizontal scroll for long lines, copy to clipboard; inline code styled
  distinctly (line 92)
- `FEATURE_PLAN.md` § 2 — no AI-generated diagrams or images in v1 (line 56)

## Depends on

`C02`, `E04` (copy confirmation feedback)

## Depended on by

`C08`, `C17`

## Decisions inherited

- **Four card types in v1: concept, code, example, recap** (`FEATURE_PLAN.md:54`).
- **One idea per card** is the constraint that keeps cards short
  (`FEATURE_PLAN.md:53`) — renderers should be designed for brevity and look wrong
  when given too much, so violations are visible.
- **No images or diagrams in v1**, so no renderer needs an image path
  (`FEATURE_PLAN.md:56`).
- **Code scrolls horizontally rather than wrapping** — wrapping code changes its
  meaning (`FEATURE_PLAN.md:92`).

## Feel spec

Code cards are where a learning app looks credible or amateur. Syntax
highlighting must be correct for the languages in the tech vertical, the
monospace metrics must not shift as the card enters, and copy must confirm itself
with a haptic and a brief inline acknowledgement rather than a toast that covers
the code.

The recap card should feel like an arrival — it ends every lesson and is the last
thing read before the win screen.

## Latency budget

Highlighting must not block the frame a card enters on. For long snippets, either
highlight ahead of time or render plain first and enrich within the same
animation.

## Degradation

An unknown language falls back to plain monospace rather than mis-highlighting.
Malformed content renders as plain text rather than an error card — a broken card
should still be readable.

## Accessibility

Code respects dynamic type up to a readable ceiling and scrolls rather than
reflowing. Highlight colours meet AA contrast in both themes and never carry
meaning by colour alone. Copy is reachable by screen reader with a clear label.

## Open questions

- Highlighting library and theme, and whether it is shared with `C11`'s snippet
  display and `C18`'s code blocks — it should be.
- Which languages ship at launch, given the vertical is tech but the topic is
  user-chosen.
- Whether recap cards get distinct visual treatment or rely on content alone.

## Acceptance criteria

- [ ] All four types render correctly from real generated content
- [ ] Code cards highlight correctly for the launch language set
- [ ] Long lines scroll horizontally without wrapping or clipping
- [ ] Copy works and confirms without obscuring the snippet
- [ ] An unknown language degrades to plain monospace
- [ ] Highlight colours pass AA in both themes
