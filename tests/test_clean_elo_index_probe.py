import csv
import json
import re
from pathlib import Path

from src.analysis.clean_elo.index_probe import (
    BinningPolicy,
    convert_chii,
    probe_indices,
    write_probe_outputs,
)
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import (
    Day,
    Month,
    Pair,
    RikId,
    Riks,
    Shikona,
    Torikumi,
    Year,
)
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Kimarite import Kimarite
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


def test_bp1_through_bp4_convert_expected_components() -> None:
    annotated = Chii.from_str("Y2wHD")
    no_side = Chii.from_str("Ms60HD")

    assert convert_chii(annotated, BinningPolicy.BP1).index.display == "Y2wHD"
    assert convert_chii(annotated, BinningPolicy.BP2).index.display == "Y2w"
    assert convert_chii(annotated, BinningPolicy.BP3).index.display == "Y2"
    assert convert_chii(annotated, BinningPolicy.BP4).index.display == "Y"
    assert convert_chii(annotated, BinningPolicy.BP1).index.ordinal == 221
    assert convert_chii(annotated, BinningPolicy.BP2).index.ordinal == 201
    assert convert_chii(annotated, BinningPolicy.BP3).index.ordinal == 200
    assert convert_chii(annotated, BinningPolicy.BP4).index.ordinal == 0

    bp1_no_side = convert_chii(no_side, BinningPolicy.BP1)
    bp2_no_side = convert_chii(no_side, BinningPolicy.BP2)
    assert bp1_no_side.index.display == "Ms60HD"
    assert not bp2_no_side.valid
    assert "requires an east or west side" in bp2_no_side.failure_reason
    assert convert_chii(no_side, BinningPolicy.BP3).index.display == "Ms60"
    assert convert_chii(no_side, BinningPolicy.BP4).index.display == "Ms60"


def test_probe_counts_actual_fight_endpoints_and_policy_exceptions() -> None:
    history, date = _probe_history()

    result = probe_indices(history, date)

    assert result.eligible_fight_count == 3
    assert result.endpoint_occurrence_count == 6
    assert result.raw_chii_form_frequencies == {
        "lns": 3,
        "lnsa": 1,
        "lna": 1,
        "missing_chii": 1,
    }

    expected = {
        BinningPolicy.BP1: (5, 0, 4),
        BinningPolicy.BP2: (4, 1, 3),
        BinningPolicy.BP3: (5, 0, 4),
        BinningPolicy.BP4: (5, 0, 4),
    }
    for policy, (
        converted,
        exception_occurrences,
        distinct_indices,
    ) in expected.items():
        frequencies = result.index_frequencies[policy]
        failures = sum(
            item.occurrence_count
            for item in result.exceptions
            if item.policy == policy
        )
        assert sum(frequencies.values()) == converted
        assert failures == exception_occurrences
        assert len(frequencies) == distinct_indices
        assert (
            converted
            + failures
            + len(result.missing_banzuke_occurrences)
            == result.endpoint_occurrence_count
        )
    assert len(result.missing_banzuke_occurrences) == 1
    missing = result.missing_banzuke_occurrences[0]
    assert missing.rikid == RikId(5)
    assert missing.opponent_rikid == RikId(2)
    assert str(missing.opponent_chii) == "M1e"


