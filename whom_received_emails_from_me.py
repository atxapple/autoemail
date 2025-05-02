import os
from dotenv import load_dotenv
import requests
from msal import ConfidentialClientApplication

# Load environment variables
load_dotenv()

# Load credentials from .env
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
user_email = os.getenv("USER_EMAIL")
exclusion_emails = os.getenv("SENT_RECIPIENTS_EMAIL_LISTS")
authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = ["https://graph.microsoft.com/.default"]

# Authenticate with Microsoft Graph
app = ConfidentialClientApplication(
    client_id=client_id,
    authority=authority,
    client_credential=client_secret
)

result = app.acquire_token_for_client(scopes=scope)

if "access_token" not in result:
    print("❌ Failed to acquire token:", result.get("error_description"))
    exit(1)

access_token = result["access_token"]
print("✅ Access token acquired.")
print("📤 Fetching sent emails...")

# Request sent emails
url = (
    f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/SentItems/messages"
    f"?$top=100&$select=toRecipients,ccRecipients,bccRecipients"
)

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("❌ Failed to fetch sent emails:", response.text)
    exit(1)

sent_emails = response.json().get("value", [])

# Extract recipients
def extract_addresses(recipients):
    return [r["emailAddress"]["address"] for r in recipients or []]

all_recipients = set()

for msg in sent_emails:
    to = extract_addresses(msg.get("toRecipients"))
    cc = extract_addresses(msg.get("ccRecipients"))
    bcc = extract_addresses(msg.get("bccRecipients"))
    all_recipients.update(to + cc + bcc)

print(f"\n📥 Found {len(all_recipients)} total unique recipient(s).")

# Load existing emails
sent_file = exclusion_emails
if os.path.exists(sent_file):
    with open(sent_file, "r", encoding="utf-8") as f:
        existing_recipients = set(line.strip().lower() for line in f if line.strip())
else:
    existing_recipients = set()

# Identify new recipients
new_recipients = sorted(email for email in all_recipients if email.lower() not in existing_recipients)

# Append only new recipients
with open(sent_file, "a", encoding="utf-8") as f:
    for email in new_recipients:
        f.write(email + "\n")

print(f"🆕 Added {len(new_recipients)} new email(s) to '{sent_file}'.")
