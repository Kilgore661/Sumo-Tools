from src.analysis.promotion.yokozuna.score_partitions import SEQUENCES
from src.analysis.promotion.yokozuna.score_triples import (
    TRIPLES,
    find_best_threshold_partition,
)


def _counts(sequences, *, default_fp=1):
    return {
        sequence: {"tp": 0, "fp": default_fp, "observations": default_fp}
        for sequence in sequences
    }


def test_threshold_optimizer_finds_exact_synthetic_triple_optimum():
    counts = _counts(TRIPLES)
    counts["YYY"] = {"tp": 3, "fp": 0, "observations": 3}
    counts["JYY"] = {"tp": 2, "fp": 1, "observations": 3}

    result = find_best_threshold_partition(counts, TRIPLES, actual_promotions=5)

    assert result["best_f1_fraction"] == "10/11"
    assert result["included_in_every_best_partition"] == ["YYY", "JYY"]
    assert not result["included_in_some_but_not_all_best_partitions"]
    assert result["conservative_best_partition"]["included"] == ["YYY", "JYY"]


def test_threshold_optimizer_reports_neutral_boundary_cells():
    counts = {sequence: {"tp": 0, "fp": 0, "observations": 0} for sequence in SEQUENCES}
    counts["YY"] = {"tp": 2, "fp": 0, "observations": 2}
    counts["DY"] = {"tp": 1, "fp": 2, "observations": 3}

    result = find_best_threshold_partition(counts, SEQUENCES, actual_promotions=4)

    assert result["best_f1_fraction"] == "2/3"
    assert result["included_in_every_best_partition"] == ["YY"]
    assert result["included_in_some_but_not_all_best_partitions"] == ["DY"]
    assert result["observationally_distinct_best_partition_count"] == 2
