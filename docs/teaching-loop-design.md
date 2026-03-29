# Teaching Loop Design

Architecture for the AI Tutor's teaching loop: how student knowledge is modeled,
how sessions are structured, and how the tutor adapts per turn.

---

## Knowledge Hierarchy

Content is organized in a three-level hierarchy:

```
Subject: "Probability"
  ├─ Topic 1: "Basics of Probability"      ← order 1
  │     ├─ Sub-topic 1: "Introduction"     ← order 1
  │     ├─ Sub-topic 2: "Sample Spaces"    ← order 2
  │     └─ Sub-topic 3: "Conditional Probability"  ← order 3
  │
  └─ Topic 2: "Bayes' Theorem"             ← order 2
        ├─ Sub-topic 1: "The Formula"
        └─ Sub-topic 2: "Applications"
```

**Rules:**
- A Topic belongs to one Subject. A Sub-topic belongs to one Topic.
- Bayes' Theorem can appear as a light sub-topic under "Basics" AND as its own Topic
  for deeper coverage — two separate notebooks, both valid, progressive depth by design.
- Content structure is shared across all students. Mastery is per-student.
- Sub-topics carry no difficulty tags — they are curriculum entries only.

---

## Curriculum Bootstrapping

The `subjects`, `topics`, and `subtopics` tables must be populated before a notebook can
function. For MVP, this happens dynamically:

1. Student says "teach me probability"
2. The tutor makes an LLM call to generate a topic/subtopic breakdown for that subject
3. The tutor presents the plan: "Here's what I plan to cover — does this look right?"
4. On confirmation, the generated curriculum is stored in SQLite

The generated curriculum is a starting point, not a contract. Topics and sub-topics can
be added or reordered as the student's needs become clearer. Post-MVP: curated/editable
curricula, versioning, curriculum templates per domain.

---

## The Subject as Roadmap

The Subject is a loose index and guidance layer. It shows what Topics exist in a domain
and tracks which Topics have active Notebooks for a student.

Example view for a student:

```
Probability (Subject)
  ✓ Basics of Probability    [in progress — 2/3 sub-topics taught, topic mastery: 3.1/5]
  ○ Bayes' Theorem            [not started]
  ○ Probability Distributions [not started]
```

This is derived from Notebooks + mastery_beliefs — no extra table needed. Topic ordering
within a Subject is defined by `order_index`. Dynamic/adaptive ordering is a future feature.

---

## The Notebook — Teaching Unit

One Notebook per (student, topic). It is the student's complete learning record for
that Topic. Sessions pick up exactly where the previous session left off.

**States:** `not_started` → `in_progress` → `completed`

**State transitions:**
- `not_started → in_progress`: when the first session on this notebook begins
- `in_progress → completed`: when ALL sub-topics have mastery_score >= 3
- `completed → in_progress`: allowed — student can revisit a topic

**Constraint:** One active notebook per session. Switching topics = ending the current
session and starting a new one.

**End-of-notebook:** When the last sub-topic is completed, the tutor gives a brief
summary of the topic ("Here's where you stand across all sub-topics"), marks the notebook
as `completed`, and suggests the next topic in the subject roadmap.

**Contains:**
- Ordered list of sub-topics to teach (the curriculum for this topic)
- Which sub-topics have been taught (`taught` flag per sub-topic)
- Current sub-topic in progress (`current_subtopic_id`)
- Mastery score per sub-topic (0–5)
- Topic-level mastery score (derived aggregate, cached)
- Weaknesses identified per sub-topic
- A chronological progress log

---

## Two-Level Mastery

### Sub-topic Mastery (Direct)
The granular unit. Updated by the post-turn assessment pass after each student message.

| Score | Label | What It Means |
|---|---|---|
| 0 | Untested | Never discussed |
| 1 | Introduced | Student has seen it, no coherent model yet |
| 2 | Developing | Partial/rough understanding |
| 3 | Proficient | Correct basic model, can apply in simple cases |
| 4 | Advanced | Can apply and extend to new situations |
| 5 | Expert | Can teach it, spot edge cases, handle novel problems |

**Update rules:**
- Max delta per turn: ±1
- Multiple confirmations needed to reach 4 or 5
- Score never drops below 0

### Topic Mastery (Derived)
Computed as `AVG(subtopic_mastery_scores)` across all sub-topics in the notebook.
Cached in `notebooks.topic_mastery_score` and refreshed after each assessment pass.

This is the single-number answer to "how well does this student know this topic?"

---

## Mastery vs. Weakness

| | Mastery | Weakness |
|---|---|---|
| What | Overall proficiency score per sub-topic | A specific gap or wrong mental model |
| Type | Integer 0–5 | Text description + severity |
| Example | "Conditional Probability: 2/5" | "Confuses P(A\|B) with P(B\|A) in multi-step problems" |
| Updated | After each assessment pass | When a specific error pattern is detected |
| Resolved | Implicitly (score rises) | Explicit `resolved` flag |

