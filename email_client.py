
# ---------------------------
# 📄 email_client.py
# ---------------------------
import os
import requests
from dotenv import load_dotenv
from msal import ConfidentialClientApplication

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = ["https://graph.microsoft.com/.default"]
user_email = os.getenv("USER_EMAIL")

def get_access_token():
    app = ConfidentialClientApplication(
        client_id=client_id,
        authority=authority,
        client_credential=client_secret
    )
    result = app.acquire_token_for_client(scopes=scope)
    if "access_token" not in result:
        raise RuntimeError("Failed to acquire token: " + result.get("error_description", ""))
    return result["access_token"]

def fetch_unread_emails(access_token, url):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError("Failed to fetch emails: " + response.text)
    return response.json().get("value", [])
def reply_to_email(access_token, message_id, html_reply_body):
    user_email = os.getenv("USER_EMAIL")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Create the reply draft
    draft_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}/createReply"
    create_resp = requests.post(draft_url, headers=headers)
    if create_resp.status_code != 201:
        raise RuntimeError(f"❌ Failed to create reply draft: {create_resp.text}")
    draft = create_resp.json()
    draft_id = draft["id"]

    # Step 2: Get original draft body (includes quoted thread)
    original_body = draft.get("body", {}).get("content", "")

    # Step 3: Combine your HTML with original email content
    full_body = f"""
    <div style="font-family:Arial, sans-serif; font-size:14px;">
        {html_reply_body}
        <br><br>
        <hr>
        {original_body}
    </div>
    """

    # Step 4: Update the reply draft with HTML content
    update_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{draft_id}"
    patch_body = {
        "body": {
            "contentType": "HTML",
            "content": full_body
        }
    }
    update_resp = requests.patch(update_url, headers=headers, json=patch_body)
    if update_resp.status_code != 200:
        raise RuntimeError(f"❌ Failed to update reply draft: {update_resp.text}")

    # Step 5: Send the email
    send_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{draft_id}/send"
    send_resp = requests.post(send_url, headers=headers)
    if send_resp.status_code != 202:
        raise RuntimeError(f"❌ Failed to send reply: {send_resp.text}")

    print(f"📤 Replied to message {message_id}")

    # Step 6: Mark the original message as read
    mark_read_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}"
    mark_read_body = {
        "isRead": True
    }
    mark_resp = requests.patch(mark_read_url, headers=headers, json=mark_read_body)
    if mark_resp.status_code != 200:
        raise RuntimeError(f"❌ Failed to mark email as read: {mark_resp.text}")

    print(f"📩 Marked message {message_id} as read.")