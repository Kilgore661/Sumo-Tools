"""Current-page shikona annotations for the Elo-89 site bundle."""

from __future__ import annotations

from dataclasses import dataclass

from src.analysis.banzuke_compare.results import calculate_record
from src.sumo_core.BasicEnums import MSD, Prize
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


_OZEKI32_LEVELS = frozenset({MSD.SEKIWAKE, MSD.KOMUSUBI})


@dataclass(frozen=True)
class ShikonaAnnotation:
    """Structured facts rendered beside one canonical shikona."""

    highest_chii: bool
    promotion_kind: str = ""
    promotion_status: str = ""
    promotion_required: int | None = None
    promotion_previous_result: str = ""

    def csv_fields(self, prefix: str = "") -> dict[str, str]:
        return {
            f"{prefix}highest_chii": "true" if self.highest_chii else "false",
            f"{prefix}promotion_kind": self.promotion_kind,
            f"{prefix}promotion_status": self.promotion_status,
            f"{prefix}promotion_required": (
                "" if self.promotion_required is None else str(self.promotion_required)
            ),
            f"{prefix}promotion_previous_result": self.promotion_previous_result,
        }


def banzuke_annotations(
    history: History, date: Date
) -> dict[RikId, ShikonaAnnotation]:
    """Return fixed start-of-basho annotations for one current banzuke."""

    state = history(date)
    highest = _first_time_highest_chii_flags(history, date)
    prospects = _promotion_prospects_at_start(history, date)
    return {
        rikishi_id: _combine(highest[rikishi_id], prospects.get(rikishi_id))
        for rikishi_id in state.banzuke.riks
    }


def current_basho_annotations(
    history: History, date: Date
) -> dict[RikId, ShikonaAnnotation]:
    """Return developing annotations only for the current represented basho."""

    dates = sorted(history)
    state = history(date)
    if not dates or date != dates[-1] or state.summary.last_defined() is None:
        return {}

    annotations = banzuke_annotations(history, date)
    latest_day = int(state.summary.last_defined())
    result = {}
    for rikishi_id, annotation in annotations.items():
        if annotation.promotion_kind == "ozeki32":
            wins, _, _ = calculate_record(
                rikishi_id=rikishi_id,
                chii=state.banzuke.rikchii[rikishi_id],
                summary=state.summary,
            )
            remaining_required = max(0, int(annotation.promotion_required) - wins)
            if remaining_required == 0:
                status = "achieved"
                remaining = None
            elif wins + (15 - latest_day) < int(annotation.promotion_required):
                status = "impossible"
                remaining = None
            else:
                status = "open"
                remaining = remaining_required
            annotation = ShikonaAnnotation(
                highest_chii=annotation.highest_chii,
                promotion_kind=annotation.promotion_kind,
                promotion_status=status,
                promotion_required=remaining,
            )
        elif annotation.promotion_kind == "yokydj" and latest_day >= 15:
            current_result = _ydj_result(state, rikishi_id)
            achieved = _yokydj_pair_qualifies(
                annotation.promotion_previous_result, current_result
            )
            annotation = ShikonaAnnotation(
                highest_chii=annotation.highest_chii,
                promotion_kind=annotation.promotion_kind,
                promotion_status="achieved" if achieved else "impossible",
                promotion_previous_result=annotation.promotion_previous_result,
            )
        result[rikishi_id] = annotation
    return result


def _combine(
    highest_chii: bool, prospect: ShikonaAnnotation | None
) -> ShikonaAnnotation:
    if prospect is None:
        return ShikonaAnnotation(highest_chii=highest_chii)
    return ShikonaAnnotation(
        highest_chii=highest_chii,
        promotion_kind=prospect.promotion_kind,
        promotion_status=prospect.promotion_status,
        promotion_required=prospect.promotion_required,
        promotion_previous_result=prospect.promotion_previous_result,
    )


def _first_time_highest_chii_flags(history: History, date: Date) -> dict[RikId, bool]:
    current = history(date).banzuke
    prior_best_ordinals: dict[RikId, int] = {}
    for candidate in sorted(history):
        if candidate >= date:
            break
        for rikishi_id, chii in history(candidate).banzuke.rikchii.items():
            prior_best_ordinals[rikishi_id] = min(
                prior_best_ordinals.get(rikishi_id, chii.ordinal()), chii.ordinal()
            )
    return {
        rikishi_id: (
            rikishi_id not in prior_best_ordinals
            or chii.ordinal() < prior_best_ordinals[rikishi_id]
        )
        for rikishi_id, chii in current.rikchii.items()
    }


def _promotion_prospects_at_start(
    history: History, date: Date
) -> dict[RikId, ShikonaAnnotation]:
    held_before = [
        candidate
        for candidate in sorted(history)
        if candidate < date and history(candidate).summary.last_defined() is not None
    ]
    if not held_before:
        return {}

    current = history(date)
    previous_date = held_before[-1]
    previous = history(previous_date)
    result = {}
    for rikishi_id, chii in current.banzuke.rikchii.items():
        if chii.level in _OZEKI32_LEVELS and len(held_before) >= 2:
            prior_states = [history(candidate) for candidate in held_before[-2:]]
            prior_chii = [state.banzuke.rikchii.get(rikishi_id) for state in prior_states]
            if all(rank is not None and rank.level in _OZEKI32_LEVELS for rank in prior_chii):
                wins = sum(
                    calculate_record(
                        rikishi_id=rikishi_id,
                        chii=rank,
                        summary=state.summary,
                    )[0]
                    for state, rank in zip(prior_states, prior_chii)
                )
                if wins >= 17:
                    result[rikishi_id] = ShikonaAnnotation(
                        highest_chii=False,
                        promotion_kind="ozeki32",
                        promotion_status="open",
                        promotion_required=32 - wins,
                    )
        elif chii.level == MSD.OZEKI:
            previous_chii = previous.banzuke.rikchii.get(rikishi_id)
            previous_result = _ydj_result(previous, rikishi_id)
            if previous_chii is not None and previous_chii.level == MSD.OZEKI and previous_result:
                result[rikishi_id] = ShikonaAnnotation(
                    highest_chii=False,
                    promotion_kind="yokydj",
                    promotion_status="open",
                    promotion_previous_result=previous_result,
                )
    return result


def _ydj_result(state, rikishi_id: RikId) -> str:
    performance = state.summary.performances.get(rikishi_id)
    if performance is None:
        return ""
    for prize, marker in (
        (Prize.YUSHO, "Y"),
        (Prize.DOTEN_YUSHO, "D"),
        (Prize.JUN_YUSHO, "J"),
    ):
        if prize in performance.prizes:
            return marker
    return ""


def _yokydj_pair_qualifies(previous: str, current: str) -> bool:
    if previous in {"D", "J"}:
        return current == "Y"
    return previous == "Y" and current in {"Y", "D", "J"}
