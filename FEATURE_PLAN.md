# Feature Plan: Bite-Sized Learning App (working name TBD)

## Context

A mobile learning app in the spirit of Google's (retired) Grasshopper, combined with Duolingo's daily-habit mechanics. The core insight: people learn in short-form now, so lessons are delivered as small swipeable cards followed by exercises that lock in the learning. Content will ultimately come from two separate sources — an AI that generates a personalized course on demand for any topic the user asks for, and a community catalog of human-authored courses. This session pinned down the v1 feature set; no code exists yet.

**Decisions made:**
- **Vertical at launch:** tech/coding skills (best fit for card + checkable-exercise format, lowest AI-accuracy risk, densest early community; architecture stays topic-agnostic so other verticals can be added later).
- **Platform:** mobile app.
- **Content model:** two separate sources long-term (community-authored catalog + AI on-demand), but **v1 is AI-only**; community authoring is v2.
- **Gamification:** core habit loop only in v1 (streak, daily goal, XP, reminders) — no leagues/leaderboards yet.

---

## The Core Loop (v1)

1. User types a tech topic they want to learn ("Git basics", "Python decorators", "How DNS works").
2. AI generates a structured course sized to the topic — as many lessons and cards as the material genuinely needs, each lesson a run of short cards followed by exercises.
3. User swipes through cards, answers exercises, gets instant feedback and XP.
4. A daily goal + streak + reminder notification brings them back tomorrow to continue the course (or start a new one).

**Guiding principle: completeness, delivered short-form.** The short-form is the *format* (one idea per card, bite-sized sessions), not a limit on *coverage*. A course should teach a topic as thoroughly as a good book, tutorial series, or class would — the length is whatever that takes. We chunk the depth into many small cards; we don't cut the depth to fit a fixed length.

---

## v1 Feature Set

### 1. Onboarding & First Run

The single most important screen sequence in the app — it decides whether a new install becomes a day-2 user. Design goal: **topic → first card in under 60 seconds**, and let the user taste the product before asking them to create an account.

**Sequence**
1. **Value teaser (1 screen)** — one line on what the app does, one "Start learning" button. No sign-up wall yet.
2. **Topic pick** — "What do you want to learn?" free-text box + popular-topic chips (Git, Python, SQL, How the web works, etc.). This is the hook; it comes before any account step.
3. **Quick calibration (2 taps)** — experience level (New / Some / Confident) and daily goal (Casual 5 min / Regular 10 min / Serious 15 min). These feed difficulty and the daily-goal target. Skippable with sensible defaults (Some / Regular).
4. **Generation with payoff** — outline appears within seconds (streamed), user confirms, lesson 1 streams in. **User completes their first lesson as a guest** — full card + exercise experience, no account required.
5. **Soft account gate** — after the first lesson's win screen ("You earned 40 XP, day-1 streak started!"), prompt to create an account to *save progress and keep the streak*. Email + Google/Apple social login. Guest progress migrates into the new account on sign-up (don't lose their first lesson).
6. **Notification permission** — requested here, framed around the streak ("We'll remind you at [time] so you don't lose your streak"), with the user's chosen reminder time — not a cold OS prompt on launch.

**Edge cases to handle**
- Generation fails / times out → friendly retry, offer a pre-cached starter topic so the first run is never a dead end.
- User abandons mid-generation → resume state on next open.
- Guest who never signs up → keep local progress; re-prompt gently, don't nag.

### 2. AI Course Generation (the differentiator — detailed spec)

**Flow**
1. **Topic entry** — free-text prompt box plus suggested popular-topic chips. If the topic is too broad (e.g. "Python"), the AI asks one quick scoping question ("for web, data, or general?") before building anything.
2. **Outline confirmation** — AI returns a full syllabus covering the topic end-to-end (lesson titles + one-liners + estimated minutes). Lesson count is driven by the topic's actual scope, not a fixed range — a narrow topic ("Python decorators") is a handful of lessons; a broad one ("Backend engineering") is many. A **depth control** lets the user set intent — *Quick intro* / *Solid working knowledge* / *Deep / comprehensive* — which scales how much the outline covers and how granular each lesson gets. The user can still remove lessons, mark "I already know this," or ask for more depth on any part, then confirms. Cheap to generate and the main up-front personalization lever.
3. **Just-in-time generation** — lesson 1 generates immediately (streamed; first card visible within seconds). Each subsequent lesson generates in the background while the user works through the current one, so difficulty adaptation always uses the latest performance data.

