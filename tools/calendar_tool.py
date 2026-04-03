import sqlite3

def init_calendar_db():
    conn = sqlite3.connect("calendar.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        time TEXT,
        participants TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_meeting(title: str, date: str, time: str, participants: str = "") -> str:
    try:
        conn = sqlite3.connect("calendar.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO meetings (title, date, time, participants)
            VALUES (?, ?, ?, ?)
        """, (title, date, time, participants))

        conn.commit()
        conn.close()

        return f"Meeting '{title}' scheduled on {date} at {time}."

    except Exception as e:
        print("Calendar error:", e)
        return "Sorry, I couldn't schedule the meeting."
    
def check_availability(date: str, time: str) -> str:
    conn = sqlite3.connect("calendar.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM meetings WHERE date=? AND time=?
    """, (date, time))

    meeting = cursor.fetchone()
    conn.close()

    if meeting:
        return "You already have a meeting at that time."
    else:
        return "You are available at that time."
    
def list_meetings() -> str:
    conn = sqlite3.connect("calendar.db")
    cursor = conn.cursor()

    cursor.execute("SELECT title, date, time FROM meetings ORDER BY date, time")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "You have no scheduled meetings."

    result = "Your upcoming meetings:\n"
    for r in rows:
        result += f"- {r[0]} on {r[1]} at {r[2]}\n"

    return result

def reschedule_meeting(title: str, new_date: str, new_time: str) -> str:
    conn = sqlite3.connect("calendar.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE meetings
        SET date=?, time=?
        WHERE title=?
    """, (new_date, new_time, title))

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        return f"Meeting '{title}' rescheduled to {new_date} at {new_time}."
    else:
        return "I couldn't find that meeting."
    
