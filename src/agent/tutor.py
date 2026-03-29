"""
TutorAgent: A lightweight conversational agent implementing a Socratic tutoring style.

It wraps an BaseLLMClient, maintains chat history, and injects a system prompt to guide
responses toward structured, question-driven explanations.
"""

from src.llm.base import BaseLLMClient
from .prompts import SOCRATIC_FEYNMAN_SYSTEM_PROMPT

class TutorAgent:
    def __init__(self, llm: BaseLLMClient) -> None:
        self._llm: BaseLLMClient = llm
        self._history: list[dict] = []

    def chat(self, user_input: str) -> str:
        self._history.append({"role": "user", "content": user_input})
        messages = [{"role": "system", "content": SOCRATIC_FEYNMAN_SYSTEM_PROMPT}] + self._history
        response = self._llm.chat(messages)

        self._history.append({"role": "assistant", "content": response})
        return response

    def reset(self) -> None:
        self._history.clear()