from types import SimpleNamespace
from types import MappingProxyType

from src.analysis.banzuke_compare.classes import BanzukeChange, BanzukeDiff
from src.analysis.banzuke_compare.report_view import build_report_side
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicEnums import Division, Side
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.Chii import Chii


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
        lambda rikishi_id, fallback: f"graph:{fallback}",
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
        full_shikona_store=FullShikonaStore(
            MappingProxyType({rikishi_id: "Hakuho Sho"})
        ),
    )

    assert side.shikona == Shikona("Hakuho Sho")
    assert side.graph_shikona == "graph:Hakuho"
    assert side.rikishi_id == rikishi_id
