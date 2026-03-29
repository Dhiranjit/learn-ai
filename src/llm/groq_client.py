"""
GroqClient: Concrete LLM client using Groq’s OpenAI-compatible API.

Handles model configuration, environment-based credentials, and chat
completion calls behind a BaseLLMClient interface.
"""

import os

from openai import OpenAI
from dotenv import load_dotenv

from src.llm.base import BaseLLMClient


class GroqClient(BaseLLMClient):
    def __init__(self) -> None:
        load_dotenv()
        self._model = os.environ["GROQ_MODEL"]
        self._client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_completion_tokens: int = 1024,
    ) -> str:
        """Send a messages list to the LLM and return the reply as a string."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            reasoning_effort="none"
        )
        return response.choices[0].message.content
