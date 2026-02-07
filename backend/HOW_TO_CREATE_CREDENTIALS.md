# How to Create credentials.json (Step-by-Step)

## You're on the right page! Here's what to do:

### Step 1: Copy Client ID ✅
**Status**: DONE! (I see "Client ID copied to clipboard")

The Client ID is already in your clipboard. Save it somewhere temporarily (like Notepad).

### Step 2: Reveal and Copy Client Secret

1. In the Google Cloud Console (where you are now)
2. Look at the "Client secret" row
3. You see: `****2pQ_`
4. **Click on it** or look for a "Show" button
5. Copy the full secret (it will be longer than what's shown)

### Step 3: Run the Helper Script

I've created a script to help you. Run this:

```bash
cd c:\Desktop\tracers\backend
python create_credentials.py
```

It will ask you to paste:
1. Your Client ID (paste what you copied)
2. Your Client Secret (paste after revealing it)

And it will create `credentials.json` for you!

---

## Alternative: Create Manually

If you prefer to create it manually, here's the template:

1. Create a new file: `c:\Desktop\tracers\backend\credentials.json`

2. Paste this content:

```json
{
  "web": {
    "client_id": "PASTE_YOUR_CLIENT_ID_HERE",
    "project_id": "tracers-calendar",
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

3. Replace:
   - `PASTE_YOUR_CLIENT_ID_HERE` → Your actual Client ID (from clipboard)
   - `PASTE_YOUR_CLIENT_SECRET_HERE` → Your actual Client Secret (after revealing)

---

## How to Reveal Client Secret

In the Google Cloud Console screenshot you showed:

1. Find the "Client secret" row
2. It shows: `****2pQ_`
3. **Options to reveal it**:
   - Click directly on `****2pQ_`
   - Look for an "eye" icon 👁️ next to it
   - Look for a "Show" button
   - Right-click and select "Reveal"

Once revealed, it will show the full secret (probably 20-30 characters).

---

## Quick Test

After creating credentials.json, test it:

```bash
cd c:\Desktop\tracers\backend
python -c "import json; print(json.load(open('credentials.json')))"
```

You should see your credentials printed (without errors).

---

## What You Have So Far

✅ Client ID - Copied to clipboard
✅ Redirect URIs - Already configured (localhost:5173, 3000, 8000/docs)
❓ Client Secret - Need to reveal and copy

**Just one more step: Reveal that client secret and you're done!**
