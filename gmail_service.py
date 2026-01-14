"""
Gmail Service Module for OAuth 2.0 Authentication

This module handles user-based OAuth 2.0 authentication for the Gmail API,
enabling secure access to Gmail data without requiring login on every run.
It uses token reuse to persist authentication state.

Key Features:
- User-based OAuth (interactive login flow)
- Token persistence for reuse
- Returns a Gmail API service object for further operations

Dependencies: google-api-python-client, google-auth-oauthlib, google-auth-httplib2
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes for Gmail API access
# SCOPES: List of permissions the app requests from the user
# 'https://www.googleapis.com/auth/gmail.readonly' allows reading emails but not modifying them
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """
    Authenticates with Gmail API using OAuth 2.0 and returns a service object.

    This function handles the entire authentication flow:
    1. Loads existing credentials if available
    2. Refreshes expired tokens
    3. Initiates new login if no valid credentials exist
    4. Builds and returns the Gmail API service

    Returns:
        googleapiclient.discovery.Resource: Gmail API service object for making API calls

    Raises:
        FileNotFoundError: If credentials.json is missing
        Exception: For other authentication errors
    """
    creds = None

    # Step 1: Check for existing token file
    # This allows reusing authentication without re-login
    # token.pickle stores the user's access and refresh tokens securely
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Step 2: Refresh or re-authenticate if credentials are invalid/expired
    # Credentials can expire, so we check validity and refresh if possible
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token using the refresh token (no user interaction needed)
            creds.refresh(Request())
        else:
            # Step 3: Start new OAuth flow if no valid credentials
            # This requires user interaction: open browser, login, grant permissions
            # credentials.json must be downloaded from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Step 4: Save the credentials for future use
        # This enables token reuse - no login needed on subsequent runs
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Step 5: Build the Gmail API service object
    # This service object is used to make actual API calls (e.g., list messages, get email content)
    # Version 'v1' is the current stable version of Gmail API
    service = build('gmail', 'v1', credentials=creds)

    return service

# Example usage (uncomment to test):
# if __name__ == '__main__':
#     gmail_service = authenticate_gmail()
#     print("Gmail service authenticated successfully!")
#     # Now you can use gmail_service to call Gmail API methods
