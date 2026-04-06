import pytest
from conftest import SAMPLE_ACCOUNT_INFO, SAMPLE_PIXELS, SAMPLE_CAMPAIGNS, SAMPLE_AD_SETS, SAMPLE_ADS, SAMPLE_INSIGHTS_DAILY


def test_score_to_grade():
    from analyzer import score_to_grade
    assert score_to_grade(95) == "A"
    assert score_to_grade(85) == "B"
    assert score_to_grade(75) == "C"
    assert score_to_grade(65) == "D"
    assert score_to_grade(40) == "F"
    assert score_to_grade(90) == "A"
    assert score_to_grade(0) == "F"
    assert score_to_grade(100) == "A"


def test_analyze_account_health_good_account():
    from analyzer import analyze_account_health

    result = analyze_account_health(
        account_info=SAMPLE_ACCOUNT_INFO,
        pixels=SAMPLE_PIXELS,
        campaigns=SAMPLE_CAMPAIGNS,
    )

    assert "score" in result
    assert "grade" in result
    assert "findings" in result
    assert isinstance(result["findings"], list)
    assert result["score"] >= 0
    assert result["score"] <= 100


def test_analyze_account_health_no_pixel():
    from analyzer import analyze_account_health

    result = analyze_account_health(
        account_info=SAMPLE_ACCOUNT_INFO,
        pixels=[],
        campaigns=SAMPLE_CAMPAIGNS,
    )

    assert result["score"] < 80
    finding_texts = [f["text"] for f in result["findings"]]
    assert any("pixel" in t.lower() for t in finding_texts)


def test_analyze_account_health_no_spend_cap():
    from analyzer import analyze_account_health

    account_no_cap = {**SAMPLE_ACCOUNT_INFO, "spend_cap": "0"}
    result = analyze_account_health(
        account_info=account_no_cap,
        pixels=SAMPLE_PIXELS,
        campaigns=SAMPLE_CAMPAIGNS,
    )

    finding_texts = [f["text"] for f in result["findings"]]
    assert any("spend" in t.lower() or "cap" in t.lower() for t in finding_texts)


def test_analyze_campaign_structure_good():
    from analyzer import analyze_campaign_structure

    result = analyze_campaign_structure(SAMPLE_CAMPAIGNS)

    assert result["area"] == "Campaign Structure"
    assert result["score"] >= 70
    assert result["grade"] in ("A", "B", "C")


def test_analyze_campaign_structure_too_many_campaigns():
    from analyzer import analyze_campaign_structure

    many_campaigns = [
        {"id": str(i), "name": f"Campaign {i}", "status": "ACTIVE",
         "objective": "OUTCOME_LEADS", "daily_budget": "1000"}
        for i in range(15)
    ]

    result = analyze_campaign_structure(many_campaigns)

    assert result["score"] < 80
    finding_texts = [f["text"] for f in result["findings"]]
    assert any("many" in t.lower() or "campaigns" in t.lower() for t in finding_texts)


def test_analyze_campaign_structure_budget_concentration():
    from analyzer import analyze_campaign_structure

    skewed = [
        {"id": "1", "name": "Big Spender", "status": "ACTIVE",
         "objective": "OUTCOME_LEADS", "daily_budget": "10000"},
        {"id": "2", "name": "Tiny", "status": "ACTIVE",
         "objective": "OUTCOME_LEADS", "daily_budget": "100"},
    ]

    result = analyze_campaign_structure(skewed)

    finding_texts = [f["text"] for f in result["findings"]]
    assert any("budget" in t.lower() for t in finding_texts)


def test_analyze_audience_targeting_good():
    from analyzer import analyze_audience_targeting

    result = analyze_audience_targeting(SAMPLE_AD_SETS)

    assert result["area"] == "Audience Targeting"
    assert "score" in result
    assert "grade" in result
    assert isinstance(result["findings"], list)


def test_analyze_audience_targeting_no_retargeting():
    from analyzer import analyze_audience_targeting

    ad_sets_no_retarget = [
        {
            "id": "1", "name": "Broad", "campaign_id": "c1", "status": "ACTIVE",
            "targeting": {"age_min": 18, "age_max": 65, "geo_locations": {"countries": ["US"]}},
        },
    ]

    result = analyze_audience_targeting(ad_sets_no_retarget)

    finding_texts = [f["text"] for f in result["findings"]]
    assert any("retarget" in t.lower() for t in finding_texts)


def test_analyze_audience_targeting_single_ad_set():
    from analyzer import analyze_audience_targeting

    single = [
        {
            "id": "1", "name": "Only One", "campaign_id": "c1", "status": "ACTIVE",
            "targeting": {"age_min": 25, "age_max": 55, "geo_locations": {"countries": ["US"]}},
        },
    ]

    result = analyze_audience_targeting(single)
    assert result["score"] <= 100


