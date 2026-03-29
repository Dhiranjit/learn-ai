from src.llm.base import BaseLLMClient
from src.agent.tutor import TutorAgent


class StubLLMClient(BaseLLMClient):
    def __init__(self, reply: str = "stub reply") -> None:
        self.reply = reply

    def chat(self, messages: list[dict], **kwargs) -> str:
        return self.reply


def test_history_accumulates_across_turns():
    stub = StubLLMClient(reply="good question")
    agent = TutorAgent(llm=stub)

    agent.chat("What is gravity?")
    agent.chat("Can you give an example?")

    # history holds both user turns and both assistant turns
    roles = [m["role"] for m in agent._history]
    assert roles == ["user", "assistant", "user", "assistant"]


def test_reset_clears_history():
    stub = StubLLMClient()
    agent = TutorAgent(llm=stub)

    agent.chat("What is gravity?")
    agent.reset()

    assert agent._history == []
