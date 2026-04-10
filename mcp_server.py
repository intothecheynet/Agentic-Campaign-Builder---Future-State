"""
Agentic Campaign Builder — MCP Server.

Exposes each agent as a separate MCP tool so both Claude Code
and the FastAPI app can call them via the Model Context Protocol.

Tools exposed:
  - translate_media_plan      (media-plan-translator agent)
  - generate_placement_names  (placement-name-generator agent)
  - build_ttd_campaign        (ttd-campaign-builder agent)
  - build_dv360_campaign      (dv360-campaign-builder agent)
  - build_amazon_campaign     (amazon-campaign-builder agent)
  - build_campaign            (full orchestrator — runs all agents end-to-end)
  - run_qc_check              (qc-platform agent — checks one DSP campaign)
  - run_full_qc               (qc-platform agent — checks all DSPs for a campaign)

Running as a stdio MCP server (Claude Code):
  python3 mcp_server.py

Running as a FastAPI-mounted MCP server:
  from mcp_server import create_mcp_app
  app.mount("/mcp", create_mcp_app())
"""

import json
import sys
import dataclasses
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from shared.models import CampaignInput, TranslatedCampaign, PlacementNames

from agents.media_plan_translator.agent import run as _translate_media_plan
from agents.placement_name_generator.agent import run as _generate_placement_names
from agents.ttd_campaign_builder.agent import run as _build_ttd_campaign
from agents.dv360_campaign_builder.agent import run as _build_dv360_campaign
from agents.amazon_campaign_builder.agent import run as _build_amazon_campaign
from orchestrator.orchestrator import run as _run_orchestrator
from agents.qc_platform.agent import run as _run_qc
from agents.qc_platform.subagents.ttd_qc_subagent   import run as _qc_ttd
from agents.qc_platform.subagents.dv360_qc_subagent import run as _qc_dv360


# ── Helpers ────────────────────────────────────────────────────────────────────

def _dataclass_to_dict(obj: Any) -> Any:
    """Recursively convert dataclasses to dicts for JSON serialization."""
    if dataclasses.is_dataclass(obj):
        return {k: _dataclass_to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, list):
        return [_dataclass_to_dict(i) for i in obj]
    return obj


def _ok(data: Any) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=json.dumps(_dataclass_to_dict(data), indent=2))]


def _err(message: str) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=json.dumps({"error": message}))]


# ── Server setup ───────────────────────────────────────────────────────────────

