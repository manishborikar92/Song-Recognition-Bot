from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Path to client secrets file
CLIENT_SECRETS_FILE = "client_secrets.json"

# Scopes for YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# Initialize the OAuth flow
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)

# Run the flow locally to obtain credentials
credentials = flow.run_local_server(port=8080)

# Save credentials to oauth.json
with open("oauth.json", "w") as token:
    json.dump({
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }, token)

print("OAuth token saved to oauth.json")
