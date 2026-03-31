"""
Placement Name Generator Agent.

Generates standardized placement names for each line item
in the translated campaign.

TODO: Implement naming convention once confirmed with the team.
      The structure below is a placeholder — update build_placement_name()
      with the agreed format before using in production.
"""

from shared.models import TranslatedCampaign, PlacementNames


# ── Naming convention ─────────────────────────────────────────────────────────
# TODO: Replace with confirmed naming convention.
# Example format: {LOB}_{Campaign}_{Channel}_{Tactic}_{Year}
# Update this function once the convention is confirmed.

def build_placement_name(campaign_name: str, lob: str, channel: str, tactic: str) -> str:
    """
    Build a single placement name from campaign components.
    TODO: implement confirmed naming convention.
    """
    parts = [p for p in [lob, campaign_name, channel, tactic] if p]
    return "_".join(parts)


def run(translated: TranslatedCampaign) -> PlacementNames:
    """
    Generate placement names for every line item across all DSPs.
    """
    names = []

    # Generate from TTD ad groups if present
    if translated.ttd_data:
        for ag in translated.ttd_data.get("ad_groups", []):
            name = build_placement_name(
                campaign_name=translated.campaign_name,
                lob=translated.lob,
                channel=ag.get("Channel", ""),
                tactic=ag.get("Ad Group Name", ""),
            )
            names.append(name)

    # Generate from DV360 IOs if present
    if translated.dv360_data:
        for io in translated.dv360_data.get("insertion_orders", []):
            name = build_placement_name(
                campaign_name=translated.campaign_name,
                lob=translated.lob,
                channel="",
                tactic=io.get("Name", ""),
            )
            names.append(name)

    return PlacementNames(names=names)
