"""
Banzuke comparison contract for the Banzuke Change Report.
"""

from .classes import BanzukeChange, BanzukeDiff, PublicationSource
from src.sumo_core.BasicEnums import Annotation, Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.Chii import Chii


def build_banzuke_diff(source: PublicationSource) -> BanzukeDiff:
    """
    Contract:
        source satisfies banzuke_source.load_publication_source's output
        contract.

        Returns neutral banzuke-change facts.  The result does not know about
        CSV, HTML, or browser rendering.
    """

    local_delta_by_rikishi = calculate_local_deltas(
        previous_banzuke=source.previous_banzuke,
        current_banzuke=source.current_banzuke,
    )

    changes = tuple(
        build_change(
            source=source,
            rikishi_id=rikishi_id,
            local_delta_by_rikishi=local_delta_by_rikishi,
        )
        for rikishi_id in sorted(
            source.current_banzuke.riks,
            key=lambda rid: source.current_banzuke.get_chii(rid),
        )
    )

    exits = tuple(
        sorted(
            source.previous_banzuke.riks - source.current_banzuke.riks,
            key=lambda rid: source.previous_banzuke.get_chii(rid),
        )
    )

    return BanzukeDiff(
        source=source,
        changes=changes,
        exits=exits,
    )


def build_change(
    source: PublicationSource,
    rikishi_id: RikId,
    local_delta_by_rikishi: dict[RikId, float],
) -> BanzukeChange:
    """
    Contract:
        rikishi_id is present in source.current_banzuke.
        local_delta_by_rikishi was built from source previous/current banzuke.

        Returns the neutral comparison fact for this current-banzuke rikishi.
    """

    current_banzuke = source.current_banzuke
    previous_banzuke = source.previous_banzuke

    current_chii = current_banzuke.get_chii(rikishi_id)
    previous_chii = (
        previous_banzuke.get_chii(rikishi_id)
        if rikishi_id in previous_banzuke
        else None
    )

    return BanzukeChange(
        rikishi_id=rikishi_id,
        current_shikona=current_banzuke.get_shik(rikishi_id),
        current_chii=current_chii,
        current_division=division_for_chii(current_chii),
        current_side=current_chii.side,
        current_bz_chii=bz_chii_for_chii(current_chii),
        previous_shikona=(
            previous_banzuke.get_shik(rikishi_id)
            if rikishi_id in previous_banzuke
            else None
        ),
        previous_chii=previous_chii,
        previous_division=(
            division_for_chii(previous_chii)
            if previous_chii is not None
            else None
        ),
        local_delta=local_delta_by_rikishi.get(rikishi_id),
    )


def calculate_local_deltas(
    previous_banzuke: Banzuke,
    current_banzuke: Banzuke,
) -> dict[RikId, float]:
    """
    Contract:
        previous_banzuke and current_banzuke are the compared pair.

        Returns local observed-slot deltas for rikishi present in both banzuke.
        Positive means moved up, negative means moved down.
    """

    observed_slots = sorted(
        set(previous_banzuke.rikchii.values()) | set(current_banzuke.rikchii.values())
    )
    slot_index = {chii: index for index, chii in enumerate(observed_slots)}

    shared_rikishi = previous_banzuke.riks & current_banzuke.riks
    return {
        rikishi_id: (
            slot_index[previous_banzuke.get_chii(rikishi_id)]
            - slot_index[current_banzuke.get_chii(rikishi_id)]
        )
        / 2
        for rikishi_id in shared_rikishi
    }


def division_for_chii(chii: Chii) -> Division:
    """
    Contract:
        chii is a valid rank.

        Returns the main division containing chii.
    """

    if isinstance(chii.level, MSD):
        return Division.MAKUUCHI

    return chii.level


def bz_chii_for_chii(chii: Chii) -> str:
    """
    Contract:
        chii is a valid rank.

        Returns the displayed banzuke row heading: side removed, annotation
        preserved.
    """

    ann_str = "" if chii.ann == Annotation.EMPTY else chii.ann.name

    return f"{chii.level.as_abbreviation()}{chii.number}{ann_str}"
