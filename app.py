import os
import json
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from groq import Groq

# ================== ENV ==================
load_dotenv()

# ================== GROQ CLIENT ==================

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================== FLASK ==================
app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# ================== TOOLS ==================
from tools.weather_tool import get_weather
from tools.calculator_tool import calculate
from tools.time_tool import get_time
from tools.email_tool import send_email
from tools.document_tool import search_documents
from tools.task_tool import init_task_db, create_task, list_tasks, complete_task
from tools.meeting_tool import summarize_meeting, email_meeting_summary
from tools.calendar_tool import (
    init_calendar_db,
    create_meeting,
    check_availability,
    list_meetings,
    reschedule_meeting,
)
from tools.employee_tool import (
    init_employee_db,
    add_employee,
    list_employees,
    update_employee,
    delete_employee
)

init_employee_db()
init_task_db()
init_calendar_db()

TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_time": get_time,
    "send_email": send_email,
    "create_meeting": create_meeting,
    "check_availability": check_availability,
    "list_meetings": list_meetings,
    "reschedule_meeting": reschedule_meeting,
    "search_documents": search_documents,
    "create_task": create_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    " summarize_meeting": summarize_meeting,
    " email_meeting_summary": email_meeting_summary,
    "add_employee": add_employee,
    "list_employees": list_employees,
    "update_employee": update_employee,
    "delete_employee": delete_employee,
}

def clean_text(text):
    import re

    # Fix missing spaces between lowercase-uppercase (e.g., "salesReport")
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Add space after punctuation if missing
    text = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', text)

    # Normalize multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# ================== HELPERS ==================
def extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()

def run_chat(messages, temperature=0.7, max_tokens=1024):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# ================== AGENT DECIDER ==================
def agent_decide(user_message, history, is_voice=False):
    system_prompt = """
You are an AI assistant with tool access.

AVAILABLE TOOLS:

1. get_weather(city)
2. calculate(expression)
3. get_time(city)
4. send_email(to, subject, body)
5. create_meeting(title, date, time, participants)
6. check_availability(date, time)
7. list_meetings()
8. reschedule_meeting(title, new_date, new_time)
9. search_documents(query)
   → Use when user asks about: files, reports, documents, PDFs, sales data, revenue, performance, regions, action items, summaries
10. create_task(title, deadline, assigned_to)
    → Use when user asks to create or remember tasks
11. list_tasks()
    → Use when user asks to see tasks
12. complete_task(task_id)
    → Use when user wants to mark task done
13. summarize_meeting(text)
   → Use when user asks to summarize meeting
   - Keep summary concise for voice (max 3-5 lines)
14. email_meeting_summary(to, meeting_text)
   → Use when user wants summary emailed
15. add_employee(name, role, sector, email)
    → Use when user adds employee
16. list_employees(sector)
    → Use to show employees
17. update_employee(emp_id, name, role, sector, email)
    → Use to modify employee
18. delete_employee(emp_id)
    → Use to remove employee

EXAMPLES:
- User: "What's the weather in Paris?" → {"tool": "get_weather", "arguments": {"city": "Paris"}}
- User: "Calculate 5 + 3" → {"tool": "calculate", "arguments": {"expression": "5 + 3"}}
- User: "What time is it in Tokyo?" → {"tool": "get_time", "arguments": {"city": "Tokyo"}}
- User: "Send email to john@example.com subject Hello body Hi" → {"tool": "send_email", "arguments": {"to": "john@example.com", "subject": "Hello", "body": "Hi"}}
- User: "Schedule a meeting titled 'Team Call' on 2024-05-01 at 10:00 with participants 'alice,bob'" → {"tool": "create_meeting", "arguments": {"title": "Team Call", "date": "2024-05-01", "time": "10:00", "participants": "alice,bob"}}
- User: "Search for sales data" → {"tool": "search_documents", "arguments": {"query": "sales data"}}

CRITICAL:
- If a tool is needed → return ONLY the JSON, no explanation, no markdown.
- If no tool needed → respond normally.
""" + ("Be concise in your responses unless the user explicitly says 'explain'." if is_voice else "") + """

JSON FORMAT:
{
  "tool": "tool_name",
  "arguments": {"param": "value"}
}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    return run_chat(messages, temperature=0, max_tokens=256).strip()

# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/voice")
def voice_page():
    return render_template("voice.html")

@app.route("/response")
def response_page():
    return render_template("response.html")

# ================== MAIN CHAT ==================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message") if data else None
    is_voice = data.get("is_voice", False) if data else False

    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    if "history" not in session:
        session["history"] = []

    try:
        # ===== Agent decision =====
        decision = agent_decide(user_message, session["history"], is_voice)
        with open("debug.log", "a") as f:
            f.write(f"User: {user_message}\nDecision: {decision}\n\n")
        print("Agent decision:", decision)

        # Pretty print decision if it's JSON
        try:
            if decision.strip().startswith(('{', '[')):
                decision_json = json.loads(decision)
                decision = json.dumps(decision_json, indent=2)
        except json.JSONDecodeError:
            pass  # Keep as is if not valid JSON

        reply = None

        # ===== Tool execution =====
        try:
            plan = agent_plan(user_message)
            clean_plan = extract_json(plan)
            steps = json.loads(clean_plan)

            if isinstance(steps, list):
                final_output = ""

                for step in steps:
                    tool_name = step.get("tool")
                    args = step.get("arguments", {})

                    if tool_name in TOOLS:
                        result = TOOLS[tool_name](**args)
                        final_output += result + "\n"

                return jsonify({"reply": final_output})

        except Exception as e:
            print("Planner error:", e)
                
            if tool_name in TOOLS:
                    # Process arguments
                    if tool_name == "create_meeting":
                        if "date" in args and args["date"].lower() == "tomorrow":
                            from datetime import datetime, timedelta
                            tomorrow = datetime.now() + timedelta(days=1)
                            args["date"] = tomorrow.strftime("%Y-%m-%d")
                        if "participants" in args and isinstance(args["participants"], list):
                            args["participants"] = ", ".join(args["participants"])

                    tool_result = TOOLS[tool_name](**args)
                    reply = clean_text(tool_result)

                    session["history"].append(
                        {"role": "user", "content": user_message}
                    )
                    session["history"].append(
                        {"role": "assistant", "content": tool_result}
                    )
                    session.modified = True

        except Exception as e:
            print("No tool used:", e)

        if reply is None:
            # ===== Normal chat =====
            session["history"].append(
                {"role": "user", "content": user_message}
            )

            ai_reply = run_chat(session["history"], temperature=0.7, max_tokens=512 if is_voice else 1024)
            reply = clean_text(ai_reply)

            session["history"].append(
                {"role": "assistant", "content": ai_reply}
            )
            session.modified = True

        return jsonify({"decision": decision, "reply": reply})

    except Exception as e:
        print("Groq ERROR:", e)
        return jsonify({"reply": str(e)})

def agent_plan(user_message):
    prompt = f"""
You are an autonomous AI agent.

Break the user request into steps.

Return ONLY JSON like:
[
  {{"tool": "tool_name", "arguments": {{}}}},
  {{"tool": "tool_name", "arguments": {{}}}}
]

User request:
{user_message}
"""

    response = run_chat([
        {"role": "user", "content": prompt}
    ], temperature=0)

    return response
    

# ================== RUN ==================
if __name__ == "__main__":
    app.run(debug=True)