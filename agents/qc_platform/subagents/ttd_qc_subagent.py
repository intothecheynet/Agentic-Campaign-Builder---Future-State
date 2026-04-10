"""
TTD QC Subagent.

Pulls live campaign settings from The Trade Desk and compares them
against the translated campaign data to surface discrepancies.

Checks performed:
  - Campaign naming convention
  - Budget vs media plan
  - Flight dates vs media plan
  - Goal Type matches channel defaults
  - Goal Value within expected range
  - Base Bid / Max Bid within expected range
  - Marketplace matches channel type
  - Pacing Mode set correctly
  - Audience segments applied

TODO: Replace stub API calls with real TTD API reads once credentials available.
      TTD Read API reference: https://api.thetradedesk.com/v3/campaign
"""

import os
from shared.models import QCCheck, QCResult

TTD_API_BASE   = "https://api.thetradedesk.com/v3"
TTD_API_KEY    = os.getenv("TTD_API_KEY", "")


def _check(field: str, expected, actual, tolerance=None) -> QCCheck:
    """
    Compare expected vs actual and return a QCCheck.
    Numeric tolerance: warn if within 10% of expected, fail if further off.
    """
    exp_str = str(expected)
    act_str = str(actual)

    if expected == actual:
        return QCCheck(field=field, expected=exp_str, actual=act_str, status="pass")

    if tolerance is not None and isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        pct_diff = abs(actual - expected) / max(abs(expected), 1)
        if pct_diff <= tolerance:
            return QCCheck(field=field, expected=exp_str, actual=act_str,
                           status="warn", note=f"{pct_diff:.1%} deviation")
        return QCCheck(field=field, expected=exp_str, actual=act_str,
                       status="fail", note=f"{pct_diff:.1%} deviation — exceeds tolerance")

    return QCCheck(field=field, expected=exp_str, actual=act_str, status="fail")


def run(ttd_data: dict, dsp_result_id: str) -> QCResult:
    """
    QC check for a TTD campaign.

    In production: pulls live data from TTD API and compares field-by-field.
    Currently: validates structure of ttd_data and flags any missing required fields.

    TODO: Uncomment API reads when TTD_API_KEY is available:
        GET /v3/campaignset/{campaign_set_id}
        GET /v3/campaign/{campaign_id}
        GET /v3/adgroup/{ad_group_id}
        GET /v3/budgetflight/{flight_id}
    """
    checks = []

    # ── Stub: validate translated data structure before API creation ───────────
    # In production these checks would compare translated data vs live API reads.

    campaigns  = ttd_data.get("campaigns", [])
    ad_groups  = ttd_data.get("ad_groups", [])
    flights    = ttd_data.get("budget_flights", [])

    # Check: at least one campaign exists
    checks.append(_check(
        "Campaign count",
        expected="≥ 1",
        actual=str(len(campaigns)) if campaigns else "0",
    ) if campaigns else QCCheck(
        field="Campaign count", expected="≥ 1", actual="0",
        status="fail", note="No campaigns found in translated data"
    ))

    # Check: every campaign has a name
    unnamed = [i for i, c in enumerate(campaigns) if not c.get("Campaign Name")]
    checks.append(QCCheck(
        field="Campaign names",
        expected="All campaigns named",
        actual="Missing names" if unnamed else "All named",
        status="fail" if unnamed else "pass",
        note=f"Campaigns at index {unnamed} have no name" if unnamed else "",
    ))

    # Check: every campaign has Goal Type set
    missing_goal = [c.get("Campaign Name", f"#{i}") for i, c in enumerate(campaigns)
                    if not c.get("Goal Type")]
    checks.append(QCCheck(
        field="Goal Type",
        expected="Set on all campaigns",
        actual="Missing on some" if missing_goal else "All set",
        status="fail" if missing_goal else "pass",
        note=f"Missing on: {missing_goal}" if missing_goal else "",
    ))

    # Check: budget flights match campaign count
    flight_campaigns = {f.get("Campaign Name") for f in flights}
    campaign_names   = {c.get("Campaign Name") for c in campaigns}
    unflighted = campaign_names - flight_campaigns
    checks.append(QCCheck(
        field="Budget flight coverage",
        expected="Every campaign has a budget flight",
        actual="All covered" if not unflighted else f"Missing flights: {unflighted}",
        status="pass" if not unflighted else "fail",
    ))

    # Check: ad groups link to known campaigns
    orphan_ags = [ag.get("Ad Group Name", "?") for ag in ad_groups
                  if ag.get("Campaign Name") not in campaign_names]
    checks.append(QCCheck(
        field="Ad group campaign links",
        expected="All ad groups linked to a campaign",
        actual="All linked" if not orphan_ags else f"Orphaned: {orphan_ags}",
        status="pass" if not orphan_ags else "warn",
        note="These ad groups reference unknown campaigns" if orphan_ags else "",
    ))

    # TODO: Add live API checks once credentials are available:
    # - GET campaign and compare Goal Type, Goal Value, dates, pacing
    # - GET ad groups and compare bids, marketplace, audience
    # - GET budget flights and compare amounts and dates

    overall = "fail" if any(c.status == "fail" for c in checks) \
         else "warn" if any(c.status == "warn" for c in checks) \
         else "pass"

    return QCResult(
        dsp="TTD",
        campaign_id=dsp_result_id,
        checks=checks,
        overall=overall,
    )
