"""Measure cumulative rating-mass change from unequal-K bout updates.

The experiment consumes the persisted controlled model-selection forecast
ledger. It does not rerun or alter any rating model. Its pure core reduces
ledger rows into model, K-pair and basho accounting; the CLI persists those
results with the source-ledger hash and a short findings report.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Iterator


MODEL_ORDER = ("B", "B_k", "B_P", "B_kP")
REQUIRED_FIELDS = frozenset(
    {"model", "date", "k_a", "k_b", "delta_a", "delta_b"}
)
K_PAIR_LABELS = {
    (10.0, 15.0): "sanyaku--maegashira",
    (15.0, 25.0): "maegashira--juryo",
    (25.0, 35.0): "juryo--sub-sekitori",
}


@dataclass(frozen=True, slots=True)
class LedgerMassRow:
    """The forecast-ledger fields required by this experiment."""

    model: str
    date: str
    k_a: float
    k_b: float
    delta_a: float
    delta_b: float


@dataclass(frozen=True, slots=True)
class ModelMassSummary:
    """Whole-period rating-mass accounting for one model."""

    model: str
    rated_bout_count: int
    unequal_k_bout_count: int
    unequal_k_bout_share: float
    net_mass_change: float
    gross_absolute_mass_change: float
    positive_mass_change: float
    negative_mass_change: float
    mean_signed_change_per_rated_bout: float
    mean_signed_change_per_unequal_k_bout: float
    mean_absolute_change_per_unequal_k_bout: float
    max_absolute_single_bout_change: float
    cancellation_share: float
    same_k_residual: float
    max_absolute_same_k_residual: float


@dataclass(frozen=True, slots=True)
class KPairMassSummary:
    """Rating-mass accounting for one unordered unequal-K pair."""

    model: str
    k_low: float
    k_high: float
    boundary: str
    bout_count: int
    share_of_model_unequal_k_bouts: float
    net_mass_change: float
    gross_absolute_mass_change: float
    mean_signed_change_per_bout: float
    mean_absolute_change_per_bout: float
    max_absolute_single_bout_change: float


@dataclass(frozen=True, slots=True)
class BashoMassSummary:
    """Unequal-K mass flow for one model and basho."""

    model: str
    date: str
    bout_count: int
    net_mass_change: float
    gross_absolute_mass_change: float
    cumulative_net_mass_change: float


@dataclass(frozen=True, slots=True)
class DualKMassResult:
    """Complete immutable output of the ledger reduction."""

    models: tuple[ModelMassSummary, ...]
    k_pairs: tuple[KPairMassSummary, ...]
    basho: tuple[BashoMassSummary, ...]


@dataclass(slots=True)
class _MassAccumulator:
    rated_bouts: int = 0
    unequal_k_bouts: int = 0
    net: float = 0.0
    gross: float = 0.0
    positive: float = 0.0
    negative: float = 0.0
    max_absolute: float = 0.0
    same_k_residual: float = 0.0
    max_absolute_same_k_residual: float = 0.0

    def add(self, mass_change: float, *, unequal_k: bool) -> None:
        self.rated_bouts += 1
        if not unequal_k:
            self.same_k_residual += mass_change
            self.max_absolute_same_k_residual = max(
                self.max_absolute_same_k_residual,
                abs(mass_change),
            )
            return
        self.unequal_k_bouts += 1
        self.net += mass_change
        self.gross += abs(mass_change)
        self.positive += max(mass_change, 0.0)
        self.negative += min(mass_change, 0.0)
        self.max_absolute = max(self.max_absolute, abs(mass_change))


@dataclass(slots=True)
class _GroupAccumulator:
    bouts: int = 0
    net: float = 0.0
    gross: float = 0.0
    max_absolute: float = 0.0

    def add(self, mass_change: float) -> None:
        self.bouts += 1
        self.net += mass_change
        self.gross += abs(mass_change)
        self.max_absolute = max(self.max_absolute, abs(mass_change))


def read_ledger(path: Path) -> Iterator[LedgerMassRow]:
    """Stream the required typed fields from a forecast ledger."""

    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        missing = REQUIRED_FIELDS - frozenset(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Forecast ledger is missing required fields: {sorted(missing)}")
        for row in reader:
            yield LedgerMassRow(
                model=row["model"],
                date=row["date"],
                k_a=float(row["k_a"]),
                k_b=float(row["k_b"]),
                delta_a=float(row["delta_a"]),
                delta_b=float(row["delta_b"]),
            )


def analyse(rows: Iterable[LedgerMassRow]) -> DualKMassResult:
    """Reduce forecast rows into model, K-pair and basho mass accounting."""

    models = {name: _MassAccumulator() for name in MODEL_ORDER}
    pairs: dict[tuple[str, float, float], _GroupAccumulator] = {}
    basho: dict[tuple[str, str], _GroupAccumulator] = {}

    for row in rows:
        model = models[row.model]
        mass_change = row.delta_a + row.delta_b
        unequal_k = row.k_a != row.k_b
        model.add(mass_change, unequal_k=unequal_k)
        if not unequal_k:
            continue
        k_low, k_high = sorted((row.k_a, row.k_b))
        pairs.setdefault(
            (row.model, k_low, k_high), _GroupAccumulator()
        ).add(mass_change)
        basho.setdefault((row.model, row.date), _GroupAccumulator()).add(mass_change)

    if any(model.rated_bouts == 0 for model in models.values()):
        missing = [name for name, model in models.items() if model.rated_bouts == 0]
        raise ValueError(f"Forecast ledger has no rows for declared models: {missing}")

    model_rows = tuple(_model_summary(name, models[name]) for name in MODEL_ORDER)
    pair_rows = tuple(
        _pair_summary(key, value, models[key[0]].unequal_k_bouts)
        for key, value in sorted(
            pairs.items(), key=lambda item: (MODEL_ORDER.index(item[0][0]), item[0][1:])
        )
    )
    basho_rows = _basho_summaries(basho)
    return DualKMassResult(models=model_rows, k_pairs=pair_rows, basho=basho_rows)


def _model_summary(name: str, value: _MassAccumulator) -> ModelMassSummary:
    unequal = value.unequal_k_bouts
    return ModelMassSummary(
        model=name,
        rated_bout_count=value.rated_bouts,
        unequal_k_bout_count=unequal,
        unequal_k_bout_share=unequal / value.rated_bouts,
        net_mass_change=value.net,
        gross_absolute_mass_change=value.gross,
        positive_mass_change=value.positive,
        negative_mass_change=value.negative,
        mean_signed_change_per_rated_bout=value.net / value.rated_bouts,
        mean_signed_change_per_unequal_k_bout=(value.net / unequal if unequal else 0.0),
        mean_absolute_change_per_unequal_k_bout=(
            value.gross / unequal if unequal else 0.0
        ),
        max_absolute_single_bout_change=value.max_absolute,
        cancellation_share=(1.0 - abs(value.net) / value.gross if value.gross else 0.0),
        same_k_residual=value.same_k_residual,
        max_absolute_same_k_residual=value.max_absolute_same_k_residual,
    )


def _pair_summary(
    key: tuple[str, float, float],
    value: _GroupAccumulator,
    model_unequal_k_bouts: int,
) -> KPairMassSummary:
    model, k_low, k_high = key
    return KPairMassSummary(
        model=model,
        k_low=k_low,
        k_high=k_high,
        boundary=K_PAIR_LABELS[(k_low, k_high)],
        bout_count=value.bouts,
        share_of_model_unequal_k_bouts=value.bouts / model_unequal_k_bouts,
        net_mass_change=value.net,
        gross_absolute_mass_change=value.gross,
        mean_signed_change_per_bout=value.net / value.bouts,
        mean_absolute_change_per_bout=value.gross / value.bouts,
        max_absolute_single_bout_change=value.max_absolute,
    )


def _basho_summaries(
    values: dict[tuple[str, str], _GroupAccumulator],
) -> tuple[BashoMassSummary, ...]:
    rows: list[BashoMassSummary] = []
    for model in MODEL_ORDER:
        cumulative = 0.0
        model_values = sorted(
            (key, value) for key, value in values.items() if key[0] == model
        )
        for (_, date), value in model_values:
            cumulative += value.net
            rows.append(
                BashoMassSummary(
                    model=model,
                    date=date,
                    bout_count=value.bouts,
                    net_mass_change=value.net,
                    gross_absolute_mass_change=value.gross,
                    cumulative_net_mass_change=cumulative,
                )
            )
    return tuple(rows)


def write_outputs(result: DualKMassResult, ledger: Path, output: Path) -> None:
    """Persist reproducible experiment artifacts and source provenance."""

    output.mkdir(parents=True, exist_ok=True)
    _write_csv(output / "summary.csv", result.models)
    _write_csv(output / "by_k_pair.csv", result.k_pairs)
    _write_csv(output / "by_basho.csv", result.basho)
    source = ledger.resolve()
    manifest = {
        "experiment": "Cumulative unequal-K rating-mass measurement",
        "status": "diagnostic; does not apply a normalisation policy",
        "source_ledger": {
            "path": str(source),
            "sha256": _sha256(source),
            "size_bytes": source.stat().st_size,
        },
        "definition": {
            "bout_mass_change": "delta_a + delta_b",
            "unequal_k_bout": "k_a != k_b",
            "net_mass_change": "signed sum of bout mass changes",
            "gross_absolute_mass_change": "sum of absolute bout mass changes",
            "models": list(MODEL_ORDER),
        },
        "artifacts": {
            "summary": "summary.csv",
            "by_k_pair": "by_k_pair.csv",
            "by_basho": "by_basho.csv",
            "report": "report.md",
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (output / "report.md").write_text(_report(result, source), encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[object]) -> None:
    values = tuple(asdict(row) for row in rows)
    if not values:
        raise ValueError(f"Cannot write empty analytical output: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(values[0]))
        writer.writeheader()
        writer.writerows(values)


def _report(result: DualKMassResult, ledger: Path) -> str:
    summaries = {row.model: row for row in result.models}
    selected = summaries["B_kP"]
    pairs = tuple(row for row in result.k_pairs if row.model == "B_kP")
    pair_lines = "\n".join(
        f"| {row.k_low:g}--{row.k_high:g} | {row.boundary} | "
        f"{row.bout_count:,} | {row.net_mass_change:+.3f} | "
        f"{row.gross_absolute_mass_change:.3f} |"
        for row in pairs
    )
    return f"""# Cumulative Unequal-K Rating Mass

