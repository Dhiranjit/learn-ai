"""
CLI entrypoint for the AI tutor: runs a simple REPL loop that captures user input,
routes it through the TutorAgent, and prints responses until an exit command or interrupt.

Usage:
    learn-ai
    python -m src.cli # directly
"""

import os

import sqlite3
from src.agent import TutorAgent
from src.llm import GroqClient
from src.memory.db import get_connection, init_db
from src.memory.profile import StudentProfile
from src.session import SessionManager

EXIT_COMMANDS = {"quit", "exit", "q"}
SLASH_COMMANDS = {"/clear", "/help", "/notebooks"}

_CYAN = "\033[96m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _info(msg: str) -> None:
    print(f"{_CYAN}{msg}{_RESET}")


def _print_header(student_name: str, notebook_title: str | None) -> None:
    notebook = notebook_title or "no notebook selected"
    print(f"{_BOLD}[ {student_name}  |  {notebook} ]{_RESET}")


def _load_student(profile: StudentProfile) -> tuple[int, str]:
    name = input("Enter your name: ").strip()
    student = profile.get_student(name)
    if student:
        _info(f"Welcome back, {name}!")
        return student["id"], name
    else:
        student_id = profile.create_student(name)
        _info(f"New user profile created for {name}!")
        return student_id, name
    

def _select_notebook(profile: StudentProfile, session: SessionManager) -> sqlite3.Row | None:
    notebooks = profile.get_notebooks(session.student_id)
    if not notebooks:
        _info("No notebooks yet.")
        return None

    for i, nb in enumerate(notebooks):
        _info(f"{i}. {nb['title']}  [{nb['state']}]")

    while True:
        try:
            choice = input(f"\nSelect notebook (0-{len(notebooks) - 1}): ").strip()
            idx = int(choice)
            if 0 <= idx < len(notebooks):
                return notebooks[idx]
        except ValueError:
            pass
        _info("Invalid selection.")


def run_repl(agent: TutorAgent, profile: StudentProfile, session: SessionManager) -> None:
    """Runs the interactive chat loop."""
    _print_header(session.student_name, None)
    print("Type '/help' for available commands.")

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
                os.system("clear")
                _print_header(session.student_name, session.current_notebook_title)

            elif user_input.lower() == "/help":
                _info("/clear      — reset the conversation")
                _info("/notebooks  — browse and select a notebook")
                _info("/help       — show this message")
                _info("quit        — exit the tutor")

            elif user_input.lower() == "/notebooks":
                selected = _select_notebook(profile, session)
                if selected:
                    session.load_notebook(selected["id"], selected["title"])
                    _info(f"Notebook set to: {selected['title']}")

            continue

        response = agent.chat(user_input)
        print(f"\nTutor: {response}")


def _onboard_notebook(profile: StudentProfile, session: SessionManager) -> None:
    notebooks = profile.get_notebooks(session.student_id)
    if not notebooks:
        topic = input("What would you like to learn today? ").strip()
        nb = profile.create_notebook(session.student_id, topic, [])
        session.load_notebook(nb["id"], nb["title"])
        _info(f"Notebook '{topic}' created!")


def main():
    init_db()
    conn = get_connection()
    profile = StudentProfile(conn)

    student_id, student_name = _load_student(profile)
    session = SessionManager(student_id, student_name)

    _onboard_notebook(profile, session)

    llm = GroqClient()
    agent = TutorAgent(llm)
    run_repl(agent, profile, session)


if __name__ == "__main__":
    main()
