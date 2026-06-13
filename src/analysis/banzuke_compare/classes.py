"""
Data contracts for the Banzuke Change Report publisher.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.sumo_core.BasicEnums import Division, Side
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


@dataclass(frozen=True)
class PublicationRequest:
    """
    Contract:
        requested_date is the requested banzuke to report, or None to use the
        latest date supported by the source-loading policy.
        output_root is the directory that will become the static app root.
        static_dir contains the BCR HTML/CSS/JS assets named by the publisher.
        common_static_dir contains shared lab CSS used by the BCR HTML.
    """

    requested_date: Date | None
    output_root: Path
    static_dir: Path
    common_static_dir: Path

    @property
    def data_dir(self) -> Path:
        return self.output_root / "data"

    @property
    def common_output_dir(self) -> Path:
        return self.output_root.parent / "common" / "files"


@dataclass(frozen=True)
class PublicationSource:
    """
    Contract:
        Contains all domain data needed to build the BCR report for
        request.current_date.

        The current banzuke drives the displayed report.  Previous banzuke and
        previous summary context are available for old-rank, result, and local
        movement fields.
    """

    request: PublicationRequest
    history: History
    current_date: Date
    current_banzuke: Banzuke
    previous_date: Date
    previous_basho: BashoState

    @property
    def previous_banzuke(self) -> Banzuke:
        return self.previous_basho.banzuke

    @property
    def previous_summary(self):
        return self.previous_basho.summary


@dataclass(frozen=True)
class BanzukeChange:
    """
    Contract:
        Neutral per-rikishi banzuke comparison fact.

        current_* fields are defined for every row because the current banzuke
        drives the BCR main table.  previous_* fields are None for entrants.
        local_delta is the pair-local observed-slot movement metric, or None
        when the rikishi was not on the previous banzuke.
    """

    rikishi_id: RikId
    current_shikona: Shikona
    current_chii: Chii
    current_division: Division
    current_side: Side
    current_bz_chii: str
    previous_shikona: Shikona | None
    previous_chii: Chii | None
    previous_division: Division | None
    local_delta: float | None


@dataclass(frozen=True)
class BanzukeDiff:
    """
    Contract:
        Neutral banzuke-change facts derived from a PublicationSource.

        The current banzuke drives the main table.  Facts identify current
        rank, previous rank, display row rank, side, and local movement, but do
        not encode browser layout or persistence policy.
    """

    source: PublicationSource
    changes: tuple[BanzukeChange, ...]
    exits: tuple[RikId, ...]


@dataclass(frozen=True)
class BcrReport:
    """
    Contract:
        Browser-neutral report model.

        Every row belongs to exactly one division and one displayed bz_chii.
        A row may have an east side, a west side, or both; it must not have
        neither.  The model is ready to serialize to the BCR CSV/config
        contract without further domain decisions.
    """

    diff: BanzukeDiff
    divisions: tuple["BcrDivisionReport", ...]


@dataclass(frozen=True)
class BcrDivisionReport:
    """
    Contract:
        Browser-facing report section for one division.

        rows are ordered by the current banzuke rank order and contain the
        east/west cells to render for each displayed bz_chii.
    """

    division: Division
    division_id: str
    division_label: str
    rows: tuple["BcrReportRow", ...]


@dataclass(frozen=True)
class BcrReportRow:
    """
    Contract:
        One displayed banzuke row in the BCR browser table.

        At least one of east/west is not None.
    """

    bz_chii: str
    east: "BcrReportSide | None"
    west: "BcrReportSide | None"


@dataclass(frozen=True)
class BcrReportSide:
    """
    Contract:
        Browser-facing cell payload for one side of one displayed banzuke row.
    """

    rikishi_id: RikId
    chii: str
    shikona: str
    graph_shikona: str
    old_chii: str
    previous_result: str
    result_movement: str
    delta: str
    delta_class: str
    equelo_rating: str


@dataclass(frozen=True)
class PublishedFiles:
    """
    Contract:
        Names the generated browser data/config files written under the output
        root.  Static asset copying is a separate publication step.
    """

    csv_file: Path
    site_config_file: Path
    page_bundle_file: Path