def test_probe_outputs_are_timestamped_and_auditable(tmp_path: Path) -> None:
    history, date = _probe_history()
    result = probe_indices(history, date)

    outputs = write_probe_outputs(result, tmp_path)

    assert outputs.run_directory.parent == tmp_path
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}",
        outputs.run_directory.name,
    )
    for path in (
        outputs.manifest_json,
        outputs.policy_summary_csv,
        outputs.index_frequencies_csv,
        outputs.frequency_bands_csv,
        outputs.chii_forms_csv,
        outputs.chii_index_map_csv,
        outputs.conversion_exceptions_csv,
        outputs.missing_banzuke_occurrences_csv,
    ):
        assert path.exists()

    with outputs.policy_summary_csv.open(
        newline="",
        encoding="utf-8",
    ) as stream:
        summaries = {
            row["policy"]: row
            for row in csv.DictReader(stream)
        }
    assert summaries["BP1"]["converted_occurrences"] == "5"
    assert summaries["BP2"]["conversion_exception_occurrences"] == "1"
    assert summaries["BP2"]["missing_banzuke_occurrences"] == "1"

    with outputs.chii_index_map_csv.open(
        newline="",
        encoding="utf-8",
    ) as stream:
        mappings = list(csv.DictReader(stream))
    ms60_bp2 = next(
        row
        for row in mappings
        if row["chii"] == "Ms60HD" and row["policy"] == "BP2"
    )
    assert ms60_bp2["valid"] == "False"
    assert ms60_bp2["index"] == ""
    assert ms60_bp2["index_ordinal"] == ""

    y2_bp4 = next(
        row
        for row in mappings
        if row["chii"] == "Y2wHD" and row["policy"] == "BP4"
    )
    assert y2_bp4["index"] == "Y"
    assert y2_bp4["index_ordinal"] == "0"

    with outputs.missing_banzuke_occurrences_csv.open(
        newline="",
        encoding="utf-8",
    ) as stream:
        missing_rows = list(csv.DictReader(stream))
    assert len(missing_rows) == 1
    assert missing_rows[0]["rikid"] == "5"
    assert missing_rows[0]["opponent_chii"] == "M1e"

    manifest = json.loads(
        outputs.manifest_json.read_text(encoding="utf-8")
    )
    assert manifest["requested_start_date"] == "1989/01"
    assert manifest["first_processed_date"] == "1989/01"
    assert manifest["last_processed_date"] == "1989/01"
    assert manifest["missing_banzuke_occurrence_count"] == 1
    assert manifest["policy_summaries"]["BP2"][
        "conversion_exception_occurrences"
    ] == 1


def _probe_history() -> tuple[History, Date]:
    a, b, c, d, unranked = (RikId(value) for value in range(1, 6))
    date = Date(Year(1989), Month(1))
    ranks = {
        a: "Y2wHD",
        b: "M1e",
        c: "Ms60HD",
        d: "J1w",
    }
    bouts = {
        Day(1): [_bout(a, b, decision=Kimarite.OSHIDASHI)],
        Day(2): [_bout(c, d, decision="blank")],
        Day(3): [_fusen(a, b)],
        Day(4): [_bout(unranked, b, decision=Kimarite.YORIKIRI)],
    }
    lookup_by_day = {}
    for day, day_bouts in bouts.items():
        lookup = ResultLookup(
            {
                Pair(bout.rikishi1, bout.rikishi2): bout
                for bout in day_bouts
            }
        )
        lookup_by_day[day] = DailyResults(
            torikumi=Torikumi(lookup),
            results_lookup=lookup,
        )
    banzuke = Banzuke(
        riks=Riks(ranks),
        rikchii=RikChii(
            {
                rikid: Chii.from_str(chii)
                for rikid, chii in ranks.items()
            }
        ),
        rikshik=RikShikona(
            {
                rikid: Shikona(f"Rikishi {int(rikid)}")
                for rikid in ranks
            }
        ),
    )
    return (
        History(
            {
                date: BashoState(
                    banzuke=banzuke,
                    summary=Summary(lookup_by_day),
                )
            }
        ),
        date,
    )


def _bout(rikishi1: RikId, rikishi2: RikId, *, decision) -> BoutResult:
    return BoutResult(
        rikishi1=rikishi1,
        outcome1=Outcome.W,
        rikishi2=rikishi2,
        outcome2=Outcome.L,
        decision=decision,
        symbol=Symbol.W,
    )


def _fusen(winner: RikId, loser: RikId) -> BoutResult:
    return BoutResult(
        rikishi1=winner,
        outcome1=Outcome.FS,
        rikishi2=loser,
        outcome2=Outcome.FP,
        decision="fusen",
        symbol=Symbol.FS,
    )