**Lesson & card structure**
- A lesson is a run of cards followed by its exercises. **No fixed card or lesson count** — the AI uses as many cards as the concept needs (constraint is *one idea per card*, so cards stay short; a dense lesson simply has more of them). Lessons are sized to stay finishable in a sitting, and a longer topic means more lessons, not longer cards.
- Card types (v1): **concept card** (short text, one idea), **code card** (snippet + caption, syntax highlighted), **example card**, **recap card** (ends every lesson).
- Exercises are interleaved at a healthy cadence (roughly every few concept cards, plus an end-of-lesson set) so practice tracks the volume of new material rather than a fixed quota.
- No AI-generated diagrams/images in v1 — quality is too unreliable for teaching material.

**Depth / completeness**
- Coverage target is *equivalence to a good external source* on the topic — the user shouldn't finish and feel they still need to go read the "real" tutorial. The outline generator is prompted for comprehensive scope (fundamentals → practical application → common pitfalls → next steps), tuned by the user's chosen depth level.
- Because courses can be long, the **just-in-time generation** and **shared-course cache** (below) matter more, not less — they keep a 40-card course cheap and fast rather than generating everything up front.
- Long courses lean on the habit loop: a big topic is meant to be worked through over many days, which is exactly the daily-return behavior the app is built around.

**Exercise types (all auto-checkable)**
- Multiple choice
- Predict the output (of a code snippet)
- Fill in the blank — **input adapts to difficulty**: tap-to-choose from 3–5 provided tokens at easier levels; **free typing** at harder levels and in review mode (needs fuzzy/normalized answer matching — trim whitespace, case-insensitive where appropriate, accept known synonyms)
- Arrange the steps / order the lines

**Answer-key verification (trust)**
- Code-based exercises are **executed in a server sandbox at generation time**; if the real output doesn't match the AI's answer key, the exercise is regenerated. Wrong answer keys are fatal to trust in a learning app, so this ships in v1.
- All generated lessons must pass schema validation; malformed output is regenerated automatically.

**Difficulty adaptation**
- Inputs: experience level from onboarding + per-lesson miss rate.
- Miss >~40% of a lesson's exercises → next lesson is generated easier and opens with a review card.
- Ace two lessons in a row → offer a faster/harder pace toggle.

**Explanations & tutor chat**
- Every exercise's right/wrong explanation is **pre-generated with the lesson** (zero latency after answering).
- **Full conversational tutor** per course: a persistent chat thread the user can open from any card or exercise. The tutor is context-aware — it knows the current card, the user's answer, and where they are in the course — so questions like "why is my answer wrong?" or "can you explain this differently?" work without the user re-explaining. Preset quick actions ("explain differently", "give me an example", "why is this wrong?") seed the thread but the user can free-type follow-ups.
- Tutor build considerations: cost per message (cap/meter free-tier usage), content moderation on both user input and model output, and keeping the tutor on-topic (scoped to learning, declines off-topic requests). These are why a full chat is a meaningfully bigger surface than preset actions — flagged so implementation budgets for it.

**Cost control & reuse**
- **Shared base + personal deltas**: popular topics map to a cached shared course; personalization (difficulty, skipped lessons) is applied per user on top. One generation serves many users, and the best cached courses seed the v2 community catalog.
- Per-user generation limits (ties into monetization later).

### 3. Learning Experience (in-lesson)

**Card reader**
- One card per screen; advance by tap (right side) or swipe. Back is allowed within a lesson (re-read a card) but you can't skip ahead past unseen content.
- Persistent **progress bar** at top showing position within the lesson; segmented so the user sees "3 of 7 cards, then exercises".
- **Code cards**: monospaced, syntax-highlighted, horizontal scroll for long lines, copy-to-clipboard. Inline code in prose cards is styled distinctly.
- Tutor entry point (chat icon) available on every card — see AI Course Generation § tutor.

**Exercise flow**
- Exercise fills the screen; answer control matches the type (MCQ buttons, token bank + blanks, draggable step list, text field).
- **Immediate feedback**: correct → satisfying confirmation + XP tick; wrong → the pre-generated explanation of *why*, plus the correct answer, and a "still confused? ask the tutor" affordance.
- **No hard fail**: a wrong answer doesn't block progress. Instead the missed exercise is **re-queued at the end of the lesson** (must clear it to finish) — in-session reinforcement without a punishing gate.
- Every answer result is logged (exercise id, correct/incorrect, latency) — feeds both difficulty adaptation and cross-session review.

