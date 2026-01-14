"""
Google Sheets Service Module for OAuth 2.0 Authentication

This module handles user-based OAuth 2.0 authentication for the Google Sheets API,
enabling secure access to Google Sheets for appending rows to existing spreadsheets.
It uses token reuse to persist authentication state.

Key Features:
- User-based OAuth (interactive login flow)
- Token persistence for reuse
- Returns a Google Sheets API service object for appending rows

Dependencies: google-api-python-client, google-auth-oauthlib, google-auth-httplib2
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes for Google Sheets API access
# SCOPES: List of permissions the app requests from the user
# 'https://www.googleapis.com/auth/spreadsheets' allows reading and writing to spreadsheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def authenticate_sheets():
    """
    Authenticates with Google Sheets API using OAuth 2.0 and returns a service object.

    This function handles the entire authentication flow:
    1. Loads existing credentials if available
    2. Refreshes expired tokens
    3. Initiates new login if no valid credentials exist
    4. Builds and returns the Google Sheets API service

    Returns:
        googleapiclient.discovery.Resource: Google Sheets API service object for making API calls

    Raises:
        FileNotFoundError: If credentials.json is missing
        Exception: For other authentication errors
    """
    creds = None

    # Step 1: Check for existing token file
    # This allows reusing authentication without re-login
    # token_sheets.pickle stores the user's access and refresh tokens securely
    token_file = 'token_sheets.pickle'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
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
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    # Step 5: Build the Google Sheets API service object
    # This service object is used to make actual API calls (e.g., append rows to spreadsheets)
    # Version 'v4' is the current stable version of Google Sheets API
    service = build('sheets', 'v4', credentials=creds)

    return service

def append_email_to_sheet(service, spreadsheet_id, email_data):
    """
    Appends a row of email data to a Google Sheet.

    This function takes a list of email data [sender, subject, date, body] and appends
    it as a new row to the specified Google Sheet. It does not overwrite existing rows;
    instead, it adds to the end of the sheet.

    Args:
        service: Google Sheets API service object from authenticate_sheets()
        spreadsheet_id (str): The ID of the Google Sheet (from the URL)
        email_data (list): List of [sender, subject, date, body]

    Returns:
        dict: Response from the API with update details

    Raises:
        Exception: For API errors
    """
    # Prepare the data as a 2D list (one row)
    values = [email_data]

    # Define the range to append to (e.g., 'Sheet1' appends to the next available row)
    range_name = 'Sheet1'

    # Body for the append request
    body = {
        'values': values
    }

    # Append the row
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',  # 'RAW' inserts data as-is, 'USER_ENTERED' parses formulas
        body=body
    ).execute()

    return result

# Example usage (uncomment to test):
# if __name__ == '__main__':
#     sheets_service = authenticate_sheets()
#     print("Google Sheets service authenticated successfully!")
#     # Example email data
#     email_row = ['sender@example.com', 'Test Subject', '2023-10-01', 'Email body text']
#     # Replace 'YOUR_SPREADSHEET_ID' with actual ID
#     response = append_email_to_sheet(sheets_service, 'YOUR_SPREADSHEET_ID', email_row)
#     print(f"Appended row: {response}")
