import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from auth import build_login_url, exchange_code_for_token, get_user_profile


def test_build_login_url_contains_required_params():
    url = build_login_url()
    assert "client_id=test_app_id" in url
    assert "redirect_uri=" in url
    assert "scope=" in url
    assert "ads_read" in url
    assert "email" in url


def test_build_login_url_uses_correct_base():
    url = build_login_url()
    assert url.startswith("https://www.facebook.com/v21.0/dialog/oauth")


@pytest.mark.asyncio
async def test_exchange_code_for_token_sends_correct_params():
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake_token_123", "token_type": "bearer"}
    mock_response.raise_for_status = MagicMock()

    with patch("auth.httpx.AsyncClient") as MockClient:
        client_instance = AsyncMock()
        client_instance.get.return_value = mock_response
        client_instance.__aenter__ = AsyncMock(return_value=client_instance)
        client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = client_instance

        token = await exchange_code_for_token("auth_code_abc")

        assert token == "fake_token_123"
        call_kwargs = client_instance.get.call_args
        params = call_kwargs.kwargs["params"]
        assert params["code"] == "auth_code_abc"
        assert params["client_id"] == "test_app_id"
        assert params["client_secret"] == "test_app_secret"


@pytest.mark.asyncio
async def test_get_user_profile_returns_name_and_email():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "fb_123",
        "name": "John Smith",
        "email": "john@example.com",
    }
    mock_response.raise_for_status = MagicMock()

    with patch("auth.httpx.AsyncClient") as MockClient:
        client_instance = AsyncMock()
        client_instance.get.return_value = mock_response
        client_instance.__aenter__ = AsyncMock(return_value=client_instance)
        client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = client_instance

        profile = await get_user_profile("fake_token_123")

        assert profile["id"] == "fb_123"
        assert profile["name"] == "John Smith"
        assert profile["email"] == "john@example.com"
