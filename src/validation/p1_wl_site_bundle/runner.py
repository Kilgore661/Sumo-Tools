"""Build and compare site89 bundles which differ only in their fixed prior."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import heapq
from itertools import zip_longest
import json
import math
from pathlib import Path, PurePosixPath
import re
from time import perf_counter

from src.analysis.elo89.producer import DEFAULT_PRIOR
from src.analysis.site89.producer import (
    DEFAULT_BANZUKE_SOURCE,
    produce_site89_bundle,
)
from src.infra.get_bios.parser import OUTPUT_JSON as BIO_STORE_PATH
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.infra.torikumi import Future, load_future
from src.products.make_site89.bundle import SiteDataBundle, load_site_data_bundle
from src.sumo_core.History import Date, History
from src.validation.provenance import history_fingerprint


DEFAULT_CANDIDATE_PRIOR = Path(
    "src/validation/elo89-expert-account/Matters Arising/Kimarite/"
    "output/p1-wl-comparison-2026-10-25-rerun/p1-wl/prior.csv"
)
DEFAULT_OUTPUT_PARENT = Path(
    "src/validation/elo89-expert-account/Matters Arising/Kimarite/"
    "P1-WL Site Bundle Comparison/output"
)
ELO89_START = Date.from_ints(1989, 1)
DEPENDENCY_CLASS = {
    "banzuke_changes": "direct-prior-and-replay",
    "basho_results_browser": "replay-derived",
    "career_comparisons": "replay-derived",
    "highest_rating": "replay-derived",
    "rating_changes": "replay-derived",
    "torikumi": "replay-derived",
    "typical_rating_values": "direct-prior",
    "win_probability_by_standing": "direct-prior-and-observed",
}
IDENTITY_FIELDS = frozenset(
    {
        "date", "day", "basho", "rikishi_id", "rikid", "rikishi_a",
        "rikishi_b", "east_id", "west_id", "rank_pair", "selected_chii",
        "opponent_chii", "chii", "table", "label", "window", "num_basho",
        "start", "end", "threshold", "route", "order",
    }
)
ARTIFACT_IDENTITY_FIELDS = {
    # Peak rank and date are properties of the peak selected by the model, not
    # part of the rikishi's identity.  Both may legitimately change when the
    # prior changes.
    "highest_rating": ("rikishi_id",),
}
FILE_FIELDS = (
    "artifact_id", "dependency_class", "path", "format", "byte_identical",
    "semantic_identical", "baseline_sha256", "candidate_sha256",
    "schema_equal", "baseline_record_count", "candidate_record_count",
    "identity_fields", "identity_keys_equal", "order_changed_count",
    "changed_record_count", "changed_fields",
)
NUMERIC_FIELDS = (
    "artifact_id", "path", "field", "comparison_count", "mean_difference",
    "mean_absolute_difference", "rms_difference", "maximum_absolute_difference",
)
LARGEST_FIELDS = (
    "artifact_id", "path", "identity", "field", "baseline", "candidate",
    "difference", "absolute_difference",
)
SEKITORI_SUMMARY_FIELDS = (
    "division", "observation_count", "changed_observation_count",
    "mean_difference", "mean_absolute_difference", "rms_difference",
    "median_absolute_difference", "p90_absolute_difference",
    "p95_absolute_difference", "p99_absolute_difference",
    "maximum_absolute_difference", "count_abs_ge_10", "count_abs_ge_25",
    "count_abs_ge_50",
)
SEKITORI_DETAIL_FIELDS = (
    "date", "day", "division", "rikishi_id", "shikona", "chii",
    "opponent_id", "opponent_chii", "baseline_rating", "candidate_rating",
    "difference", "absolute_difference",
)


def run_comparison(
    history: History,
    *,
    output_root: Path,
    baseline_prior: Path = DEFAULT_PRIOR,
    candidate_prior: Path = DEFAULT_CANDIDATE_PRIOR,
    banzuke_source_root: Path = DEFAULT_BANZUKE_SOURCE,
    future: Future | None = None,
    history_source: dict[str, object] | None = None,
) -> Path:
    """Build two isolated production bundles and write comparison evidence."""

    started = perf_counter()
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite comparison: {output_root}")
    dates = sorted(history)
    if not dates or dates[0] != ELO89_START:
        first = None if not dates else str(dates[0])
        raise ValueError(
            "Site-bundle comparison History must begin at 1989/01; "
            f"received {first!r}"
        )
    baseline_prior = baseline_prior.resolve()
    candidate_prior = candidate_prior.resolve()
    if baseline_prior == candidate_prior:
        raise ValueError("Baseline and candidate prior paths must differ")
    baseline_identity = _file_identity(baseline_prior)
    candidate_identity = _file_identity(candidate_prior)
    if baseline_identity["sha256"] == candidate_identity["sha256"]:
        raise ValueError("Baseline and candidate prior contents are identical")

    output_root.mkdir(parents=True)
    source = dict(history_source or {"kind": "provided History"})
    source["selected_history_sha256"] = history_fingerprint(history)
    resolved_future = future or Future(
        date=dates[-1],
        completed_through=history[dates[-1]].summary.last_defined(),
        days=(),
        generated_at=datetime.now(timezone.utc),
    )
    manifest = {
        "schema_version": 1,
        "experiment": "controlled P1 versus P1-WL site-bundle comparison",
        "status": "running",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "history": {
            **source,
            "start": str(dates[0]),
            "end": str(dates[-1]),
            "basho_count": len(dates),
        },
        "controlled_difference": "fixed Elo-89 prior only",
        "priors": {
            "baseline": baseline_identity,
            "candidate": candidate_identity,
        },
        "ancillary_inputs": {
            "banzuke_source": _tree_identity(banzuke_source_root.resolve()),
            "bio_store": _optional_file_identity(Path(BIO_STORE_PATH)),
            "future": _future_identity(resolved_future),
        },
        "outputs": {
            "baseline_bundle": "baseline",
            "candidate_bundle": "candidate",
            "file_comparison": "comparison/files.csv",
            "numeric_comparison": "comparison/numeric_differences.csv",
            "largest_differences": "comparison/largest_numeric_differences.csv",
            "sekitori_summary": "comparison/sekitori_rating_summary.csv",
            "sekitori_differences": "comparison/sekitori_rating_differences.csv",
            "violations": "comparison/violations.csv",
        },
    }
    _write_json(output_root / "manifest.json", manifest)

    try:
        for label, prior in (
            ("baseline", baseline_prior),
            ("candidate", candidate_prior),
        ):
            print(f"[{label}] producing site89 bundle", flush=True)
            produce_site89_bundle(
                history=history,
                output_root=output_root / label,
                history_source=_history_source_label(source),
                banzuke_source_root=banzuke_source_root,
                prior_path=prior,
                future=resolved_future,
            )
        print("[comparison] validating and comparing bundles", flush=True)
        summary = compare_bundles(
            baseline_root=output_root / "baseline",
            candidate_root=output_root / "candidate",
            output_root=output_root / "comparison",
        )
    except BaseException as error:
        manifest["status"] = "failed"
        manifest["failure"] = f"{type(error).__name__}: {error}"
        manifest["runtime_seconds"] = perf_counter() - started
        _write_json(output_root / "manifest.json", manifest)
        raise

    elapsed = perf_counter() - started
    manifest["status"] = "complete" if not summary["violations"] else "comparison-failed"
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["runtime_seconds"] = elapsed
    manifest["summary"] = summary
    _write_json(output_root / "manifest.json", manifest)
    print(
        f"Comparison complete: {summary['changed_files']} changed files; "
        f"{len(summary['violations'])} violations",
        flush=True,
    )
    print(f"Total wall-clock time: {elapsed:.3f} seconds", flush=True)
    print(f"Output: {output_root.resolve()}", flush=True)
    return output_root


def compare_bundles(
    *, baseline_root: Path, candidate_root: Path, output_root: Path
) -> dict[str, object]:
    """Validate two existing bundles and write a complete declared-file diff."""

    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite comparison output: {output_root}")
    baseline = load_site_data_bundle(baseline_root)
    candidate = load_site_data_bundle(candidate_root)
    output_root.mkdir(parents=True)
    violations: list[dict[str, str]] = []

    baseline_artifacts = {item.id: item for item in baseline.artifacts}
    candidate_artifacts = {item.id: item for item in candidate.artifacts}
    if set(baseline_artifacts) != set(candidate_artifacts):
        violations.append(_violation("bundle", "artifact ids differ"))

    file_rows: list[dict[str, object]] = []
    numeric_rows: list[dict[str, object]] = []
    largest_heap: list[tuple[float, int, dict[str, object]]] = []
    sequence = 0
    for artifact_id in sorted(set(baseline_artifacts) & set(candidate_artifacts)):
        left_artifact = baseline_artifacts[artifact_id]
        right_artifact = candidate_artifacts[artifact_id]
        left_files = set(left_artifact.files)
        right_files = set(right_artifact.files)
        if left_files != right_files:
            violations.append(_violation(artifact_id, "declared file sets differ"))
        for relative in sorted(left_files & right_files):
            row, numbers, largest = _compare_file(
                artifact_id,
                _dependency_class(artifact_id),
                relative,
                baseline.site_root.joinpath(*relative.parts),
                candidate.site_root.joinpath(*relative.parts),
            )
            file_rows.append(row)
            numeric_rows.extend(numbers)
            for item in largest:
                sequence += 1
                entry = (float(item["absolute_difference"]), sequence, item)
                if len(largest_heap) < 100:
                    heapq.heappush(largest_heap, entry)
                else:
                    heapq.heappushpop(largest_heap, entry)
            _file_violations(row, violations)

    _compare_rating_sources(
        baseline, candidate, file_rows, numeric_rows, largest_heap, violations
    )
    sekitori_summary, sekitori_details = _compare_sekitori_ratings(
        baseline, candidate, violations
    )
    largest_rows = [
        item for _magnitude, _sequence, item in sorted(largest_heap, reverse=True)
    ]
    _write_csv(output_root / "files.csv", FILE_FIELDS, file_rows)
    _write_csv(output_root / "numeric_differences.csv", NUMERIC_FIELDS, numeric_rows)
    _write_csv(output_root / "largest_numeric_differences.csv", LARGEST_FIELDS, largest_rows)
    _write_csv(
        output_root / "sekitori_rating_summary.csv",
        SEKITORI_SUMMARY_FIELDS,
        sekitori_summary,
    )
    _write_csv(
        output_root / "sekitori_rating_differences.csv",
        SEKITORI_DETAIL_FIELDS,
        sekitori_details,
    )
    _write_csv(
        output_root / "violations.csv",
        ("scope", "message"),
        violations,
    )
    summary = {
        "validated_history_start": baseline.history_start,
        "validated_history_end": baseline.history_end,
        "artifact_count": len(baseline_artifacts),
        "compared_files": len(file_rows),
        "changed_files": sum(not _bool(row["byte_identical"]) for row in file_rows),
        "semantic_changed_files": sum(
            not _bool(row["semantic_identical"]) for row in file_rows
        ),
        "model_independent_changed_files": sum(
            row["dependency_class"] == "model-independent"
            and not _bool(row["semantic_identical"])
            for row in file_rows
        ),
        "sekitori_rating_observations": next(
            (
                row["observation_count"]
                for row in sekitori_summary
                if row["division"] == "sekitori"
            ),
            0,
        ),
        "violations": violations,
    }
    _write_json(output_root / "summary.json", summary)
    (output_root / "findings.md").write_text(
        _findings(summary, file_rows), encoding="utf-8"
    )
    return summary


def _compare_rating_sources(
    baseline: SiteDataBundle,
    candidate: SiteDataBundle,
    file_rows: list[dict[str, object]],
    numeric_rows: list[dict[str, object]],
    largest_heap: list[tuple[float, int, dict[str, object]]],
    violations: list[dict[str, str]],
) -> None:
    left = baseline.root / baseline.manifest["rating_run"]  # type: ignore[index]
    right = candidate.root / candidate.manifest["rating_run"]  # type: ignore[index]
    left_root, right_root = left.parent, right.parent
    left_files = {path.relative_to(left_root).as_posix() for path in left_root.iterdir() if path.is_file()}
    right_files = {path.relative_to(right_root).as_posix() for path in right_root.iterdir() if path.is_file()}
    if left_files != right_files:
        violations.append(_violation("__elo89__", "rating-run file sets differ"))
    sequence = max((entry[1] for entry in largest_heap), default=0)
    for relative_text in sorted(left_files & right_files):
        relative = PurePosixPath(relative_text)
        row, numbers, largest = _compare_file(
            "__elo89__", "replay-source", relative,
            left_root / relative_text, right_root / relative_text,
        )
        file_rows.append(row)
        numeric_rows.extend(numbers)
        for item in largest:
            sequence += 1
            entry = (float(item["absolute_difference"]), sequence, item)
            if len(largest_heap) < 100:
                heapq.heappush(largest_heap, entry)
            else:
                heapq.heappushpop(largest_heap, entry)
        _file_violations(row, violations)


def _compare_sekitori_ratings(
    baseline: SiteDataBundle,
    candidate: SiteDataBundle,
    violations: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Compare each sekitori's post-bout rating throughout the replay."""

    left = baseline.root / baseline.manifest["rating_run"]  # type: ignore[index]
    right = candidate.root / candidate.manifest["rating_run"]  # type: ignore[index]
    left_ledger = left.parent / "bout_ledger.csv"
    right_ledger = right.parent / "bout_ledger.csv"
    if not left_ledger.is_file() or not right_ledger.is_file():
        violations.append(
            _violation("sekitori_rating_history", "bout ledger is missing")
        )
        return [], []

    differences: dict[str, list[float]] = {
        "makuuchi": [],
        "juryo": [],
        "sekitori": [],
    }
    details: list[dict[str, object]] = []
    shikona_by_basho = _shikona_by_basho(baseline)
    with left_ledger.open(newline="", encoding="utf-8") as left_stream, right_ledger.open(
        newline="", encoding="utf-8"
    ) as right_stream:
        left_reader = csv.DictReader(left_stream)
        right_reader = csv.DictReader(right_stream)
        for row_number, (left_row, right_row) in enumerate(
            zip_longest(left_reader, right_reader), start=2
        ):
            if left_row is None or right_row is None:
                violations.append(
                    _violation(
                        "sekitori_rating_history",
                        "bout-ledger record counts differ",
                    )
                )
                break
            bout_identity = ("date", "day", "rikishi_a", "rikishi_b", "chii_a", "chii_b")
            if any(left_row[field] != right_row[field] for field in bout_identity):
                violations.append(
                    _violation(
                        "sekitori_rating_history",
                        f"bout-ledger identity differs at CSV row {row_number}",
                    )
                )
                break
            for side, opponent in (("a", "b"), ("b", "a")):
                division = _sekitori_division(left_row[f"chii_{side}"])
                if division is None:
                    continue
                before = float(left_row[f"rating_{side}_after"])
                after = float(right_row[f"rating_{side}_after"])
                difference = after - before
                differences[division].append(difference)
                differences["sekitori"].append(difference)
                if difference == 0:
                    continue
                details.append(
                    {
                        "date": left_row["date"],
                        "day": left_row["day"],
                        "division": division,
                        "rikishi_id": left_row[f"rikishi_{side}"],
                        "shikona": shikona_by_basho.get(
                            (left_row["date"], left_row[f"rikishi_{side}"]), ""
                        ),
                        "chii": left_row[f"chii_{side}"],
                        "opponent_id": left_row[f"rikishi_{opponent}"],
                        "opponent_chii": left_row[f"chii_{opponent}"],
                        "baseline_rating": before,
                        "candidate_rating": after,
                        "difference": difference,
                        "absolute_difference": abs(difference),
                    }
                )

    details.sort(
        key=lambda row: (
            -float(row["absolute_difference"]),
            str(row["date"]),
            int(row["day"]),
            int(row["rikishi_id"]),
        )
    )
    summary = [
        _sekitori_summary_row(division, differences[division])
        for division in ("makuuchi", "juryo", "sekitori")
    ]
    return summary, details


