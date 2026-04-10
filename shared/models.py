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
class QCCheck:
    """A single field-level QC check."""
    field: str
    expected: str
    actual: str
    status: str          # "pass" | "warn" | "fail"
    note: str = ""


@dataclass
class QCResult:
    """QC result for one DSP campaign."""
    dsp: str
    campaign_id: str
    checks: list[QCCheck] = field(default_factory=list)
    overall: str = "pass"   # "pass" | "warn" | "fail"

    @property
    def passed(self)  -> int: return sum(1 for c in self.checks if c.status == "pass")
    @property
    def warned(self)  -> int: return sum(1 for c in self.checks if c.status == "warn")
    @property
    def failed(self)  -> int: return sum(1 for c in self.checks if c.status == "fail")


@dataclass
class QCReport:
    """Full QC report across all DSPs for a campaign."""
    campaign_name: str
    results: list[QCResult] = field(default_factory=list)
    overall: str = "pass"   # "pass" | "warn" | "fail"


@dataclass
class OrchestratorResult:
    """Final result returned by the orchestrator."""
    campaign_name: str
    placement_names: PlacementNames
    dsp_results: list[DSPResult] = field(default_factory=list)
    qc_report: Optional[QCReport] = None
