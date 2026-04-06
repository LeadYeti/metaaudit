import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_index_returns_html():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_auth_login_redirects_to_facebook():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 307
    assert "facebook.com" in response.headers["location"]


@pytest.mark.asyncio
async def test_auth_callback_without_code_returns_error():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/auth/callback")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_api_accounts_without_session_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/accounts")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_audit_without_session_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/audit?account_id=act_123&days=30")
    assert response.status_code == 401
