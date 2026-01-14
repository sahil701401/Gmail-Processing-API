from flask import Flask, render_template, request, redirect, url_for, flash
import threading
from src.main import main as run_automation
from src.gmail_client import get_unread_email_ids, extract_email_data
from src.gmail_service import authenticate_gmail
from src.sheets_service import authenticate_sheets, append_email_to_sheet
from src.config import SPREADSHEET_ID

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure key

@app.route('/')
def index():
    try:
        gmail_service = authenticate_gmail()
        unread_ids = get_unread_email_ids()
        emails = []
        for message_id in unread_ids:
            message = gmail_service.users().messages().get(userId='me', id=message_id).execute()
            email_data = extract_email_data(message)
            emails.append({
                'id': message_id,
                'sender': email_data['sender'],
                'subject': email_data['subject'],
                'received_at': email_data['received_at'],
                'body': email_data['body'][:100] + '...' if len(email_data['body']) > 100 else email_data['body']
            })
        return render_template('index.html', emails=emails)
    except Exception as e:
        flash(f"Error fetching emails: {str(e)}")
        return render_template('index.html', emails=[])

@app.route('/run_automation', methods=['POST'])
def run_automation_route():
    selected_emails = request.form.getlist('selected_emails')
    if not selected_emails:
        flash("No emails selected for automation.")
        return redirect(url_for('index'))
    
    # Run the automation in a separate thread to avoid blocking
    thread = threading.Thread(target=run_automation)
    thread.start()
    flash("Email automation started successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