def _shikona_by_basho(bundle: SiteDataBundle) -> dict[tuple[str, str], str]:
    artifact = next(
        (item for item in bundle.artifacts if item.id == "basho_results_browser"),
        None,
    )
    if artifact is None:
        return {}
    result: dict[tuple[str, str], str] = {}
    for relative in artifact.files:
        if "data/by-basho/" not in relative.as_posix() or relative.suffix != ".csv":
            continue
        path = bundle.site_root.joinpath(*relative.parts)
        with path.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                if all(field in row for field in ("basho", "rikishi_id", "shikona")):
                    result[(row["basho"], row["rikishi_id"])] = row["shikona"]
    return result


def _sekitori_division(chii: str) -> str | None:
    if re.match(r"^(?:Y|O|S|K|M)\d", chii):
        return "makuuchi"
    if re.match(r"^J\d", chii):
        return "juryo"
    return None


def _sekitori_summary_row(
    division: str, differences: list[float]
) -> dict[str, object]:
    absolute = sorted(abs(value) for value in differences)
    count = len(differences)
    return {
        "division": division,
        "observation_count": count,
        "changed_observation_count": sum(value != 0 for value in differences),
        "mean_difference": sum(differences) / count if count else 0.0,
        "mean_absolute_difference": sum(absolute) / count if count else 0.0,
        "rms_difference": (
            math.sqrt(sum(value * value for value in differences) / count)
            if count
            else 0.0
        ),
        "median_absolute_difference": _percentile(absolute, 0.50),
        "p90_absolute_difference": _percentile(absolute, 0.90),
        "p95_absolute_difference": _percentile(absolute, 0.95),
        "p99_absolute_difference": _percentile(absolute, 0.99),
        "maximum_absolute_difference": absolute[-1] if absolute else 0.0,
        "count_abs_ge_10": sum(value >= 10 for value in absolute),
        "count_abs_ge_25": sum(value >= 25 for value in absolute),
        "count_abs_ge_50": sum(value >= 50 for value in absolute),
    }


