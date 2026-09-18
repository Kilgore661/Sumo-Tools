from src.analysis.promotion.yokozuna.score_partitions import (
    SEQUENCES,
    find_best_partitions,
)


def test_exhaustive_partition_search_finds_unique_synthetic_optimum():
    counts = {
        sequence: {"tp": 0, "fp": 1, "observations": 1}
        for sequence in SEQUENCES
    }
    counts["YY"] = {"tp": 2, "fp": 0, "observations": 2}
    counts["YD"] = {"tp": 1, "fp": 1, "observations": 2}

    result = find_best_partitions(counts, actual_promotions=3)

    assert result["partitions_evaluated"] == 65_536
    assert result["best_partition_count"] == 1
    assert result["best_f1_fraction"] == "6/7"
    winner = result["partitions"][0]
    assert winner["included"] == ["YY", "YD"]
    assert (winner["tp"], winner["fp"], winner["fn"]) == (3, 1, 0)
