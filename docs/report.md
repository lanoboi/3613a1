<!-- student-build:skill-integrity
status: pass
root: e84cd692d0b85eefe546385661958c27d07e8be6c5176a82012f68ccff5c8beb
expected_root: e84cd692d0b85eefe546385661958c27d07e8be6c5176a82012f68ccff5c8beb
mismatches: none
-->

# COMP 3613 Assignment 1

Draft this file with the Guide. **Update it after every phase milestone** before you pause. The use-case diagram is a UML PNG at `docs/diagrams/use-case.png`, linked from this file as `diagrams/use-case.png` (path relative to `docs/report.md`). The model diagram is Mermaid. **Embed wireframe images** as `wireframes/<file>` (files live in `docs/wireframes/`).

Do not put your student ID in this file if you will commit it. The PDF cover adds your name and ID at export time.

## Assigned project
Alumni App

## Named workflows

### 1. View Alumni Profile (User)

### 2. Follow Alumni (Alumni)

### 3. Join event (Alumni)

### 4. Message Alumni (Alumni)

### 5. Make post (Alumni)

## Use case diagram

![Use case diagram](diagrams/use-case.png)

This draft keeps the actor boundary to the named Phase 1 flows: `User` can view a profile, while `Alumni` can follow, message, join, and post. The shared profile lookup is set as an include for "Follow Alumni" and "Message Alumni" so those flows do not duplicate an actor connection to every use case.

## Model diagram

This model represents the alumni network behind the named flows: a general `User` can view an alumni profile, while `Alumni` records carry follow, message, post, and event participation data. The Phase 4 revision adds the profile details, repeated experience records, and event metadata visible in the wireframes. The same person can act as both a viewer and a profile owner, so profile, follow, and message tables are tied to a shared account record. A later Phase 5 addition (content moderation) adds the `is_banned` / `is_muted` / `muted_until` flags on `USER` and a `REPORT` table so users can flag posts and the admin account can review, remove, dismiss, ban, or mute.


```mermaid
erDiagram
    USER ||--o| ALUMNI_PROFILE : views
    USER ||--o{ FOLLOW : initiates
    USER ||--o{ MESSAGE : sends
    USER ||--o{ MESSAGE : receives
    USER ||--o{ CONVERSATION : member_one
    USER ||--o{ CONVERSATION : member_two
    USER ||--o{ EVENT_ATTENDEE : registers
    USER ||--o{ REPORT : files

    ALUMNI_PROFILE ||--o{ FOLLOW : receives
    ALUMNI_PROFILE ||--o{ POST : authors
    ALUMNI_PROFILE ||--o{ EXPERIENCE : has
    ALUMNI_PROFILE ||--o{ EVENT_ATTENDEE : joins

    CONVERSATION ||--o{ MESSAGE : contains

    EVENT ||--o{ EVENT_ATTENDEE : has

    POST ||--o{ REPORT : receives

    USER {
        int id PK
        string name
        string email
        string password_hash
        datetime created_at
        bool is_banned
        bool is_muted
        datetime muted_until
    }

    ALUMNI_PROFILE {
        int id PK
        int user_id FK
        string headline
        string bio
        string graduation_year
        string major
        string school
        string location
        string industry
        string help_offered
        datetime updated_at
    }

    EXPERIENCE {
        int id PK
        int alumni_profile_id FK
        string title
        string employer
        date start_date
        date end_date
    }

    FOLLOW {
        int id PK
        int follower_user_id FK
        int followed_profile_id FK
        datetime followed_at
    }

    MESSAGE {
        int id PK
        int conversation_id FK
        int sender_user_id FK
        int recipient_user_id FK
        string subject
        text body
        datetime sent_at
    }

    CONVERSATION {
        int id PK
        int participant_one_user_id FK
        int participant_two_user_id FK
    }

    POST {
        int id PK
        int author_profile_id FK
        text body
        datetime created_at
    }

    REPORT {
        int id PK
        int post_id FK
        int reporter_user_id FK
        string reason
        datetime created_at
    }

    EVENT {
        int id PK
        string title
        text description
        datetime event_date
        string event_time
        string event_format
        string location
        int organizer_profile_id FK
    }

    EVENT_ATTENDEE {
        int id PK
        int event_id FK
        int attendee_profile_id FK
        datetime joined_at
    }
```

