import os
from pathlib import Path

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import httpx

from config import SESSION_SECRET, GHL_CALENDAR_URL, FACEBOOK_GRAPH_URL
from auth import build_login_url, exchange_code_for_token, get_user_profile
from meta_api import (
    fetch_ad_accounts,
    fetch_campaigns,
    fetch_ad_sets,
    fetch_ads,
    fetch_insights,
    fetch_account_info,
    fetch_pixels,
)
from analyzer import run_full_audit
from ghl_webhook import send_lead_webhook, send_audit_webhook

app = FastAPI(title="Meta Ads Audit Tool")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the single-page frontend."""
    html_path = FRONTEND_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text())


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    """Serve the privacy policy page."""
    html_path = FRONTEND_DIR / "privacy.html"
    return HTMLResponse(content=html_path.read_text())


@app.get("/auth/login")
async def auth_login():
    """Redirect to Facebook OAuth consent screen."""
    return RedirectResponse(url=build_login_url(), status_code=307)


@app.get("/auth/callback")
async def auth_callback(request: Request, code: str = Query(default=None), error: str = Query(default=None)):
    """Handle the OAuth callback from Facebook."""
    if error or not code:
        return JSONResponse({"error": error or "No authorization code received"}, status_code=400)

    access_token = await exchange_code_for_token(code)
    profile = await get_user_profile(access_token)

    request.session["access_token"] = access_token
    request.session["user_id"] = profile["id"]
    request.session["user_name"] = profile.get("name", "")
    request.session["user_email"] = profile.get("email", "")

    try:
        await send_lead_webhook(
            name=profile.get("name", ""),
            email=profile.get("email", ""),
            facebook_id=profile["id"],
        )
    except Exception:
        pass

    return RedirectResponse(url="/?view=accounts", status_code=302)


@app.get("/api/accounts")
async def api_accounts(request: Request):
    """Return the user's ad accounts."""
    access_token = request.session.get("access_token")
    user_id = request.session.get("user_id")
    if not access_token:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    accounts = fetch_ad_accounts(access_token, user_id)
    return {"accounts": accounts}


@app.get("/api/debug-permissions")
async def debug_permissions(request: Request):
    """Debug: check what permissions the current token has."""
    access_token = request.session.get("access_token")
    if not access_token:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{FACEBOOK_GRAPH_URL}/me/permissions",
            params={"access_token": access_token},
        )
        return resp.json()


@app.get("/api/debug-campaigns")
async def debug_campaigns(request: Request, account_id: str = Query(...)):
    """Debug: fetch campaigns directly via HTTP to see raw response."""
    access_token = request.session.get("access_token")
    if not access_token:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{FACEBOOK_GRAPH_URL}/{account_id}/campaigns",
            params={
                "access_token": access_token,
                "fields": "id,name,status,objective,daily_budget",
                "filtering": '[{"field":"status","operator":"IN","value":["ACTIVE"]}]',
            },
        )
        return {"status_code": resp.status_code, "body": resp.json()}


@app.get("/api/audit")
async def api_audit(
    request: Request,
    account_id: str = Query(...),
    days: int = Query(default=30),
    industry: str = Query(default="default"),
    status_filter: str = Query(default="ACTIVE"),
):
    """Run the full audit on a selected ad account."""
    access_token = request.session.get("access_token")
    if not access_token:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    try:
        account_info = fetch_account_info(access_token, account_id)
        await send_audit_webhook(
            email=request.session.get("user_email", ""),
            ad_account_id=account_id,
            ad_account_name=account_info.get("name", account_id),
        )
    except Exception:
        account_info = {"id": account_id, "name": account_id, "account_status": 1, "currency": "USD"}

    active_only = status_filter == "ACTIVE"

    try:
        campaigns = fetch_campaigns(access_token, account_id, active_only=active_only)
    except Exception as e:
        campaigns = []
        print(f"Error fetching campaigns: {e}")

    try:
        ad_sets = fetch_ad_sets(access_token, account_id, active_only=active_only)
    except Exception as e:
        ad_sets = []
        print(f"Error fetching ad sets: {e}")

    try:
        ads = fetch_ads(access_token, account_id, active_only=active_only)
    except Exception as e:
        ads = []
        print(f"Error fetching ads: {e}")

    try:
        insights = fetch_insights(access_token, account_id, days=days)
    except Exception as e:
        insights = []
        print(f"Error fetching insights: {e}")

    try:
        pixels = fetch_pixels(access_token, account_id)
    except Exception as e:
        pixels = []
        print(f"Error fetching pixels: {e}")

    result = run_full_audit(
        account_info=account_info,
        pixels=pixels,
        campaigns=campaigns,
        ad_sets=ad_sets,
        ads=ads,
        insights=insights,
        industry=industry,
    )

    result["account_name"] = account_info.get("name", account_id)
    result["currency"] = account_info.get("currency", "USD")
    result["calendar_url"] = GHL_CALENDAR_URL

    # Data summary so user can verify against Ads Manager
    total_spend = sum(float(row.get("spend", 0)) for row in insights)
    total_impressions = sum(int(row.get("impressions", 0)) for row in insights)
    total_clicks = sum(int(row.get("clicks", 0)) for row in insights)
    result["data_summary"] = {
        "campaigns_found": len(campaigns),
        "ad_sets_found": len(ad_sets),
        "ads_found": len(ads),
        "total_spend": round(total_spend, 2),
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "days_analyzed": days,
        "status_filter": "Active only" if active_only else "All statuses",
        "campaign_names": [c.get("name", "Unknown") for c in campaigns],
    }

    return result
