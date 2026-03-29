"""
TutorAgent: A lightweight conversational agent implementing a Socratic tutoring style.

It wraps an BaseLLMClient, maintains chat history, and injects a system prompt to guide
responses toward structured, question-driven explanations.
"""

from src.llm.base import BaseLLMClient
from .prompts import COMPRESSION_PROMPT, SOCRATIC_FEYNMAN_SYSTEM_PROMPT

HISTORY_THRESHOLD = 15  # total history entries before compression triggers
RECENT_TURNS_TO_KEEP = 10  # entries to keep verbatim after compression


class TutorAgent:
    def __init__(self, llm: BaseLLMClient) -> None:
        self._llm: BaseLLMClient = llm
        self._history: list[dict] = []
        self._summary: str | None = None

    def chat(self, user_input: str, context: str | None = None) -> str:
        self._history.append({"role": "user", "content": user_input})

        if len(self._history) > HISTORY_THRESHOLD:
            old_turns = self._history[:-RECENT_TURNS_TO_KEEP] # Everything except last k
            self._summary = self._compress(old_turns)
            self._history = self._history[-RECENT_TURNS_TO_KEEP:]

        messages = [{"role": "system", "content": SOCRATIC_FEYNMAN_SYSTEM_PROMPT}]
        if self._summary is not None:
            messages.append({"role": "system", "content": self._summary})
        if context is not None:
            messages.append({"role": "system", "content": context})
        messages = messages + self._history

        response = self._llm.chat(messages)
        self._history.append({"role": "assistant", "content": response})
        return response

    def _compress(self, turns: list[dict]) -> str:
        messages = [{"role": "system", "content": COMPRESSION_PROMPT}] + turns
        return self._llm.chat(messages)

    def reset(self) -> None:
        self._history.clear()
        self._summary = None