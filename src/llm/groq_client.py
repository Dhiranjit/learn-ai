"""
GroqClient: raw OpenAI-SDK wrapper pointed at Groq's API.

This is the foundational LLM interface for the project. All LLM calls go
through here so the model and provider can be swapped without touching other code.
"""

import os

from openai import OpenAI
from dotenv import load_dotenv


class GroqClient:
    def __init__(self) -> None:
        load_dotenv()
        self._model = os.environ["GROQ_MODEL"]
        self._client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )

    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        Send a messages list to the LLM and return the reply as a string.

        Args:
            messages: list of {"role": "system"/"user"/"assistant", "content": str}
            **kwargs: forwarded to chat.completions.create (e.g. temperature, max_tokens)
        """
        params = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.7,
            "max_comepletion_tokens": 1024,

        }
        params.update(kwargs)
        response = self._client.chat.completions.create(**params)
        return response.choices[0].message.content
