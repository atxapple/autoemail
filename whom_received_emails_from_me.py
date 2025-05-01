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
    f"?$top=20000&$select=toRecipients,ccRecipients,bccRecipients"
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

# Output
print(f"\n✅ Found {len(all_recipients)} unique recipient(s):\n")
for email in sorted(all_recipients):
    print(f"📧 {email}")


output_path = "sent_recipients.txt"
with open(output_path, "w", encoding="utf-8") as f:
    for email in sorted(all_recipients):
        f.write(email + "\n")

print(f"\n📁 Saved {len(all_recipients)} unique email(s) to: {output_path}")
