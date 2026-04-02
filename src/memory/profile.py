import json
import sqlite3


class StudentProfile:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create_student(self, name: str) -> int:
        cursor = self.conn.execute(
            "INSERT INTO students (name) VALUES (?)", (name,)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_student(self, name: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM students WHERE name = ?", (name,)
        ).fetchone()

    def get_notebooks(self, student_id: int) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT id, title FROM notebooks WHERE student_id = ? ORDER BY created_at DESC",
            (student_id,),
        ).fetchall()

    def get_notebook_by_id(self, notebook_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM notebooks WHERE id = ?", (notebook_id,)
        ).fetchone()

    def get_notebook_by_title(self, student_id: int, title: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM notebooks WHERE student_id = ? AND LOWER(title) = LOWER(?)",
            (student_id, title),
        ).fetchone()

    def create_notebook(self, student_id: int, title: str, subtopics: list[dict]) -> sqlite3.Row:
        cursor = self.conn.execute(
            """INSERT INTO notebooks (student_id, title, state, subtopics,
               current_position, topic_mastery_score, needs_assessment)
               VALUES (?, ?, 'not_started', ?, 0, 0.0, 1)""",
            (student_id, title, json.dumps(subtopics)),
        )
        self.conn.commit()
        return self.conn.execute(
            "SELECT * FROM notebooks WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    def update_notebook(self, notebook_id: int, **fields) -> None:
        if "subtopics" in fields and isinstance(fields["subtopics"], list):
            fields["subtopics"] = json.dumps(fields["subtopics"])
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [notebook_id]
        self.conn.execute(
            f"UPDATE notebooks SET {set_clause} WHERE id = ?", values
        )
        self.conn.commit()
