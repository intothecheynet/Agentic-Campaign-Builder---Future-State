"""
Amazon DSP QC Subagent.

Pulls live campaign settings from Amazon DSP and compares them
against the translated campaign data to surface discrepancies.

Checks performed (planned):
  - Campaign naming convention
  - Budget vs media plan
  - Flight dates vs media plan
  - Goal type and value
  - Audience segments applied
  - Supply source configuration

TODO: Implement once Amazon DSP mapper and API credentials are available.
      Amazon DSP Read API reference:
      https://advertising.amazon.com/API/docs/en-us/dsp-campaign-builder
"""

import os
from shared.models import QCCheck, QCResult

AMAZON_API_BASE     = "https://advertising-api.amazon.com"
AMAZON_ACCESS_TOKEN = os.getenv("AMAZON_ACCESS_TOKEN", "")
AMAZON_PROFILE_ID   = os.getenv("AMAZON_PROFILE_ID", "")


def run(amazon_data: dict, dsp_result_id: str) -> QCResult:
    """
    QC check for an Amazon DSP campaign.

    TODO: Implement once Amazon DSP mapper is built and credentials are available.
          Pattern follows TTD and DV360 QC subagents:
          1. Read live campaign data from Amazon DSP API
          2. Compare each field against amazon_data (translated source)
          3. Return QCResult with pass/warn/fail per check

    TODO: API reads to implement:
        GET /dsp/campaigns/{campaignId}
        GET /dsp/lineItems?campaignId={campaignId}
        Compare budgets, dates, goals, audiences against translated data.
    """
    return QCResult(
        dsp="Amazon",
        campaign_id=dsp_result_id,
        checks=[
            QCCheck(
                field="Amazon QC",
                expected="Implemented",
                actual="Not yet implemented",
                status="warn",
                note="Amazon DSP QC subagent is a placeholder — implement once mapper and credentials are ready.",
            )
        ],
        overall="warn",
    )