def _percentile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        return 0.0
    position = (len(sorted_values) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def _compare_file(artifact_id, dependency, relative, left: Path, right: Path):
    left_hash, right_hash = _sha256(left), _sha256(right)
    base = {
        "artifact_id": artifact_id,
        "dependency_class": dependency,
        "path": relative.as_posix(),
        "format": left.suffix.lower().lstrip(".") or "binary",
        "byte_identical": left_hash == right_hash,
        "semantic_identical": left_hash == right_hash,
        "baseline_sha256": left_hash,
        "candidate_sha256": right_hash,
        "schema_equal": "",
        "baseline_record_count": "",
        "candidate_record_count": "",
        "identity_fields": "",
        "identity_keys_equal": "",
        "order_changed_count": "",
        "changed_record_count": 0 if left_hash == right_hash else "",
        "changed_fields": "",
    }
    if left.suffix.lower() == ".csv":
        if max(left.stat().st_size, right.stat().st_size) > 50_000_000:
            detail, numeric, largest = _compare_csv_streaming(
                artifact_id, relative, left, right
            )
        else:
            detail, numeric, largest = _compare_csv(
                artifact_id, relative, left, right
            )
        base.update(detail)
        return base, numeric, largest
    if left.suffix.lower() == ".json":
        if max(left.stat().st_size, right.stat().st_size) > 20_000_000:
            return base, [], []
        left_value = json.loads(left.read_text(encoding="utf-8"))
        right_value = json.loads(right.read_text(encoding="utf-8"))
        base["semantic_identical"] = left_value == right_value
        base["schema_equal"] = _json_shape(left_value) == _json_shape(right_value)
        base["baseline_record_count"] = _json_count(left_value)
        base["candidate_record_count"] = _json_count(right_value)
        return base, [], []
    return base, [], []


def _compare_csv(artifact_id, relative, left: Path, right: Path):
    with left.open(newline="", encoding="utf-8") as left_stream, right.open(
        newline="", encoding="utf-8"
    ) as right_stream:
        left_reader, right_reader = csv.DictReader(left_stream), csv.DictReader(right_stream)
        left_fields = tuple(left_reader.fieldnames or ())
        right_fields = tuple(right_reader.fieldnames or ())
        identity = _identity_fields(artifact_id, left_fields)
        left_rows, right_rows = list(left_reader), list(right_reader)

    aligned, keys_equal, order_changed = _align_rows(left_rows, right_rows, identity)
    changed_records = 0
    changed_fields: defaultdict[str, int] = defaultdict(int)
    stats = _new_stats()
    largest_heap = []
    sequence = 0
    for key, left_row, right_row in aligned:
        row_changed = False
        for field in left_fields:
            before, after = left_row.get(field, ""), right_row.get(field, "")
            if before == after:
                continue
            row_changed = True
            changed_fields[field] += 1
            numeric = _numeric_difference(before, after)
            if numeric is not None:
                _add_stat(stats[field], numeric)
                sequence += 1
                _retain_largest(
                    largest_heap,
                    sequence,
                    _largest_row(
                        artifact_id, relative, key, field, before, after, numeric
                    ),
                )
        changed_records += int(row_changed)
    numeric_rows = _numeric_rows(artifact_id, relative, stats)
    detail = {
        "semantic_identical": left_fields == right_fields and left_rows == right_rows,
        "schema_equal": left_fields == right_fields,
        "baseline_record_count": len(left_rows),
        "candidate_record_count": len(right_rows),
        "identity_fields": ",".join(identity),
        "identity_keys_equal": keys_equal,
        "order_changed_count": order_changed,
        "changed_record_count": changed_records,
        "changed_fields": json.dumps(dict(sorted(changed_fields.items())), separators=(",", ":")),
    }
    largest = [item for _value, _sequence, item in sorted(largest_heap, reverse=True)]
    return detail, numeric_rows, largest


def _compare_csv_streaming(artifact_id, relative, left: Path, right: Path):
    """Compare a large, order-stable ledger without retaining all its rows."""

    with left.open(newline="", encoding="utf-8") as left_stream, right.open(
        newline="", encoding="utf-8"
    ) as right_stream:
        left_reader, right_reader = csv.DictReader(left_stream), csv.DictReader(right_stream)
        left_fields = tuple(left_reader.fieldnames or ())
        right_fields = tuple(right_reader.fieldnames or ())
        identity = _identity_fields(artifact_id, left_fields)
        left_count = right_count = changed_records = identity_mismatches = 0
        changed_fields: defaultdict[str, int] = defaultdict(int)
        stats = _new_stats()
        largest_heap = []
        sequence = 0
        left_iterator, right_iterator = iter(left_reader), iter(right_reader)
        while True:
            left_row = next(left_iterator, None)
            right_row = next(right_iterator, None)
            if left_row is None and right_row is None:
                break
            if left_row is not None:
                left_count += 1
            if right_row is not None:
                right_count += 1
            if left_row is None or right_row is None:
                continue
            key = tuple(left_row.get(field, "") for field in identity) or (left_count - 1,)
            right_key = tuple(right_row.get(field, "") for field in identity) or (right_count - 1,)
            identity_mismatches += int(key != right_key)
            row_changed = False
            for field in left_fields:
                before, after = left_row.get(field, ""), right_row.get(field, "")
                if before == after:
                    continue
                row_changed = True
                changed_fields[field] += 1
                numeric = _numeric_difference(before, after)
                if numeric is not None and key == right_key:
                    _add_stat(stats[field], numeric)
                    sequence += 1
                    _retain_largest(
                        largest_heap,
                        sequence,
                        _largest_row(
                            artifact_id, relative, key, field, before, after, numeric
                        ),
                    )
            changed_records += int(row_changed)
    detail = {
        "semantic_identical": (
            left_fields == right_fields
            and left_count == right_count
            and changed_records == 0
        ),
        "schema_equal": left_fields == right_fields,
        "baseline_record_count": left_count,
        "candidate_record_count": right_count,
        "identity_fields": ",".join(identity),
        "identity_keys_equal": identity_mismatches == 0,
        "order_changed_count": identity_mismatches,
        "changed_record_count": changed_records,
        "changed_fields": json.dumps(dict(sorted(changed_fields.items())), separators=(",", ":")),
    }
    largest = [item for _value, _sequence, item in sorted(largest_heap, reverse=True)]
    return detail, _numeric_rows(artifact_id, relative, stats), largest


def _new_stats():
    return defaultdict(lambda: {"count": 0, "sum": 0.0, "sum_abs": 0.0, "sum_sq": 0.0, "max_abs": 0.0})


def _identity_fields(artifact_id: str, fields: tuple[str, ...]) -> tuple[str, ...]:
    configured = ARTIFACT_IDENTITY_FIELDS.get(artifact_id)
    if configured is not None:
        return tuple(field for field in configured if field in fields)
    return tuple(
        field
        for field in fields
        if field in IDENTITY_FIELDS or field.endswith("_id")
    )


def _add_stat(stat, value):
    stat["count"] += 1
    stat["sum"] += value
    stat["sum_abs"] += abs(value)
    stat["sum_sq"] += value * value
    stat["max_abs"] = max(stat["max_abs"], abs(value))


def _numeric_rows(artifact_id, relative, stats):
    rows = []
    for field, stat in sorted(stats.items()):
        count = stat["count"]
        rows.append(
            {
                "artifact_id": artifact_id,
                "path": relative.as_posix(),
                "field": field,
                "comparison_count": count,
                "mean_difference": stat["sum"] / count,
                "mean_absolute_difference": stat["sum_abs"] / count,
                "rms_difference": math.sqrt(stat["sum_sq"] / count),
                "maximum_absolute_difference": stat["max_abs"],
            }
        )
    return rows


def _largest_row(artifact_id, relative, key, field, before, after, numeric):
    return {
        "artifact_id": artifact_id,
        "path": relative.as_posix(),
        "identity": json.dumps(key, separators=(",", ":")),
        "field": field,
        "baseline": before,
        "candidate": after,
        "difference": numeric,
        "absolute_difference": abs(numeric),
    }


def _retain_largest(heap, sequence, row):
    entry = (float(row["absolute_difference"]), sequence, row)
    if len(heap) < 100:
        heapq.heappush(heap, entry)
    else:
        heapq.heappushpop(heap, entry)


def _align_rows(left_rows, right_rows, identity):
    if not identity:
        return [((index,), left, right) for index, (left, right) in enumerate(zip(left_rows, right_rows, strict=False))], "", ""
    left_keys = [tuple(row.get(field, "") for field in identity) for row in left_rows]
    right_keys = [tuple(row.get(field, "") for field in identity) for row in right_rows]
    if len(set(left_keys)) != len(left_keys) or len(set(right_keys)) != len(right_keys):
        return [((index,), left, right) for index, (left, right) in enumerate(zip(left_rows, right_rows, strict=False))], "", ""
    if set(left_keys) != set(right_keys):
        return [((index,), left, right) for index, (left, right) in enumerate(zip(left_rows, right_rows, strict=False))], False, ""
    right_by_key = dict(zip(right_keys, right_rows, strict=True))
    right_positions = {key: index for index, key in enumerate(right_keys)}
    aligned = [(key, row, right_by_key[key]) for key, row in zip(left_keys, left_rows, strict=True)]
    order_changed = sum(index != right_positions[key] for index, key in enumerate(left_keys))
    return aligned, True, order_changed


def _file_violations(row, violations):
    scope = f"{row['artifact_id']}:{row['path']}"
    if row["schema_equal"] is False:
        violations.append(_violation(scope, "schema differs"))
    if row["baseline_record_count"] != row["candidate_record_count"]:
        violations.append(_violation(scope, "record counts differ"))
    if row["identity_keys_equal"] is False:
        violations.append(_violation(scope, "identity-key sets differ"))
    if row["dependency_class"] == "model-independent" and not _bool(row["semantic_identical"]):
        violations.append(_violation(scope, "model-independent content changed"))


def _dependency_class(artifact_id: str) -> str:
    return DEPENDENCY_CLASS.get(artifact_id, "model-independent")


def _numeric_difference(left: str, right: str) -> float | None:
    try:
        return float(right) - float(left)
    except (TypeError, ValueError):
        return None


def _json_shape(value):
    if isinstance(value, dict):
        return {key: _json_shape(item) for key, item in value.items()}
    if isinstance(value, list):
        return [None] if value else []
    return type(value).__name__


def _json_count(value) -> int:
    if isinstance(value, (list, dict)):
        return len(value)
    return 1


def _findings(summary, rows) -> str:
    by_class: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_class[str(row["dependency_class"])].append(row)
    lines = [
        "# P1 versus P1-WL site-bundle comparison", "",
        f"Compared {summary['compared_files']} declared files across {summary['artifact_count']} site artifacts plus the Elo-89 source run.", "",
        "| Dependency class | Files | Changed bytes | Changed semantics |", "|---|---:|---:|---:|",
    ]
    for dependency, values in sorted(by_class.items()):
        lines.append(
            f"| {dependency} | {len(values)} | "
            f"{sum(not _bool(row['byte_identical']) for row in values)} | "
            f"{sum(not _bool(row['semantic_identical']) for row in values)} |"
        )
    lines.extend([
        "", f"Invariant violations: {len(summary['violations'])}.", "",
        "See `files.csv`, `numeric_differences.csv`, `largest_numeric_differences.csv`, `sekitori_rating_summary.csv`, `sekitori_rating_differences.csv` and `violations.csv` for the evidence.", "",
    ])
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--start", type=_parse_date, default=ELO89_START)
    parser.add_argument("--end", type=_parse_date)
    parser.add_argument("--baseline-prior", type=Path, default=DEFAULT_PRIOR)
    parser.add_argument("--candidate-prior", type=Path, default=DEFAULT_CANDIDATE_PRIOR)
    parser.add_argument("--banzuke-source-root", type=Path, default=DEFAULT_BANZUKE_SOURCE)
    parser.add_argument("--future", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    zip_path = _zip_path(args.history_zip)
    full = load_history_with_annotations(str(zip_path.with_suffix("")))
    history = _selected_history(full, args.start, args.end)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output = args.output or DEFAULT_OUTPUT_PARENT / f"site-bundle-comparison-{stamp}"
    run_comparison(
        history,
        output_root=output,
        baseline_prior=args.baseline_prior,
        candidate_prior=args.candidate_prior,
        banzuke_source_root=args.banzuke_source_root,
        future=load_future(args.future) if args.future is not None else None,
        history_source={"kind": "annotated History zip", **_file_identity(zip_path)},
    )
    summary = json.loads((output / "comparison/summary.json").read_text(encoding="utf-8"))
    return 0 if not summary["violations"] else 2


def _selected_history(full: History, start: Date, end: Date | None) -> History:
    selected = History({date: full[date] for date in sorted(full) if date >= start and (end is None or date <= end)})
    if not selected:
        raise ValueError("Selected site-bundle comparison interval is empty")
    return selected


def _parse_date(value: str) -> Date:
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM")
    return Date.from_ints(int(match.group(1)), int(match.group(2)))


def _zip_path(path: Path) -> Path:
    resolved = path.resolve()
    result = resolved if resolved.suffix.lower() == ".zip" else resolved.with_suffix(".zip")
    if not result.is_file():
        raise FileNotFoundError(f"History zip not found: {result}")
    return result


def _history_source_label(source: dict[str, object]) -> str:
    return str(source.get("path") or source.get("kind") or "provided History")


def _future_identity(future: Future) -> dict[str, object]:
    return {
        "date": str(future.date),
        "completed_through": None if future.completed_through is None else int(future.completed_through),
        "day_count": len(future.days),
        "generated_at": future.generated_at.isoformat(),
    }


def _tree_identity(root: Path) -> dict[str, object]:
    if not root.is_dir():
        raise FileNotFoundError(f"Banzuke source root not found: {root}")
    files = [path for path in sorted(root.rglob("*")) if path.is_file()]
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha256(path)))
    return {"path": str(root), "file_count": len(files), "tree_sha256": digest.hexdigest()}


def _optional_file_identity(path: Path) -> dict[str, object]:
    return _file_identity(path) if path.is_file() else {"path": str(path.resolve()), "missing": True}


def _file_identity(path: Path) -> dict[str, str]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Input file not found: {resolved}")
    return {"path": str(resolved), "sha256": _sha256(resolved)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, fields, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _violation(scope: str, message: str) -> dict[str, str]:
    return {"scope": scope, "message": message}


def _bool(value: object) -> bool:
    return bool(value is True or value == "True" or value == "true")