**Lesson completion**
- End-of-lesson **win screen**: XP earned, accuracy, streak status, "continue to next lesson" CTA. This is the dopamine beat — keep it snappy and celebratory.
- If the user has hit their daily goal, the win screen doubles as the "goal met" moment (see Habit Loop).

**Review mode (cross-session spaced repetition)**
- A separate **daily Review session** surfaced on the home screen, built from exercises the user previously got wrong or hasn't seen in a while, across all their courses.
- Scheduling: simple, well-understood algorithm (Leitner-style boxes or SM-2-lite) — an item missed today comes back tomorrow, an item aced repeatedly stretches out. Full-blown FSRS is overkill for v1.
- Review counts toward the daily goal and streak, so users have a fast option on busy days.

**Session sizing**
- A session targets the user's chosen daily minutes; the app aims to make one lesson-or-review finishable in that window and shows an honest time estimate before starting.

### 4. Habit Loop (core only)

The retention engine. Deliberately minimal in v1 — streak, goal, XP, notifications — but each defined concretely so it can be built without guesswork.

**Daily goal**
- Chosen at onboarding (5/10/15 min), editable in settings. Internally represented as an **XP target** (minutes are the user-facing framing; XP is what's actually counted, so review and lessons both contribute cleanly).
- The day "counts" when the user hits the XP target. Timezone: goal resets at local midnight; store the user's timezone and compute day boundaries against it.

**XP**
- Earned per exercise answered correctly (base amount) and a small amount per card completed, with a **lesson-completion bonus**. Review-item correct answers grant XP too.
- Keep the numbers simple and legible (e.g. correct exercise = 10 XP, lesson complete = +20). Exact values are a tuning detail, not an architecture decision.

**Streak**
- Consecutive days the daily goal was met. Prominent flame + count on the home screen.
- Increments once per day when the goal is hit; breaks if a day passes without meeting the goal.
- **No streak freezes / repair in v1** (explicitly deferred) — but store streak history in a way that lets freezes be added later without migration pain.

**Notifications**
- **Daily reminder** at the user-chosen time, copy referencing their active course ("Your Python course is waiting — 8 min to keep your streak").
- **Streak-at-risk** evening nudge if the goal isn't met by, say, a few hours before local midnight.
- Respect OS permission state and a quiet-hours setting; cap at these two per day — no spam.
- Notification scheduling is server-driven (so copy can be personalized) with local fallbacks.

*(Deferred, noted so the data model leaves room: leagues/leaderboards, achievements/badges, streak freezes.)*

### 5. Home / My Courses

The daily landing screen; its job is to make "what do I do right now" a one-tap answer.

- **Top bar**: streak flame + count, today's goal progress ring (XP toward target), total XP.
- **Continue card** (hero): the active course with "Continue — Lesson N" CTA and progress %. This is the default action every day.
- **Daily Review card**: shown when review items are due, with the count ("12 items to review"). Fast path to hit the goal.
- **My courses list**: in-progress and completed courses, each with progress. Tap to resume or review.
- **Start a new topic**: always-available entry back into the generation flow (topic box + chips).
- Empty state (brand-new account beyond onboarding): guided toward starting a second topic or reviewing.

### 6. Profile & Settings

- **Profile**: display name/avatar, join date, headline stats (streak, total XP, courses completed, lessons done).
- **Learning settings**: daily goal, reminder time + quiet hours, experience level (adjustable; feeds future difficulty).
- **Account**: manage sign-in method, sign out, **delete account** (full data deletion — must actually purge user data, matters for app-store review and privacy law).
- **Legal/support**: privacy policy, terms, contact/feedback link, app version. (App stores require these.)

### 7. Backend / Platform

**Data model (sketch — source-agnostic on purpose)**
- `user` — auth identity, timezone, experience level, daily-goal XP target, reminder time, quiet hours, notification token.
- `course` — topic, outline/syllabus, `source` enum (`ai` | `community` — only `ai` used in v1, but the column exists so community content in v2 is additive, not a rewrite), `visibility` (private vs shared/cached), author ref (null for AI). A shared cached course is just a `course` row reused across users.
- `lesson` — belongs to a course, ordered index, title, generation status (`pending` | `generating` | `ready` | `failed`).
- `card` — belongs to a lesson, ordered, `type` (concept/code/example/recap), content payload.
- `exercise` — belongs to a lesson, ordered, `type` (mcq/predict-output/fill-blank/order-steps), prompt, options/tokens, **verified answer key**, pre-generated explanation, difficulty.
- `enrollment` — user↔course, with **personal deltas** (skipped lessons, difficulty adjustments) layered over a possibly-shared course.
- `progress` — per user per lesson: status, per-exercise results (correct/incorrect, latency, timestamp).
- `review_item` — per user per exercise: spaced-repetition box/interval, next-due date.
- `streak` / `daily_activity` — per user per local day: XP earned, goal-met flag; streak derived from this history (leaves room for freezes later).
- `tutor_thread` / `tutor_message` — per user per course, with usage metering counters.
- `analytics_event` — append-only event log.

**Services**
- **Auth**: email + Google/Apple; guest sessions that migrate to a real account on sign-up (first-lesson progress must carry over).
- **Generation pipeline**: outline generator → lesson generator (streamed) → per-exercise **schema validation** → **code-execution sandbox** verifying answer keys (regenerate on mismatch) → persist. Just-in-time: generate lesson N+1 while user is on lesson N. Shared-course cache keyed by normalized topic + level.
- **Sandbox**: isolated, resource-capped, time-limited code execution for supported languages; used only for answer-key verification in v1 (not user-run code — that's the deferred Grasshopper-style feature).
- **Tutor service**: context-injected chat (current card, user answer, course position), per-user usage metering, moderation on input and output, on-topic guardrail.
- **Notification service**: server-scheduled daily reminder + streak-at-risk, timezone-aware, respects permission + quiet hours.
- **Analytics**: session start/finish, exercise results, generation success/latency/cost, streak/retention (D1/D7). Needed from day one to tune difficulty and retention.

**Cross-cutting**
- Cost observability on every LLM call (generation + tutor) — per-user and per-topic, to protect margins and inform monetization limits later.
- Content moderation applies to tutor I/O and to any user-entered free text.
- Privacy: account deletion purges user data; store the minimum PII needed.

---

## v1 Build Milestones (suggested order)

A sequence that gets to a testable core loop fast, then layers retention on top.

1. **Skeleton + auth** — app shell, navigation, account/guest sessions, data model migrations.
2. **Generation vertical slice** — topic → outline → one lesson (cards + one exercise type), rendered in the card reader. Prove the end-to-end AI pipeline before breadth.
3. **All card & exercise types** — the four card types and four exercise types, with immediate feedback and re-queue-on-miss.
4. **Answer-key sandbox + schema validation** — make generated content trustworthy.
5. **Progress + win screen** — persist results, lesson completion, XP.
6. **Habit loop** — daily goal, streak, home screen, notifications.
7. **Review mode** — cross-session spaced repetition.
8. **Tutor chat** — the biggest single feature; build after the core loop is solid so it's additive.
9. **Shared-course cache + cost controls** — optimize once real usage exists.
10. **Polish + onboarding tuning + analytics dashboards** — the pre-launch pass.

The **launch-blocking minimum** is milestones 1–6 (a new user can learn a topic and be pulled back by the streak). Review (7) and tutor (8) are high-value but could ship in a fast-follow if timelines slip — noted so scope can flex without touching architecture.

---

## v2 and Beyond (explicitly out of v1 scope)

**v2 — Community content (the second source):**
- Course builder for creators (write cards, add exercises from the same exercise-type palette, publish).
- Public course catalog with search, categories, ratings, and completion counts.
- Reporting/moderation for quality control; creator profiles.
- AI-assist inside the builder (draft cards/questions for the creator) — bridges the two sources without merging them.

**Later:**
- Full gamification: leagues, achievements, streak freezes.
- New verticals beyond tech (languages, exam prep, professional skills) — enabled by the topic-agnostic data model.
- Social: follow creators, share courses/streaks.
- Monetization (e.g. free tier with limited AI generations per week; premium = unlimited generations + offline mode). Decision deferred.
- Runnable code exercises (in-app code execution) — the Grasshopper signature; big lift, high payoff for the tech vertical.

---

## Open Questions (for the next session)

- **Tech stack — LOCKED.** See `ARCHITECTURE.md` (Flutter + Firebase + Vertex AI/Gemini + Cloud Run + PostHog).
- Per-course generation cost budget — needs a first real cost measurement to set.
- App name and branding.

## Verification

This is a planning-only deliverable — no code to test. "Done" means the user agrees this feature list captures their app vision and is ready to hand to a design/implementation session. Success criteria for v1 when built: a new user can go from typing a topic to answering their first exercise in one session, and the streak/notification loop brings them back on day 2.
