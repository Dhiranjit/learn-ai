-- learn-ai schema  —  students 1:N notebooks
--
-- students
--   ├── name
--   └── context {}              grade, age, learning_style, pace
--
-- notebooks  (one per student per topic, ordered by id)
--   ├── title                   topic name
--   ├── state                   not_started | in_progress | completed
--   ├── current_position        index into subtopics array
--   ├── topic_mastery_score     cached AVG of subtopic mastery scores
--   └── subtopics []
--         ├── title
--         ├── position
--         ├── status            not_started | in_progress | completed
--         ├── mastery           0–5
--         ├── weaknesses []     identified gaps
--         └── notes             tutor observations


CREATE TABLE IF NOT EXISTS students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    context     TEXT NOT NULL DEFAULT '{}',  -- JSON: grade, age, learning style, pace, etc.
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notebooks (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id          INTEGER NOT NULL REFERENCES students(id),
    title               TEXT NOT NULL,                             -- topic title (e.g. "Basics of Probability")
    state               TEXT NOT NULL DEFAULT 'not_started',       -- 'not_started' | 'in_progress' | 'completed'
    subtopics           TEXT NOT NULL DEFAULT '[]',                -- JSON array of subtopic objects
    current_position    INTEGER NOT NULL DEFAULT 0,                -- index into the subtopics array
    topic_mastery_score REAL NOT NULL DEFAULT 0.0,                 -- cached AVG of subtopic mastery scores
    needs_assessment    INTEGER NOT NULL DEFAULT 1,                -- 1 until initial quiz or first session
    started_at          TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
