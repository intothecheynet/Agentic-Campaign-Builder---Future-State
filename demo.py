"""
Agentic Campaign Builder — Demo Script.

Simulates a full end-to-end campaign build using realistic mock data.
No Excel files or API credentials required.

Run:
  python3 demo.py

What this demonstrates:
  1. Media Plan Translator  — parses inputs and maps to DSP-specific formats
  2. Placement Name Generator — generates standardized placement names
  3. TTD Campaign Builder   — creates Campaign Sets, Campaigns, Ad Groups, Budget Flights
  4. DV360 Campaign Builder — creates Insertion Orders
  5. Orchestrator           — coordinates all agents and returns a unified result
"""

import time
import json


# ── Console helpers ────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"

def header(text: str):
    width = 62
    print()
    print(BOLD + "─" * width + RESET)
    print(BOLD + f"  {text}" + RESET)
    print(BOLD + "─" * width + RESET)

def step(icon: str, label: str, detail: str = ""):
    print(f"  {icon}  {BOLD}{label}{RESET}" + (f"  {DIM}{detail}{RESET}" if detail else ""))

def substep(text: str):
    print(f"       {DIM}↳ {text}{RESET}")

def success(label: str, value: str = ""):
    print(f"  {GREEN}✓{RESET}  {label}" + (f"  {DIM}{value}{RESET}" if value else ""))

def warn(label: str):
    print(f"  {YELLOW}⚠{RESET}  {DIM}{label}{RESET}")

def pause(ms: int = 400):
    time.sleep(ms / 1000)


# ── Mock campaign data ─────────────────────────────────────────────────────────
# Represents a real-world Q2 brand awareness campaign across TTD and DV360.

MOCK_CAMPAIGN = {
    "campaign_name": "Acme_BrandAwareness_Q2_2026",
    "lob":           "Brand",
    "objective":     "Awareness",
    "dsps":          ["TTD", "DV360"],
    "flight":        "4/1/2026 - 6/30/2026",
    "total_budget":  500_000,
}

MOCK_TTD_DATA = {
    "campaign_set_name": "Acme_BrandAwareness_Q2_2026",
    "campaigns": [
        {
            "Campaign Name":   "Acme_Brand_CTV_Q2_2026",
            "Channel":         "CTV",
            "Budget":          200_000,
            "Start Date":      "04/01/2026",
            "End Date":        "06/30/2026",
            "Goal Type":       "CPCV",
            "Goal Value":      0.04,
            "Pacing":          "Even",
        },
        {
            "Campaign Name":   "Acme_Brand_Display_Q2_2026",
            "Channel":         "Display",
            "Budget":          100_000,
            "Start Date":      "04/01/2026",
            "End Date":        "06/30/2026",
            "Goal Type":       "CPM",
            "Goal Value":      5.00,
            "Pacing":          "Even",
        },
    ],
    "ad_groups": [
        {
            "Ad Group Name":   "CTV_HHI100K+_Demo",
            "Campaign Name":   "Acme_Brand_CTV_Q2_2026",
            "Channel":         "CTV",
            "Budget":          100_000,
            "Audience":        "HHI $100K+",
            "Device Types":    "ConnectedTV",
        },
        {
            "Ad Group Name":   "CTV_AutoIntender_Retarget",
            "Campaign Name":   "Acme_Brand_CTV_Q2_2026",
            "Channel":         "CTV",
            "Budget":          100_000,
            "Audience":        "Auto Intenders",
            "Device Types":    "ConnectedTV",
        },
        {
            "Ad Group Name":   "Display_Prospecting_18-54",
            "Campaign Name":   "Acme_Brand_Display_Q2_2026",
            "Channel":         "Display",
            "Budget":          100_000,
            "Audience":        "18-54 Broad",
            "Device Types":    "Desktop,Mobile",
        },
    ],
    "budget_flights": [
        {"Campaign Name": "Acme_Brand_CTV_Q2_2026",     "Budget": 200_000, "Start": "04/01/2026", "End": "06/30/2026"},
        {"Campaign Name": "Acme_Brand_Display_Q2_2026", "Budget": 100_000, "Start": "04/01/2026", "End": "06/30/2026"},
    ],
}

