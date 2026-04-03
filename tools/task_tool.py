import sqlite3
from datetime import datetime

DB_PATH = "tasks.db"

# =========================
# INIT DATABASE
# =========================
def init_task_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        deadline TEXT,
        assigned_to TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# CREATE TASK
# =========================
def create_task(title: str, deadline: str = "", assigned_to: str = "") -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    INSERT INTO tasks (title, deadline, assigned_to, created_at)
    VALUES (?, ?, ?, ?)
    """, (title, deadline, assigned_to, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return f"Task created: {title}"


# =========================
# LIST TASKS
# =========================
def list_tasks() -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, title, deadline, status FROM tasks")
    rows = c.fetchall()

    conn.close()

    if not rows:
        return "No tasks found."

    result = "Here are your tasks:\n"
    for r in rows:
        result += f"{r[0]}. {r[1]} | Deadline: {r[2]} | Status: {r[3]}\n"

    return result


# =========================
# COMPLETE TASK
# =========================
def complete_task(task_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("UPDATE tasks SET status='completed' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

    return f"Task {task_id} marked as completed."