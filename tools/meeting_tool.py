from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# =========================
# 🧠 SUMMARIZE MEETING
# =========================
def summarize_meeting(text: str) -> str:
    prompt = f"""
Summarize the meeting clearly.

Also extract action items.

Return format:

Summary:
- ...

Action Items:
- Person → Task
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content


# =========================
# 📧 EMAIL SUMMARY
# =========================
def email_meeting_summary(to: str, meeting_text: str) -> str:
    summary = summarize_meeting(meeting_text)

    subject = "Meeting Summary & Action Items"

    body = f"""
Hello,

Here is the summary of the meeting:

{summary}

Regards,
AI Assistant
"""

    from tools.email_tool import send_email
    return send_email(to, subject, body)