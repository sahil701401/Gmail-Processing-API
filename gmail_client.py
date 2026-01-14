"""
Handles Gmail API interactions.
Responsibilities:
- Authenticate with Gmail API
- Fetch unread emails
- Mark emails as read
"""

import base64
import json
import os
from src.gmail_service import authenticate_gmail

def get_unread_email_ids():
    """
    Fetches message IDs of unread emails from the INBOX.

    This function authenticates with the Gmail API, queries for unread messages
    in the INBOX label, and returns a list of message IDs. These IDs can be used
    for further processing, such as fetching full message details or marking as read.

    Returns:
        list: A list of message IDs (strings) for unread emails in the INBOX.
              Returns an empty list if no unread emails are found.

    Note:
        This is a simple implementation for small automation scripts.
        For large volumes of emails, consider handling pagination.
    """
    # Authenticate and get the Gmail service object
    service = authenticate_gmail()

    # Query Gmail API for unread messages in INBOX
    # 'q' parameter uses Gmail search syntax: 'is:unread in:inbox'
    results = service.users().messages().list(userId='me', q='is:unread in:inbox').execute()

    # Extract messages from the response
    messages = results.get('messages', [])

    # Return list of message IDs
    message_ids = [msg['id'] for msg in messages]
    return message_ids

def extract_email_data(message):
    """
    Extracts key data from a full Gmail message object.

    This function parses the Gmail API message response to extract sender email,
    subject, received date and time, and plain text body. It handles both simple
    and multipart emails by recursively searching for the plain text part.

    Args:
        message (dict): Full Gmail message object from API response.

    Returns:
        dict: Extracted data with keys 'sender', 'subject', 'received_at', 'body'.
              Values are strings or None if not found.
    """
    # Initialize extracted data
    extracted = {
        'sender': None,
        'subject': None,
        'received_at': None,
        'body': None
    }

    # Extract headers
    headers = message.get('payload', {}).get('headers', [])
    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')

        if name == 'from':
            # Extract email from 'From' header (e.g., "Name <email@example.com>")
            import re
            email_match = re.search(r'<([^>]+)>', value)
            if email_match:
                extracted['sender'] = email_match.group(1)
            else:
                extracted['sender'] = value  # Fallback if no angle brackets
        elif name == 'subject':
            extracted['subject'] = value
        elif name == 'date':
            extracted['received_at'] = value

    # Extract body (plain text)
    payload = message.get('payload', {})
    extracted['body'] = _get_plain_text_body(payload)

    return extracted

def _get_plain_text_body(payload):
    """
    Recursively extracts plain text body from message payload.

    Handles simple and multipart emails by searching for 'text/plain' parts.

    Args:
        payload (dict): Message payload from Gmail API.

    Returns:
        str: Plain text body or empty string if not found.
    """
    mime_type = payload.get('mimeType', '')

    if mime_type == 'text/plain':
        # Simple plain text email
        data = payload.get('body', {}).get('data', '')
        if data:
            # Decode base64url encoded data
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        return ''

    elif mime_type.startswith('multipart/'):
        # Multipart email, search parts recursively
        parts = payload.get('parts', [])
        for part in parts:
            body = _get_plain_text_body(part)
            if body:
                return body
        return ''

    else:
        # Other types (e.g., HTML only), return empty for plain text
        return ''

def load_processed_ids():
    """
    Loads the set of processed message IDs from the JSON file.

    Returns:
        set: Set of processed message IDs. Empty set if file doesn't exist or is corrupted.
    """
    try:
        if os.path.exists('processed_emails.json'):
            with open('processed_emails.json', 'r') as f:
                data = json.load(f)
                return set(data.get('processed_ids', []))
    except (json.JSONDecodeError, KeyError):
        pass  # Return empty set on error
    return set()

def save_processed_ids(processed_ids):
    """
    Saves the set of processed message IDs to the JSON file.

    Args:
        processed_ids (set): Set of message IDs to save.
    """
    data = {'processed_ids': list(processed_ids)}
    with open('processed_emails.json', 'w') as f:
        json.dump(data, f, indent=2)

def mark_email_as_read(service, message_id):
    """
    Marks a Gmail message as read by removing the 'UNREAD' label.

    Args:
        service: Gmail API service object.
        message_id (str): The ID of the message to mark as read.

    Returns:
        dict: API response from the modify request.
    """
    # Modify the message to remove 'UNREAD' label
    result = service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()
    return result

# Example usage (uncomment to test):
# if __name__ == '__main__':
#     # Assuming you have a message ID
#     service = authenticate_gmail()
#     message = service.users().messages().get(userId='me', id='MESSAGE_ID_HERE').execute()
#     data = extract_email_data(message)
#     print(f"Sender: {data['sender']}")
#     print(f"Subject: {data['subject']}")
#     print(f"Received: {data['received_at']}")
#     print(f"Body: {data['body'][:100]}...")  # First 100 chars
