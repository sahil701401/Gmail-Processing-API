"""
Main script to orchestrate the email processing workflow.
Responsibilities:
- Load configurations
- Fetch unread emails
- Process and store email data
- Handle errors and logging
"""

# Hey there! Let's bring in the tools we need to chat with Gmail and Google Sheets.
# These imports are like our trusty sidekicks for handling emails and spreadsheets.
import logging
from src.gmail_client import (
    get_unread_email_ids,  # Grabs the IDs of emails we haven't read yet
    extract_email_data,    # Pulls out the juicy details from an email
    load_processed_ids,    # Remembers which emails we've already handled
    save_processed_ids,    # Saves that memory for next time
    mark_email_as_read     # Marks an email as read, like checking it off our list
)
from src.gmail_service import authenticate_gmail  # Gets us logged into Gmail securely
from src.sheets_service import authenticate_sheets, append_email_to_sheet  # Logs into Sheets and adds rows
from src.config import SPREADSHEET_ID  # Our special sheet ID where we store the data

# Alright, let's set up some logging so we can keep track of what's happening.
# Think of this as our diary for the script – it'll tell us if things go smoothly or if there's a hiccup.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to process unread emails and append data to Google Sheets.

    Workflow:
    1. Load previously processed message IDs
    2. Authenticate with Gmail and Sheets APIs
    3. Get unread email IDs from INBOX
    4. For each unread email:
       - Skip if already processed
       - Fetch full message
       - Extract data (sender, subject, date, body)
       - Append to Google Sheet
       - Mark as read
       - Add to processed IDs
    5. Save updated processed IDs
    """
    logging.info("Starting email processing script...")

    # Alright, first things first – let's load up the IDs of emails we've already handled so we don't process them again.
    try:
        processed_ids = load_processed_ids()
        logging.info(f"Loaded {len(processed_ids)} previously processed message IDs.")
    except Exception as e:
        logging.error(f"Failed to load processed IDs: {e}")
        return  # If we can't remember what we've done, better to stop here!

    # Next up, we need to log in to Gmail and Google Sheets securely – think of it as getting our VIP passes.
    try:
        gmail_service = authenticate_gmail()
        sheets_service = authenticate_sheets()
        logging.info("Authenticated with Gmail and Google Sheets APIs.")
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        return  # Can't proceed without access, so we'll bail out.

    # Now, let's check out what unread emails are waiting in our inbox.
    try:
        unread_ids = get_unread_email_ids()
        logging.info(f"Found {len(unread_ids)} unread emails in INBOX.")
        if not unread_ids:
            logging.info("No unread emails to process.")
            return  # Nothing to do? Cool, we're done!
    except Exception as e:
        logging.error(f"Failed to get unread emails: {e}")
        return  # Oops, couldn't fetch emails, time to exit.

    # Time to dive into each unread email and give it some love!
    processed_count = 0
    for message_id in unread_ids:
        if message_id in processed_ids:
            logging.info(f"Skipping already processed email: {message_id}")
            continue  # We've already handled this one, moving on!

        try:
            # Let's grab the full email details from Gmail.
            message = gmail_service.users().messages().get(userId='me', id=message_id).execute()

            # Now, pull out the key info like sender, subject, etc.
            email_data = extract_email_data(message)

            # Just in case something went wrong and we got no data, skip this email.
            if not any(email_data.values()):
                logging.warning(f"No data extracted from email {message_id}, skipping.")
                continue

            # Get ready to add this to our Google Sheet – format it nicely!
            row = [
                email_data['sender'] or 'Unknown',
                email_data['subject'] or 'No Subject',
                email_data['received_at'] or 'Unknown Date',
                email_data['body'] or 'No Body'
            ]

            # Pop it into the spreadsheet!
            append_email_to_sheet(sheets_service, SPREADSHEET_ID, row)
            logging.info(f"Appended email from {row[0]} to Google Sheet.")

            # Mark it as read so we don't see it again.
            mark_email_as_read(gmail_service, message_id)
            logging.info(f"Marked email {message_id} as read.")

            # Remember we processed this one.
            processed_ids.add(message_id)
            processed_count += 1

        except Exception as e:
            logging.error(f"Error processing email {message_id}: {e}")
            # If something goes wrong, just skip and try the next one.

    # Finally, let's save our updated list of processed emails for next time.
    try:
        save_processed_ids(processed_ids)
        logging.info(f"Saved {len(processed_ids)} processed message IDs. Processed {processed_count} new emails.")
    except Exception as e:
        logging.error(f"Failed to save processed IDs: {e}")
            
    logging.info("Email processing script completed.")

if __name__ == '__main__':
    main()
