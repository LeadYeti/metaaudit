import pytest
from unittest.mock import MagicMock, patch
from conftest import (
    SAMPLE_CAMPAIGNS,
    SAMPLE_AD_SETS,
    SAMPLE_ADS,
    SAMPLE_INSIGHTS_DAILY,
    SAMPLE_ACCOUNT_INFO,
    SAMPLE_PIXELS,
)
from meta_api import (
    fetch_ad_accounts,
    fetch_campaigns,
    fetch_ad_sets,
    fetch_ads,
    fetch_insights,
    fetch_account_info,
    fetch_pixels,
)


def test_fetch_ad_accounts_returns_list():
    mock_user = MagicMock()
    mock_account = MagicMock()
    mock_account.__getitem__ = lambda self, key: {"id": "act_123", "name": "My Biz", "account_status": 1}[key]
    mock_account.export_all_data.return_value = {"id": "act_123", "name": "My Biz", "account_status": 1}
    mock_user.get_ad_accounts.return_value = [mock_account]

    with patch("meta_api.User", return_value=mock_user):
        with patch("meta_api.FacebookAdsApi.init"):
            accounts = fetch_ad_accounts("fake_token", "fb_user_id")

    assert len(accounts) == 1
    assert accounts[0]["id"] == "act_123"


def test_fetch_campaigns_returns_campaign_list():
    mock_account = MagicMock()
    mock_campaigns = []
    for c in SAMPLE_CAMPAIGNS:
        m = MagicMock()
        m.export_all_data.return_value = c
        mock_campaigns.append(m)
    mock_account.get_campaigns.return_value = mock_campaigns

    with patch("meta_api.AdAccount", return_value=mock_account):
        with patch("meta_api.FacebookAdsApi.init"):
            campaigns = fetch_campaigns("fake_token", "act_123")

    assert len(campaigns) == 3
    assert campaigns[0]["name"] == "Summer Sale - Leads"


def test_fetch_insights_returns_daily_data():
    mock_account = MagicMock()
    mock_insights = []
    for row in SAMPLE_INSIGHTS_DAILY:
        m = MagicMock()
        m.export_all_data.return_value = row
        mock_insights.append(m)
    mock_account.get_insights.return_value = mock_insights

    with patch("meta_api.AdAccount", return_value=mock_account):
        with patch("meta_api.FacebookAdsApi.init"):
            insights = fetch_insights("fake_token", "act_123", days=7)

    assert len(insights) == 3
    assert insights[0]["campaign_name"] == "Summer Sale - Leads"
