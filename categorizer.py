
# ---------------------------
# 📄 categorizer.py
# ---------------------------
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def categorize_email(subject: str, body: str) -> str:
    prompt = f"""
You are an assistant that determine if the given business email requests a meeting or not.
Read the email below and return a JSON with:
- meeting-request (Yes or No)
- sender email address
- one-short-sentence summary

Example JSON output: {{"meeting_request": "Yes", "sender_email": "john.doe@example.com", "summary": "Meeting request: Project kickoff"}}

Email Subject: {subject}
Email Body: {body[:3000]}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful email analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

