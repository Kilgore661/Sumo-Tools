import csv
import math
from pathlib import Path

from src.analysis.clean_elo.monotonicity_probe import (
    IndexEstimate,
    Scope,
    fit_non_increasing,
    read_bp4_estimates,
    test_monotonicity as run_monotonicity_test,
)


def test_weighted_non_increasing_fit_pools_violations() -> None:
    fitted = fit_non_increasing(
        [10.0, 8.0, 9.0, 4.0],
        [1.0, 1.0, 1.0, 1.0],
    )
    assert fitted == (10.0, 8.5, 8.5, 4.0)

    weighted = fit_non_increasing(
        [10.0, 8.0, 9.0],
        [1.0, 3.0, 1.0],
    )
    assert weighted == (10.0, 8.25, 8.25)


def test_monotonic_data_has_zero_observed_lack_of_fit() -> None:
    estimates = [
        _estimate("M1", 400100, 2047.688462),
        _estimate("M2", 400200, 2022.236888),
        _estimate("M3", 400300, 2002.977651),
    ]
    result = run_monotonicity_test(
        estimates,
        _all_scope(),
        bootstrap_samples=100,
        random_seed=1,
    )
    assert result.statistic == 0.0
    assert result.exceedances == 100
    assert result.p_value == 1.0


def test_strong_reversal_has_small_bootstrap_p_value() -> None:
    estimates = [
        _estimate("M1", 400100, 10.0, standard_error=0.1),
        _estimate("M2", 400200, 9.0, standard_error=0.1),
        _estimate("M3", 400300, 20.0, standard_error=0.1),
    ]
    result = run_monotonicity_test(
        estimates,
        _all_scope(),
        bootstrap_samples=999,
        random_seed=2,
    )
    assert result.p_value <= 0.01
    assert result.statistic > 1000.0


def test_reader_marks_undefined_or_nonpositive_bp4_se_unusable(
    tmp_path: Path,
) -> None:
    path = tmp_path / "statistics.csv"
    fields = [
        "policy",
        "index",
        "index_ordinal",
        "level",
        "number",
        "n",
        "mean_rating",
        "standard_error",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(
            [
                _row("BP1", "M1e", 400100, "M", 1, 20, 10.0, 1.0),
                _row("BP4", "M2", 400200, "M", 2, 20, 9.0, 1.0),
                _row("BP4", "M3", 400300, "M", 3, 1, 8.0, ""),
                _row("BP4", "M4", 400400, "M", 4, 20, 7.0, 0.0),
            ]
        )
    estimates = read_bp4_estimates(path)
    assert len(estimates) == 3
    assert estimates[0].index == "M2"
    assert math.isclose(estimates[0].standard_error, 1.0)
    assert estimates[1].standard_error is None
    assert estimates[2].standard_error is None


def _estimate(
    index: str,
    ordinal: int,
    mean: float,
    *,
    standard_error: float = 1.0,
) -> IndexEstimate:
    return IndexEstimate(
        index=index,
        ordinal=ordinal,
        level="M",
        number=int(index[1:]),
        n=20,
        mean=mean,
        standard_error=standard_error,
    )


def _all_scope() -> Scope:
    return Scope("all", "all", lambda item: True)


def _row(
    policy: str,
    index: str,
    ordinal: int,
    level: str,
    number: int,
    n: int,
    mean: float,
    standard_error: float | str,
) -> dict[str, object]:
    return {
        "policy": policy,
        "index": index,
        "index_ordinal": ordinal,
        "level": level,
        "number": number,
        "n": n,
        "mean_rating": mean,
        "standard_error": standard_error,
    }
