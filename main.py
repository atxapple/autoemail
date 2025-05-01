
# ---------------------------
# 📄 main.py
# ---------------------------
from email_client import get_access_token, fetch_unread_emails
from html_cleaner import extract_text_from_html
from categorizer import categorize_email
from email_client import reply_to_email


print("🔑 Authenticating...")
access_token = get_access_token()
print("✅ Access token acquired.")

print("📥 Fetching unread emails...")
emails = fetch_unread_emails(access_token)
print(f"📬 Found {len(emails)} unread email(s):\n")

for email in emails:
    sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
    subject = email.get("subject", "[No Subject]")
    body_html = email.get("body", {}).get("content", "")
    body_text = extract_text_from_html(body_html)

    print(f"From: {sender}")
    print(f"Subject: {subject}")
    print("-" * 50)

    print(f"🔍 Categorizing...")
    result = categorize_email(subject, body_text)
    print(result)
    print("=" * 60)

    # Assuming categorization result contains a "meeting_request" field
    if '"meeting_request": "Yes"' in result:
        reply_text = f"Indeed, I am interested in a meeting. Can you please arrange a meeting through my DonaTalk page? \n https://app.donatalk.com/listener/W4onxwz4OOUymoNbhGW9i6trAe83 \n I found that a small commitment makes meetings more meaningful. \n Thanks. \n\n  \n -Mok-"
        reply_to_email(access_token, email["id"], reply_text)





