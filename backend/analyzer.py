"""Audit analysis engine — scores five areas of a Meta ads account."""

from benchmarks import get_benchmarks


def score_to_grade(score: int) -> str:
    """Map a 0-100 score to a letter grade."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _finding(text: str, severity: str = "info") -> dict:
    """Create a finding dict. severity: 'good', 'warning', 'critical', 'info'."""
    return {"text": text, "severity": severity}


def analyze_account_health(account_info: dict, pixels: list, campaigns: list) -> dict:
    """Analyze account-level health: pixel, tracking, spend cap."""
    score = 100
    findings = []

    # Pixel check
    if not pixels:
        score -= 30
        findings.append(_finding("No Meta Pixel found. You can't track conversions without one.", "critical"))
    else:
        unavailable = [p for p in pixels if p.get("is_unavailable", True)]
        if len(unavailable) == len(pixels):
            score -= 25
            findings.append(_finding("Pixel is installed but not firing. Check your website integration.", "critical"))
        else:
            findings.append(_finding("Meta Pixel is installed and active.", "good"))

    # Conversion tracking — check if any campaign uses a conversion objective
    conversion_objectives = {"OUTCOME_LEADS", "OUTCOME_SALES", "OUTCOME_APP_PROMOTION"}
    has_conversion_campaign = any(c.get("objective") in conversion_objectives for c in campaigns)
    if not has_conversion_campaign:
        score -= 15
        findings.append(_finding("No campaigns optimizing for conversions. Consider adding lead or sales campaigns.", "warning"))
    else:
        findings.append(_finding("Conversion-optimized campaigns detected.", "good"))

    # Spend cap
    spend_cap = account_info.get("spend_cap", "0")
    if spend_cap == "0" or not spend_cap:
        score -= 10
        findings.append(_finding("No account spend cap set. Set one to prevent accidental overspend.", "warning"))
    else:
        findings.append(_finding(f"Account spend cap set at ${int(spend_cap) / 100:,.0f}.", "good"))

    # Account status
    status = account_info.get("account_status", 0)
    if status != 1:
        score -= 20
        findings.append(_finding("Account status is not active. Check for policy violations or billing issues.", "critical"))

    score = max(0, min(100, score))
    return {"area": "Account Health", "score": score, "grade": score_to_grade(score), "findings": findings}


def analyze_campaign_structure(campaigns: list) -> dict:
    """Analyze campaign count, budget distribution, and objective mix."""
    score = 100
    findings = []
    count = len(campaigns)

    if count == 0:
        score -= 40
        findings.append(_finding("No active campaigns found.", "critical"))
        return {"area": "Campaign Structure", "score": max(0, score), "grade": score_to_grade(max(0, score)), "findings": findings}

    if count > 10:
        score -= 20
        findings.append(_finding(f"{count} active campaigns is too many. Consolidate to reduce overlap and simplify management.", "warning"))
    elif count > 6:
        score -= 10
        findings.append(_finding(f"{count} active campaigns — consider consolidating if audiences overlap.", "warning"))
    else:
        findings.append(_finding(f"{count} active campaigns — manageable structure.", "good"))

    budgets = []
    for c in campaigns:
        budget = int(c.get("daily_budget", 0) or 0)
        budgets.append(budget)

    total_budget = sum(budgets)
    if total_budget > 0:
        max_budget = max(budgets)
        concentration = max_budget / total_budget
        if concentration > 0.80:
            score -= 15
            findings.append(_finding(f"{concentration:.0%} of budget goes to one campaign. Diversify to reduce risk.", "warning"))
        elif concentration > 0.60:
            score -= 5
            findings.append(_finding(f"Budget is moderately concentrated ({concentration:.0%} in top campaign).", "info"))
        else:
            findings.append(_finding("Budget is well-distributed across campaigns.", "good"))

    objectives = {c.get("objective", "UNKNOWN") for c in campaigns}
    if len(objectives) == 1:
        score -= 10
        findings.append(_finding("All campaigns use the same objective. Consider a full-funnel approach (awareness + leads + sales).", "warning"))
    else:
        findings.append(_finding(f"Using {len(objectives)} different objectives — good full-funnel approach.", "good"))

    score = max(0, min(100, score))
    return {"area": "Campaign Structure", "score": score, "grade": score_to_grade(score), "findings": findings}


def analyze_audience_targeting(ad_sets: list) -> dict:
    """Analyze audience sizes, types, overlap risk, and retargeting."""
    score = 100
    findings = []

    if not ad_sets:
        score -= 40
        findings.append(_finding("No active ad sets found.", "critical"))
        return {"area": "Audience Targeting", "score": max(0, score), "grade": score_to_grade(max(0, score)), "findings": findings}

    has_interest = False
    has_lookalike = False
    has_custom_audience = False
    has_broad = False

    for ad_set in ad_sets:
        targeting = ad_set.get("targeting", {})
        if targeting.get("flexible_spec"):
            has_interest = True
        if targeting.get("custom_audiences"):
            ca_list = targeting["custom_audiences"]
            for ca in ca_list:
                name = ca.get("name", "").lower()
                if "lookalike" in name:
                    has_lookalike = True
                else:
                    has_custom_audience = True
        if not targeting.get("flexible_spec") and not targeting.get("custom_audiences"):
            has_broad = True

    type_count = sum([has_interest, has_lookalike, has_custom_audience, has_broad])
    if type_count >= 3:
        findings.append(_finding("Good audience mix — testing multiple targeting approaches.", "good"))
    elif type_count == 2:
        findings.append(_finding("Decent audience variety. Consider testing additional targeting types.", "info"))
    else:
        score -= 15
        findings.append(_finding("Only one audience type in use. Test interest, lookalike, and custom audiences.", "warning"))

    if not has_custom_audience:
        score -= 15
        findings.append(_finding("No retargeting audiences detected. Retargeting typically has 2-3x better ROAS.", "warning"))
    else:
        findings.append(_finding("Retargeting audiences are active.", "good"))

    campaign_ad_sets = {}
    for ad_set in ad_sets:
        cid = ad_set.get("campaign_id", "unknown")
        campaign_ad_sets.setdefault(cid, []).append(ad_set)

    for cid, sets in campaign_ad_sets.items():
        if len(sets) > 3:
            score -= 10
            findings.append(_finding(f"Campaign has {len(sets)} ad sets — high risk of audience overlap and budget dilution.", "warning"))
            break

    if len(ad_sets) == 1:
        score -= 10
        findings.append(_finding("Only 1 active ad set. Test multiple audiences to find your best performers.", "warning"))

    score = max(0, min(100, score))
    return {"area": "Audience Targeting", "score": score, "grade": score_to_grade(score), "findings": findings}


def analyze_creative_performance(ads: list, ad_sets: list, insights: list) -> dict:
    """Analyze ad creative count, fatigue, format mix, and performance spread."""
    score = 100
    findings = []

    if not ads:
        score -= 40
        findings.append(_finding("No active ads found.", "critical"))
        return {"area": "Ad Creative", "score": max(0, score), "grade": score_to_grade(max(0, score)), "findings": findings}

    # Match ads to their ad sets — only count ads whose ad set is in our list
    known_adset_ids = {s.get("id") for s in ad_sets}
    ads_by_adset = {}
    for ad in ads:
        adset_id = ad.get("adset_id", "unknown")
        if known_adset_ids and adset_id not in known_adset_ids:
            continue
        ads_by_adset.setdefault(adset_id, []).append(ad)

    undertested = []
    overtested = []
    for adset_id, adset_ads in ads_by_adset.items():
        count = len(adset_ads)
        adset_name = next((s.get("name", adset_id) for s in ad_sets if s.get("id") == adset_id), adset_id)
        if count < 2:
            undertested.append(adset_name)
        elif count > 6:
            overtested.append((adset_name, count))

    if undertested:
        score -= min(15, len(undertested) * 5)
        if len(undertested) == 1:
            findings.append(_finding(f"Ad set '{undertested[0]}' has only 1 ad — consider adding more to enable A/B testing.", "info"))
        else:
            findings.append(_finding(f"{len(undertested)} ad sets have only 1 ad — consider adding variants for A/B testing.", "info"))

    if overtested:
        score -= min(15, len(overtested) * 5)
        for name, count in overtested:
            findings.append(_finding(f"Ad set '{name}' has {count} ads — too many dilutes budget. Keep 3-5 per ad set.", "warning"))

    max_frequency = 0.0
    fatigued_ads = []
    for row in insights:
        freq = float(row.get("frequency", 0))
        if freq > max_frequency:
            max_frequency = freq
        if freq > 3.0:
            fatigued_ads.append(row.get("ad_id", "unknown"))

    if fatigued_ads:
        score -= 15
        findings.append(_finding(f"{len(set(fatigued_ads))} ad(s) have frequency above 3.0 — creative fatigue is likely. Refresh your creatives.", "warning"))
    else:
        findings.append(_finding("No creative fatigue detected (frequency under 3.0).", "good"))

    formats = set()
    for ad in ads:
        creative = ad.get("creative", {})
        obj_type = creative.get("object_type", "UNKNOWN")
        formats.add(obj_type)

    if len(formats) >= 3:
        findings.append(_finding(f"Good creative mix — using {len(formats)} formats ({', '.join(formats)}).", "good"))
    elif len(formats) == 2:
        findings.append(_finding(f"Using {len(formats)} ad formats. Consider testing video if you haven't.", "info"))
    else:
        score -= 10
        findings.append(_finding("Only one ad format in use. Test image, video, and carousel for better results.", "warning"))

    ad_spend = {}
    for row in insights:
        aid = row.get("ad_id", "unknown")
        ad_spend[aid] = ad_spend.get(aid, 0) + float(row.get("spend", 0))

    if len(ad_spend) > 1:
        total = sum(ad_spend.values())
        if total > 0:
            max_share = max(ad_spend.values()) / total
            if max_share > 0.80:
                score -= 10
                findings.append(_finding(f"One ad is consuming {max_share:.0%} of spend. Other ads aren't getting enough budget to test properly.", "warning"))

    score = max(0, min(100, score))
    return {"area": "Ad Creative", "score": score, "grade": score_to_grade(score), "findings": findings}


def analyze_spend_efficiency(insights: list, benchmarks: dict) -> dict:
    """Analyze CPM, CPC, CPA, ROAS, wasted spend, and trends."""
    score = 100
    findings = []
    trends = {"dates": [], "cpm": [], "cpc": [], "cpa": [], "spend": []}

    if not insights:
        score -= 40
        findings.append(_finding("No spend data found for this time range.", "critical"))
        return {"area": "Spend Efficiency", "score": max(0, score), "grade": score_to_grade(max(0, score)), "findings": findings, "trends": trends}

    daily = {}
    for row in insights:
        date = row.get("date_start", "unknown")
        if date not in daily:
            daily[date] = {"impressions": 0, "clicks": 0, "spend": 0.0, "conversions": 0, "cost_per_conversion": []}

        daily[date]["impressions"] += int(row.get("impressions", 0))
        daily[date]["clicks"] += int(row.get("clicks", 0))
        daily[date]["spend"] += float(row.get("spend", 0))

        actions = row.get("actions", []) or []
        for action in actions:
            if action.get("action_type") in ("lead", "purchase", "complete_registration", "contact"):
                daily[date]["conversions"] += int(action.get("value", 0))

        cpa_list = row.get("cost_per_action_type", []) or []
        for cpa in cpa_list:
            if cpa.get("action_type") in ("lead", "purchase", "complete_registration", "contact"):
                daily[date]["cost_per_conversion"].append(float(cpa.get("value", 0)))

    for date in sorted(daily.keys()):
        d = daily[date]
        trends["dates"].append(date)
        trends["spend"].append(round(d["spend"], 2))
        trends["cpm"].append(round(d["spend"] / d["impressions"] * 1000, 2) if d["impressions"] > 0 else 0)
        trends["cpc"].append(round(d["spend"] / d["clicks"], 2) if d["clicks"] > 0 else 0)
        avg_cpa = sum(d["cost_per_conversion"]) / len(d["cost_per_conversion"]) if d["cost_per_conversion"] else 0
        trends["cpa"].append(round(avg_cpa, 2))

    total_spend = sum(d["spend"] for d in daily.values())
    total_impressions = sum(d["impressions"] for d in daily.values())
    total_clicks = sum(d["clicks"] for d in daily.values())
    total_conversions = sum(d["conversions"] for d in daily.values())

    avg_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
    avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0

    bench_cpm = benchmarks.get("cpm", 18)
    bench_cpc = benchmarks.get("cpc", 1.40)
    bench_cpa = benchmarks.get("cpa", 22)

    if avg_cpm > bench_cpm * 1.5:
        score -= 15
        findings.append(_finding(f"CPM (${avg_cpm:.2f}) is significantly above benchmark (${bench_cpm:.2f}). Review targeting — overly narrow audiences drive CPM up.", "warning"))
    elif avg_cpm > bench_cpm:
        score -= 5
        findings.append(_finding(f"CPM (${avg_cpm:.2f}) is slightly above benchmark (${bench_cpm:.2f}).", "info"))
    else:
        findings.append(_finding(f"CPM (${avg_cpm:.2f}) is at or below benchmark (${bench_cpm:.2f}).", "good"))

    if total_conversions > 0:
        if avg_cpa > bench_cpa * 1.5:
            score -= 15
            findings.append(_finding(f"CPA (${avg_cpa:.2f}) is well above benchmark (${bench_cpa:.2f}). Review your funnel and targeting.", "warning"))
        elif avg_cpa <= bench_cpa:
            findings.append(_finding(f"CPA (${avg_cpa:.2f}) is at or below benchmark (${bench_cpa:.2f}).", "good"))

    adset_spend = {}
    adset_conversions = {}
    for row in insights:
        asid = row.get("adset_id", "unknown")
        adset_spend[asid] = adset_spend.get(asid, 0) + float(row.get("spend", 0))
        actions = row.get("actions", []) or []
        convs = sum(int(a.get("value", 0)) for a in actions if a.get("action_type") in ("lead", "purchase", "complete_registration", "contact"))
        adset_conversions[asid] = adset_conversions.get(asid, 0) + convs

    wasted = sum(spend for asid, spend in adset_spend.items() if adset_conversions.get(asid, 0) == 0)
    if wasted > 0:
        score -= 15
        findings.append(_finding(f"${wasted:,.2f} spent on ad sets with zero conversions — wasted spend.", "critical"))
    else:
        findings.append(_finding("No wasted spend detected — all ad sets have conversions.", "good"))

    spend_values = trends["spend"]
    if len(spend_values) >= 4:
        mid = len(spend_values) // 2
        first_half_cpm = trends["cpm"][:mid]
        second_half_cpm = trends["cpm"][mid:]
        avg_first = sum(first_half_cpm) / len(first_half_cpm) if first_half_cpm else 0
        avg_second = sum(second_half_cpm) / len(second_half_cpm) if second_half_cpm else 0
        if avg_second > avg_first * 1.2:
            findings.append(_finding("CPM is trending upward — audiences may be getting saturated.", "warning"))
        elif avg_second < avg_first * 0.8:
            findings.append(_finding("CPM is trending downward — good sign, efficiency is improving.", "good"))

    score = max(0, min(100, score))
    return {"area": "Spend Efficiency", "score": score, "grade": score_to_grade(score), "findings": findings, "trends": trends}


def run_full_audit(
    account_info: dict,
    pixels: list,
    campaigns: list,
    ad_sets: list,
    ads: list,
    insights: list,
    industry: str = "default",
) -> dict:
    """Run all five analyzers and compute an overall score."""
    benchmarks = get_benchmarks(industry)

    areas = [
        analyze_account_health(account_info, pixels, campaigns),
        analyze_campaign_structure(campaigns),
        analyze_audience_targeting(ad_sets),
        analyze_creative_performance(ads, ad_sets, insights),
        analyze_spend_efficiency(insights, benchmarks),
    ]

    area_scores = [a["score"] for a in areas]
    overall_score = round(sum(area_scores) / len(area_scores))

    return {
        "overall_score": overall_score,
        "overall_grade": score_to_grade(overall_score),
        "areas": areas,
    }
