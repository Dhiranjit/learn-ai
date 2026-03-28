# Architecture Decision Records

Key architectural decisions for the AI Tutor system. Detailed design docs will be added per component as they are built.

---

## ADR-001: LLM Provider

**Status:** Accepted | **Date:** 2026-03-25

Use **Qwen 3 32B** as the primary model via **Groq** and **OpenRouter** (free tier APIs). All LLM calls go through `GroqClient` in `src/llm/` so the model and provider can be swapped without touching other code.

---

## ADR-002: Vector Database

**Status:** Accepted | **Date:** 2026-03-24

**MVP: ChromaDB** (in-process, SQLite-backed, zero infrastructure). Migrate to **Qdrant** in production when advanced filtering or concurrent users are needed.

---

## ADR-003: Memory Architecture

**Status:** Accepted | **Date:** 2026-03-24

Dual storage: **SQLite** for structured data (mastery beliefs, interaction logs, misconceptions) and **ChromaDB** for semantic data (student goals, preferences, motivational context). All state mutations go through a central memory module (`src/memory/`).

---

## ADR-004: Orchestration Approach

**Status:** Revised | **Date:** 2026-03-27

**Build manually first, introduce frameworks when complexity warrants it.**

The original decision (LangChain + LangGraph for the agent loop) is deferred. The primary goal of this project is to learn how agentic systems work — memory management, tool calling, multi-step reasoning — by implementing these mechanisms explicitly. Frameworks like LangGraph abstract away exactly what is worth understanding at this stage.

**Current approach:**
- Agent loop: plain Python in `TutorAgent`
- Conversation history: manual `list[dict]`
- Tool calling: implemented by hand when tools are added (step 7)

**When to revisit:** Introduce LangGraph/LangChain once the manual implementation becomes genuinely difficult to maintain — likely after tool calling and memory persistence are in place.

**LlamaIndex** remains the plan for RAG (step 6), as document ingestion and chunking are not the learning target.

**DSPy** for structured classification (mastery scoring, hint-level selection) remains deferred to post-MVP.
