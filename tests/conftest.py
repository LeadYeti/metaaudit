import os
import sys
import pytest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Set test environment variables before any imports
os.environ.setdefault("META_APP_ID", "test_app_id")
os.environ.setdefault("META_APP_SECRET", "test_app_secret")
os.environ.setdefault("SESSION_SECRET", "a" * 64)
os.environ.setdefault("APP_URL", "http://localhost:8000")
os.environ.setdefault("GHL_WEBHOOK_URL_LEAD", "https://hooks.example.com/lead")
os.environ.setdefault("GHL_WEBHOOK_URL_AUDIT", "https://hooks.example.com/audit")
os.environ.setdefault("GHL_CALENDAR_URL", "https://calendar.example.com/book")


SAMPLE_CAMPAIGNS = [
    {
        "id": "123001",
        "name": "Summer Sale - Leads",
        "status": "ACTIVE",
        "objective": "OUTCOME_LEADS",
        "daily_budget": "2000",
    },
    {
        "id": "123002",
        "name": "Brand Awareness",
        "status": "ACTIVE",
        "objective": "OUTCOME_AWARENESS",
        "daily_budget": "500",
    },
    {
        "id": "123003",
        "name": "Retargeting - Sales",
        "status": "ACTIVE",
        "objective": "OUTCOME_SALES",
        "daily_budget": "1500",
    },
]

SAMPLE_AD_SETS = [
    {
        "id": "456001",
        "name": "Broad - 25-54",
        "campaign_id": "123001",
        "status": "ACTIVE",
        "targeting": {"age_min": 25, "age_max": 54, "geo_locations": {"countries": ["US"]}},
    },
    {
        "id": "456002",
        "name": "Interest - Home Services",
        "campaign_id": "123001",
        "status": "ACTIVE",
        "targeting": {
            "age_min": 30,
            "age_max": 60,
            "flexible_spec": [{"interests": [{"id": "6003", "name": "Home improvement"}]}],
            "geo_locations": {"countries": ["US"]},
        },
    },
    {
        "id": "456003",
        "name": "Lookalike 1%",
        "campaign_id": "123002",
        "status": "ACTIVE",
        "targeting": {
            "age_min": 25,
            "age_max": 65,
            "custom_audiences": [{"id": "789001", "name": "Lookalike (US, 1%)"}],
            "geo_locations": {"countries": ["US"]},
        },
    },
]

SAMPLE_ADS = [
    {"id": "789001", "name": "Video Ad 1", "adset_id": "456001", "status": "ACTIVE",
     "creative": {"id": "cr001", "object_type": "VIDEO"}},
    {"id": "789002", "name": "Image Ad 1", "adset_id": "456001", "status": "ACTIVE",
     "creative": {"id": "cr002", "object_type": "PHOTO"}},
    {"id": "789003", "name": "Carousel Ad", "adset_id": "456002", "status": "ACTIVE",
     "creative": {"id": "cr003", "object_type": "CAROUSEL"}},
]

SAMPLE_INSIGHTS_DAILY = [
    {
        "date_start": "2026-03-25",
        "date_stop": "2026-03-25",
        "campaign_id": "123001",
        "campaign_name": "Summer Sale - Leads",
        "adset_id": "456001",
        "ad_id": "789001",
        "impressions": "1200",
        "clicks": "45",
        "spend": "32.50",
        "cpm": "27.08",
        "cpc": "0.72",
        "ctr": "3.75",
        "frequency": "1.8",
        "actions": [{"action_type": "lead", "value": "5"}],
        "cost_per_action_type": [{"action_type": "lead", "value": "6.50"}],
    },
    {
        "date_start": "2026-03-26",
        "date_stop": "2026-03-26",
        "campaign_id": "123001",
        "campaign_name": "Summer Sale - Leads",
        "adset_id": "456001",
        "ad_id": "789001",
        "impressions": "1400",
        "clicks": "52",
        "spend": "38.00",
        "cpm": "27.14",
        "cpc": "0.73",
        "ctr": "3.71",
        "frequency": "2.1",
        "actions": [{"action_type": "lead", "value": "6"}],
        "cost_per_action_type": [{"action_type": "lead", "value": "6.33"}],
    },
    {
        "date_start": "2026-03-25",
        "date_stop": "2026-03-25",
        "campaign_id": "123002",
        "campaign_name": "Brand Awareness",
        "adset_id": "456003",
        "ad_id": "789003",
        "impressions": "5000",
        "clicks": "30",
        "spend": "15.00",
        "cpm": "3.00",
        "cpc": "0.50",
        "ctr": "0.60",
        "frequency": "3.5",
        "actions": [],
        "cost_per_action_type": [],
    },
]

SAMPLE_ACCOUNT_INFO = {
    "id": "act_12345",
    "name": "Test Business Account",
    "account_status": 1,
    "currency": "USD",
    "spend_cap": "50000",
    "amount_spent": "12345",
}

SAMPLE_PIXELS = [
    {"id": "px001", "name": "Main Pixel", "is_unavailable": False}
]
