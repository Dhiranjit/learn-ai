from src.llm.base import BaseLLMClient
from src.agent.tutor import TutorAgent, HISTORY_THRESHOLD, RECENT_TURNS_TO_KEEP


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


def _fill_history(agent, turns: int) -> None:
    """Drive agent.chat() for `turns` rounds without caring about responses."""
    for i in range(turns):
        agent.chat(f"question {i}")


def test_compression_triggered_at_threshold():
    stub = StubLLMClient(reply="stub summary")
    agent = TutorAgent(llm=stub)

    # Drive enough turns to trigger compression at least once, then keep going
    _fill_history(agent, HISTORY_THRESHOLD + 1)

    # Compression fired and history stays bounded — never exceeds threshold
    assert agent._summary == "stub summary"
    assert len(agent._history) <= HISTORY_THRESHOLD


def test_compression_not_triggered_below_threshold():
    stub = StubLLMClient()
    agent = TutorAgent(llm=stub)

    # Exactly at threshold — should not compress yet
    # Each chat() appends user turn, then assistant turn → 2 entries per call
    # We want history length == HISTORY_THRESHOLD after the call, so do HISTORY_THRESHOLD // 2 calls
    for i in range(HISTORY_THRESHOLD // 2):
        agent.chat(f"question {i}")

    assert agent._summary is None


def test_summary_injected_into_messages_after_compression():
    stub = StubLLMClient(reply="stub summary")
    agent = TutorAgent(llm=stub)

    _fill_history(agent, HISTORY_THRESHOLD + 1)

    # Next chat() should inject the summary at index 1
    agent.chat("follow-up question")
    messages = stub.last_messages

    assert messages[0]["role"] == "system"  # main system prompt
    assert messages[1] == {"role": "system", "content": "stub summary"}


def test_reset_clears_summary():
    stub = StubLLMClient(reply="stub summary")
    agent = TutorAgent(llm=stub)

    _fill_history(agent, HISTORY_THRESHOLD + 1)
    assert agent._summary is not None

    agent.reset()

    assert agent._history == []
    assert agent._summary is None
