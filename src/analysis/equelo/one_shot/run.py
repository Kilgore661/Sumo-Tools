from dataclasses import dataclass
import datetime
import json
import csv
from pathlib import Path

from ..config_main import CONSTANT_K, INITIAL_Q
from ..expt1.params import EloParams, constant_k_fn
from ..expt1.simulate import SimulationMode, simulate

from .boundary_stats import BoundaryAdjustmentCollector, AdjustmentSummary
from .charts import write_probe_chart
from .config import MODERN_START_YEAR, PROBE_CHII, RUNS_ROOT
from .history import load_modern_history
from .init import RunSpec, build_run_plan, make_initialiser
from .project import count_observations, project_day_end_ratings, write_probe_rating_dump


@dataclass(frozen=True)
class RunRecord:
    name: str
    seed: int | None
    chart: str
    counts: str
    probe_dump: str
    adjustment_detail: str


def run_one_shot(
    end_year: int | None,
    use_zip: bool,
    seed_base: int,
) -> Path:
    history = load_modern_history(
        end_year=end_year,
        use_zip=use_zip,
    )

    params = EloParams(
        q=INITIAL_Q,
        k=constant_k_fn(CONSTANT_K),
    )

    run_specs = build_run_plan(seed_base)
    run_dir = _make_run_dir()
    effective_end_year = max(date.year for date in history.keys())

    records: list[RunRecord] = []
    summaries: list[tuple[RunSpec, AdjustmentSummary]] = []

    for spec in run_specs:
        adjustment_collector = BoundaryAdjustmentCollector()

        result = simulate(
            history=history,
            params=params,
            entrant_initialiser=make_initialiser(spec),
            mode=SimulationMode.CLOSED,
            observer=adjustment_collector,
        )

        timeline_to_ratings = project_day_end_ratings(
            history=history,
            day_end_ratings=result.day_end_ratings,
        )

        counts = count_observations(timeline_to_ratings)
        counts_path = _write_observation_counts(run_dir, spec, counts)

        probe_dump_path = _probe_dump_path(run_dir, spec)
        write_probe_rating_dump(
            output_path=probe_dump_path,
            timeline_to_ratings=timeline_to_ratings,
            probes=PROBE_CHII,
        )

        chart_path = _chart_path(run_dir, spec)
        write_probe_chart(
            output_path=chart_path,
            timeline_to_ratings=timeline_to_ratings,
            probes=PROBE_CHII,
            title=_chart_title(spec),
        )

        adjustment_detail_path = _adjustment_detail_path(run_dir, spec)
        adjustment_collector.write_detail_csv(adjustment_detail_path)
        summaries.append((spec, adjustment_collector.summarise()))

        records.append(
            RunRecord(
                name=spec.name,
                seed=spec.seed,
                chart=str(chart_path),
                counts=str(counts_path),
                probe_dump=str(probe_dump_path),
                adjustment_detail=str(adjustment_detail_path),
            )
        )

    summary_csv_path = _write_adjustment_summary_csv(run_dir, summaries)

    _write_run_json(
        run_dir=run_dir,
        requested_end_year=end_year,
        effective_end_year=effective_end_year,
        use_zip=use_zip,
        seed_base=seed_base,
        records=records,
        adjustment_summary_csv=summary_csv_path,
    )

    return run_dir


def _make_run_dir() -> Path:
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    path = RUNS_ROOT / timestamp
    path.mkdir(parents=True, exist_ok=False)
    return path


def _chart_path(run_dir: Path, spec: RunSpec) -> Path:
    if spec.seed is None:
        return run_dir / "charts" / f"{spec.name}.html"
    return run_dir / "charts" / "random" / f"{spec.name}_seed_{spec.seed}.html"


def _probe_dump_path(run_dir: Path, spec: RunSpec) -> Path:
    if spec.seed is None:
        return run_dir / "data" / f"{spec.name}_probe_ratings.csv"
    return run_dir / "data" / "random" / f"{spec.name}_seed_{spec.seed}_probe_ratings.csv"


def _adjustment_detail_path(run_dir: Path, spec: RunSpec) -> Path:
    if spec.seed is None:
        return run_dir / "data" / f"{spec.name}_boundary_adjustments.csv"
    return run_dir / "data" / "random" / f"{spec.name}_seed_{spec.seed}_boundary_adjustments.csv"


def _chart_title(spec: RunSpec) -> str:
    if spec.seed is None:
        return f"One-shot daily probes: {spec.name}"
    return f"One-shot daily probes: {spec.name} (seed={spec.seed})"


def _write_observation_counts(run_dir: Path, spec: RunSpec, counts) -> Path:
    if spec.seed is None:
        path = run_dir / "data" / f"{spec.name}_counts.json"
    else:
        path = run_dir / "data" / "random" / f"{spec.name}_seed_{spec.seed}_counts.json"

    path.parent.mkdir(parents=True, exist_ok=True)

    serialisable = {str(chii): count for chii, count in counts.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serialisable, f, indent=2, sort_keys=True)

    return path


def _write_adjustment_summary_csv(
    run_dir: Path,
    summaries: list[tuple[RunSpec, AdjustmentSummary]],
) -> str:
    path = run_dir / "data" / "boundary_adjustment_summary.csv"
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "run_name",
            "seed",
            "count",
            "mean_abs",
            "stdev_abs",
            "max_abs",
            "max_date",
            "max_rikid",
            "max_rating",
            "max_n",
        ])

        for spec, summary in summaries:
            writer.writerow([
                spec.name,
                spec.seed if spec.seed is not None else "",
                summary.count,
                summary.mean_abs,
                summary.stdev_abs,
                summary.max_abs,
                str(summary.max_date) if summary.max_date is not None else "",
                int(summary.max_rikid) if summary.max_rikid is not None else "",
                summary.max_rating if summary.max_rating is not None else "",
                summary.max_n if summary.max_n is not None else "",
            ])

    return str(path)


def _write_run_json(
    run_dir: Path,
    requested_end_year: int | None,
    effective_end_year: int,
    use_zip: bool,
    seed_base: int,
    records: list[RunRecord],
    adjustment_summary_csv: str,
) -> None:
    path = run_dir / "run.json"

    payload = {
        "regime": "modern",
        "mode": "closed",
        "start_year": MODERN_START_YEAR,
        "requested_end_year": requested_end_year,
        "effective_end_year": effective_end_year,
        "use_zip": use_zip,
        "seed_base": seed_base,
        "q": INITIAL_Q,
        "k_value": CONSTANT_K,
        "probe_chii": [str(chii) for chii in PROBE_CHII],
        "adjustment_summary_csv": adjustment_summary_csv,
        "runs": [
            {
                "name": record.name,
                "seed": record.seed,
                "chart": record.chart,
                "counts": record.counts,
                "probe_dump": record.probe_dump,
                "adjustment_detail": record.adjustment_detail,
            }
            for record in records
        ],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
