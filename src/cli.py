"""
CLI entrypoint for the AI tutor: runs a simple REPL loop that captures user input,
routes it through the TutorAgent, and prints responses until an exit command or interrupt.

Usage:
    learn-ai    
    python -m src.cli # directly
"""

from src.agent import TutorAgent
from src.llm import GroqClient

EXIT_COMMANDS = {"quit", "exit", "q"}
SLASH_COMMANDS = {"/clear"}


def run_repl(agent: TutorAgent) -> None:
    """Runs the interactive chat loop."""
    print("AI Tutor - type 'quit' to exit, '/clear' to reset the conversation.")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("exiting...")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("exiting...")
            break

        if user_input.lower() in SLASH_COMMANDS:
            if user_input.lower() == "/clear":
                agent.reset()
                print("\033[2J\033[H", end="")  # clear terminal
            continue

        response = agent.chat(user_input)
        print(f"\nTutor: {response}")


def main():
    llm = GroqClient()
    agent = TutorAgent(llm)
    run_repl(agent)


if __name__ == "__main__":
    main()
