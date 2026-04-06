from datetime import datetime, timedelta

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.user import User

from config import META_APP_ID, META_APP_SECRET


def _init_api(access_token: str):
    """Initialize the Facebook Ads API with a user's access token."""
    FacebookAdsApi.init(META_APP_ID, META_APP_SECRET, access_token)


def fetch_ad_accounts(access_token: str, user_id: str) -> list[dict]:
    """Fetch all ad accounts the user has access to."""
    _init_api(access_token)
    user = User(user_id)
    accounts = user.get_ad_accounts(fields=[
        AdAccount.Field.id,
        AdAccount.Field.name,
        AdAccount.Field.account_status,
        AdAccount.Field.currency,
    ])
    return [a.export_all_data() for a in accounts]


def fetch_campaigns(access_token: str, account_id: str, active_only: bool = True) -> list[dict]:
    """Fetch campaigns for an ad account. If active_only, filter to ACTIVE status."""
    _init_api(access_token)
    account = AdAccount(account_id)
    campaigns = account.get_campaigns(
        fields=[
            Campaign.Field.id,
            Campaign.Field.name,
            Campaign.Field.status,
            Campaign.Field.effective_status,
            Campaign.Field.objective,
            Campaign.Field.daily_budget,
            Campaign.Field.lifetime_budget,
        ],
    )
    all_data = [c.export_all_data() for c in campaigns]
    if active_only:
        return [c for c in all_data if c.get("effective_status") == "ACTIVE"]
    return all_data


def fetch_ad_sets(access_token: str, account_id: str, active_only: bool = True) -> list[dict]:
    """Fetch ad sets for an ad account. If active_only, filter to ACTIVE status."""
    _init_api(access_token)
    account = AdAccount(account_id)
    ad_sets = account.get_ad_sets(
        fields=[
            AdSet.Field.id,
            AdSet.Field.name,
            AdSet.Field.campaign_id,
            AdSet.Field.status,
            AdSet.Field.effective_status,
            AdSet.Field.targeting,
            AdSet.Field.daily_budget,
        ],
    )
    all_data = [s.export_all_data() for s in ad_sets]
    statuses = set(s.get("status") for s in all_data)
    effective = set(s.get("effective_status") for s in all_data)
    print(f"Ad set statuses found: {statuses}, effective: {effective}, total: {len(all_data)}")
    if active_only:
        return [s for s in all_data if s.get("effective_status") == "ACTIVE"]
    return all_data


def fetch_ads(access_token: str, account_id: str, active_only: bool = True) -> list[dict]:
    """Fetch ads for an ad account. If active_only, filter to ACTIVE status."""
    _init_api(access_token)
    account = AdAccount(account_id)
    ads = account.get_ads(
        fields=[
            Ad.Field.id,
            Ad.Field.name,
            Ad.Field.adset_id,
            Ad.Field.status,
            Ad.Field.effective_status,
            Ad.Field.creative,
        ],
    )
    all_data = [a.export_all_data() for a in ads]
    if active_only:
        return [a for a in all_data if a.get("effective_status") == "ACTIVE"]
    return all_data


def fetch_insights(access_token: str, account_id: str, days: int = 30) -> list[dict]:
    """Fetch daily insights for the account over the given time range."""
    _init_api(access_token)
    account = AdAccount(account_id)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    insights = account.get_insights(
        fields=[
            AdsInsights.Field.campaign_id,
            AdsInsights.Field.campaign_name,
            AdsInsights.Field.adset_id,
            AdsInsights.Field.ad_id,
            AdsInsights.Field.impressions,
            AdsInsights.Field.clicks,
            AdsInsights.Field.spend,
            AdsInsights.Field.cpm,
            AdsInsights.Field.cpc,
            AdsInsights.Field.ctr,
            AdsInsights.Field.frequency,
            AdsInsights.Field.actions,
            AdsInsights.Field.cost_per_action_type,
        ],
        params={
            "time_range": {"since": start_date, "until": end_date},
            "time_increment": 1,
            "level": "ad",
        },
    )
    return [row.export_all_data() for row in insights]


def fetch_account_info(access_token: str, account_id: str) -> dict:
    """Fetch account-level info (status, currency, spend cap)."""
    _init_api(access_token)
    account = AdAccount(account_id)
    info = account.api_get(fields=[
        AdAccount.Field.id,
        AdAccount.Field.name,
        AdAccount.Field.account_status,
        AdAccount.Field.currency,
        AdAccount.Field.spend_cap,
        AdAccount.Field.amount_spent,
    ])
    return info.export_all_data()


def fetch_pixels(access_token: str, account_id: str) -> list[dict]:
    """Fetch pixels associated with the ad account."""
    _init_api(access_token)
    account = AdAccount(account_id)
    pixels = account.get_ads_pixels(fields=["id", "name", "is_unavailable"])
    return [p.export_all_data() for p in pixels]
