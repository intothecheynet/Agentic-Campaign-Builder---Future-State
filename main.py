"""
Agentic Campaign Builder — entry point.

Usage:
  python3 main.py \
    --brief   path/to/media_brief.xlsx \
    --plan    path/to/media_plan.xlsx \
    --audience path/to/audience_matrix.xlsx \
    --trafficking path/to/trafficking_sheet.xlsx
"""

import argparse
from orchestrator.orchestrator import run
from shared.models import CampaignInput


def main():
    parser = argparse.ArgumentParser(description="Agentic Campaign Builder")
    parser.add_argument("--brief",       required=True, help="Path to Media Brief Excel file")
    parser.add_argument("--plan",        required=True, help="Path to Media Plan Excel file")
    parser.add_argument("--audience",    required=True, help="Path to Audience Matrix Excel file")
    parser.add_argument("--trafficking", required=True, help="Path to Trafficking Sheet Excel file")
    args = parser.parse_args()

    campaign_input = CampaignInput(
        media_brief_path=args.brief,
        media_plan_path=args.plan,
        audience_matrix_path=args.audience,
        trafficking_sheet_path=args.trafficking,
    )

    result = run(campaign_input)

    print("\n── Campaign Build Complete ──────────────────────────────")
    print(f"Campaign: {result.campaign_name}")
    print(f"Placement names generated: {len(result.placement_names.names)}")
    for r in result.dsp_results:
        status = "✓" if r.success else "✗"
        print(f"  {status} {r.dsp}: {r.campaign_id or r.error}")


if __name__ == "__main__":
    main()