## Status

Completed diagnostic over `{ledger}`.

This experiment measures rating mass created or destroyed by the dual-K bout
rule in the persisted controlled post-1988 model-selection ledger. It does not
measure entrant or departure mass, active-population mean inflation, or the
effect of any normalisation policy.

## Headline result

For the selected `B_kP` model, {selected.unequal_k_bout_count:,} of
{selected.rated_bout_count:,} rated bouts ({selected.unequal_k_bout_share:.2%})
used unequal K values. Their cumulative signed rating-mass change was
{selected.net_mass_change:+.3f} points. Gross absolute flow was
{selected.gross_absolute_mass_change:.3f} points, so
{selected.cancellation_share:.2%} of gross flow cancelled in the signed total.

The mean signed contribution was
{selected.mean_signed_change_per_rated_bout:+.6f} points per rated bout and
{selected.mean_signed_change_per_unequal_k_bout:+.6f} points per unequal-K
bout. The largest absolute single-bout mass change was
{selected.max_absolute_single_bout_change:.3f} points.

## `B_kP` by K pair

| K pair | Boundary | Bouts | Net mass | Gross absolute mass |
|---|---|---:|---:|---:|
{pair_lines}

Cross-division bouts are not the whole unequal-K population. The
sanyaku--maegashira boundary is within Makuuchi and accounts for the largest
number of affected bouts.

## Initialisation sensitivity

The same bout population under `B_k` produced a cumulative signed mass change
of {summaries['B_k'].net_mass_change:+.3f} points. The sign and magnitude of
the unequal-K mass term therefore depend on the rating state and forecast
residuals, not just on the K schedule or affected-bout count.

## Interpretation boundary

The cumulative signed total is the rating mass added to or removed from all
ratings by unequal-K bout updates during the run. It is not itself the change
in the active-population mean at the endpoint: some recipients subsequently
leave the active population. Comparing this term with entrant/retirement
inflation requires active-population boundary accounting from the simulator.

Same-K residual mass is reported in `summary.csv` as a numerical invariant.
It should be zero apart from floating-point representation.
"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    """Run the experiment against one persisted forecast ledger."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    ledger = args.ledger.resolve()
    output = args.output or ledger.parent / "dual_k_mass"
    result = analyse(read_ledger(ledger))
    write_outputs(result, ledger, output)
    print(f"Wrote cumulative unequal-K mass artifacts to {output.resolve()}")


if __name__ == "__main__":
    main()
