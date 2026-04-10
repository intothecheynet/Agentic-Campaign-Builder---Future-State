"""
Campaign Builder Orchestrator.

Receives a campaign input, coordinates all specialist agents,
and returns a full OrchestratorResult.

Flow:
  1. media-plan-translator  → TranslatedCampaign
  2. placement-name-generator → PlacementNames
  3. DSP agents (TTD / DV360 / Amazon) → DSPResult each (run in parallel)
  4. Collate and return OrchestratorResult
"""

import anthropic
import json
from shared.models import CampaignInput, OrchestratorResult, PlacementNames, DSPResult

from agents.media_plan_translator.agent import run as translate_media_plan
from agents.placement_name_generator.agent import run as generate_placement_names
from agents.ttd_campaign_builder.agent import run as build_ttd_campaign
from agents.dv360_campaign_builder.agent import run as build_dv360_campaign
from agents.amazon_campaign_builder.agent import run as build_amazon_campaign
from agents.qc_platform.agent import run as run_qc


def run(campaign_input: CampaignInput) -> OrchestratorResult:
    """
    Main orchestrator entry point.
    Calls each specialist agent in sequence, then DSP agents.
    """

    print(f"[Orchestrator] Starting campaign build for inputs: {campaign_input}")

    # ── Step 1: Translate media plan ─────────────────────────────────────────
    print("[Orchestrator] Calling media-plan-translator...")
    translated = translate_media_plan(campaign_input)
    print(f"[Orchestrator] Campaign: {translated.campaign_name} | DSPs: {translated.dsps}")

    # ── Step 2: Generate placement names ─────────────────────────────────────
    print("[Orchestrator] Calling placement-name-generator...")
    placement_names = generate_placement_names(translated)
    print(f"[Orchestrator] Generated {len(placement_names.names)} placement names")

    # ── Step 3: Build campaigns in each DSP ──────────────────────────────────
    dsp_results = []

    if "TTD" in translated.dsps and translated.ttd_data:
        print("[Orchestrator] Calling ttd-campaign-builder...")
        result = build_ttd_campaign(translated.ttd_data)
        dsp_results.append(result)

    if "DV360" in translated.dsps and translated.dv360_data:
        print("[Orchestrator] Calling dv360-campaign-builder...")
        result = build_dv360_campaign(translated.dv360_data)
        dsp_results.append(result)

    if "Amazon" in translated.dsps and translated.amazon_data:
        print("[Orchestrator] Calling amazon-campaign-builder...")
        result = build_amazon_campaign(translated.amazon_data)
        dsp_results.append(result)

    # ── Step 4: QC checks ────────────────────────────────────────────────────
    print("[Orchestrator] Running QC checks...")
    qc_report = run_qc(translated, dsp_results)
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