def test_analyze_creative_performance_good():
    from analyzer import analyze_creative_performance

    result = analyze_creative_performance(SAMPLE_ADS, SAMPLE_AD_SETS, SAMPLE_INSIGHTS_DAILY)

    assert result["area"] == "Ad Creative"
    assert "score" in result
    assert isinstance(result["findings"], list)


def test_analyze_creative_performance_high_frequency():
    from analyzer import analyze_creative_performance

    high_freq_insights = [
        {**SAMPLE_INSIGHTS_DAILY[0], "frequency": "5.2", "ad_id": "789001"},
    ]

    result = analyze_creative_performance(SAMPLE_ADS, SAMPLE_AD_SETS, high_freq_insights)

    finding_texts = [f["text"] for f in result["findings"]]
    assert any("fatigue" in t.lower() or "frequency" in t.lower() for t in finding_texts)


def test_analyze_creative_performance_too_many_ads():
    from analyzer import analyze_creative_performance

    many_ads = [
        {"id": str(i), "name": f"Ad {i}", "adset_id": "456001", "status": "ACTIVE",
         "creative": {"id": f"cr{i}", "object_type": "PHOTO"}}
        for i in range(8)
    ]

    result = analyze_creative_performance(many_ads, SAMPLE_AD_SETS, SAMPLE_INSIGHTS_DAILY)

    finding_texts = [f["text"] for f in result["findings"]]
    assert any("too many" in t.lower() or "dilut" in t.lower() for t in finding_texts)


def test_analyze_spend_efficiency_basic():
    from analyzer import analyze_spend_efficiency
    from benchmarks import get_benchmarks

    benchmarks = get_benchmarks("home_services")
    result = analyze_spend_efficiency(SAMPLE_INSIGHTS_DAILY, benchmarks)

    assert result["area"] == "Spend Efficiency"
    assert "score" in result
    assert "trends" in result
    assert isinstance(result["findings"], list)


def test_analyze_spend_efficiency_wasted_spend():
    from analyzer import analyze_spend_efficiency
    from benchmarks import get_benchmarks

    wasted_insights = [
        {
            "date_start": "2026-03-25", "date_stop": "2026-03-25",
            "campaign_id": "c1", "campaign_name": "Bad Campaign",
            "adset_id": "as1", "ad_id": "a1",
            "impressions": "5000", "clicks": "50", "spend": "100.00",
            "cpm": "20.00", "cpc": "2.00", "ctr": "1.0", "frequency": "1.5",
            "actions": [], "cost_per_action_type": [],
        },
    ]

    benchmarks = get_benchmarks("default")
    result = analyze_spend_efficiency(wasted_insights, benchmarks)

    finding_texts = [f["text"] for f in result["findings"]]
    assert any("wasted" in t.lower() or "zero conversion" in t.lower() for t in finding_texts)


def test_analyze_spend_efficiency_returns_trend_data():
    from analyzer import analyze_spend_efficiency
    from benchmarks import get_benchmarks

    benchmarks = get_benchmarks("default")
    result = analyze_spend_efficiency(SAMPLE_INSIGHTS_DAILY, benchmarks)

    assert "trends" in result
    trends = result["trends"]
    assert "dates" in trends
    assert "cpm" in trends
    assert "cpc" in trends
    assert isinstance(trends["dates"], list)


def test_run_full_audit_returns_all_areas():
    from analyzer import run_full_audit

    result = run_full_audit(
        account_info=SAMPLE_ACCOUNT_INFO,
        pixels=SAMPLE_PIXELS,
        campaigns=SAMPLE_CAMPAIGNS,
        ad_sets=SAMPLE_AD_SETS,
        ads=SAMPLE_ADS,
        insights=SAMPLE_INSIGHTS_DAILY,
        industry="home_services",
    )

    assert "overall_score" in result
    assert "overall_grade" in result
    assert "areas" in result
    assert len(result["areas"]) == 5

    area_names = {a["area"] for a in result["areas"]}
    assert area_names == {"Account Health", "Campaign Structure", "Audience Targeting", "Ad Creative", "Spend Efficiency"}


def test_run_full_audit_overall_score_is_average():
    from analyzer import run_full_audit

    result = run_full_audit(
        account_info=SAMPLE_ACCOUNT_INFO,
        pixels=SAMPLE_PIXELS,
        campaigns=SAMPLE_CAMPAIGNS,
        ad_sets=SAMPLE_AD_SETS,
        ads=SAMPLE_ADS,
        insights=SAMPLE_INSIGHTS_DAILY,
        industry="default",
    )

    area_scores = [a["score"] for a in result["areas"]]
    expected_avg = round(sum(area_scores) / len(area_scores))
    assert result["overall_score"] == expected_avg
