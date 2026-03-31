"""
Media Plan Translator Agent.

Calls the Campaign Builder Python automations (from the Campaign Builder repo)
to parse the 4 source documents and return structured TTD and DV360 data.

Responsibilities:
- Parse Media Brief, Media Plan, Audience Matrix, Trafficking Sheet
- Run TTD mapper for TTD rows
- Run DV360 mapper for DV360 rows
- Return a TranslatedCampaign with data ready for each DSP agent

Dependencies:
- Expects the Campaign Builder repo to be available as a sibling directory
  or installable package. Update CAMPAIGN_BUILDER_PATH as needed.
"""

import sys
import os

# ── Path to Campaign Builder repo ─────────────────────────────────────────────
# Update this path to point to your local Campaign Builder repo.
CAMPAIGN_BUILDER_PATH = os.path.expanduser("~/my-project/my-project")
if CAMPAIGN_BUILDER_PATH not in sys.path:
    sys.path.insert(0, CAMPAIGN_BUILDER_PATH)

from shared.models import CampaignInput, TranslatedCampaign


def run(campaign_input: CampaignInput) -> TranslatedCampaign:
    """
    Parse all 4 source files and run the appropriate DSP mappers.
    Returns a TranslatedCampaign with structured data for each DSP.
    """
    import openpyxl
    import io

    # Import Campaign Builder modules
    from app import excel_to_dict
    from mapper import map_to_ttd, extract_lob, build_campaign_name, parse_trafficking_sheet, parse_media_brief, parse_media_plan
    from dv360_mapper import map_to_dv360

    # ── Load all 4 input files ────────────────────────────────────────────────
    files_data = {}
    for label, path in [
        ("Media Brief",       campaign_input.media_brief_path),
        ("Media Plan",        campaign_input.media_plan_path),
        ("Audience Matrix",   campaign_input.audience_matrix_path),
        ("Trafficking Sheet", campaign_input.trafficking_sheet_path),
    ]:
        with open(path, "rb") as f:
            files_data[label] = excel_to_dict(f.read())

    # ── Detect DSPs from Media Plan ───────────────────────────────────────────
    raw_rows = files_data["Media Plan"].get("Sheet1", {}).get("rows", [])
    dsps_found = set()
    if len(raw_rows) >= 2:
        header_row = raw_rows[0]
        headers = list(header_row.values())
        for row in raw_rows[1:]:
            vals = list(row.values())
            record = dict(zip(headers, vals))
            dsp = str(record.get("DSP", "")).strip().upper()
            if dsp:
                dsps_found.add(dsp)

    # ── Extract campaign metadata ─────────────────────────────────────────────
    brief       = parse_media_brief(files_data["Media Brief"])
    trafficking = parse_trafficking_sheet(files_data["Trafficking Sheet"])
    campaign_name = build_campaign_name(brief, trafficking)
    lob           = extract_lob(brief, trafficking[0] if trafficking else None)
    objective     = brief.get("Media Objectives", brief.get("Communications Objective", ""))

    # ── Run DSP mappers ───────────────────────────────────────────────────────
    ttd_data    = map_to_ttd(files_data)    if "TTD"    in dsps_found else None
    dv360_data  = map_to_dv360(files_data)  if "DV360"  in dsps_found else None
    amazon_data = None  # Amazon mapper not yet implemented

    return TranslatedCampaign(
        campaign_name=campaign_name,
        lob=lob,
        objective=objective,
        dsps=list(dsps_found),
        ttd_data=ttd_data,
        dv360_data=dv360_data,
        amazon_data=amazon_data,
    )