Weaknesses complement mastery: mastery says *how much*, weakness says *what specifically*.
The Socratic system prompt already handles weaknesses correctly (never directly correct —
ask a revealing question). The DB record ensures weaknesses persist across sessions.

---

## Student Profile

Students carry profile data used for teaching alignment:

| Field | Purpose |
|---|---|
| name | Personalization ("Good thinking, Alice") |
| gender | Pronoun alignment in responses |
| grade | Vocabulary and example depth calibration |
| age | Additional context for pacing and references |

Example context injection: `Student: Alice (female, Grade 10, age 15)`

The tutor uses this to select age-appropriate examples and vocabulary complexity.

---

## Initial Mastery Assessment

When a student opens a new Notebook (no mastery records), all sub-topics start at
`mastery_score=0` (Untested). The tutor begins with broad exploratory questions to calibrate.

**Future (deferred):** A quiz tool at session start will assess the student's initial
mastery level across sub-topics before the Socratic session begins. This requires a UI
and a quiz-calling tool. The design accommodates this hook via the `needs_assessment` flag
on the notebook: if `needs_assessment=True` and no quiz result exists, the system will
eventually trigger the quiz. For now the flag exists; sessions proceed with score=0.

---

## Context Block (Injected Per Turn)

Before each LLM call, a context block is built from the current DB state and injected
before the conversation history. It covers ALL sub-topics in the topic — not just the
current one — so the tutor has the full mastery picture:

```
Student: Alice (female, Grade 10, age 15)
Subject: Probability
Topic: Basics of Probability
Current sub-topic: Conditional Probability (order 3/3)

Topic mastery: 2.3/5 (Developing)

Sub-topic breakdown:
  ✓ Introduction               — mastery: 4/5 (Advanced)
  ✓ Sample Spaces              — mastery: 3/5 (Proficient)
  → Conditional Probability    — mastery: 2/5 (Developing) ← current

Active weaknesses (unresolved only):
  - "Confuses P(A|B) with P(B|A) in multi-step problems" [major]
```

Only unresolved weaknesses are injected — resolved ones stay in DB for history but don't
consume tokens.

No explicit hint level is injected. The tutor infers how much scaffolding to provide from
the mastery scores, weakness records, and conversation flow. This is simpler and more
flexible than a numeric hint state.

The system prompt (Socratic style guide) stays static — only the context block changes.

---

## Per-Turn Data Flow

The turn loop is owned by a **SessionManager** — the orchestration layer between the CLI
and all other components. The CLI calls `session_manager.handle_turn(user_input)`, not
`agent.chat()` directly.

```
cli.py  →  SessionManager.handle_turn(user_input)

Session starts:
  ├─ Load student profile
  ├─ Load active notebook (or create one, state → in_progress)
  └─ Resume at notebook.current_subtopic_id

Each turn:
  ├─ Build context block from DB (all sub-topics, unresolved weaknesses)
  ├─ [Step 6] RAG: fetch doc chunks for current sub-topic
  │
  ├─ TutorAgent.chat():
  │     messages = [system_prompt] + [context_block] + [history]
  │     → Socratic response (returned to student)
  │
  ├─ Log turn to conversation_turns
  │
  └─ Post-turn assessment (separate lightweight LLM call):
        Inputs:
          - last 2–4 turns (tutor question + student response, at minimum)
          - current sub-topic name and description
          - current mastery score
        Outputs:
          mastery_delta: -1 | 0 | +1
          assessed_subtopic: str     ← which sub-topic the message relates to
          weakness: str | None
          stuck: bool
          subtopic_complete: bool
        → Update the *assessed* sub-topic's mastery (may differ from current)
        → Recompute notebooks.topic_mastery_score (AVG)
        → Insert weakness record if detected
        → Advance current_subtopic_id (see completion rules below)
        → Append to notebook_log
```

**Sub-topic completion rules:**
Advancing to the next sub-topic requires BOTH:
1. mastery_score >= 3 on the current sub-topic
2. The assessment flags `subtopic_complete: true`

Neither condition alone is sufficient. The notebook's sub-topic order is a guide — the
`current_subtopic_id` pointer can move backwards if the student revisits earlier material.

**Non-linear navigation:** The assessment outputs `assessed_subtopic` — which sub-topic
the student's message actually relates to. If a student goes back to a previous sub-topic,
its mastery is updated without moving the notebook pointer. The pointer only advances when
the *current* sub-topic is completed.

**One-turn mastery lag (accepted tradeoff):** The context block on turn N reflects mastery
from *before* turn N's student message. The assessment updates mastery *after* the tutor
responds. This is acceptable: the tutor reads the raw conversation and reacts to what the
student said, regardless of the score. The score matters more for cross-session persistence
than intra-turn decisions.

