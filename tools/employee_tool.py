import sqlite3

DB = "employees.db"

# =========================
# INIT DB
# =========================
def init_employee_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        sector TEXT,
        email TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# ADD EMPLOYEE
# =========================
def add_employee(name: str, role: str, sector: str, email: str) -> str:
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO employees (name, role, sector, email)
    VALUES (?, ?, ?, ?)
    """, (name, role, sector, email))

    conn.commit()
    conn.close()

    return f"{name} added as {role} in {sector}."


# =========================
# LIST EMPLOYEES
# =========================
def list_employees(sector: str = "") -> str:
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if sector:
        c.execute("SELECT * FROM employees WHERE sector=?", (sector,))
    else:
        c.execute("SELECT * FROM employees")

    rows = c.fetchall()
    conn.close()

    if not rows:
        return "No employees found."

    result = "Employees:\n"
    for r in rows:
        result += f"{r[0]}. {r[1]} | {r[2]} | {r[3]} | {r[4]}\n"

    return result


# =========================
# UPDATE EMPLOYEE
# =========================
def update_employee(emp_id: int, name: str = "", role: str = "", sector: str = "", email: str = "") -> str:
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if name:
        c.execute("UPDATE employees SET name=? WHERE id=?", (name, emp_id))
    if role:
        c.execute("UPDATE employees SET role=? WHERE id=?", (role, emp_id))
    if sector:
        c.execute("UPDATE employees SET sector=? WHERE id=?", (sector, emp_id))
    if email:
        c.execute("UPDATE employees SET email=? WHERE id=?", (email, emp_id))

    conn.commit()
    conn.close()

    return f"Employee {emp_id} updated."


# =========================
# DELETE EMPLOYEE
# =========================
def delete_employee(emp_id: int) -> str:
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM employees WHERE id=?", (emp_id,))
    conn.commit()
    conn.close()

    return f"Employee {emp_id} deleted."