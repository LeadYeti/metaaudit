import os
from dotenv import load_dotenv

load_dotenv()

META_APP_ID = os.environ["META_APP_ID"]
META_APP_SECRET = os.environ["META_APP_SECRET"]
GHL_WEBHOOK_URL_LEAD = os.environ.get("GHL_WEBHOOK_URL_LEAD", "")
GHL_WEBHOOK_URL_AUDIT = os.environ.get("GHL_WEBHOOK_URL_AUDIT", "")
SESSION_SECRET = os.environ["SESSION_SECRET"]
APP_URL = os.environ.get("APP_URL", "http://localhost:8000")
GHL_CALENDAR_URL = os.environ.get("GHL_CALENDAR_URL", "")

OAUTH_REDIRECT_URI = f"{APP_URL}/auth/callback"
FACEBOOK_AUTH_URL = "https://www.facebook.com/v21.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v21.0/oauth/access_token"
FACEBOOK_GRAPH_URL = "https://graph.facebook.com/v21.0"

OAUTH_SCOPES = "email,public_profile,ads_read,read_insights,business_management"
