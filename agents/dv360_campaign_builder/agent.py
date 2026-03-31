"""
DV360 Campaign Builder Agent.

Takes translated DV360 campaign data and creates Insertion Orders
in Google Display & Video 360 via the DV360 API.

DV360 API docs: https://developers.google.com/display-video/api/reference/rest
TODO: Add API credentials to .env before running.
      DV360 uses OAuth 2.0 — set up a service account with DV360 API access.
"""

import os
from shared.models import DSPResult

from agents.dv360_campaign_builder.subagents.insertion_order_subagent import create_insertion_orders


# ── DV360 API config ───────────────────────────────────────────────────────────
# TODO: Load from environment variables
DV360_API_BASE    = "https://displayvideo.googleapis.com/v3"
DV360_ADVERTISER_ID = os.getenv("DV360_ADVERTISER_ID", "")
DV360_ACCESS_TOKEN  = os.getenv("DV360_ACCESS_TOKEN", "")  # OAuth 2.0 bearer token


def run(dv360_data: dict) -> DSPResult:
    """
    Orchestrates DV360 campaign creation via subagents.
    Returns a DSPResult with created IO IDs or error.
    """
    if not DV360_ACCESS_TOKEN:
        return DSPResult(
            dsp="DV360",
            success=False,
            error="DV360_ACCESS_TOKEN not set in environment variables."
        )

    try:
        io_result = create_insertion_orders(
            dv360_data=dv360_data,
            api_base=DV360_API_BASE,
            access_token=DV360_ACCESS_TOKEN,
            advertiser_id=DV360_ADVERTISER_ID,
        )

        return DSPResult(
            dsp="DV360",
            success=True,
            campaign_id=io_result["io_ids"][0] if io_result["io_ids"] else None,
            details={"insertion_order_ids": io_result["io_ids"]}
        )

    except Exception as e:
        return DSPResult(dsp="DV360", success=False, error=str(e))
