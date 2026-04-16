"""
Campaign Builder Orchestrator.

Receives a campaign input, coordinates all specialist agents,
and returns a full OrchestratorResult.

Flow:
  1. media-plan-translator    → TranslatedCampaign
  2. placement-name-generator → PlacementNames
  3. DSP agents (TTD / DV360 / Amazon) → DSPResult each (run in parallel)
  4. QC checks
  5. Collate and return OrchestratorResult
"""

import asyncio
from shared.models import CampaignInput, OrchestratorResult

from agents.media_plan_translator.agent import run as translate_media_plan
from agents.placement_name_generator.agent import run as generate_placement_names
from agents.ttd_campaign_builder.agent import run as build_ttd_campaign
from agents.dv360_campaign_builder.agent import run as build_dv360_campaign
from agents.amazon_campaign_builder.agent import run as build_amazon_campaign
from agents.qc_platform.agent import run as run_qc


async def run_async(campaign_input: CampaignInput) -> OrchestratorResult:
    """
    Main orchestrator entry point (async).
    DSP builders run concurrently via asyncio.gather().
    """

    print(f"[Orchestrator] Starting campaign build for inputs: {campaign_input}")

    # ── Step 1: Translate media plan ─────────────────────────────────────────
    print("[Orchestrator] Calling media-plan-translator...")
    translated = await asyncio.to_thread(translate_media_plan, campaign_input)
    print(f"[Orchestrator] Campaign: {translated.campaign_name} | DSPs: {translated.dsps}")

    # ── Step 2: Generate placement names ─────────────────────────────────────
    print("[Orchestrator] Calling placement-name-generator...")
    placement_names = await asyncio.to_thread(generate_placement_names, translated)
    print(f"[Orchestrator] Generated {len(placement_names.names)} placement names")

    # ── Step 3: Build campaigns in each DSP — run in parallel ────────────────
    tasks = {}
    if "TTD" in translated.dsps and translated.ttd_data:
        tasks["TTD"] = asyncio.to_thread(build_ttd_campaign, translated.ttd_data)
    if "DV360" in translated.dsps and translated.dv360_data:
        tasks["DV360"] = asyncio.to_thread(build_dv360_campaign, translated.dv360_data)
    if "Amazon" in translated.dsps and translated.amazon_data:
        tasks["Amazon"] = asyncio.to_thread(build_amazon_campaign, translated.amazon_data)

    if tasks:
        dsp_names = list(tasks.keys())
        print(f"[Orchestrator] Building DSPs in parallel: {', '.join(dsp_names)}")
        results = await asyncio.gather(*tasks.values())
        dsp_results = list(results)
    else:
        dsp_results = []

    # ── Step 4: QC checks ────────────────────────────────────────────────────
    print("[Orchestrator] Running QC checks...")
    qc_report = await asyncio.to_thread(run_qc, translated, dsp_results)
    overall_icon = "✓" if qc_report.overall == "pass" \
               else "⚠" if qc_report.overall == "warn" \
               else "✗"
    print(f"[Orchestrator] QC {overall_icon} {qc_report.overall.upper()}")
    for r in qc_report.results:
        print(f"  {r.dsp}: {r.passed} passed, {r.warned} warned, {r.failed} failed")

    # ── Step 5: Collate results ───────────────────────────────────────────────
    orchestrator_result = OrchestratorResult(
        campaign_name=translated.campaign_name,
        placement_names=placement_names,
        dsp_results=dsp_results,
        qc_report=qc_report,
    )

    print("[Orchestrator] Complete.")
    for r in dsp_results:
        status = "✓" if r.success else "✗"
        print(f"  {status} {r.dsp}: {r.campaign_id or r.error}")

    return orchestrator_result


def run(campaign_input: CampaignInput) -> OrchestratorResult:
    """Sync wrapper around run_async — for callers that cannot await."""
    return asyncio.run(run_async(campaign_input))
