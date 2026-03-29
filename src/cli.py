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
    llm = GroqClient()
    agent = TutorAgent(llm)
    run_repl(agent)


if __name__ == "__main__":
    main()
