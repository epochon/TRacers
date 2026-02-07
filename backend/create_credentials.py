"""
Interactive script to create credentials.json
Run this and paste your Client ID and Client Secret when prompted
"""

import json

print("="*60)
print("Google Calendar credentials.json Creator")
print("="*60)
print()

# Get Client ID
print("Step 1: Paste your Client ID")
print("(It should end with .apps.googleusercontent.com)")
client_id = input("Client ID: ").strip()

# Get Client Secret
print("\nStep 2: Reveal and paste your Client Secret")
print("(Click on ****2pQ_ in Google Console to reveal it)")
client_secret = input("Client Secret: ").strip()

# Get Project ID (optional)
print("\nStep 3: Enter your Project ID (optional, press Enter to skip)")
project_id = input("Project ID: ").strip() or "tracers-calendar"

# Create credentials structure
credentials = {
    "web": {
        "client_id": client_id,
        "project_id": project_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": client_secret,
        "redirect_uris": [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000/docs"
        ]
    }
}

# Save to file
output_file = "credentials.json"
with open(output_file, 'w') as f:
    json.dump(credentials, f, indent=2)

print()
print("="*60)
print(f"✓ SUCCESS! Created {output_file}")
print("="*60)
print()
print("File contents:")
print(json.dumps(credentials, indent=2))
print()
print("Your credentials.json file is ready to use!")
print("Location:", output_file)