---

## SQLite Schema

### Curriculum (shared across all students)

```sql
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects(id),
    name TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    description TEXT
);

CREATE TABLE subtopics (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id),
    name TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    description TEXT
);
```

### Student State (per-student)

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT,
    grade TEXT,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notebooks (
    id INTEGER PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    topic_id INTEGER REFERENCES topics(id),
    state TEXT DEFAULT 'not_started',       -- 'not_started'|'in_progress'|'completed'
    current_subtopic_id INTEGER REFERENCES subtopics(id),
    topic_mastery_score REAL DEFAULT 0.0,   -- cached AVG of subtopic scores
    needs_assessment BOOLEAN DEFAULT TRUE,  -- True until initial quiz or first session
    started_at TIMESTAMP,
    UNIQUE(student_id, topic_id)
);

CREATE TABLE mastery_beliefs (
    id INTEGER PRIMARY KEY,
    notebook_id INTEGER REFERENCES notebooks(id),
    subtopic_id INTEGER REFERENCES subtopics(id),
    mastery_score INTEGER DEFAULT 0,        -- 0–5
    taught BOOLEAN DEFAULT FALSE,           -- has sub-topic been introduced?
    last_assessed TIMESTAMP,
    UNIQUE(notebook_id, subtopic_id)
);

CREATE TABLE weaknesses (
    id INTEGER PRIMARY KEY,
    notebook_id INTEGER REFERENCES notebooks(id),
    subtopic_id INTEGER REFERENCES subtopics(id),
    description TEXT NOT NULL,
    severity TEXT DEFAULT 'minor',          -- 'minor' | 'major'
    resolved BOOLEAN DEFAULT FALSE,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    notebook_id INTEGER REFERENCES notebooks(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE notebook_log (
    id INTEGER PRIMARY KEY,
    notebook_id INTEGER REFERENCES notebooks(id),
    session_id INTEGER REFERENCES sessions(id),
    subtopic_id INTEGER REFERENCES subtopics(id),
    event TEXT NOT NULL,  -- 'started'|'assessed'|'subtopic_completed'|'weakness_found'|'notebook_completed'
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_turns (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    turn_number INTEGER NOT NULL,
    role TEXT NOT NULL,                     -- 'user' | 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Design Notes

**`taught` ≠ `mastered`**
`taught=True` means the sub-topic has been introduced in a session.
`mastery_score` measures how well it was absorbed. A student can be taught a sub-topic
(score=1) without having mastered it. This distinction drives the tutor's decision to
re-introduce vs. deepen.

**Assessment is a silent, separate LLM call**
After each student message, a second lightweight LLM call extracts mastery signals.
It runs after the tutor has already responded — the student never sees it. Output is
structured JSON. This keeps the tutoring call focused entirely on Socratic teaching.

**Stuck detection (in-memory, per session)**
The SessionManager tracks consecutive turns where `mastery_delta <= 0` on the current
sub-topic. Thresholds:
- 3+ turns stuck → the tutor tries a different explanation angle (injected via context)
- 6+ turns stuck → the tutor suggests moving on or taking a break from this sub-topic
Reset on new session or sub-topic change. Not persisted to SQLite.

**History truncation (design for it early)**
Raw history grows without bound. At ~40 turns, token cost becomes significant. The history
management code should support summarization of old turns into a compressed context block,
even before the feature is implemented.

**`needs_assessment` flag**
New notebooks start with `needs_assessment=True`. When the quiz tool is built (future),
it fires at session start for any notebook in this state. For now the flag is a no-op;
sessions proceed with all sub-topics at mastery_score=0 (Untested).

---

## Module Structure

```
src/
  cli.py              # REPL — delegates to SessionManager
  session.py          # SessionManager — orchestrates the per-turn loop
  agent/
    tutor.py          # TutorAgent — Socratic LLM call, context injection slot
    prompts.py        # System prompts: SOCRATIC, TOPIC_DETECT, ASSESSMENT
  memory/             # (step 4)
    __init__.py
    profile.py        # StudentProfile — load/save student, notebook, mastery, weaknesses
    logger.py         # ConversationLogger — write turns to conversation_turns
    schema.sql        # Full SQLite schema
```

**Responsibilities:**
- `cli.py`: user I/O, slash commands. Calls `session_manager.handle_turn()`.
- `session.py`: owns the turn loop. Coordinates TutorAgent, StudentProfile,
  ConversationLogger, and the assessment LLM call. Tracks in-memory session
  state (turns_stuck, current sub-topic).
- `agent/tutor.py`: stateless-ish — takes messages, returns a response.
  Accepts an injected context block. Does NOT know about SQLite.
- `memory/profile.py`: all DB reads/writes for student, notebook, mastery, weaknesses.
