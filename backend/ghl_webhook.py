import httpx

from config import GHL_WEBHOOK_URL_LEAD, GHL_WEBHOOK_URL_AUDIT


async def send_lead_webhook(name: str, email: str, facebook_id: str) -> None:
    """Send lead data to GHL when user completes Facebook OAuth."""
    if not GHL_WEBHOOK_URL_LEAD:
        return

    payload = {
        "name": name,
        "email": email,
        "facebook_id": facebook_id,
        "source": "meta_ads_audit_tool",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GHL_WEBHOOK_URL_LEAD, json=payload, timeout=10)
        response.raise_for_status()


async def send_audit_webhook(email: str, ad_account_id: str, ad_account_name: str) -> None:
    """Send audit context to GHL when user selects an ad account and runs audit."""
    if not GHL_WEBHOOK_URL_AUDIT:
        return

    payload = {
        "email": email,
        "ad_account_id": ad_account_id,
        "ad_account_name": ad_account_name,
        "source": "meta_ads_audit_tool",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GHL_WEBHOOK_URL_AUDIT, json=payload, timeout=10)
        response.raise_for_status()