MOCK_DV360_DATA = {
    "insertion_orders": [
        {
            "Name":               "Acme_Brand_Video_Q2_2026_IO",
            "Io Objective":       "BRAND_AWARENESS_AND_REACH",
            "Io Type":            "RTB",
            "Io Subtype":         "Regular Over The Top",
            "Budget Type":        "Amount",
            "Kpi Type":           "CPM",
            "Kpi Value":          12.00,
            "Pacing":             "PACING_PERIOD_FLIGHT",
            "Pacing Rate":        "PACING_TYPE_EVEN",
            "Frequency Enabled":  "TRUE",
            "Frequency Exposures": 3,
            "Frequency Period":   "WEEK",
            "Budget Segments":    "(200000;04/01/2026;06/30/2026;;Q2 Brand Video;);",
        },
        {
            "Name":               "Acme_Brand_Display_Q2_2026_IO",
            "Io Objective":       "BRAND_AWARENESS_AND_REACH",
            "Io Type":            "RTB",
            "Io Subtype":         "Default",
            "Budget Type":        "Amount",
            "Kpi Type":           "CPM",
            "Kpi Value":          5.00,
            "Pacing":             "PACING_PERIOD_FLIGHT",
            "Pacing Rate":        "PACING_TYPE_EVEN",
            "Frequency Enabled":  "TRUE",
            "Frequency Exposures": 5,
            "Frequency Period":   "WEEK",
            "Budget Segments":    "(100000;04/01/2026;06/30/2026;;Q2 Brand Display;);",
        },
    ],
}


# ── Demo orchestration ─────────────────────────────────────────────────────────

def demo_translate_media_plan() -> dict:
    header("STEP 1 of 5  ·  Media Plan Translator")
    step("📄", "Reading input files")
    pause(300)
    substep("Media Brief: Acme_MediaBrief_Q2_2026.xlsx")
    substep("Media Plan:  Acme_MediaPlan_Q2_2026.xlsx")
    substep("Audience Matrix: Acme_AudienceMatrix_Q2_2026.xlsx")
    substep("Trafficking Sheet: Acme_Trafficking_Q2_2026.xlsx")
    pause(500)

    step("🔍", "Detecting DSPs in media plan")
    pause(400)
    substep("Found: TTD  (12 line items)")
    substep("Found: DV360  (4 line items)")

    step("🗂 ", "Mapping TTD fields")
    pause(500)
    substep(f"Campaigns:     {len(MOCK_TTD_DATA['campaigns'])}")
    substep(f"Ad Groups:     {len(MOCK_TTD_DATA['ad_groups'])}")
    substep(f"Budget Flights:{len(MOCK_TTD_DATA['budget_flights'])}")

    step("🗂 ", "Mapping DV360 fields")
    pause(500)
    substep(f"Insertion Orders: {len(MOCK_DV360_DATA['insertion_orders'])}")

    success("Translation complete",
            f"{MOCK_CAMPAIGN['campaign_name']}  |  DSPs: TTD, DV360")
    return {"ttd_data": MOCK_TTD_DATA, "dv360_data": MOCK_DV360_DATA}


def demo_generate_placement_names(ttd_data: dict, dv360_data: dict) -> list[str]:
    header("STEP 2 of 5  ·  Placement Name Generator")
    step("🏷 ", "Applying naming convention to all line items")
    pause(600)

    names = []
    for ag in ttd_data.get("ad_groups", []):
        name = f"Brand_{MOCK_CAMPAIGN['campaign_name']}_{ag['Channel']}_{ag['Ad Group Name']}"
        names.append(name)
        substep(name)
        pause(150)

    for io in dv360_data.get("insertion_orders", []):
        name = f"Brand_{MOCK_CAMPAIGN['campaign_name']}_{io['Name']}"
        names.append(name)
        substep(name)
        pause(150)

    success(f"{len(names)} placement names generated")
    return names


def demo_build_ttd(ttd_data: dict) -> dict:
    header("STEP 3 of 5  ·  TTD Campaign Builder")

    step("📡", "Calling TTD API  —  POST /campaignset")
    pause(700)
    success("Campaign Set created", "STUB_CAMPSET_Acme_BrandAwareness_Q2_2026")

    for c in ttd_data["campaigns"]:
        step("📡", f"Creating Campaign: {c['Campaign Name']}")
        pause(500)
        success("Campaign created", f"STUB_CAMP_{c['Campaign Name']}")

    for ag in ttd_data["ad_groups"]:
        step("📡", f"Creating Ad Group: {ag['Ad Group Name']}")
        pause(300)
        success("Ad Group created", f"STUB_AG_{ag['Ad Group Name']}")

    for bf in ttd_data["budget_flights"]:
        step("📡", f"Creating Budget Flight: {bf['Campaign Name']}")
        pause(300)
        success("Budget Flight created", f"${bf['Budget']:,.0f}  {bf['Start']} – {bf['End']}")

    warn("API calls are stubbed — set TTD_API_KEY and TTD_ADVERTISER_ID to activate")
    return {"dsp": "TTD", "success": True, "campaign_id": "STUB_CAMPSET_Acme_BrandAwareness_Q2_2026"}