server = Server("campaign-builder")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="translate_media_plan",
            description=(
                "Translates Excel media-plan input files into structured campaign data "
                "for each DSP (TTD, DV360, Amazon). Returns a TranslatedCampaign JSON "
                "object containing the campaign name, objective, DSPs detected, and "
                "DSP-specific field mappings."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "media_brief_path": {
                        "type": "string",
                        "description": "Absolute path to the Media Brief Excel file."
                    },
                    "media_plan_path": {
                        "type": "string",
                        "description": "Absolute path to the Media Plan Excel file."
                    },
                    "audience_matrix_path": {
                        "type": "string",
                        "description": "Absolute path to the Audience Matrix Excel file."
                    },
                    "trafficking_sheet_path": {
                        "type": "string",
                        "description": "Absolute path to the Trafficking Sheet Excel file."
                    },
                },
                "required": [
                    "media_brief_path",
                    "media_plan_path",
                    "audience_matrix_path",
                    "trafficking_sheet_path",
                ],
            },
        ),
        types.Tool(
            name="generate_placement_names",
            description=(
                "Generates standardized placement names from a translated campaign. "
                "Accepts the JSON output of translate_media_plan. "
                "Returns a PlacementNames object with a list of name strings."
                "\n\nNote: naming convention is pending — returns a placeholder until confirmed."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "translated_campaign": {
                        "type": "object",
                        "description": (
                            "TranslatedCampaign JSON object from translate_media_plan. "
                            "Must include: campaign_name, lob, objective, dsps."
                        ),
                    },
                },
                "required": ["translated_campaign"],
            },
        ),
        types.Tool(
            name="build_ttd_campaign",
            description=(
                "Creates a campaign in The Trade Desk DSP via the TTD API. "
                "Accepts ttd_data (the ttd_data field from a TranslatedCampaign). "
                "Creates Campaign Sets, Campaigns, Ad Groups, and Budget Flights. "
                "\n\nNote: API calls are stubbed — set TTD_API_KEY and TTD_ADVERTISER_ID "
                "environment variables to activate real creation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ttd_data": {
                        "type": "object",
                        "description": (
                            "TTD-specific mapped data. Typically the ttd_data field "
                            "from the output of translate_media_plan."
                        ),
                    },
                },
                "required": ["ttd_data"],
            },
        ),
        types.Tool(
            name="build_dv360_campaign",
            description=(
                "Creates Insertion Orders in Google Display & Video 360 via the DV360 API. "
                "Accepts dv360_data (the dv360_data field from a TranslatedCampaign). "
                "\n\nNote: API calls are stubbed — set DV360_ACCESS_TOKEN and "
                "DV360_ADVERTISER_ID environment variables to activate real creation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dv360_data": {
                        "type": "object",
                        "description": (
                            "DV360-specific mapped data. Typically the dv360_data field "
                            "from the output of translate_media_plan."
                        ),
                    },
                },
                "required": ["dv360_data"],
            },
        ),
        types.Tool(
            name="build_amazon_campaign",
            description=(
                "Creates a campaign in Amazon DSP via the Amazon Advertising API. "
                "Accepts amazon_data (the amazon_data field from a TranslatedCampaign). "
                "\n\nNote: Not yet implemented — set AMAZON_CLIENT_ID, AMAZON_ACCESS_TOKEN, "
                "and AMAZON_PROFILE_ID environment variables when ready."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "amazon_data": {
                        "type": "object",
                        "description": (
                            "Amazon-specific mapped data. Typically the amazon_data field "
                            "from the output of translate_media_plan."
                        ),
                    },
                },
                "required": ["amazon_data"],
            },
        ),
        types.Tool(
            name="run_qc_check",
            description=(
                "Runs a quality check on a single DSP campaign after it has been built. "
                "Compares the translated campaign data against what was created in the DSP "
                "and returns a QCResult with pass / warn / fail per field. "
                "\n\nSupported DSPs: TTD, DV360. Amazon is a placeholder."
                "\n\nNote: API reads are stubbed — connects to live DSP APIs once credentials are set."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dsp": {
                        "type": "string",
                        "enum": ["TTD", "DV360", "Amazon"],
                        "description": "Which DSP to run QC against."
                    },
                    "dsp_data": {
                        "type": "object",
                        "description": "The DSP-specific mapped data (ttd_data, dv360_data, or amazon_data from translate_media_plan)."
                    },
                    "campaign_id": {
                        "type": "string",
                        "description": "The campaign ID returned by the build step (from DSPResult.campaign_id)."
                    },
                },
                "required": ["dsp", "dsp_data", "campaign_id"],
            },
        ),
        types.Tool(
            name="run_full_qc",
            description=(
                "Runs QC checks across all DSPs for a campaign. "
                "Accepts a TranslatedCampaign and a list of DSPResults, "
                "routes each to the appropriate DSP QC subagent, "
                "and returns a QCReport with overall pass / warn / fail. "
                "\n\nTypically called after build_campaign or after individual build steps."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "translated_campaign": {
                        "type": "object",
                        "description": "TranslatedCampaign JSON from translate_media_plan."
                    },
                    "dsp_results": {
                        "type": "array",
                        "description": "List of DSPResult objects returned by the build steps.",
                        "items": {"type": "object"},
                    },
                },
                "required": ["translated_campaign", "dsp_results"],
            },
        ),
        types.Tool(
            name="build_campaign",
            description=(
                "Runs the full campaign build pipeline end-to-end: "
                "translate media plan → generate placement names → create campaigns in each DSP. "
                "This is the main entry point for a complete campaign build. "
                "Returns an OrchestratorResult with campaign name, placement names, "
                "and per-DSP results."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "media_brief_path": {
                        "type": "string",
                        "description": "Absolute path to the Media Brief Excel file."
                    },
                    "media_plan_path": {
                        "type": "string",
                        "description": "Absolute path to the Media Plan Excel file."
                    },
                    "audience_matrix_path": {
                        "type": "string",
                        "description": "Absolute path to the Audience Matrix Excel file."
                    },
                    "trafficking_sheet_path": {
                        "type": "string",
                        "description": "Absolute path to the Trafficking Sheet Excel file."
                    },
                },
                "required": [
                    "media_brief_path",
                    "media_plan_path",
                    "audience_matrix_path",
                    "trafficking_sheet_path",
                ],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "translate_media_plan":
            campaign_input = CampaignInput(
                media_brief_path=arguments["media_brief_path"],
                media_plan_path=arguments["media_plan_path"],
                audience_matrix_path=arguments["audience_matrix_path"],
                trafficking_sheet_path=arguments["trafficking_sheet_path"],
            )
            result = _translate_media_plan(campaign_input)
            return _ok(result)

        elif name == "generate_placement_names":
            raw = arguments["translated_campaign"]
            translated = TranslatedCampaign(
                campaign_name=raw["campaign_name"],
                lob=raw["lob"],
                objective=raw["objective"],
                dsps=raw["dsps"],
                ttd_data=raw.get("ttd_data"),
                dv360_data=raw.get("dv360_data"),
                amazon_data=raw.get("amazon_data"),
            )
            result = _generate_placement_names(translated)
            return _ok(result)

        elif name == "build_ttd_campaign":
            result = _build_ttd_campaign(arguments["ttd_data"])
            return _ok(result)

        elif name == "build_dv360_campaign":
            result = _build_dv360_campaign(arguments["dv360_data"])
            return _ok(result)

        elif name == "build_amazon_campaign":
            result = _build_amazon_campaign(arguments["amazon_data"])
            return _ok(result)

        elif name == "run_qc_check":
            dsp        = arguments["dsp"]
            dsp_data   = arguments["dsp_data"]
            campaign_id = arguments["campaign_id"]
            if dsp == "TTD":
                result = _qc_ttd(dsp_data, campaign_id)
            elif dsp == "DV360":
                result = _qc_dv360(dsp_data, campaign_id)
            else:
                from agents.qc_platform.subagents.amazon_qc_subagent import run as _qc_amazon
                result = _qc_amazon(dsp_data, campaign_id)
            return _ok(result)

        elif name == "run_full_qc":
            from shared.models import DSPResult as _DSPResult
            raw = arguments["translated_campaign"]
            translated = TranslatedCampaign(
                campaign_name=raw["campaign_name"],
                lob=raw["lob"],
                objective=raw["objective"],
                dsps=raw["dsps"],
                ttd_data=raw.get("ttd_data"),
                dv360_data=raw.get("dv360_data"),
                amazon_data=raw.get("amazon_data"),
            )
            dsp_results = [
                _DSPResult(
                    dsp=r["dsp"],
                    success=r["success"],
                    campaign_id=r.get("campaign_id"),
                    error=r.get("error"),
                )
                for r in arguments["dsp_results"]
            ]
            result = _run_qc(translated, dsp_results)
            return _ok(result)

        elif name == "build_campaign":
            campaign_input = CampaignInput(
                media_brief_path=arguments["media_brief_path"],
                media_plan_path=arguments["media_plan_path"],
                audience_matrix_path=arguments["audience_matrix_path"],
                trafficking_sheet_path=arguments["trafficking_sheet_path"],
            )
            result = _run_orchestrator(campaign_input)
            return _ok(result)

        else:
            return _err(f"Unknown tool: {name}")

    except Exception as exc:
        return _err(str(exc))


# ── stdio entry point (Claude Code) ────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


# ── FastAPI-mountable app (Option 3) ───────────────────────────────────────────

def create_mcp_app():
    """
    Returns an ASGI app that serves the MCP server over HTTP/SSE.
    Mount this into your FastAPI app:

        from mcp_server import create_mcp_app
        app.mount("/mcp", create_mcp_app())

    Then point clients at: http://localhost:8000/mcp/sse
    """
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount

    sse = SseServerTransport("/mcp/messages")

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    return Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=sse.handle_post_message),
        ]
    )
