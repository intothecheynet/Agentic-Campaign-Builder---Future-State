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
