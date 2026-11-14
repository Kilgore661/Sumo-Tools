from __future__ import annotations

from src.infra.get_bios.career_rows import CutoffCareerStatus, UNRANKED_ACTIVE_STATUSES
from src.infra.get_bios.api import BioBashoDate, RikishiBio
from src.sumo_core.Chii import Chii


def classify_non_success_outcome(
    rikishi_id,
    *,
    bio: RikishiBio,
    latest_ids,
    cutoff_bio: BioBashoDate,
    cutoff_statuses: dict,
) -> tuple[str, str]:
    if bio.intai is not None and bio.intai <= cutoff_bio:
        return "failure", f"bio_intai:{bio.intai}"
    if rikishi_id in latest_ids:
        return "right_censored", "present_on_cutoff_banzuke"

    evidence: CutoffCareerStatus | None = cutoff_statuses.get(rikishi_id)
    if evidence is None:
        return "unknown", "career_status_source_not_supplied"
    if evidence.evidence == "no_cutoff_status_row":
        return "failure", "absent_from_cutoff_banzuke_and_career_rows"
    if evidence.evidence in {"missing_career_page", "invalid_career_page"}:
        return "unknown", evidence.evidence

    status = evidence.status
    if status in UNRANKED_ACTIVE_STATUSES:
        return "right_censored", f"cutoff_unranked_status:{status}"
    if status in {None, "??"}:
        return "unknown", "unresolved_cutoff_status"
    try:
        Chii.from_str(status)
    except (TypeError, ValueError):
        return "unknown", f"unrecognised_cutoff_status:{status}"
    return "unknown", f"cutoff_formal_status_missing_from_history:{status}"
