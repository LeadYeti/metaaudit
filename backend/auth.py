from urllib.parse import urlencode

import httpx

from config import (
    META_APP_ID,
    META_APP_SECRET,
    OAUTH_REDIRECT_URI,
    FACEBOOK_AUTH_URL,
    FACEBOOK_TOKEN_URL,
    FACEBOOK_GRAPH_URL,
    OAUTH_SCOPES,
)


def build_login_url() -> str:
    """Build the Facebook OAuth authorization URL."""
    params = {
        "client_id": META_APP_ID,
        "redirect_uri": OAUTH_REDIRECT_URI,
        "scope": OAUTH_SCOPES,
        "response_type": "code",
    }
    return f"{FACEBOOK_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> str:
    """Exchange an OAuth authorization code for an access token."""
    params = {
        "client_id": META_APP_ID,
        "client_secret": META_APP_SECRET,
        "redirect_uri": OAUTH_REDIRECT_URI,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(FACEBOOK_TOKEN_URL, params=params)
        response.raise_for_status()
        data = response.json()
    return data["access_token"]


async def get_user_profile(access_token: str) -> dict:
    """Fetch the user's Facebook profile (id, name, email)."""
    params = {
        "fields": "id,name,email",
        "access_token": access_token,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FACEBOOK_GRAPH_URL}/me", params=params)
        response.raise_for_status()
        return response.json()
