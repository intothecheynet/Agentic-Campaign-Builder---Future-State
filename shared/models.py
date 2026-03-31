"""
Shared data models passed between agents.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CampaignInput:
    """Raw inputs provided to the orchestrator."""
    media_brief_path: str
    media_plan_path: str
    audience_matrix_path: str
    trafficking_sheet_path: str


@dataclass
class TranslatedCampaign:
    """Structured campaign data output from the media plan translator."""
    campaign_name: str
    lob: str
    objective: str
    dsps: list[str]               # e.g. ["TTD", "DV360", "Amazon"]
    ttd_data: Optional[dict] = None
    dv360_data: Optional[dict] = None
    amazon_data: Optional[dict] = None


@dataclass
class PlacementNames:
    """Placement names generated for each line."""
    names: list[str] = field(default_factory=list)
    # TODO: populate with naming convention once confirmed


@dataclass
class DSPResult:
    """Result returned by each DSP agent."""
    dsp: str
    success: bool
    campaign_id: Optional[str] = None
    error: Optional[str] = None
    details: Optional[dict] = None


@dataclass
class OrchestratorResult:
    """Final result returned by the orchestrator."""
    campaign_name: str
    placement_names: PlacementNames
    dsp_results: list[DSPResult] = field(default_factory=list)
