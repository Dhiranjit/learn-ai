"""
CLI chat interface — terminal REPL for interacting with the AI tutor.

Usage:
    learn-ai          # via installed entry point
    python -m src.cli # directly
"""

from src.agent import TutorAgent

EXIT_COMMANDS = {"quit", "exit", "q"}


def run_repl(agent: TutorAgent) -> None:
    """Runs the interactive chat loop."""
    print("AI Tutor - type 'quit' to exit.")

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

        response = agent.chat(user_input)
        print(f"\nTutor: {response}")


def main():
    agent = TutorAgent()
    run_repl(agent)


if __name__ == "__main__":
    main()
