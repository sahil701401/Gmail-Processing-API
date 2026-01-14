# Gmail to Google Sheets Automation

Hey there! This is my little automation project I built for the company assignment. Basically, it's a Python script that automatically grabs unread emails from your Gmail inbox, pulls out the important stuff (like who sent it, the subject, when it was received, and the body), and sticks it all into a Google Sheet. Then it marks those emails as read so you don't have to deal with them again. Pretty cool, right?

## What This Project Does

I wanted to create something that could help automate email processing without having to manually check and copy-paste stuff. The script:
- Connects to Gmail and Google Sheets using their APIs
- Finds all unread emails in your inbox
- Extracts key info from each email
- Adds that info as a new row in a Google Sheet
- Marks the emails as read
- Remembers which emails it's already processed so it doesn't duplicate work

It's super simple but gets the job done for basic email automation.

## Setup Instructions

Alright, let's get this thing running. I tried to make the setup as straightforward as possible, but there are a few steps since we're dealing with Google APIs.

### Step 1: Get Your Dependencies
First, install the required Python packages. I used pip for this:

```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### Step 2: Set Up Google Cloud Project
This was the trickiest part for me. You need to create a project in Google Cloud Console:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable the Gmail API and Google Sheets API for your project
4. Create credentials (OAuth 2.0 Client ID) - download the JSON file
5. Put that JSON file in a `credentials/` folder in your project root and rename it to `credentials.json`

### Step 3: Create Your Google Sheet
1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet
2. Copy the spreadsheet ID from the URL (it's the long string between `/d/` and `/edit`)
3. Open `src/config.py` and replace `YOUR_SPREADSHEET_ID_HERE` with your actual ID

### Step 4: Run the Script
That's it! Now you can run:

```bash
python src/main.py
```

The first time you run it, it'll open a browser window for you to log in and grant permissions. After that, it should work automatically.

## How OAuth Works (The Login Stuff)

OAuth was confusing at first, but it's actually pretty clever. Instead of giving my script your Gmail password (which would be super insecure), Google lets you grant specific permissions through their system.

Here's what happens:
1. The script tries to load saved login info from `token.pickle`
2. If there's no saved info, it opens your browser and takes you to Google's login page
3. You log in and Google asks if you want to let this app read your emails and write to Sheets
4. If you say yes, Google gives the script a special token that proves it has permission
5. The script saves this token so it doesn't need to ask again

The cool part is that the token expires, but Google automatically refreshes it behind the scenes. So once you set it up, it just works.

## Preventing Duplicates

I didn't want the script to keep processing the same emails over and over, so I added a simple tracking system:

- Before processing any emails, it loads a list of message IDs it's already handled from `processed_emails.json`
- For each unread email, it checks if the ID is already in that list
- If it is, it skips it
- If not, it processes it and adds the ID to the list
- At the end, it saves the updated list back to the file

This way, even if you run the script multiple times, it won't create duplicate rows in your sheet.

## Limitations and What I Learned

This project taught me a lot about APIs and error handling, but it's not perfect. Here are some limitations:

- **Only works with Gmail**: If you use another email service, you're out of luck
- **No fancy email parsing**: It just grabs basic text content. HTML emails or attachments aren't handled
- **Rate limits**: Google limits how many API calls you can make per minute. If you have tons of emails, it might hit those limits
- **No scheduling**: You have to run it manually. For real automation, you'd need to set up a cron job or something
- **Simple error handling**: If something goes wrong with one email, it just logs it and moves on, but it might miss important stuff
- **Security**: You're trusting the script with your email access, so be careful!

Overall, I'm pretty happy with how it turned out. It was a great way to learn about OAuth, API integration, and Python file handling. If I were to improve it, I'd add better email parsing and maybe some scheduling features.