Edge-case notes: a follow is modeled as a distinct relation because a user can follow many different alumni, and the same alumni profile can be followed by many users. Messaging is separate from the profile so the sender/recipient relationship can be recorded without collapsing the app into one generic “contact list.” Event participation is modeled as a join table to support multiple attendees per event and multiple events per alumni profile. `REPORT` is a distinct relation with a `(post_id, reporter_user_id)` unique constraint so one person cannot flag the same post twice; its optional `reason` supports the optional-reason report flow. `muted_until` is `NULL` for an indefinite mute and holds an expiry timestamp for a timed mute.

## Wireframes

### View Alumni Profile

![View Alumni Profile](wireframes/View%20Alumni%20Profile.png)

<!-- student-build:wireframe-coverage
use_case: View Alumni Profile
image: docs/wireframes/View Alumni Profile.png
covered: yes
-->

The profile overview shows identity, alumni details, experience, and mutual connections.

### Follow Alumni

![Follow Alumni](wireframes/Follow%20Alumni.png)

<!-- student-build:wireframe-coverage
use_case: Follow Alumni
image: docs/wireframes/Follow Alumni.png
covered: yes
-->

The profile's Follow action and workflow header cover opening a profile and following. The student clarified that followed alumni's updates appear on the alum's profile and on a shared posting board; the existing `FOLLOW` and `POST` relationships support this outcome.

### Join event

![Join event](wireframes/Join%20an%20event.png)

<!-- student-build:wireframe-coverage
use_case: Join event
image: docs/wireframes/Join an event.png
covered: yes
-->

The event listing shows event details, attendance, and a Join event action. The workflow header names a confirmation step, but its outcome/state is not shown.
The student clarified that Join event registers immediately; confirmation is the success state after registration.

### Message Alumni

![Message Alumni](wireframes/Message%20an%20alumni.png)

<!-- student-build:wireframe-coverage
use_case: Message Alumni
image: docs/wireframes/Message an alumni.png
covered: yes
-->

The inbox shows conversation previews, a selected conversation, message history, and a composer with a Send action.

### Make post

![Make post](wireframes/Make%20a%20Post.png)

<!-- student-build:wireframe-coverage
use_case: Make post
image: docs/wireframes/Make a Post.png
covered: yes
-->

The home feed shows a post composer and a published post. Reaction and comment counts are visible, though no workflows for changing them are named.

### Follow Alumni

![Follow Alumni](wireframes/Follow Alumni.png)

### Join an event

![Join an event](wireframes/Join an event.png)

### Make a Post

![Make a Post](wireframes/Make a Post.png)

### Message an alumni

![Message an alumni](wireframes/Message an alumni.png)

### View Alumni Profile

![View Alumni Profile](wireframes/View Alumni Profile.png)

## Phase 4 Model Fit Review

The student accepted these wireframe-backed additions:
The student accepted these wireframe-backed additions:

- `ALUMNI_PROFILE.school`, `location`, `industry`, and `help_offered` — visible on View Alumni Profile and Follow Alumni. Existing `graduation_year`, `headline`, and `bio` cover the class year, role summary, and about text.
- `EXPERIENCE.title`, `employer`, `start_date`, and `end_date` — the repeated role/company/date entries on both profile wireframes; each profile can have multiple experience records. "Present" is represented by an open end date.
- `EVENT.event_time` and `EVENT.event_format` — time and the "in person" label on Join an event.
- `CONVERSATION` groups a user's message thread with another user; `MESSAGE.conversation_id` links each message to the thread. Sender and recipient now reference `USER` so messages in either direction can be represented.

The existing `FOLLOW` and `POST` relationships support followed alumni updates on their profile and the shared posting board. Mutual connections and event attendance totals can be derived from existing follow and attendance records. Reaction and comment counts are displayed on Make a Post, but the student confirmed they are not necessary and they are not modeled.

## Theming

Branding: university blue and marine grey, Georgia typography, and a formal, academic tone that remains social. The wordmark is **AlumCircle**.

