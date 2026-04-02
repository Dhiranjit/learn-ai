class SessionManager:
    """Manages the state of a session for a student."""
    def __init__(self, student_id: int, student_name: str) -> None:
        self.student_id = student_id
        self.student_name = student_name
        self.current_notebook_id: int | None = None
        self.current_notebook_title: str | None = None

    def load_notebook(self, notebook_id: int, notebook_title: str) -> None:
        self.current_notebook_id = notebook_id
        self.current_notebook_title = notebook_title
