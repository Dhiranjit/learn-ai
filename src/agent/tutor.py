"""
TutorAgent: Socratic tutor backed by GroqClient.
Manages conversation history as a plain list of message dicts.
"""

from src.llm.groq_client import GroqClient
from src.agent.prompts import SOCRATIC_FEYNMAN_SYSTEM_PROMPT 


class TutorAgent:
    def __init__(self) -> None:
        self._llm = GroqClient()
        self._history: list[dict] = []

    def chat(self, user_input: str) -> str:
        self._history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": SOCRATIC_FEYNMAN_SYSTEM_PROMPT}] + self._history

        response = self._llm.chat(messages)

        self._history.append({"role": "assistant", "content": response})
        return response