Applied the brand colors and Georgia font stack through shared CSS tokens. The landing page now presents AlumCircle and its alumni-community purpose; login and registration use the same wordmark and tone. Removed the unused display/body webfont imports and the generic landing-page demo copy and decorations.

Polish: added a UWI St Augustine campus-building photo as the landing background, removed duplicate anonymous sign-in/get-started links from the header, and changed the hero registration action to “Get started.” Signed-in navigation remains available in the header.

Login and registration now share the campus background with a slightly stronger blue overlay for contrast.

## Implementation notes

One named workflow at a time. Include verify notes and polish / model revisions (Phase 5). Do not treat the first build as final.

### View Alumni Profile

Implemented the searchable alumni directory at `/profiles` and profile details at `/profiles/{profile_id}`. The profile view shows the account name, alumni details, and experience entries. Registration collects `User.name` to match the ERD. `python manage.py init` seeds Maya Chen's wireframe profile and experience history.

Polish: the sidebar is fixed with its own scroll area; the profile back link and top navbar are removed on the detail view; the banner starts the page and contains the sidebar toggle. Added an Education section that displays the exact degree from the existing `major` field alongside school and graduation year; an unset degree shows “Not provided.” Student reviewed the profile and requested these final layout/education refinements before moving on.

<!-- student-build:code-check
workflow: View Alumni Profile
snippet: AlumniProfile account FK and profile fields in app/models/user.py
passed: yes
architecture_ok: yes
-->

<!-- student-build:code-check
workflow: View Alumni Profile
snippet: UserService delegates alumni-profile lookup to UserRepository in app/services/user_service.py
passed: yes
architecture_ok: yes
-->

<!-- student-build:code-check
workflow: View Alumni Profile
snippet: view_alumni_profile service call and response in app/routers/users.py
passed: yes
architecture_ok: yes
note: TemplateResponse follows the workspace runtime signature.
-->

<!-- student-build:code-check
workflow: View Alumni Profile
snippet: UserRepository profile lookup by primary key in app/repositories/user.py
passed: yes
architecture_ok: yes
-->

### Follow Alumni

Interaction decision: after following, the button shows “Following”; on hover it shows “Unfollow,” and clicking removes the follow.

<!-- student-build:code-check
workflow: Follow Alumni
snippet: Follow table with account/profile foreign keys, timestamp, and duplicate-pair constraint in app/models/user.py
passed: yes
architecture_ok: yes
-->

<!-- student-build:code-check
workflow: Follow Alumni
snippet: toggle_alumni_follow service call and redirect in app/routers/users.py
passed: yes
architecture_ok: yes
-->

Implemented the Follow toggle through repository and service layers. The profile button shows “Following” after activation and changes to “Unfollow” on hover; submitting it removes the follow. An isolated SQLite check confirmed the state transitions. Student confirmed the local Follow workflow works.

### Join event

Interaction decision: attendees can withdraw from an event. The Events page will include separate sections for upcoming events and events the signed-in user has joined.

Eligibility decision: only signed-in users with an `AlumniProfile` may join or withdraw; attendance records link to that profile.

<!-- student-build:code-check
workflow: Join event
snippet: Event and EventAttendee SQLModel definitions in app/models/user.py
passed: yes
architecture_ok: yes
note: both AlumniProfile foreign keys resolve to `alumni_profile.id`; the attendance pair is unique.
-->

<!-- student-build:code-check
workflow: Join event
snippet: toggle_event_attendance service call and redirect in app/routers/events.py
passed: yes
architecture_ok: yes
note: redirect resolves to the registered `events_view` endpoint.
-->

Implemented `/events` with **My events** above Upcoming events. Only users with an `AlumniProfile` can join or withdraw; event attendance is stored against that profile. Withdrawing returns the event to Upcoming. `python manage.py init` seeds two sample campus events. An isolated repository check confirmed the alumni-only gate and join/withdraw transitions. Student confirmed the local workflow works.

### Message Alumni

The flow starts from an alum's profile, then composes the first message and continues in the inbox conversation. The inbox pencil is the new-message entry point.

<!-- student-build:code-check
workflow: Message Alumni
snippet: Conversation participants and Message foreign keys/content fields in app/models/user.py
passed: yes
architecture_ok: yes
note: runtime inspection confirms all conversation, sender, and recipient foreign keys resolve.
-->

