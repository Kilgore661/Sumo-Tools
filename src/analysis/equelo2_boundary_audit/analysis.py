"""Analyse the two rating states at the start of the January 1989 basho."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import fmean, median, pstdev

from src.analysis.boundary_positions import competitive_division
from src.analysis.elo_model_selection.model import rank_pair
from src.sumo_core.Chii import Chii


REQUIRED_FIELDS = frozenset({
    "rikishi_id",
    "shikona_1988_11",
    "chii_1989_01",
    "equelo2_1988_11_end_rating",
    "equelo2_1989_01_start_rating",
    "elo89_1989_01_start_rating",
    "equelo2_minus_elo89_at_1989_01_start",
    "pre_1989_rated_bouts",
})

DIVISION_ORDER = {"M": 0, "J": 1, "Ms": 2, "Sd": 3, "Jd": 4, "Jk": 5}
DIVISION_LABEL = {
    "M": "Makuuchi",
    "J": "Juryo",
    "Ms": "Makushita",
    "Sd": "Sandanme",
    "Jd": "Jonidan",
    "Jk": "Jonokuchi",
}
TENURE_THRESHOLDS = (0, 1, 2, 3, 5, 10)
PRIMARY_TENURE_YEARS = 5
REFERENCE_YEAR = 1989
REFERENCE_MONTH = 1
MINIMUM_DIVISION_COHORT = 10


@dataclass(frozen=True)
class Match:
    rikishi_id: int
    shikona: str
    chii_1989_01: str
    chii_ordinal: int
    canonical_rank_pair: str
    division: str
    historical_1988_11_end_rating: float
    january_population_adjustment: float
    historical_1989_01_start_rating: float
    elo89_1989_01_start_rating: float
    historical_minus_elo89: float
    absolute_difference: float
    pre_1989_rated_bouts: int


@dataclass(frozen=True)
class AuditOutputs:
    output_root: Path
    findings: Path
    manifest: Path
    matched_count: int


def run_audit(
    handover_path: Path,
    output_root: Path,
    *,
    rating_ledger_path: Path | None = None,
) -> AuditOutputs:
    """Write the matched-rikishi and chii views of one handover artifact."""

    handover_path = handover_path.resolve()
    matches = _load_matches(handover_path)
    if not matches:
        raise ValueError(f"Handover contains no matched rikishi: {handover_path}")

    output_root.mkdir(parents=True, exist_ok=True)
    ordered = sorted(matches, key=lambda row: (row.chii_ordinal, row.rikishi_id))
    _write_csv(output_root / "matched_rikishi.csv", [asdict(row) for row in ordered])

    overall = _summary_row("All matched incumbents", matches)
    divisions = [
        _summary_row(DIVISION_LABEL[division], selected)
        for division in DIVISION_ORDER
        if (selected := [row for row in matches if row.division == division])
    ]
    _write_csv(output_root / "overall_summary.csv", [overall])
    _write_csv(output_root / "division_summary.csv", divisions)

    literal_rows = _grouped_chii_rows(matches, paired=False)
    paired_rows = _grouped_chii_rows(matches, paired=True)
    _write_csv(output_root / "literal_chii_comparison.csv", literal_rows)
    _write_csv(output_root / "canonical_pair_comparison.csv", paired_rows)

    tails = _tail_rows(matches, count=15)
    _write_csv(output_root / "largest_differences.csv", tails)

    tenure_summaries: list[dict[str, object]] = []
    tenure_divisions: list[dict[str, object]] = []
    if rating_ledger_path is not None:
        rating_ledger_path = rating_ledger_path.resolve()
        first_dates = _load_first_ranked_dates(
            rating_ledger_path, {row.rikishi_id for row in matches}
        )
        tenure_rows = _tenure_membership_rows(matches, first_dates)
        tenure_summaries, tenure_divisions = _tenure_summaries(
            matches, first_dates
        )
        _write_csv(output_root / "tenure_cohort_membership.csv", tenure_rows)
        _write_csv(output_root / "tenure_threshold_summary.csv", tenure_summaries)
        _write_csv(output_root / "tenure_division_summary.csv", tenure_divisions)

    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "experiment": "Equelo2 January-1989 matched boundary audit",
                "generated_at": datetime.now().astimezone().isoformat(),
                "source_handover": str(handover_path),
                "source_rating_ledger": (
                    str(rating_ledger_path) if rating_ledger_path is not None else None
                ),
                "population": (
                    "intersection of rikishi represented in 1988/11 and 1989/01; "
                    "joiners and leavers excluded"
                ),
                "observation": (
                    "start of 1989/01 before January bouts; historical ratings include "
                    "the January population-normalisation adjustment"
                ),
                "difference": "historical 1989/01 start minus fresh Elo-89 start",
                "standard_deviation": "population standard deviation",
                "matched_rikishi": len(matches),
                "outputs": {
                    "matched_rikishi.csv": "One matched record per incumbent.",
                    "overall_summary.csv": "Whole matched-population metrics.",
                    "division_summary.csv": "The same metrics by January division.",
                    "literal_chii_comparison.csv": (
                        "The two January-start rating maps at literal January chii."
                    ),
                    "canonical_pair_comparison.csv": (
                        "The same map using Elo-89's side- and annotation-free prior keys."
                    ),
                    "largest_differences.csv": "The 15 largest differences in each direction.",
                    "tenure_cohort_membership.csv": (
                        "First represented proper chii, tenure, and nested cohort membership."
                    ),
                    "tenure_threshold_summary.csv": (
                        "Whole-cohort metrics at 0, 1, 2, 3, 5 and 10 years."
                    ),
                    "tenure_division_summary.csv": (
                        "Metrics by threshold and division where at least 10 rikishi remain."
                    ),
                    "findings.md": "Human-readable result summary.",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    findings_path = output_root / "findings.md"
    findings_path.write_text(
        _findings(
            overall,
            divisions,
            matches,
            tails,
            tenure_summaries=tenure_summaries,
            tenure_divisions=tenure_divisions,
        ),
        encoding="utf-8",
    )
    return AuditOutputs(output_root, findings_path, manifest_path, len(matches))


def _load_matches(path: Path) -> list[Match]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or ())
        missing = REQUIRED_FIELDS - fields
        if missing:
            raise ValueError(f"Handover is missing fields: {sorted(missing)}")
        matches = []
        for source in reader:
            chii = Chii.from_str(source["chii_1989_01"])
            end = float(source["equelo2_1988_11_end_rating"])
            historical = float(source["equelo2_1989_01_start_rating"])
            elo89 = float(source["elo89_1989_01_start_rating"])
            difference = historical - elo89
            recorded_difference = float(
                source["equelo2_minus_elo89_at_1989_01_start"]
            )
            if not math.isclose(difference, recorded_difference, abs_tol=1e-9):
                raise ValueError(
                    f"Inconsistent difference for rikishi {source['rikishi_id']}"
                )
            matches.append(
                Match(
                    rikishi_id=int(source["rikishi_id"]),
                    shikona=source["shikona_1988_11"],
                    chii_1989_01=str(chii),
                    chii_ordinal=chii.ordinal(),
                    canonical_rank_pair=rank_pair(chii),
                    division=competitive_division(chii),
                    historical_1988_11_end_rating=end,
                    january_population_adjustment=historical - end,
                    historical_1989_01_start_rating=historical,
                    elo89_1989_01_start_rating=elo89,
                    historical_minus_elo89=difference,
                    absolute_difference=abs(difference),
                    pre_1989_rated_bouts=int(source["pre_1989_rated_bouts"]),
                )
            )
    return matches


def _summary_row(label: str, matches: list[Match]) -> dict[str, object]:
    historical = [row.historical_1989_01_start_rating for row in matches]
    elo89 = [row.elo89_1989_01_start_rating for row in matches]
    differences = [row.historical_minus_elo89 for row in matches]
    absolute = [abs(value) for value in differences]
    return {
        "group": label,
        "rikishi_count": len(matches),
        "historical_mean": fmean(historical),
        "elo89_mean": fmean(elo89),
        "historical_population_stdev": pstdev(historical),
        "elo89_population_stdev": pstdev(elo89),
        "difference_mean": fmean(differences),
        "difference_median": median(differences),
        "difference_population_stdev": pstdev(differences),
        "mean_absolute_difference": fmean(absolute),
        "root_mean_square_difference": math.sqrt(
            fmean(value * value for value in differences)
        ),
        "difference_q01": _quantile(differences, 0.01),
        "difference_q05": _quantile(differences, 0.05),
        "difference_q25": _quantile(differences, 0.25),
        "difference_q75": _quantile(differences, 0.75),
        "difference_q95": _quantile(differences, 0.95),
        "difference_q99": _quantile(differences, 0.99),
        "difference_min": min(differences),
        "difference_max": max(differences),
        "pearson_rating_correlation": _correlation(historical, elo89),
        "spearman_rating_correlation": _correlation(
            _average_ranks(historical), _average_ranks(elo89)
        ),
        "mean_pre_1989_rated_bouts": fmean(
            row.pre_1989_rated_bouts for row in matches
        ),
        "median_pre_1989_rated_bouts": median(
            row.pre_1989_rated_bouts for row in matches
        ),
    }


def _load_first_ranked_dates(
    path: Path, matched_ids: set[int]
) -> dict[int, tuple[int, int]]:
    """Return first represented proper-chii dates from the baseline ledger."""

    required = {"run", "basho", "phase", "rikishi_id", "chii"}
    first_dates: dict[int, tuple[int, int]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Rating ledger is missing fields: {sorted(missing)}")
        for row in reader:
            if row["run"] != "equelo2_full_history" or row["phase"] != "start":
                continue
            rikishi_id = int(row["rikishi_id"])
            if rikishi_id not in matched_ids or rikishi_id in first_dates:
                continue
            # The baseline ledger contains Chii values only. Parsing enforces that
            # administrative Mz/Bg/Kg appearances cannot start the tenure clock.
            Chii.from_str(row["chii"])
            first_dates[rikishi_id] = _parse_basho(row["basho"])
            if len(first_dates) == len(matched_ids):
                break
    missing_ids = matched_ids - set(first_dates)
    if missing_ids:
        raise ValueError(
            f"Rating ledger has no first proper-chii date for "
            f"{len(missing_ids)} matched rikishi"
        )
    return first_dates


def _parse_basho(value: str) -> tuple[int, int]:
    year_text, month_text = value.split("/", maxsplit=1)
    return int(year_text), int(month_text)


def _tenure_months(first_date: tuple[int, int]) -> int:
    year, month = first_date
    return (REFERENCE_YEAR - year) * 12 + REFERENCE_MONTH - month


def _tenure_membership_rows(
    matches: list[Match], first_dates: dict[int, tuple[int, int]]
) -> list[dict[str, object]]:
    rows = []
    for match in sorted(matches, key=lambda row: (row.chii_ordinal, row.rikishi_id)):
        first_year, first_month = first_dates[match.rikishi_id]
        months = _tenure_months((first_year, first_month))
        rows.append(
            {
                **asdict(match),
                "first_proper_chii_basho": f"{first_year:04d}/{first_month:02d}",
                "tenure_months_at_1989_01": months,
                "tenure_years_at_1989_01": months / 12.0,
                **{
                    f"qualifies_{years}_years": months >= years * 12
                    for years in TENURE_THRESHOLDS
                },
            }
        )
    return rows


def _tenure_summaries(
    matches: list[Match], first_dates: dict[int, tuple[int, int]]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    summaries = []
    divisions = []
    for years in TENURE_THRESHOLDS:
        selected = [
            row
            for row in matches
            if _tenure_months(first_dates[row.rikishi_id]) >= years * 12
        ]
        summary = _summary_row(f"At least {years} years", selected)
        summaries.append(
            {
                "minimum_tenure_years": years,
                "literal_chii_count": len({row.chii_1989_01 for row in selected}),
                "canonical_pair_count": len(
                    {row.canonical_rank_pair for row in selected}
                ),
                "represented_divisions": " | ".join(
                    DIVISION_LABEL[division]
                    for division in DIVISION_ORDER
                    if any(row.division == division for row in selected)
                ),
                **summary,
            }
        )
        for division in DIVISION_ORDER:
            division_rows = [row for row in selected if row.division == division]
            if len(division_rows) < MINIMUM_DIVISION_COHORT:
                continue
            divisions.append(
                {
                    "minimum_tenure_years": years,
                    "division": DIVISION_LABEL[division],
                    **_summary_row(DIVISION_LABEL[division], division_rows),
                }
            )
    return summaries, divisions


def _grouped_chii_rows(
    matches: list[Match], *, paired: bool
) -> list[dict[str, object]]:
    grouped: dict[str, list[Match]] = defaultdict(list)
    for row in matches:
        key = row.canonical_rank_pair if paired else row.chii_1989_01
        grouped[key].append(row)

    rows = []
    for key, selected in grouped.items():
        representative = min(selected, key=lambda row: row.chii_ordinal)
        differences = [row.historical_minus_elo89 for row in selected]
        rows.append(
            {
                "chii": key,
                "chii_ordinal": representative.chii_ordinal,
                "division": representative.division,
                "rikishi_count": len(selected),
                "rikishi": " | ".join(row.shikona for row in selected),
                "historical_1989_01_start_mean": fmean(
                    row.historical_1989_01_start_rating for row in selected
                ),
                "elo89_1989_01_start_mean": fmean(
                    row.elo89_1989_01_start_rating for row in selected
                ),
                "difference_mean": fmean(differences),
                "difference_min": min(differences),
                "difference_max": max(differences),
                "mean_absolute_difference": fmean(abs(value) for value in differences),
                "pre_1989_rated_bouts_total": sum(
                    row.pre_1989_rated_bouts for row in selected
                ),
            }
        )
    return sorted(rows, key=lambda row: (row["chii_ordinal"], row["chii"]))


def _tail_rows(matches: list[Match], count: int) -> list[dict[str, object]]:
    low = sorted(matches, key=lambda row: row.historical_minus_elo89)[:count]
    high = sorted(
        matches, key=lambda row: row.historical_minus_elo89, reverse=True
    )[:count]
    rows = []
    for direction, selected in (("historical_lower", low), ("historical_higher", high)):
        for position, row in enumerate(selected, start=1):
            rows.append({"direction": direction, "position": position, **asdict(row)})
    return rows


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _average_ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(indexed):
        end = start + 1
        while end < len(indexed) and indexed[end][1] == indexed[start][1]:
            end += 1
        average = (start + 1 + end) / 2.0
        for position in range(start, end):
            ranks[indexed[position][0]] = average
        start = end
    return ranks


def _correlation(xs: list[float], ys: list[float]) -> float:
    x_mean = fmean(xs)
    y_mean = fmean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=True))
    x_ss = sum((x - x_mean) ** 2 for x in xs)
    y_ss = sum((y - y_mean) ** 2 for y in ys)
    return numerator / math.sqrt(x_ss * y_ss) if x_ss and y_ss else 0.0


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _findings(
    overall: dict[str, object],
    divisions: list[dict[str, object]],
    matches: list[Match],
    tails: list[dict[str, object]],
    *,
    tenure_summaries: list[dict[str, object]],
    tenure_divisions: list[dict[str, object]],
) -> str:
    adjustments = [row.january_population_adjustment for row in matches]
    adjustment = fmean(adjustments)
    if max(adjustments) - min(adjustments) > 1e-9:
        raise ValueError("January population adjustment is not common to incumbents")

    lines = [
        "# Equelo2 January-1989 Boundary Audit",
        "",
        "## Contract",
        "",
        f"The comparison contains **{len(matches):,} matched incumbents** represented in both ",
        "1988/11 and 1989/01. Joiners and leavers are excluded. Both ratings are the ",
        "state at the start of 1989/01, before any January bout:",
        "",
        "- **historical:** the full-history rating carried through 1988/11;",
        "- **Elo-89:** the fresh rating assigned from the rikishi's 1989/01 chii.",
        "",
        f"Loading the January population shifts every carried incumbent by `{adjustment:.6f}` ",
        "points to restore the fixed population mean. The matched comparison uses the ",
        "post-shift January start rating; `matched_rikishi.csv` retains the November end ",
        "rating and the shift separately.",
        "",
        "## Overall comparison",
        "",
        _markdown_table(
            [
                ("Matched rikishi", f"{overall['rikishi_count']:,}"),
                ("Mean difference", _points(overall["difference_mean"])),
                ("Median difference", _points(overall["difference_median"])),
                ("Population SD of differences", _points(overall["difference_population_stdev"])),
                ("Mean absolute difference", _points(overall["mean_absolute_difference"])),
                ("RMS difference", _points(overall["root_mean_square_difference"])),
                ("5th--95th percentile", f"{_points(overall['difference_q05'])} to {_points(overall['difference_q95'])}"),
                ("Minimum--maximum", f"{_points(overall['difference_min'])} to {_points(overall['difference_max'])}"),
                ("Pearson rating correlation", f"{overall['pearson_rating_correlation']:.6f}"),
                ("Spearman rating correlation", f"{overall['spearman_rating_correlation']:.6f}"),
                ("Historical rating SD", _points(overall["historical_population_stdev"])),
                ("Elo-89 prior SD", _points(overall["elo89_population_stdev"])),
            ]
        ),
        "",
        "A positive difference means that the pre-1989 replay rates the rikishi above his ",
        "fresh chii prior; a negative difference means it rates him below it.",
        "",
        "## By January division",
        "",
        "| Division | N | Mean delta | SD delta | Mean absolute | RMS | Pearson | Spearman |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in divisions:
        lines.append(
            f"| {row['group']} | {row['rikishi_count']:,} | "
            f"{row['difference_mean']:.3f} | {row['difference_population_stdev']:.3f} | "
            f"{row['mean_absolute_difference']:.3f} | "
            f"{row['root_mean_square_difference']:.3f} | "
            f"{row['pearson_rating_correlation']:.4f} | "
            f"{row['spearman_rating_correlation']:.4f} |"
        )

    lines.extend([
        "",
        "## Largest differences",
        "",
        "| Direction | Rikishi | January chii | Historical | Elo-89 | Difference | Pre-1989 bouts |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in tails:
        if row["position"] > 10:
            continue
        lines.append(
            f"| {row['direction'].replace('_', ' ')} | {row['shikona']} | "
            f"{row['chii_1989_01']} | {row['historical_1989_01_start_rating']:.3f} | "
            f"{row['elo89_1989_01_start_rating']:.3f} | "
            f"{row['historical_minus_elo89']:.3f} | {row['pre_1989_rated_bouts']:,} |"
        )

    lines.extend([
        "",
        "## Chii views",
        "",
        "`literal_chii_comparison.csv` places both start-rating sets against the exact ",
        "1989/01 chii. `canonical_pair_comparison.csv` repeats the comparison after using ",
        "the side- and annotation-free keys of the adopted Elo-89 prior. These are two ",
        "views of the same matched population, not an additional replay.",
        "",
    ])
    if tenure_summaries:
        _append_tenure_findings(lines, tenure_summaries, tenure_divisions)
    return "\n".join(lines)


def _append_tenure_findings(
    lines: list[str],
    summaries: list[dict[str, object]],
    divisions: list[dict[str, object]],
) -> None:
    baseline = next(row for row in summaries if row["minimum_tenure_years"] == 0)
    primary = next(
        row
        for row in summaries
        if row["minimum_tenure_years"] == PRIMARY_TENURE_YEARS
    )
    mae_improved = (
        primary["mean_absolute_difference"] < baseline["mean_absolute_difference"]
    )
    rms_improved = (
        primary["root_mean_square_difference"]
        < baseline["root_mean_square_difference"]
    )
    primary_passed = mae_improved and rms_improved

    lines.extend(
        [
            "## Tenure-cohort sanity check",
            "",
            "The directional hypothesis is that restricting the comparison to rikishi ",
            "with longer represented careers improves agreement. The declared primary ",
            "comparison is five years against the complete zero-year cohort; both MAE and ",
            "RMS difference must fall for the primary check to pass.",
            "",
            "| Minimum tenure | N | Median bouts | MAE | RMS | Pearson | Spearman | Literal chii |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in summaries:
        lines.append(
            f"| {row['minimum_tenure_years']} years | {row['rikishi_count']:,} | "
            f"{row['median_pre_1989_rated_bouts']:.1f} | "
            f"{row['mean_absolute_difference']:.3f} | "
            f"{row['root_mean_square_difference']:.3f} | "
            f"{row['pearson_rating_correlation']:.4f} | "
            f"{row['spearman_rating_correlation']:.4f} | "
            f"{row['literal_chii_count']:,} |"
        )

    verdict = "passes" if primary_passed else "does not pass"
    lines.extend(
        [
            "",
            f"**Primary result: the five-year cohort {verdict} the declared check.** ",
            f"MAE changes from `{baseline['mean_absolute_difference']:.3f}` to ",
            f"`{primary['mean_absolute_difference']:.3f}` points and RMS difference changes ",
            f"from `{baseline['root_mean_square_difference']:.3f}` to ",
            f"`{primary['root_mean_square_difference']:.3f}` points.",
            "",
            "Because tenure changes the mix and range of chii, the raw correlations are not ",
            "interpreted alone. `tenure_division_summary.csv` repeats the comparison within ",
            f"divisions retaining at least {MINIMUM_DIVISION_COHORT} rikishi.",
            "",
            "### Five-year division-controlled view",
            "",
            "| Division | N | Median bouts | MAE | RMS | Pearson | Spearman |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in divisions:
        if row["minimum_tenure_years"] != PRIMARY_TENURE_YEARS:
            continue
        lines.append(
            f"| {row['division']} | {row['rikishi_count']:,} | "
            f"{row['median_pre_1989_rated_bouts']:.1f} | "
            f"{row['mean_absolute_difference']:.3f} | "
            f"{row['root_mean_square_difference']:.3f} | "
            f"{row['pearson_rating_correlation']:.4f} | "
            f"{row['spearman_rating_correlation']:.4f} |"
        )
    lines.append("")


def _markdown_table(rows: list[tuple[str, str]]) -> str:
    lines = ["| Measure | Value |", "|---|---:|"]
    lines.extend(f"| {label} | {value} |" for label, value in rows)
    return "\n".join(lines)


def _points(value: object) -> str:
    return f"{float(value):.3f} points"
