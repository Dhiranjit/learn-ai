# MVP Features

Defines what gets built in the AI Tutor MVP. Everything here is in scope; everything listed under "Deferred" is explicitly out of scope until post-MVP.

---

## In Scope

| #   | Feature                      | Description                                                                                                                                                                                  |
| --- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **LLM Client**               | `GroqClient` in `src/llm/` wrapping the raw `openai` SDK pointed at Groq. All LLM calls go through this interface so the model and provider can be swapped without touching other code.     |
| 2   | **CLI Chat Interface**       | Terminal REPL — read user input, print tutor responses. No web UI. Enough to interact with and test the system manually.                                                                     |
| 3   | **Socratic Agent Loop**      | Plain Python agent in `TutorAgent`. Guides the student through questions and hints rather than giving direct answers. System prompt enforces Socratic behavior. Manual conversation history. |
| 4   | **Student Profile (SQLite)** | Persist a student record: name, current subject/topic, and a per-concept mastery table (concept, mastery level, last seen). Loaded at session start; updated as the conversation progresses. |
| 5   | **Conversation Logging**     | Each exchange (user + tutor turn) written to SQLite via the central memory module (`src/memory/`) for later review.                                                                          |
| 6   | **RAG Pipeline**             | A small curated set of educational documents ingested into ChromaDB via LlamaIndex. On each student query, relevant chunks are retrieved and injected into the agent's context.              |
| 7   | **Calculator Tool**          | A simple arithmetic tool available to the agent. Implemented via manual tool-calling (no framework). Lets the tutor evaluate expressions without hallucinating results.                      |

---

## Deferred (Post-MVP)

These are intentional cuts — not forgotten, just not yet.

- **LangGraph / LangChain** — deliberately excluded during MVP. Will be introduced if/when manual orchestration becomes a maintenance burden (after tool calling and memory are in place)
- **Web / chat UI** — CLI is sufficient for now
- **Quiz tool and graph tool** — mentioned in project goals; saved for next iteration
- **DSPy structured classification** — mastery scoring, error-type detection, hint-level selection via DSPy. Deferred until the basic loop is solid
- **Adaptive pacing / difficulty** — Socratic behavior without auto-adjusting difficulty for now
- **Fine-tuning** — post-MVP learning goal
- **Qdrant migration** — ChromaDB is sufficient for single-user MVP (per ADR-002)
- **ChromaDB semantic memory** — SQLite structured layer is enough for MVP
- **Multi-user / concurrent access** — single student, single process for MVP

---

## Build Order

Build one block at a time in this sequence. Each step is independently testable before moving to the next.

```
1. ✅ LLM Client
   └─ GroqClient in src/llm/ — foundation, all other components call this

2. ✅ CLI Interface
   └─ enables manual end-to-end testing from day one

3. 🔄 Socratic Agent Loop
   └─ TutorAgent with manual list[dict] history — working tutor conversation

4. Student Profile (SQLite)
   └─ add identity and mastery persistence; load/save around each session

5. Conversation Logging
   └─ write session turns to SQLite through src/memory/

6. RAG Pipeline
   └─ ingest docs into ChromaDB via LlamaIndex; inject retrieved context per turn

7. Calculator Tool
   └─ manual tool-calling; test the full tool-use pattern end-to-end
```

---

## Architecture Alignment

| ADR     | Decision                                                         | MVP treatment                                           |
| ------- | ---------------------------------------------------------------- | ------------------------------------------------------- |
| ADR-001 | Qwen 3 32B via Groq / OpenRouter                                 | In scope — LLM client block                             |
| ADR-002 | ChromaDB for MVP vector DB                                       | In scope — RAG pipeline block                           |
| ADR-003 | SQLite (structured) + ChromaDB (semantic) dual memory            | SQLite in scope; ChromaDB semantic layer deferred       |
| ADR-004 | Manual orchestration first; LangGraph/LangChain introduced later | Manual approach in scope; frameworks deferred post-MVP  |
