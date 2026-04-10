"""
DV360 QC Subagent.

Pulls live Insertion Order settings from DV360 and compares them
against the translated campaign data to surface discrepancies.

Checks performed:
  - IO naming convention
  - Budget segments present and correctly formatted
  - IO objective set
  - IO type / subtype correct for channel
  - KPI type and value set
  - Pacing period and type set
  - Frequency cap configured

TODO: Replace stub API calls with real DV360 API reads once credentials available.
      DV360 Read API reference:
      GET /v3/advertisers/{advertiserId}/insertionOrders/{insertionOrderId}
"""

import os
from shared.models import QCCheck, QCResult

DV360_API_BASE      = "https://displayvideo.googleapis.com/v3"
DV360_ACCESS_TOKEN  = os.getenv("DV360_ACCESS_TOKEN", "")
DV360_ADVERTISER_ID = os.getenv("DV360_ADVERTISER_ID", "")

REQUIRED_IO_FIELDS = [
    "Name", "Io Objective", "Io Type", "Io Subtype",
    "Budget Type", "Kpi Type", "Kpi Value",
    "Pacing", "Pacing Rate",
]


def run(dv360_data: dict, dsp_result_id: str) -> QCResult:
    """
    QC check for a DV360 campaign.

    In production: reads each IO from the DV360 API and validates settings.
    Currently: validates structure of dv360_data and flags missing required fields.

    TODO: Uncomment API reads when DV360_ACCESS_TOKEN is available:
        GET /v3/advertisers/{advertiserId}/insertionOrders/{io_id}
        Compare Name, pacing, frequencyCap, kpi, budget against translated data.
    """
    checks = []
    ios = dv360_data.get("insertion_orders", [])

    # Check: at least one IO exists
    checks.append(QCCheck(
        field="IO count",
        expected="≥ 1",
        actual=str(len(ios)) if ios else "0",
        status="pass" if ios else "fail",
        note="No insertion orders found in translated data" if not ios else "",
    ))

    for i, io in enumerate(ios):
        label = io.get("Name", f"IO #{i}")

        # Check: required fields present
        for field in REQUIRED_IO_FIELDS:
            val = io.get(field)
            checks.append(QCCheck(
                field=f"{label} → {field}",
                expected="Set",
                actual="Set" if val else "Missing",
                status="pass" if val else "fail",
                note=f"Required field missing on IO '{label}'" if not val else "",
            ))

        # Check: budget segments parseable
        segs = io.get("Budget Segments", "")
        has_segs = segs and segs.strip().startswith("(")
        checks.append(QCCheck(
            field=f"{label} → Budget Segments",
            expected="(Budget;Start;End;;Desc;); format",
            actual="Valid format" if has_segs else repr(segs) or "Empty",
            status="pass" if has_segs else "fail",
            note="Budget segment string missing or malformed" if not has_segs else "",
        ))

        # Check: KPI value is a positive number
        kpi_val = io.get("Kpi Value")
        checks.append(QCCheck(
            field=f"{label} → Kpi Value",
            expected="> 0",
            actual=str(kpi_val),
            status="pass" if isinstance(kpi_val, (int, float)) and kpi_val > 0
                   else "fail",
            note="KPI value must be a positive number" if not (
                isinstance(kpi_val, (int, float)) and kpi_val > 0) else "",
        ))

    # TODO: Add live API checks once credentials are available:
    # - Pull IO from DV360 API, compare each field to translated data
    # - Verify budget segments match expected flight dates
    # - Verify frequency cap matches expected settings

    overall = "fail" if any(c.status == "fail" for c in checks) \
         else "warn" if any(c.status == "warn" for c in checks) \
         else "pass"

    return QCResult(
        dsp="DV360",
        campaign_id=dsp_result_id,
        checks=checks,
        overall=overall,
    )
