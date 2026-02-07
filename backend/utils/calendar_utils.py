import os
import datetime
import pickle
import json
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pypdf import PdfReader
import re

# Use the new LLM service for intelligent parsing
from utils.llm import get_llm

CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_auth_url(redirect_uri):
    """Generate the Google OAuth URL."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Credentials file '{CREDENTIALS_FILE}' not found.")

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

def get_credentials_from_code(code, redirect_uri):
    """Exchange auth code for credentials."""
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    
    flow.fetch_token(code=code)
    return flow.credentials

def extract_text_from_file(file_content, filename):
    """
    Extract text content from uploaded file (PDF or TXT).
    """
    text = ""
    if filename.lower().endswith('.pdf'):
        from io import BytesIO
        pdf_file = BytesIO(file_content)
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    else:
        # Assume text
        text = file_content.decode('utf-8', errors='ignore')
    
    return text

def parse_events_with_llm(text_content):
    """
    Use local LLM to extract calendar events from text.
    """
    llm = get_llm()
    
    # Prompt for the LLM
    prompt = f"""
    Extract academic calendar events from the following text.
    Return a list of JSON objects with 'summary' (event name), 'start_date' (YYYY-MM-DD), and 'end_date' (YYYY-MM-DD, optional).
    Handle date ranges if present. Assume current academic year (2024-2025) if year is missing.
    Only include significant academic events (exams, holidays, deadlines).
    
    Text:
    {text_content[:2000]}  # Limit text to avoid context window issues
    
    Output format:
    [
        {{"summary": "Mid-Semester Exams", "start_date": "2024-10-15", "end_date": "2024-10-20"}},
        ...
    ]
    """
    
    # Generate response
    response = llm.generate(prompt, max_new_tokens=500, temperature=0.1)
    
    # Parse JSON from response
    try:
        # Find JSON array in response
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            json_str = match.group(0)
            events = json.loads(json_str)
            return events
    except Exception as e:
        print(f"LLM parsing failed: {e}")
    
    # Fallback to regex if LLM fails
    return parse_events_regex(text_content)

def parse_events_regex(text):
    """
    Fallback regex parser for simple date formats.
    """
    events = []
    # Pattern: Date (e.g., 15 Oct, Oct 15, 2024-10-15) - Event Name
    # This is a very basic heuristic
    lines = text.split('\n')
    for line in lines:
        if len(line.strip()) < 5:
            continue
            
        # Try finding a date
        # Example support: "Oct 15: Mid Sem"
        match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})', line, re.IGNORECASE)
        if match:
            month = match.group(1)
            day = match.group(2)
            summary = line.replace(match.group(0), '').strip(' :-')
            
            # Convert to date string (assume 2024 for now)
            try:
                date_str = datetime.datetime.strptime(f"{month} {day} 2024", "%b %d %Y").strftime("%Y-%m-%d")
                events.append({
                    "summary": summary,
                    "start_date": date_str
                })
            except:
                pass
                
    return events

def sync_events_to_google(credentials, events):
    """
    Add list of events to Google Calendar.
    """
    service = build('calendar', 'v3', credentials=credentials)
    
    created_events = []
    errors = []
    
    for event in events:
        try:
            start_date = event.get('start_date')
            end_date = event.get('end_date', start_date)
            summary = event.get('summary', 'Academic Event')
            
            # Create event body
            event_body = {
                'summary': summary,
                'start': {
                    'date': start_date,
                    'timeZone': 'UTC',
                },
                'end': {
                    'date': end_date, # For all-day events, end date is exclusive (next day)
                    'timeZone': 'UTC',
                },
            }
            
            created_event = service.events().insert(calendarId='primary', body=event_body).execute()
            created_events.append({
                'id': created_event['id'],
                'summary': summary,
                'start': start_date,
                'link': created_event.get('htmlLink')
            })
            
        except Exception as e:
            errors.append(f"Failed to add '{summary}': {str(e)}")
            
    return {
        "success_count": len(created_events),
        "error_count": len(errors),
        "created_events_details": created_events,
        "errors": errors
    }
