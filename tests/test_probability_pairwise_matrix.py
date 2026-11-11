from __future__ import annotations

from pathlib import Path

import pytest

from src.analysis.probability.pairwise_matrix.model import (
    build_snapshot,
    win_probability,
)
from src.analysis.probability.pairwise_matrix.render import write_pairwise_html
from src.sumo_core.BasicEnums import Division
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.Chii import Chii


def test_probability_is_row_win_probability() -> None:
    assert win_probability(1600, 1600, q=400) == pytest.approx(0.5)
    assert win_probability(1700, 1500, q=400) == pytest.approx(0.7597469)
    assert win_probability(1500, 1700, q=400) == pytest.approx(0.2402531)


def test_snapshot_orders_by_rating_and_chii() -> None:
    snapshot = build_snapshot(
        basho="2026/11",
        latest_day=2,
        banzuke=_banzuke(),
        ratings={"1": 1500.0, "2": 1700.0, "3": 1400.0},
        division=Division.MAKUUCHI,
        q=400,
    )
    assert [row.shikona for row in snapshot.ordered("rating")] == ["Beta", "Alpha"]
    assert [row.shikona for row in snapshot.ordered("chii")] == ["Alpha", "Beta"]


def test_html_contains_cells_original_palette_and_hover_details(tmp_path: Path) -> None:
    snapshot = build_snapshot(
        basho="2026/11",
        latest_day=2,
        banzuke=_banzuke(),
        ratings={"1": 1500.0, "2": 1700.0, "3": 1400.0},
        division=Division.MAKUUCHI,
        q=400,
    )
    path = write_pairwise_html(
        snapshot=snapshot,
        order="chii",
        output_path=tmp_path / "makuuchi_by_chii.html",
    )
    document = path.read_text(encoding="utf-8")
    assert document.count('<rect class="cell ') == 4
    assert 'width="10" height="10"' in document
    assert "var(--loss)" in document
    assert "var(--even)" in document
    assert "var(--win)" in document
    assert 'data-row="Alpha"' in document
    assert 'data-column="Beta"' in document
    assert "pointerenter" in document
    assert "P(${d.row} wins)" in document


def _banzuke() -> Banzuke:
    chii = {RikId(1): Chii.from_str("M1e"), RikId(2): Chii.from_str("M2w"), RikId(3): Chii.from_str("J1e")}
    shikona = {RikId(1): Shikona("Alpha"), RikId(2): Shikona("Beta"), RikId(3): Shikona("Gamma")}
    return Banzuke(
        riks=Riks(chii),
        rikchii=RikChii(chii),
        rikshik=RikShikona(shikona),
    )
