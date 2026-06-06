from src.analysis.banzuke_compare.equelo_ratings import EqueloSnapshot
from src.analysis.banzuke_compare.report_view import format_equelo
from src.analysis.equelo.api import EntrantRatingDomain
from src.sumo_core.BasicPrimitives import Month, RikId, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


def make_snapshot(
    *,
    ratings: dict[RikId, float] | None = None,
    entrant_ratings: dict[str, float] | None = None,
) -> EqueloSnapshot:
    return EqueloSnapshot(
        date=Date(Year(2026), Month(5)),
        day=15,
        ratings={} if ratings is None else ratings,
        entrant_rating_domain=EntrantRatingDomain.from_ratings(
            {} if entrant_ratings is None else entrant_ratings
        ),
    )


def test_existing_rating_precedes_entrant_rating_domain():
    snapshot = make_snapshot(ratings={RikId(1123): 2123.45})

    assert snapshot.rating_for(RikId(1123), Chii.from_str("Ms60eTD")) == 2123.45


def test_annotated_entrant_chii_uses_public_annotation_free_rating():
    ms60e = Chii.from_str("Ms60e")
    snapshot = make_snapshot(
        entrant_ratings={
            str(ms60e.ordinal()): 1589.5005834768378,
        }
    )

    assert (
        snapshot.rating_for(RikId(13003), Chii.from_str("Ms60eTD"))
        == 1589.5005834768378
    )


def test_no_rating_entrant_chii_returns_none():
    snapshot = make_snapshot()

    assert snapshot.rating_for(RikId(99999), Chii.from_str("Ms70e")) is None


def test_format_equelo_renders_none_as_blank():
    assert format_equelo(None) == ""
