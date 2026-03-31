"""
TTD Campaign Subagent.

Creates Campaign Sets and Campaigns via the TTD API.
TODO: Replace stub responses with real API calls once credentials are available.

TTD API reference:
  POST /v3/campaignset  — create a campaign set
  POST /v3/campaign     — create a campaign
"""

import requests


def create_campaigns(ttd_data: dict, api_base: str, api_token: str, advertiser_id: str) -> dict:
    """
    Creates one Campaign Set and one or more Campaigns in TTD.
    Returns dict with campaign_set_id and list of campaign_ids.
    """
    headers = {
        "TTD-Auth": api_token,
        "Content-Type": "application/json",
    }

    campaign_set_ids = []
    campaign_ids = []

    # ── Create Campaign Sets ──────────────────────────────────────────────────
    for row in ttd_data.get("campaign_sets", []):
        payload = {
            "AdvertiserId": advertiser_id,
            "CampaignSetName": row.get("Campaign Set Name", ""),
            "IOId": row.get("IO ID", ""),
        }
        # TODO: Uncomment when API credentials are available
        # response = requests.post(f"{api_base}/campaignset", json=payload, headers=headers)
        # response.raise_for_status()
        # campaign_set_ids.append(response.json()["CampaignSetId"])

        # Stub — remove when real API call is active
        campaign_set_ids.append(f"STUB_CAMPAIGN_SET_{row.get('Campaign Set Name', '')}")

    # ── Create Campaigns ──────────────────────────────────────────────────────
    for row in ttd_data.get("campaigns", []):
        payload = {
            "AdvertiserId": advertiser_id,
            "CampaignName": row.get("Campaign Name", ""),
            "Description": row.get("Description", ""),
            "Objective": row.get("Objective", ""),
            "PrimaryChannel": row.get("Primary Channel", ""),
            "TimeZoneId": row.get("Time Zone ID", ""),
            "PacingMode": row.get("Pacing Mode", ""),
        }
        # TODO: Uncomment when API credentials are available
        # response = requests.post(f"{api_base}/campaign", json=payload, headers=headers)
        # response.raise_for_status()
        # campaign_ids.append(response.json()["CampaignId"])

        # Stub — remove when real API call is active
        campaign_ids.append(f"STUB_CAMPAIGN_{row.get('Campaign Name', '')}")

    return {
        "campaign_set_id": campaign_set_ids[0] if campaign_set_ids else None,
        "campaign_ids": campaign_ids,
    }
