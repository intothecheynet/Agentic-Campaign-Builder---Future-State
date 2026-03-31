"""
TTD Ad Group Subagent.

Creates Ad Groups via the TTD API, linked to their parent campaigns.
TODO: Replace stub responses with real API calls once credentials are available.

TTD API reference:
  POST /v3/adgroup — create an ad group
"""

import requests


def create_ad_groups(ttd_data: dict, campaign_ids: list, api_base: str, api_token: str) -> dict:
    """
    Creates Ad Groups in TTD linked to the provided campaign IDs.
    Returns dict with list of ad_group_ids.
    """
    headers = {
        "TTD-Auth": api_token,
        "Content-Type": "application/json",
    }

    ad_group_ids = []

    for i, row in enumerate(ttd_data.get("ad_groups", [])):
        # Link to first campaign if multiple exist; extend logic as needed
        campaign_id = campaign_ids[0] if campaign_ids else None

        payload = {
            "CampaignId": campaign_id,
            "AdGroupName": row.get("Ad Group Name", ""),
            "Channel": row.get("Channel", ""),
            "GoalType": row.get("Goal Type", ""),
            "GoalValue": row.get("Goal Value", ""),
            "BaseBid": row.get("Base Bid", ""),
            "MaxBid": row.get("Max Bid", ""),
            "Marketplace": row.get("Marketplace", ""),
            "Audience": row.get("Audience", ""),
            "AudienceExcluder": row.get("Audience Excluder", ""),
        }
        # TODO: Uncomment when API credentials are available
        # response = requests.post(f"{api_base}/adgroup", json=payload, headers=headers)
        # response.raise_for_status()
        # ad_group_ids.append(response.json()["AdGroupId"])

        # Stub — remove when real API call is active
        ad_group_ids.append(f"STUB_ADGROUP_{row.get('Ad Group Name', '')}")

    return {"ad_group_ids": ad_group_ids}
