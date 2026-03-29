from src.llm.base import BaseLLMClient
from src.agent.tutor import TutorAgent


class StubLLMClient(BaseLLMClient):
    def __init__(self, reply: str = "stub reply") -> None:
        self.reply = reply
        self.last_messages: list[dict] = []

    def chat(self, messages: list[dict], **kwargs) -> str:
        self.last_messages = messages
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


def test_context_block_injected_between_system_and_history():
    stub = StubLLMClient()
    agent = TutorAgent(llm=stub)

    agent.chat("What is a sample space?", context="Student: Alice (Grade 10)")

    messages = stub.last_messages
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] != "Student: Alice (Grade 10)"  # system prompt, not context
    assert messages[1] == {"role": "system", "content": "Student: Alice (Grade 10)"}
    assert messages[2] == {"role": "user", "content": "What is a sample space?"}


def test_no_context_does_not_add_extra_message():
    stub = StubLLMClient()
    agent = TutorAgent(llm=stub)

    agent.chat("What is gravity?")

    messages = stub.last_messages
    assert len(messages) == 2  # system prompt + one user turn
    assert messages[0]["role"] == "system"
    assert messages[1] == {"role": "user", "content": "What is gravity?"}
