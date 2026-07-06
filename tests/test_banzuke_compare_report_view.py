from types import SimpleNamespace
from types import MappingProxyType

from src.analysis.banzuke_compare.classes import BanzukeChange, BanzukeDiff
from src.analysis.banzuke_compare.report_view import (
    build_bcr_display_labels,
    build_report_side,
)
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicEnums import Division, Side
from src.sumo_core.BasicPrimitives import Month, RikId, Riks, Shikona, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


class FakeEqueloSnapshot:
    def rating_for(self, rikishi_id: RikId, chii: Chii) -> float:
        return 2048.0


def test_build_report_side_uses_public_shikona_without_changing_graph_shikona(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "src.analysis.banzuke_compare.report_view.format_previous_result",
        lambda change, summary: "10-5",
    )
    monkeypatch.setattr(
        "src.analysis.banzuke_compare.report_view.graph_shikona_for",
        lambda rikishi_id, source_shikona: f"graph:{source_shikona}",
    )
    rikishi_id = RikId(1123)
    change = BanzukeChange(
        rikishi_id=rikishi_id,
        current_shikona=Shikona("Hakuho"),
        current_chii=Chii.from_str("Y1e"),
        current_division=Division.MAKUUCHI,
        current_side=Side.EAST,
        current_bz_chii="Y1",
        previous_shikona=Shikona("Hakuho"),
        previous_chii=Chii.from_str("Y1e"),
        previous_division=Division.MAKUUCHI,
        local_delta=0,
    )
    diff = BanzukeDiff(
        source=SimpleNamespace(previous_summary=object()),
        changes=(change,),
        exits=(),
    )

    side = build_report_side(
        diff=diff,
        change=change,
        equelo_snapshot=FakeEqueloSnapshot(),
        display_labels={rikishi_id: "Hakuho Sho"},
    )

    assert side.shikona == Shikona("Hakuho Sho")
    assert side.graph_shikona == "graph:Hakuho"
    assert side.rikishi_id == rikishi_id


def test_bcr_display_labels_cover_history_and_current_only_rikishi() -> None:
    represented_id = RikId(1123)
    current_only_id = RikId(13005)
    represented_change = BanzukeChange(
        rikishi_id=represented_id,
        current_shikona=Shikona("Hakuho"),
        current_chii=Chii.from_str("Y1e"),
        current_division=Division.MAKUUCHI,
        current_side=Side.EAST,
        current_bz_chii="Y1",
        previous_shikona=Shikona("Hakuho"),
        previous_chii=Chii.from_str("Y1e"),
        previous_division=Division.MAKUUCHI,
        local_delta=0,
    )
    current_only_change = BanzukeChange(
        rikishi_id=current_only_id,
        current_shikona=Shikona("Kakizoe"),
        current_chii=Chii.from_str("Jk16w"),
        current_division=Division.JONOKUCHI,
        current_side=Side.WEST,
        current_bz_chii="Jk16",
        previous_shikona=None,
        previous_chii=None,
        previous_division=None,
        local_delta=None,
    )
    previous_banzuke = Banzuke(
        riks=Riks({represented_id}),
        rikchii=RikChii({represented_id: Chii.from_str("Y1e")}),
        rikshik=RikShikona({represented_id: Shikona("Hakuho")}),
    )
    history = History(
        {
            Date(Year(2026), Month(5)): BashoState(
                banzuke=previous_banzuke,
                summary=Summary({}),
            )
        }
    )
    diff = BanzukeDiff(
        source=SimpleNamespace(history=history),
        changes=(represented_change, current_only_change),
        exits=(),
    )

    labels = build_bcr_display_labels(
        diff,
        FullShikonaStore(MappingProxyType({represented_id: "Hakuho Sho"})),
    )

    assert labels == {
        represented_id: "Hakuho Sho",
        current_only_id: "Kakizoe",
    }
