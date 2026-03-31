"""
Amazon DSP Campaign Builder Agent.

Takes translated Amazon campaign data and creates campaigns
via the Amazon DSP API.

Amazon DSP API docs: https://advertising.amazon.com/API/docs/en-us/dsp-campaign-builder
TODO: Add API credentials to .env before running.
TODO: Implement Amazon mapper in Campaign Builder repo (currently stub).
"""

import os
from shared.models import DSPResult


# ── Amazon DSP API config ──────────────────────────────────────────────────────
# TODO: Load from environment variables
AMAZON_API_BASE    = "https://advertising-api.amazon.com"
AMAZON_CLIENT_ID   = os.getenv("AMAZON_CLIENT_ID", "")
AMAZON_ACCESS_TOKEN = os.getenv("AMAZON_ACCESS_TOKEN", "")
AMAZON_PROFILE_ID  = os.getenv("AMAZON_PROFILE_ID", "")


def run(amazon_data: dict) -> DSPResult:
    """
    Orchestrates Amazon DSP campaign creation.
    TODO: Implement once Amazon mapper and API credentials are available.
    """
    if not AMAZON_ACCESS_TOKEN:
        return DSPResult(
            dsp="Amazon",
            success=False,
            error="AMAZON_ACCESS_TOKEN not set in environment variables."
        )

    # TODO: Implement subagents for Amazon campaign creation
    # from agents.amazon_campaign_builder.subagents.campaign_subagent import create_campaigns
    # from agents.amazon_campaign_builder.subagents.line_item_subagent import create_line_items

    return DSPResult(
        dsp="Amazon",
        success=False,
        error="Amazon DSP campaign builder not yet implemented."
    )
