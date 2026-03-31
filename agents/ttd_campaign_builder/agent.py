"""
TTD Campaign Builder Agent.

Takes translated TTD campaign data and creates the campaign
in The Trade Desk via the TTD API.

Subagents:
  - campaign_subagent.py     : Creates Campaign Sets and Campaigns
  - ad_group_subagent.py     : Creates Ad Groups
  - budget_flight_subagent.py: Creates Budget Flights

TTD API docs: https://api.thetradedesk.com/v3/
TODO: Add API credentials to .env before running.
"""

import os
from shared.models import DSPResult

from agents.ttd_campaign_builder.subagents.campaign_subagent import create_campaigns
from agents.ttd_campaign_builder.subagents.ad_group_subagent import create_ad_groups
from agents.ttd_campaign_builder.subagents.budget_flight_subagent import create_budget_flights


# ── TTD API config ─────────────────────────────────────────────────────────────
# TODO: Load from environment variables
TTD_API_BASE  = "https://api.thetradedesk.com/v3"
TTD_API_TOKEN = os.getenv("TTD_API_TOKEN", "")
TTD_ADVERTISER_ID = os.getenv("TTD_ADVERTISER_ID", "")


def run(ttd_data: dict) -> DSPResult:
    """
    Orchestrates the full TTD campaign creation via subagents.
    Returns a DSPResult with the created campaign ID or error.
    """
    if not TTD_API_TOKEN:
        return DSPResult(
            dsp="TTD",
            success=False,
            error="TTD_API_TOKEN not set in environment variables."
        )

    try:
        # Step 1: Create Campaign Sets + Campaigns
        campaign_result = create_campaigns(
            ttd_data=ttd_data,
            api_base=TTD_API_BASE,
            api_token=TTD_API_TOKEN,
            advertiser_id=TTD_ADVERTISER_ID,
        )

        # Step 2: Create Ad Groups (linked to campaigns)
        ad_group_result = create_ad_groups(
            ttd_data=ttd_data,
            campaign_ids=campaign_result["campaign_ids"],
            api_base=TTD_API_BASE,
            api_token=TTD_API_TOKEN,
        )

        # Step 3: Create Budget Flights (linked to ad groups)
        flight_result = create_budget_flights(
            ttd_data=ttd_data,
            ad_group_ids=ad_group_result["ad_group_ids"],
            api_base=TTD_API_BASE,
            api_token=TTD_API_TOKEN,
        )

        return DSPResult(
            dsp="TTD",
            success=True,
            campaign_id=campaign_result.get("campaign_set_id"),
            details={
                "campaigns":      campaign_result["campaign_ids"],
                "ad_groups":      ad_group_result["ad_group_ids"],
                "budget_flights": flight_result["flight_ids"],
            }
        )

    except Exception as e:
        return DSPResult(dsp="TTD", success=False, error=str(e))