def demo_build_dv360(dv360_data: dict) -> dict:
    header("STEP 4 of 5  ·  DV360 Campaign Builder")

    for io in dv360_data["insertion_orders"]:
        step("📡", f"Creating Insertion Order: {io['Name']}")
        pause(600)
        substep(f"Type:    {io['Io Subtype']}")
        substep(f"KPI:     {io['Kpi Type']}  @ ${io['Kpi Value']:.2f}")
        substep(f"Budget:  {io['Budget Segments']}")
        success("IO created", f"STUB_IO_{io['Name']}")
        pause(200)

    warn("API calls are stubbed — set DV360_ACCESS_TOKEN and DV360_ADVERTISER_ID to activate")
    return {"dsp": "DV360", "success": True, "campaign_id": f"STUB_IO_{dv360_data['insertion_orders'][0]['Name']}"}


def demo_summary(placement_names: list[str], ttd_result: dict, dv360_result: dict):
    header("STEP 5 of 5  ·  Orchestrator — Build Complete")
    pause(300)

    print(f"\n  {BOLD}Campaign:{RESET}  {MOCK_CAMPAIGN['campaign_name']}")
    print(f"  {BOLD}Flight:  {RESET}  {MOCK_CAMPAIGN['flight']}")
    print(f"  {BOLD}Budget:  {RESET}  ${MOCK_CAMPAIGN['total_budget']:,.0f}")
    print()

    print(f"  {BOLD}Placement Names:{RESET}  {len(placement_names)} generated")
    for name in placement_names:
        substep(name)

    print()
    print(f"  {BOLD}DSP Results:{RESET}")
    for result in [ttd_result, dv360_result]:
        icon = GREEN + "✓" + RESET if result["success"] else YELLOW + "✗" + RESET
        print(f"    {icon}  {BOLD}{result['dsp']}{RESET}  {DIM}{result['campaign_id']}{RESET}")

    print()
    print(BOLD + "─" * 62 + RESET)
    print(f"\n  {GREEN}{BOLD}All agents completed successfully.{RESET}")
    print(f"  {DIM}In production, real campaign IDs would be returned above.{RESET}\n")


# ── Architecture diagram ───────────────────────────────────────────────────────

def print_architecture():
    print(f"""
{BOLD}  Agentic Campaign Builder — Architecture{RESET}

  {CYAN}┌─────────────────────────────────────┐{RESET}
  {CYAN}│           Orchestrator              │{RESET}
  {CYAN}└──────────────┬──────────────────────┘{RESET}
                 │
       ┌─────────┼──────────┐
       ↓         ↓          ↓
  {BLUE}[Translator]{RESET}  {BLUE}[Namer]{RESET}  {BLUE}[DSP Agents]─────────────┐{RESET}
  Parses Excel  Names    {BLUE}│                          │{RESET}
  maps to DSP   placements{BLUE}↓                          ↓{RESET}
  fields                {BLUE}[TTD Builder]         [DV360 Builder]{RESET}
                         Campaign Sets         Insertion Orders
                         Ad Groups
                         Budget Flights

  {DIM}Future: Amazon DSP builder  ·  Bedrock runtime{RESET}
""")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    print()
    print(BOLD + "  AGENTIC CAMPAIGN BUILDER  ·  Future State Demo" + RESET)
    print(DIM  + "  Campaign: Acme Q2 2026 Brand Awareness  ·  TTD + DV360" + RESET)

    print_architecture()

    input(DIM + "  Press Enter to run the demo..." + RESET)

    translated = demo_translate_media_plan()
    pause(200)

    placement_names = demo_generate_placement_names(
        translated["ttd_data"],
        translated["dv360_data"],
    )
    pause(200)

    ttd_result   = demo_build_ttd(translated["ttd_data"])
    pause(200)

    dv360_result = demo_build_dv360(translated["dv360_data"])
    pause(200)

    demo_summary(placement_names, ttd_result, dv360_result)


if __name__ == "__main__":
    main()
