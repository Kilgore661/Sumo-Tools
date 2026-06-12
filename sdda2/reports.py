from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from .models import (
    InputActionRecord,
    InputResolutionRecord,
    InputWorklistRecord,
    ProducerSearchRecord,
    Product,
    ProductEvidenceRecord,
    ProductSummaryRecord,
)


def write_product_reports(
    product: Product,
    evidence: list[ProductEvidenceRecord],
    summary: list[ProductSummaryRecord],
    input_worklist: list[InputWorklistRecord],
    input_actions: list[InputActionRecord],
    producer_search: list[ProducerSearchRecord],
    input_resolutions: list[InputResolutionRecord],
) -> None:
    product.output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(product.output_dir / "product.csv", [_product_row(product)])
    _write_csv(product.output_dir / "product_evidence.csv", evidence)
    _write_csv(product.output_dir / "product_summary.csv", summary)
    _write_csv(product.output_dir / "product_review.csv", _review_rows(evidence))
    _write_csv(product.output_dir / "input_worklist.csv", input_worklist)
    _write_csv(product.output_dir / "input_actions.csv", input_actions)
    _write_csv(product.output_dir / "producer_search.csv", producer_search)
    _write_csv(product.output_dir / "input_resolution.csv", input_resolutions)


def _product_row(product: Product) -> dict[str, str]:
    return {
        "product_id": product.product_id,
        "builder_root_module": product.builder_root_module,
        "import_root": str(product.import_root),
        "artifact_description": product.artifact_description,
        "distribution_mode": product.distribution_mode,
        "output_dir": str(product.output_dir),
    }


def _review_rows(evidence: list[ProductEvidenceRecord]) -> list[ProductEvidenceRecord]:
    return [
        row
        for row in evidence
        if row.source_distribution_decision in {"review", "include_or_regenerate"}
        or row.effective_review_priority == "high"
    ]


def _write_csv(path: Path, rows: list[object]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    dict_rows = [row if isinstance(row, dict) else asdict(row) for row in rows]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dict_rows[0]))
        writer.writeheader()
        writer.writerows(dict_rows)
