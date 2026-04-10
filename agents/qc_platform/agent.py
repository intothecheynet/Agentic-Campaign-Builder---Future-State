"""
QC Platform Agent.

Runs post-build quality checks across all DSPs to verify that created
campaigns match the source media plan. Each DSP has a dedicated subagent.

Flow:
  1. Receives the TranslatedCampaign and the list of DSPResults from the orchestrator
  2. Routes each DSP result to the appropriate QC subagent
  3. Each subagent compares translated data vs live API reads (stubbed)
  4. Returns a QCReport with pass / warn / fail per check per DSP

QC subagents:
  - ttd_qc_subagent     → validates TTD campaigns, ad groups, budget flights
  - dv360_qc_subagent   → validates DV360 insertion orders
  - amazon_qc_subagent  → placeholder, implement with Amazon mapper

TODO: Connect to your QC platform (e.g. Looker, internal dashboard, Airtable)
      to push results and flag issues for trader review.
"""

from shared.models import TranslatedCampaign, DSPResult, QCCheck, QCResult, QCReport

from agents.qc_platform.subagents.ttd_qc_subagent     import run as qc_ttd
from agents.qc_platform.subagents.dv360_qc_subagent   import run as qc_dv360
from agents.qc_platform.subagents.amazon_qc_subagent  import run as qc_amazon


def run(translated: TranslatedCampaign, dsp_results: list[DSPResult]) -> QCReport:
    """
    Runs QC checks for every DSP that was successfully built.
    Skips DSPs that failed during campaign creation.

    Returns a QCReport with one QCResult per DSP.
    """
    qc_results = []

    for dsp_result in dsp_results:
        if not dsp_result.success:
            # Skip QC for DSPs that failed to build — nothing to check
            qc_results.append(QCResult(
                dsp=dsp_result.dsp,
                campaign_id="N/A",
                checks=[QCCheck(
                    field="Build status",
                    expected="Success",
                    actual="Failed",
                    status="fail",
                    note=f"Campaign build failed: {dsp_result.error}. QC skipped.",
                )],
                overall="fail",
            ))
            continue

        campaign_id = dsp_result.campaign_id or "unknown"

        if dsp_result.dsp == "TTD" and translated.ttd_data:
            result = qc_ttd(translated.ttd_data, campaign_id)

        elif dsp_result.dsp == "DV360" and translated.dv360_data:
            result = qc_dv360(translated.dv360_data, campaign_id)

        elif dsp_result.dsp == "Amazon" and translated.amazon_data:
            result = qc_amazon(translated.amazon_data, campaign_id)

        else:
            result = QCResult(
                dsp=dsp_result.dsp,
                campaign_id=campaign_id,
                checks=[QCCheck(
                    field="Data availability",
                    expected="Translated data present",
                    actual="No translated data found",
                    status="warn",
                    note="QC skipped — no source data to compare against.",
                )],
                overall="warn",
            )

        qc_results.append(result)

    # Overall report status: worst result across all DSPs
    if any(r.overall == "fail" for r in qc_results):
        overall = "fail"
    elif any(r.overall == "warn" for r in qc_results):
        overall = "warn"
    else:
        overall = "pass"

    return QCReport(
        campaign_name=translated.campaign_name,
        results=qc_results,
        overall=overall,
    )
