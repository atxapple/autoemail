
# ---------------------------
# 📄 main.py
# ---------------------------
from email_client import get_access_token, fetch_unread_emails
from html_cleaner import extract_text_from_html
from categorizer import categorize_email
from email_client import reply_to_email

import os
from dotenv import load_dotenv

load_dotenv()
user_email = os.getenv("USER_EMAIL")
exclusion_emails = os.getenv("SENT_RECIPIENTS_EMAIL_LISTS")
donatalk_url = os.getenv("DONATALK_URL")

def load_sent_recipient_emails(filepath=exclusion_emails) -> set:
    with open(filepath, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())



# 📨 Load historical email recipients
sent_recipients = load_sent_recipient_emails()


print("🔑 Authenticating...")
access_token = get_access_token()
print("✅ Access token acquired.")

print("📥 Fetching unread emails...")

urls = [
    # f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/Inbox/messages?$filter=isRead eq false&$top=100&$select=subject,body,bodyPreview,from",
    f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/JunkEmail/messages?$filter=isRead eq false&$top=100&$select=subject,body,bodyPreview,from"
]

for url in urls:
    emails = fetch_unread_emails(access_token, url )
    print(f"📬 Found {len(emails)} unread email(s):\n")

    for email in emails:
        sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
        subject = email.get("subject", "[No Subject]")
        body_html = email.get("body", {}).get("content", "")
        body_text = extract_text_from_html(body_html)

        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print("-" * 50)

        # 🔁 Skip if already contacted
        if sender in sent_recipients:
            print("⏩ Skipping known contact.")
            continue

        print(f"🔍 Categorizing...")
        result = categorize_email(subject, body_text)
        print(result)
        print("=" * 60)

        if '"meeting_request": "Yes"' in result:
            reply_html = f"""
                <p>Hi, I am interested in a meeting.</p>
                <p></p>
                <p>If you think the meeting would be beneficial for both of us, could you please arrange a time through my DonaTalk page? </p>
                <p><a href="{donatalk_url}" target="_blank">{donatalk_url}</a></p>
                <p>I found that a small commitment often makes a meeting more meaningful.</p>
                <p>Thanks.</p>
                <p></p>
                <p>-Mok-</p>
            """
            reply_to_email(access_token, email["id"], reply_html)