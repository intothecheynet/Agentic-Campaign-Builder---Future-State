"""
TTD Budget Flight Subagent.

Creates Budget Flights via the TTD API, linked to their parent ad groups.
TODO: Replace stub responses with real API calls once credentials are available.

TTD API reference:
  POST /v3/budgetflight — create a budget flight
"""

import requests


def create_budget_flights(ttd_data: dict, ad_group_ids: list, api_base: str, api_token: str) -> dict:
    """
    Creates Budget Flights in TTD linked to the provided ad group IDs.
    Returns dict with list of flight_ids.
    """
    headers = {
        "TTD-Auth": api_token,
        "Content-Type": "application/json",
    }

    flight_ids = []

    for i, row in enumerate(ttd_data.get("budget_flights", [])):
        # Match flight to its ad group by index
        ad_group_id = ad_group_ids[i] if i < len(ad_group_ids) else None

        payload = {
            "AdGroupId": ad_group_id,
            "FlightBudget": row.get("Flight Budget (in advertiser currency)", ""),
            "ImpressionBudget": row.get("Impression Budget", ""),
            "StartDateInclusiveUTC": row.get("Start Date Inclusive UTC", ""),
            "EndDateExclusiveUTC": row.get("End Date Exclusive UTC", ""),
            "Action": row.get("Action", "New"),
        }
        # TODO: Uncomment when API credentials are available
        # response = requests.post(f"{api_base}/budgetflight", json=payload, headers=headers)
        # response.raise_for_status()
        # flight_ids.append(response.json()["FlightId"])

        # Stub — remove when real API call is active
        flight_ids.append(f"STUB_FLIGHT_{i}")

    return {"flight_ids": flight_ids}
