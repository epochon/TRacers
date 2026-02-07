from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from utils.calendar_utils import (
    get_auth_url,
    get_credentials_from_code,
    extract_text_from_file,
    parse_events_with_llm,
    sync_events_to_google
)
import traceback

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])

@router.get("/auth-url")
async def get_google_auth_url(redirect_uri: str):
    """
    Get the Google OAuth authorization URL.
    Frontend redirects user here to start flow.
    """
    try:
        url = get_auth_url(redirect_uri)
        return {"auth_url": url}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Credentials file missing. Please configure credentials.json.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_calendar(
    file: UploadFile = File(...),
    code: str = Form(...),
    redirect_uri: str = Form(...)
):
    """
    Sync calendar events from uploaded file to Google Calendar.
    Current flow:
    1. Frontend gets auth URL -> User approves -> Frontend gets code
    2. Frontend sends code + file here
    3. Backend exchanges code for token -> Parse file -> Sync events
    """
    try:
        print(f"Syncing calendar file: {file.filename}")
        
        # 1. Exchange auth code for credentials
        credentials = get_credentials_from_code(code, redirect_uri)
        
        # 2. Read and extract text from file
        content = await file.read()
        text_content = extract_text_from_file(content, file.filename)
        
        if not text_content:
             return {"message": "No text content found in file", "details": {"success_count": 0}}

        # 3. Parse events using LLM (smart parsing)
        # Note: This might take a few seconds
        print("Parsing events with LLM...")
        events = parse_events_with_llm(text_content)
        
        print(f"Found {len(events)} events")
        
        # 4. Sync to Google Calendar
        result = sync_events_to_google(credentials, events)
        
        return {
            "message": "Sync complete",
            "details": result,
            "parsed_events_count": len(events)
        }

    except Exception as e:
        print(f"Calendar sync error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
