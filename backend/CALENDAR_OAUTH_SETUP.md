# Google Calendar OAuth Setup Guide

## Problem: credentials.json was deleted

Don't worry! Here's how to get it back:

---

## Solution 1: Download from Google Cloud Console (Recommended)

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/apis/credentials
2. Select your project (the one you were just in)

### Step 2: Download Credentials
1. Find your OAuth 2.0 Client ID (you were just looking at it)
2. Click on the client name
3. Look for **"Download JSON"** button (top right, near "Delete")
4. Click it to download

### Step 3: Rename and Move
```bash
# The downloaded file might be named something like:
# client_secret_XXXXX.apps.googleusercontent.com.json

# Rename it to credentials.json
# Move it to: c:\Desktop\tracers\backend\credentials.json
```

---

## Solution 2: Create Manually (If download doesn't work)

### Step 1: Get Your Values

From the Google Cloud Console page you're on:

1. **Client ID**: Copy the full client ID (ends with `.apps.googleusercontent.com`)
2. **Client Secret**: Click "Show" next to the masked secret (`****2pQ_`) to reveal it
3. **Project ID**: Should be visible on the page

### Step 2: Create the File

Create `c:\Desktop\tracers\backend\credentials.json`:

```json
{
  "web": {
    "client_id": "PASTE_YOUR_CLIENT_ID_HERE.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "PASTE_YOUR_CLIENT_SECRET_HERE",
    "redirect_uris": [
      "http://localhost:3000",
      "http://localhost:5173",
      "http://localhost:8000/docs"
    ]
  }
}
```

### Step 3: Fill in the Values

Replace:
- `PASTE_YOUR_CLIENT_ID_HERE` with your actual client ID
- `PASTE_YOUR_CLIENT_SECRET_HERE` with your actual client secret (reveal it first)
- `your-project-id` with your Google Cloud project ID

---

## Verify It Works

### Test the Calendar Sync

1. **Start your backend** (if not already running):
   ```bash
   cd c:\Desktop\tracers\backend
   python main.py
   ```

2. **Go to Calendar Sync** in your app:
   - Login as a student
   - Navigate to Calendar Sync feature
   - Click "Authorize with Google"

3. **You should see**:
   - Google OAuth consent screen
   - Request for calendar permissions
   - Redirect back to your app

---

## Important Notes

### ✅ Security
- ✅ `credentials.json` is now in `.gitignore`
- ✅ Won't be committed to git
- ✅ Keep it secret!

### ⚠️ Redirect URIs
Your redirect URIs are already configured:
- `http://localhost:5173` (Vite frontend)
- `http://localhost:3000` (Alternative frontend port)
- `http://localhost:8000/docs` (Backend docs)

These match what you set up in Google Cloud Console.

### 🔄 If You Need to Reset

If something goes wrong:

1. **Delete token.json** (if it exists):
   ```bash
   rm c:\Desktop\tracers\backend\token.json
   ```

2. **Re-authorize** through the app

---

## Common Issues

### Issue: "redirect_uri_mismatch"
**Solution**: Make sure the redirect URI in your app matches what's in Google Cloud Console.

Your current URIs:
- `http://localhost:5173`
- `http://localhost:3000`
- `http://localhost:8000/docs`

### Issue: "invalid_client"
**Solution**: Double-check your client ID and secret are correct.

### Issue: "access_denied"
**Solution**: Make sure you're using the correct Google account and granting calendar permissions.

---

## Quick Reference

**File Location**: `c:\Desktop\tracers\backend\credentials.json`

**Required Scopes** (already configured in your app):
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/calendar.events`

**API Enabled**: Google Calendar API (should already be enabled in your project)

---

## Next Steps After Setup

1. ✅ Download/create `credentials.json`
2. ✅ Place in `backend/` directory
3. ✅ Test calendar sync in app
4. ✅ Upload a calendar file
5. ✅ Verify events sync to Google Calendar

---

**Need Help?**

If you're stuck:
1. Check the backend logs for error messages
2. Verify the file exists: `ls c:\Desktop\tracers\backend\credentials.json`
3. Verify the JSON is valid (no syntax errors)
4. Make sure redirect URIs match in both places

**You're almost there! Just download that credentials.json file and you're good to go! 🚀**
