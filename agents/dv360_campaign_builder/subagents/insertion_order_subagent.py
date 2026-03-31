"""
DV360 Insertion Order Subagent.

Creates Insertion Orders via the DV360 API.
TODO: Replace stub responses with real API calls once credentials are available.

DV360 API reference:
  POST /v3/advertisers/{advertiserId}/insertionOrders
"""

import requests


def create_insertion_orders(dv360_data: dict, api_base: str, access_token: str, advertiser_id: str) -> dict:
    """
    Creates Insertion Orders in DV360.
    Returns dict with list of io_ids.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    io_ids = []

    for row in dv360_data.get("insertion_orders", []):
        payload = {
            "displayName":  row.get("Name", ""),
            "entityStatus": "ENTITY_STATUS_ACTIVE",
            "ioType":       "INSERTION_ORDER_TYPE_RTB",
            "pacing": {
                "pacingPeriod": row.get("Pacing", ""),
                "pacingType":   row.get("Pacing Rate", ""),
                "dailyMaxMicros": row.get("Pacing Amount", ""),
            },
            "frequencyCap": {
                "unlimited": row.get("Frequency Enabled", "") == "FALSE",
                "maxImpressions": row.get("Frequency Exposures", ""),
                "timeUnit": row.get("Frequency Period", ""),
                "timeUnitCount": row.get("Frequency Amount", ""),
            },
            "kpi": {
                "kpiType":  row.get("Kpi Type", ""),
                "kpiValue": row.get("Kpi Value", ""),
            },
            "budget": {
                "budgetUnit": "BUDGET_UNIT_CURRENCY" if row.get("Budget Type") == "Amount" else "BUDGET_UNIT_IMPRESSIONS",
                "budgetSegments": _parse_budget_segments(row.get("Budget Segments", "")),
            },
        }
        # TODO: Uncomment when API credentials are available
        # response = requests.post(
        #     f"{api_base}/advertisers/{advertiser_id}/insertionOrders",
        #     json=payload,
        #     headers=headers
        # )
        # response.raise_for_status()
        # io_ids.append(response.json()["insertionOrderId"])

        # Stub — remove when real API call is active
        io_ids.append(f"STUB_IO_{row.get('Name', '')}")

    return {"io_ids": io_ids}


def _parse_budget_segments(segment_str: str) -> list:
    """
    Parse DV360 SDF budget segment string into API payload format.
    Input format: (Budget;Start;End;;Description;);
    """
    segments = []
    if not segment_str:
        return segments

    for part in segment_str.split(");"):
        part = part.strip().lstrip("(")
        if not part:
            continue
        fields = part.split(";")
        if len(fields) >= 3:
            segments.append({
                "budgetAmountMicros": str(int(float(fields[0]) * 1_000_000)) if fields[0] else "",
                "dateRange": {
                    "startDate": fields[1],
                    "endDate":   fields[2],
                },
                "description": fields[4] if len(fields) > 4 else "",
            })
    return segments
