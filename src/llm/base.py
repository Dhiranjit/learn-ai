"""
BaseLLMClient: abstract base class for all LLM provider clients.

Any new provider (OpenAI, Anthropic, Ollama, etc.) must implement this interface,
ensuring TutorAgent and other callers are decoupled from concrete providers.
"""

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_completion_tokens: int = 1024,
    ) -> str: ...
