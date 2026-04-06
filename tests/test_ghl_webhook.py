import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_send_lead_webhook_sends_correct_payload():
    from ghl_webhook import send_lead_webhook

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch("ghl_webhook.httpx.AsyncClient") as MockClient:
        client_instance = AsyncMock()
        client_instance.post.return_value = mock_response
        client_instance.__aenter__ = AsyncMock(return_value=client_instance)
        client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = client_instance

        await send_lead_webhook(
            name="John Smith",
            email="john@example.com",
            facebook_id="fb_123",
        )

        client_instance.post.assert_called_once()
        call_args = client_instance.post.call_args
        payload = call_args.kwargs.get("json")
        assert payload["name"] == "John Smith"
        assert payload["email"] == "john@example.com"
        assert payload["facebook_id"] == "fb_123"


@pytest.mark.asyncio
async def test_send_audit_webhook_sends_account_info():
    from ghl_webhook import send_audit_webhook

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch("ghl_webhook.httpx.AsyncClient") as MockClient:
        client_instance = AsyncMock()
        client_instance.post.return_value = mock_response
        client_instance.__aenter__ = AsyncMock(return_value=client_instance)
        client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = client_instance

        await send_audit_webhook(
            email="john@example.com",
            ad_account_id="act_123",
            ad_account_name="My Business",
        )

        client_instance.post.assert_called_once()
