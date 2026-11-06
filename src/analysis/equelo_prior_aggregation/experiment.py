"""Post-fit aggregation experiment for literal-chii entrant priors."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
from typing import Iterable, Sequence

from src.analysis.elo_model_selection.model import rank_pair
from src.sumo_core.Chii import Chii


DEFAULT_P1 = Path(
    "src/validation/elo89-expert-account/Matters Arising/Kimarite/output/"
    "p1-wl-comparison-2026-10-25-rerun/p1/prior.csv"
)
DEFAULT_P1_WL = Path(
    "files/output/analysis/elo89/prior/2026-09/run-001/prior.csv"
)
DEFAULT_PERSISTED_PRIOR = Path(__file__).resolve().parent / "results" / "priors.csv"
POLICIES = (
    "legacy_unweighted",
    "support_weighted",
    "canonical_sanyaku",
)
SANYAKU_FAMILIES = frozenset({"Y", "O", "S", "K"})


@dataclass(frozen=True, slots=True)
class LiteralPriorRow:
    chii: Chii
    chii_label: str
    rating: float
    support: float


@dataclass(frozen=True, slots=True)
class AggregatedPriorRow:
    source: str
    candidate: str
    policy: str
    rank_pair: str
    ordinal: int
    rating: float
    total_support: float
    constituents: tuple[LiteralPriorRow, ...]
    weights: tuple[float, ...]


def load_literal_prior(path: Path) -> tuple[LiteralPriorRow, ...]:
    """Load a strict literal prior with explicit support."""

    resolved = path.resolve()
    with resolved.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = set(reader.fieldnames or ())
        required = {"chii", "rating", "support"}
        missing = sorted(required - fieldnames)
        if missing:
            raise ValueError(
                f"Literal prior is missing required columns {missing}: {resolved}"
            )
        rows = tuple(reader)
    if not rows:
        raise ValueError(f"Literal prior contains no rows: {resolved}")

    result = []
    seen: set[str] = set()
    for line_number, row in enumerate(rows, start=2):
        label = row["chii"].strip()
        if not label:
            raise ValueError(f"Blank chii at {resolved}:{line_number}")
        if label in seen:
            raise ValueError(f"Duplicate literal chii {label!r} in {resolved}")
        seen.add(label)
        try:
            chii = Chii.from_str(label)
            rating = float(row["rating"])
            support = float(row["support"])
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid literal prior row at {resolved}:{line_number}: {error}"
            ) from error
        if not math.isfinite(rating):
            raise ValueError(f"Non-finite rating at {resolved}:{line_number}")
        if not math.isfinite(support) or support <= 0:
            raise ValueError(
                f"Support must be finite and positive at {resolved}:{line_number}"
            )
        result.append(LiteralPriorRow(chii, label, rating, support))
    return tuple(sorted(result, key=lambda item: item.chii.ordinal()))


def aggregate_prior(
    rows: Sequence[LiteralPriorRow],
    *,
    source: str,
    policy: str,
) -> tuple[AggregatedPriorRow, ...]:
    """Aggregate literal cells under one named policy."""

    if policy not in POLICIES:
        raise ValueError(f"Unknown aggregation policy: {policy!r}")
    grouped: dict[str, list[LiteralPriorRow]] = defaultdict(list)
    for row in rows:
        pair = rank_pair(row.chii)
        if policy == "canonical_sanyaku":
            family = row.chii.level.as_abbreviation()
            if family in SANYAKU_FAMILIES and row.chii.number != 1:
                continue
        grouped[pair].append(row)
    if not grouped:
        raise ValueError("Aggregation produced no paired-prior rows")

    candidate = _candidate_name(source, policy)
    result = []
    for pair, constituents in grouped.items():
        if policy == "support_weighted":
            total_weight = sum(row.support for row in constituents)
            weights = tuple(row.support / total_weight for row in constituents)
        else:
            weights = tuple(1.0 / len(constituents) for _ in constituents)
        rating = sum(
            row.rating * weight for row, weight in zip(constituents, weights)
        )
        result.append(
            AggregatedPriorRow(
                source=source,
                candidate=candidate,
                policy=policy,
                rank_pair=pair,
                ordinal=Chii.from_str(pair).ordinal(),
                rating=rating,
                total_support=sum(row.support for row in constituents),
                constituents=tuple(constituents),
                weights=weights,
            )
        )
    return tuple(sorted(result, key=lambda item: item.ordinal))


def run_experiment(
    *,
    p1_path: Path,
    p1_wl_path: Path,
    output: Path,
    repository_root: Path | None = None,
    persisted_prior_path: Path | None = None,
) -> Path:
    """Run all policies for P1 and P1-WL and retain auditable artifacts."""

    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite experiment output: {output}")
    sources = {
        "p1": p1_path.resolve(),
        "p1-wl": p1_wl_path.resolve(),
    }
    literal = {name: load_literal_prior(path) for name, path in sources.items()}
    aggregated = {
        (source, policy): aggregate_prior(rows, source=source, policy=policy)
        for source, rows in literal.items()
        for policy in POLICIES
    }
    _validate_domains(aggregated)

    persisted_prior = None
    if persisted_prior_path is not None:
        persisted_prior = _persist_official_prior(
            persisted_prior_path.resolve(),
            aggregated[("p1-wl", "support_weighted")],
        )

    output.mkdir(parents=True)
    paired_path = output / "paired_priors.csv"
    comparison_path = output / "comparison.csv"
    findings_path = output / "findings.md"
    _write_csv(paired_path, _paired_rows(aggregated))
    comparisons = _comparison_rows(aggregated)
    _write_csv(comparison_path, comparisons)
    findings_path.write_text(_findings(comparisons), encoding="utf-8")

    root = (repository_root or Path.cwd()).resolve()
    manifest_path = output / "manifest.json"
    manifest = {
        "schema_version": 1,
        "experiment": "Equelo literal-prior aggregation policy comparison",
        "status": (
            "P1-prime-WL accepted and persisted; production replay unchanged"
            if persisted_prior is not None
            else "experimental comparison; production replay unchanged"
        ),
        "sources": {
            name: {
                "path": str(path),
                "sha256": _sha256(path),
                "row_count": len(literal[name]),
                "support_total": sum(row.support for row in literal[name]),
                "source_manifest": _source_manifest(path),
            }
            for name, path in sources.items()
        },
        "grouping": {
            "rule": (
                "remove annotations and sides; collapse every numbered Y/O/S/K "
                "slot to its canonical family consumer key; retain ordinary rank numbers"
            ),
            "implementation": "src.analysis.elo_model_selection.model.rank_pair",
            "unbounded_numbered_slots": True,
        },
        "policies": {
            "legacy_unweighted": {
                "formula": "sum(literal_rating) / literal_count",
                "scope": "all literal cells mapped to the paired key",
            },
            "support_weighted": {
                "formula": (
                    "sum(literal_rating * literal_support) / sum(literal_support)"
                ),
                "scope": (
                    "all literal cells mapped to the paired key, including east/west"
                ),
            },
            "canonical_sanyaku": {
                "formula": "unweighted mean of selected literal ratings",
                "scope": (
                    "ordinary pairs use available sides; Y/O/S/K select numbered slot 1 only"
                ),
            },
        },
        "candidate_names": {
            "p1/support_weighted": "P1-prime",
            "p1-wl/support_weighted": "P1-prime-WL",
        },
        "persisted_official_prior": (
            None
            if persisted_prior is None
            else {
                "path": str(persisted_prior),
                "sha256": _sha256(persisted_prior),
                "row_count": len(aggregated[("p1-wl", "support_weighted")]),
                "schema": ["rank_pair", "ordinal", "rating"],
                "source": "p1-wl/support_weighted",
                "candidate": "P1-prime-WL",
            }
        ),
        "software": _software_revision(root),
        "outputs": {
            path.name: {"sha256": _sha256(path)}
            for path in (paired_path, comparison_path, findings_path)
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def _candidate_name(source: str, policy: str) -> str:
    if source == "p1" and policy == "support_weighted":
        return "P1-prime"
    if source == "p1-wl" and policy == "support_weighted":
        return "P1-prime-WL"
    return f"{source}:{policy}"


def _validate_domains(
    aggregated: dict[tuple[str, str], tuple[AggregatedPriorRow, ...]],
) -> None:
    domains = {
        key: {row.rank_pair for row in rows}
        for key, rows in aggregated.items()
    }
    reference_key = ("p1", "legacy_unweighted")
    reference = domains[reference_key]
    for key, domain in domains.items():
        if domain != reference:
            missing = sorted(reference - domain)
            extra = sorted(domain - reference)
            raise ValueError(
                f"Paired-prior domain differs for {key}: missing={missing}, extra={extra}"
            )


def _paired_rows(
    aggregated: dict[tuple[str, str], tuple[AggregatedPriorRow, ...]],
) -> Iterable[dict[str, object]]:
    for source in ("p1", "p1-wl"):
        for policy in POLICIES:
            for row in aggregated[(source, policy)]:
                yield {
                    "source": source,
                    "candidate": row.candidate,
                    "policy": policy,
                    "rank_pair": row.rank_pair,
                    "ordinal": row.ordinal,
                    "rating": row.rating,
                    "total_support": row.total_support,
                    "constituent_count": len(row.constituents),
                    "constituent_chii": json.dumps(
                        [item.chii_label for item in row.constituents],
                        separators=(",", ":"),
                    ),
                    "constituent_ratings": json.dumps(
                        [item.rating for item in row.constituents],
                        separators=(",", ":"),
                    ),
                    "constituent_supports": json.dumps(
                        [item.support for item in row.constituents],
                        separators=(",", ":"),
                    ),
                    "normalised_weights": json.dumps(
                        list(row.weights), separators=(",", ":")
                    ),
                }


def _comparison_rows(
    aggregated: dict[tuple[str, str], tuple[AggregatedPriorRow, ...]],
) -> list[dict[str, object]]:
    indexed = {
        key: {row.rank_pair: row for row in rows}
        for key, rows in aggregated.items()
    }
    pairs = sorted(
        indexed[("p1", "legacy_unweighted")],
        key=lambda pair: indexed[("p1", "legacy_unweighted")][pair].ordinal,
    )
    result = []
    for pair in pairs:
        p1 = {policy: indexed[("p1", policy)][pair] for policy in POLICIES}
        p1_wl = {policy: indexed[("p1-wl", policy)][pair] for policy in POLICIES}
        result.append(
            {
                "rank_pair": pair,
                "ordinal": p1["legacy_unweighted"].ordinal,
                "p1_legacy": p1["legacy_unweighted"].rating,
                "p1_weighted": p1["support_weighted"].rating,
                "p1_canonical_sanyaku": p1["canonical_sanyaku"].rating,
                "p1_weighted_minus_legacy": (
                    p1["support_weighted"].rating
                    - p1["legacy_unweighted"].rating
                ),
                "p1_wl_legacy": p1_wl["legacy_unweighted"].rating,
                "p1_wl_weighted": p1_wl["support_weighted"].rating,
                "p1_wl_canonical_sanyaku": p1_wl["canonical_sanyaku"].rating,
                "p1_wl_weighted_minus_legacy": (
                    p1_wl["support_weighted"].rating
                    - p1_wl["legacy_unweighted"].rating
                ),
                "legacy_wl_minus_p1": (
                    p1_wl["legacy_unweighted"].rating
                    - p1["legacy_unweighted"].rating
                ),
                "weighted_wl_minus_p1": (
                    p1_wl["support_weighted"].rating
                    - p1["support_weighted"].rating
                ),
                "p1_support": p1["support_weighted"].total_support,
                "p1_wl_support": p1_wl["support_weighted"].total_support,
                "constituent_count": len(p1["support_weighted"].constituents),
            }
        )
    return result


def _persist_official_prior(
    path: Path,
    rows: Sequence[AggregatedPriorRow],
) -> Path:
    """Persist the accepted P1-prime-WL table without silently replacing it."""

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=("rank_pair", "ordinal", "rating"),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(
        {
            "rank_pair": row.rank_pair,
            "ordinal": row.ordinal,
            "rating": row.rating,
        }
        for row in rows
    )
    content = stream.getvalue().encode("utf-8")
    if path.exists():
        if path.read_bytes() != content:
            raise FileExistsError(
                "Refusing to replace a different persisted official prior: "
                f"{path}"
            )
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as destination:
        destination.write(content)
    return path


def _findings(rows: list[dict[str, object]]) -> str:
    indexed = {str(row["rank_pair"]): row for row in rows}
    lines = [
        "# Equelo prior aggregation findings",
        "",
        "This run compares post-fit aggregation policies only. It does not refit",
        "P1 or P1-WL, promote a prior, or change Elo-89 production.",
        "",
        "## Headline comparison",
        "",
        "| Source/candidate | K1 | M1 | K1 minus M1 |",
        "|---|---:|---:|---:|",
    ]
    for label, prefix in (
        ("P1 (legacy)", "p1_legacy"),
        ("P1-prime (support-weighted)", "p1_weighted"),
        ("P1-WL (legacy)", "p1_wl_legacy"),
        ("P1-prime-WL (support-weighted)", "p1_wl_weighted"),
    ):
        k = float(indexed["K1"][prefix])
        m = float(indexed["M1"][prefix])
        lines.append(f"| {label} | {k:.6f} | {m:.6f} | {k - m:+.6f} |")

    lines.extend([
        "",
        "## Sanyaku family comparison",
        "",
        "| Pair | P1 legacy | P1-prime | Change | P1-WL legacy | P1-prime-WL | Change |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for pair in (pair for pair in ("Y1", "O1", "S1", "K1") if pair in indexed):
        row = indexed[pair]
        lines.append(
            f"| {pair} | {float(row['p1_legacy']):.6f} | "
            f"{float(row['p1_weighted']):.6f} | "
            f"{float(row['p1_weighted_minus_legacy']):+.6f} | "
            f"{float(row['p1_wl_legacy']):.6f} | "
            f"{float(row['p1_wl_weighted']):.6f} | "
            f"{float(row['p1_wl_weighted_minus_legacy']):+.6f} |"
        )

    largest_p1 = max(rows, key=lambda row: abs(float(row["p1_weighted_minus_legacy"])))
    largest_wl = max(
        rows, key=lambda row: abs(float(row["p1_wl_weighted_minus_legacy"]))
    )
    lines.extend([
        "",
        "## Largest aggregation effects",
        "",
        f"- P1: {largest_p1['rank_pair']} changes by "
        f"{float(largest_p1['p1_weighted_minus_legacy']):+.6f} points.",
        f"- P1-WL: {largest_wl['rank_pair']} changes by "
        f"{float(largest_wl['p1_wl_weighted_minus_legacy']):+.6f} points.",
        "",
        "The support-weighted policy weights every literal cell by its recorded",
        "support, including east/west cells and every numbered Y/O/S/K slot present.",
        "",
    ])
    return "\n".join(lines)


def _source_manifest(path: Path) -> dict[str, str] | None:
    candidate = path.parent / "manifest.json"
    if not candidate.is_file():
        return None
    return {"path": str(candidate.resolve()), "sha256": _sha256(candidate)}


def _software_revision(repository_root: Path) -> dict[str, object]:
    def git(*args: str) -> str:
        completed = subprocess.run(
            ("git", "-C", str(repository_root), *args),
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    return {
        "repository_root": str(repository_root),
        "commit": git("rev-parse", "HEAD"),
        "working_tree_dirty": bool(git("status", "--porcelain")),
    }


def _write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    iterator = iter(rows)
    try:
        first = next(iterator)
    except StopIteration as error:
        raise ValueError(f"Cannot write empty artifact: {path}") from error
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p1", type=Path, default=DEFAULT_P1)
    parser.add_argument("--p1-wl", type=Path, default=DEFAULT_P1_WL)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--persisted-prior",
        type=Path,
        default=DEFAULT_PERSISTED_PRIOR,
        help=(
            "Fixed P1-prime-WL paired-prior path. An identical existing file is "
            "accepted; a different file is never replaced silently."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output = run_experiment(
        p1_path=args.p1,
        p1_wl_path=args.p1_wl,
        output=args.output,
        persisted_prior_path=args.persisted_prior,
    )
    print(f"Output: {output}")
    print((output / "findings.md").read_text(encoding="utf-8"))
    return 0