<!-- student-build:code-check
workflow: Message Alumni
snippet: send_message service call and redirect in app/routers/messages.py
passed: yes
architecture_ok: yes
note: calls `send_to_profile` and redirects to `messages_view` with the returned conversation ID.
-->

Implemented profile compose, the inbox pencil recipient picker, conversation threads, and replies. New messages reuse a conversation between the same two users; only participants can reply. An isolated repository check confirmed conversation reuse, inbox/thread retrieval, replies, and participant enforcement. Student confirmed the local workflow works.

### Make post

Feed scope decision: Home shows the signed-in user's own posts and posts from alumni they follow. Reaction and comment counts remain display-only; no reaction or comment workflows are modeled.

<!-- student-build:code-check
workflow: Make post
snippet: Post author profile FK, body, and creation timestamp in app/models/user.py
passed: yes
architecture_ok: yes
note: runtime inspection confirms author_profile_id references alumni_profile.id.
-->

<!-- student-build:code-check
workflow: Make post
snippet: create_post service call and redirect in app/routers/user_home.py
passed: yes
architecture_ok: yes
note: calls `create_for_user` and redirects to the registered Home route.
-->

Implemented the Home composer and feed. Posts are ordered newest first and include the user's own alumni profile and followed alumni. Publishing requires an alumni profile; reactions and comments remain unmodeled. An isolated repository check confirmed follow-feed visibility and the alumni-only publish rule. Student confirmed the local workflow works.

Supporting functionality (not a named workflow): signed-in users can complete or edit their alumni profile at `/profile/complete`. School, graduation year, and degree are required; professional details are optional. The Home prompt and **My Profile** navigation link provide entry points. Runtime checks confirmed create, update, and required-field validation; no additional workflow code-check was required.

### Content moderation (admin) — supporting functionality, not a named workflow

Sign in with `admin` / `adminpass` to land on `/admin`; no other account has these powers, and every moderation route is gated by the admin-only dependency.

- **Report a post:** any signed-in non-author can flag a feed post with an optional reason (`POST /posts/{id}/report`). The `(post_id, reporter_user_id)` unique constraint blocks duplicate reports, and self-reports are refused in `ModerationService.report_post`.
- **Reported-posts queue:** `/admin` lists each report with the post, author, reporter, reason, and timestamp. The admin can **remove the post** (also clears its reports), **dismiss the report**, or **ban the author**; all three confirm first via the shared `data-confirm` dialog.
- **Member table:** `/admin` lists every member with an Active / Muted / Banned status badge plus **Ban/Unban** and a **Mute** duration (1h, 24h, 7d, 30d, indefinite) or **Unmute**. Admins cannot ban, mute, or moderate themselves or other admin accounts.
- **Ban** refuses login with a clear message, and `get_current_user` rejects banned cookies so an existing session dies immediately. **Mute** allows browsing but blocks posting, following, joining events, messaging, and reporting; timed mutes expire automatically (`muted_until`) while indefinite mutes need an explicit unmute. A muted user sees a banner instead of the Home composer and the report control.
- **Registration hardening:** `AuthService.register_user` explicitly rejects taken usernames/emails (case-insensitive) before insert; the `unique=True` constraints remain the database backstop.
- **Schema:** additive `ALTER TABLE "user" ADD COLUMN` migration in `app/database.py` plus a new `report` table, so existing local and Render databases keep their data. Rules live in `ModerationService`, SQL in `ModerationRepository`, and routes stay thin (service call + flash + redirect).

## Deployed app

Phase 6. Public Render URL (not localhost). Markers open this to mark the three workflows.

[Deployed App](https://three613a1.onrender.com/)

## Logins

Every account a marker needs, including extra users you added. Starter accounts:

- bob / bobpass — regular user
- admin / adminpass — admin
- maya / mayapass — regular user with the wireframe alumni profile

## YouTube URL

## Session transcripts

Filled when the Guide builds the report: the agent writes chat markdown into `docs/transcripts/`; `python manage.py report` packages them.

Guide packaged **6** chat(s) in `docs/transcripts/` (and `docs/transcripts.zip`).

Index: [docs/transcripts/INDEX.md](transcripts/INDEX.md)

- [`opencode-phase5-polish-and-report`](transcripts/opencode-phase5-polish-and-report.md)
- [`phase-1-project-and-workflows`](transcripts/phase-1-project-and-workflows.md)
- [`phase-2-use-case-diagram`](transcripts/phase-2-use-case-diagram.md)
- [`phase-3-model-diagram`](transcripts/phase-3-model-diagram.md)
- [`phase-4-wireframes`](transcripts/phase-4-wireframes.md)
- [`phase-5-theming-build-polish`](transcripts/phase-5-theming-build-polish.md)

## Competency (student-judge)

Filled by Guide from the student-judge run when this report was built.

**Judged at:** 2026-10-11 21:57 (UTC-4 local)
**Evidence pass:** fresh re-run — re-read all Guide chats for this project (the five Copilot phase transcripts in `docs/transcripts/` plus the newly extracted OpenCode session `opencode-phase5-polish-and-report.md`, 13 student turns), current `docs/report.md`, `docs/diagrams/`, `docs/wireframes/`, and the shipped code (`app/routers` re-verified: zero `select(`/`db.exec`; self-follow rule correctly placed in `app/services/user_service.py`); live deployed URL re-fetched at judge time (prior judge.md discarded)

# student-judge competency report

**Student / session:** COMP 3613 student (GitHub Copilot agent chats Oct 8–9 2026; OpenCode Guide session Oct 11 2026)
**Artifact:** six Guide chats in `docs/transcripts/` (five extracted from VS Code `GitHub.copilot-chat/transcripts` JSONL merged with the Copilot `session-store.db` turns table; one extracted from the OpenCode session store), plus `docs/report.md` and the shipped code
**Phases in evidence:** 1–6 (COMP 3613; Phase 5 polish, Phase 6 deploy; never generic 0–5)

Chats read (this run — six files):
`phase-1-project-and-workflows`, `phase-2-use-case-diagram`, `phase-3-model-diagram`, `phase-4-wireframes`, `phase-5-theming-build-polish` (46 student turns), `opencode-phase5-polish-and-report` (13 student turns — post-deploy polish round: functional rules, full visual redesign, three browser-verify feedback rounds).

### Totals
| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | 0 |
| Metrics scored | 12 |
| Scoreable max | 12 × 4 = 48 |
| Awarded total | **46 / 48** |
| **Overall (avg of scored)** | **3.8 / 4** |
| Impression mark | **17 / 20** (Guide-logged confidence: 0.90 Phase 2, 0.75 Phase 3; mean 0.825 × 20 = 16.5 → 17; the Oct 11 polish session logged no suspicion/pause blocks, so no new confidence values apply) |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 4 | yes | One chat per design phase (P1 `8aa094c4`, P2 `a8d37519`, P3 `974a55f2`, P4 `ccc8bc3a`), P5 theme→build→polish in one chat, deploy last; then a separate Oct 11 OpenCode chat dedicated purely to **post-deploy polish** before any push ("do not push to github when done instead run a local instance of the app on my browser for me to confirm if i think its good"). Student enforced handoffs: "you have to give the next phase prompt at the end of every phase". No app code before the five wireframe images were in `docs/wireframes/`. |
| M2 | Problem framing | 3 | yes | Student's own words: "Alumni app"; five `Feature (user)` lines ("View Alumni Profile(User) … Make post(Alumni)"); theming prefs "Colors: university blue and marine grey / Type: Georgia / Tone: Formal and academic but still social / Logo or wordmark: AlumCircle"; new in Oct 11: product-identity reasoning for scope — "remove school from the seach examples the app is for inter school faculty events so that doesnt track with the apps identity". Include/extend answers and a typed entity list never appear because Guide asked 0 questions in Phases 2–3 (Guide miss, not a student gap). |
| M3 | Decision ownership | 3 | yes | Owned project, workflows, wireframes, theming, scope: "1, 2 and 3" (accepted 3 of 4 ERD additions), then reversed "implement conversation grouping and yes reation and comment count arent necessary", and set the business rule "only alumni should be able to join events, to stick to the sites identity". Oct 11 adds self-authored business rules — "you should be able to edit the info on your own profile / no other user should be able to do that", "you should not be able to follow yourself" — shipped as a service-layer guard. Entity/relationship naming itself was never elicited from the student (Guide drafted the ERD silently: "Questions: 0/5"), so that slice of ownership is unproven rather than refused. |
| M4 | Artefact-before-code | 4 | yes | ERD + wireframes were the spec: "Use the student-build skill. Phase 4. Here are my wireframe images in docs/wireframes/. … check whether the model still matches the flows." During code: "fix the ERD it doesnt show in the markdown preview" and "for consistency with the planned erd use name" — model kept in step with the artefact. The Oct 11 polish round revised UI, not schema — no divergent design appeared. |
| M5 | Verification habit | 4 | yes | 47 Copilot turns of run-and-report: "after signin i get a server erro message", "error 310 on events page, check for wat might be causing this erro every time you create a new page", then per-workflow confirmations "works lets move on", "it works on to the next". Oct 11 adds three browser-verify feedback rounds against a running local instance: "the webpage content is still a bit removed from the sidebar… the contyent should be aligned left instead of in the centre", "please re instate the landing page background image from before, same colored overlay and everything, everything else is fine", "the boxes with page content should span from sidebar until the end of the page" — acceptance only after personal inspection ("good job you can push this version to github"). |
| M6 | Assignment fit | 4 | yes | Shipped architecture verified twice, including after the polish round: zero `select(`/`db.exec` in `app/routers`; routes do `EventService(EventRepository(db))` and delegate (see `docs/diagrams/application-components.jpg`); the new self-follow rule was placed in `UserService.toggle_follow`, not the router. FastStarter auth reused, starter demo UI removed keeping `/config`, theme→build→polish→deploy order held. |
| M7 | Slice explanation | 4 | yes | Own-words decisions plus elicited, architecture-respecting snippets: Guide assigned "Check 4 of 4: Complete the marked handler in app/routers/users.py … Keep database access out of the route", reviewed "The route architecture is good: it calls the service, contains no SQL"; report code-checks for all five workflows record `passed: yes`, `architecture_ok: yes`. Student clarified flows in words: "the alumins updates appear on their page and on a shared posting board". |
| M8 | Prompt quality | 4 | yes | Phase-tagged openers for every chat, `Feature (user)` format, and concrete mismatch notes across both agents — Copilot: "when scrolling the sidebar ends causing a weird formatting mismatch, the sidebar should not scroll along with the page … move the sidebar button to be on top of the banner section so the banner is what starts the top of the page"; OpenCode: a 15-line fix list mixing rules and UX ("the alumcircle text on the sidebar should be larger and aligned to the left instead of the middle … change font to rubik use larger bolded font for usernames, wordmarks and headings"), each item independently checkable. |
| M9 | Response to pushback | 4 | yes | Kept steering named fixes to completion rather than accepting: "it should show unfollow when hovered after following" → later "works lets move on"; "my events should be above upcoming events" → "great, on to the next"; Oct 11: rejected part of the first redesign ("re instate the landing page background image from before … everything else is fine") and pushed two layout corrections ("content is still a bit removed from the sidebar", "boxes… should span from sidebar until the end of the page") until the result earned "good job". |
| M10 | Integrity | 4 | yes | Authentic student voice throughout (typo-heavy, e.g. "is that god?", "its read", "contyent", "seach"); `docs/report.md` skill-integrity block `status: pass`, root matches `.agents/skills.lock.json`; no suspicion blocks, no meta-laundering turns in any of the six chats. |
| M11 | Provenance continuity | 4 | yes | Every implemented workflow traces to this thread's artefacts — report code-checks reference the ERD entities (`AlumniProfile.user_id` unique FK "matches the ERD") and the five named wireframes; the Oct 11 polish restyled the same screens (profile, feed, events, messages, directory) with no parallel schema or substitute UI. |
| M12 | Sincerity trajectory | 4 | yes | No suspicion was ever raised: pause blocks record "Suspicion: none" (Phases 2, 3), zero `student-judge:sincerity` blocks exist across any of the six chats (the OpenCode session contains none either). |

## Strengths
- Exceptional Phase 5 verification/polish loop: 46 Copilot turns across theming, five workflows, and continuous fine-tuning, **plus** a dedicated post-deploy polish chat on Oct 11 — a 15-point student-authored fix list (profile-edit ownership, self-follow ban, sidebar active-state fix, logout placement + confirmation, eggshell theme with icon-rail sidebar, Rubik typography, full-width content, micro-interactions) followed by three verify-and-correct rounds. The explicit "first build is a red flag" condition is the opposite of what happened here, twice over.
- Layered architecture actually shipped and held under rapid polish: repositories own SQL, services own rules, routers bind and delegate; no persistence in any router (re-checked across `app/routers` after the polish round); the new self-follow prohibition landed as a `UserService` guard with the route flashing the service's message.
- Snippet ladder was followed per workflow (SQLModel + repository + service + thin route), with Guide rejecting an incorrect `TemplateResponse` call and the student correcting it ("not yet passed" → corrected → passed).
- Real model ownership decisions during Phase 4/5: partial ERD acceptance, then reversal to add conversation grouping, deliberate scoping-out of reaction/comment counts, and business rules in the student's own words ("only alumni should be able to join events, to stick to the sites identity"; "no other user should be able to [edit your profile]").
- Phase discipline held by the student across two different agents (Copilot then OpenCode), including demanding the next-phase handoff prompt each time and deferring the push until after local visual confirmation.
- Deployed URL `https://three613a1.onrender.com/` re-verified live at this judge time (fetched the AlumCircle landing page).

## Gaps (priority order)
1. None material after this fresh evidence pass. (Include/extend Q&A and a student-typed entity list are absent from the record because Guide asked 0 questions in Phases 2–3 — a Guide miss, not a student opportunity, so per the opportunity rule it is not a Gap.)

**Submission notes (not competency gaps):**
- The `## YouTube URL` section in `docs/report.md` is still empty — the 5-minute unlisted video link must be added before the final export (video shows your name, never your student ID).
- The Oct 11 polish round is not yet on GitHub/Render — it was authorized ("you can push this version to github") but the push had not executed when this run was judged; push, then confirm Render redeploys so the public URL serves the polished version.

## Phase gate status
| Phase | Status | Note |
|-------|--------|------|
| 1 | met | Alumni App + five `Feature (user)` lines; missing `(user)` on Follow caught and restated by the student. |
| 2 | met | UML PNG at `docs/diagrams/use-case.png`, embedded; Guide asked 0 steering questions (confidence 0.90, 0/4). |
| 3 | met | Mermaid `erDiagram` in report (confidence 0.75, 0/5); entities were agent-drafted without asking — Guide miss noted. |
| 4 | met | Five wireframe images cover all five use cases, embedded with coverage blocks; two unclear flows clarified by the student; three ERD additions accepted, then conversation grouping added. |
| 5 | met | Theme applied to landing/login/register; all five workflows implemented with elicited model+route snippets (`architecture_ok: yes`); extensive verify/polish in the Copilot session **and** a second full polish round in the Oct 11 OpenCode session — not a first-dump accept, by either agent. |
| 6 | met | Public URL live (re-verified at this judge time) + marker logins in report; final polish push pending (see submission notes). |

## Recommended next practice
- Weakest scored metrics are M2 (3): in one short pass, write your **own** include/extend pairs and entity+property list into the report's model notes (or state them in the video) so the framing layer of design ownership is on record — everything from relationships down already is.

## Integrity note
- **Clean.** Skills untouched (`skill-integrity: pass`, root matches lock); no answer-seeking, no external-LLM paste-back, no suspicion rounds in any of the six chats.
## Provenance flags
- None.
## Sincerity log summary
- Blocks found: 0 | max round: 0 | min/mean/final confidence: n/a | trend: n/a | cleared: n/a (no suspicion raised)
## Skips
- Skips: 0/3 used (from Guide pause blocks in Phases 2 and 3).

## Skill integrity

Course skills are hashed at export and compared to `.agents/skills.lock.json`. Do not edit `.agents/skills/`, `.cursor/skills/`, or `AGENTS.md`.

- Status: **pass**
- Root: `e84cd692d0b85eefe546385661958c27d07e8be6c5176a82012f68ccff5c8beb`
- none
