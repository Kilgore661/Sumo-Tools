from __future__ import annotations

from collections import Counter

from sdda.dataflow.analysis import analyse as analyse_dataflow

from .models import Product, ProductEvidenceRecord, ProductSummaryRecord


def analyse_product(product: Product) -> tuple[list[ProductEvidenceRecord], list[ProductSummaryRecord]]:
    dataflow_result = analyse_dataflow(
        root_module=product.builder_root_module,
        import_root=product.import_root,
    )
    evidence = [
        ProductEvidenceRecord(
            product_id=product.product_id,
            builder_root_module=product.builder_root_module,
            family_id=row.family_id,
            family_pattern=row.family_pattern,
            source_distribution_bucket=row.source_distribution_bucket,
            source_distribution_decision=row.source_distribution_decision,
            classification=row.classification,
            distribution_decision=row.distribution_decision,
            execution_status=row.execution_status,
            effective_review_priority=row.effective_review_priority,
            actions=row.actions,
            family_kind=row.family_kind,
            evidence_count=row.evidence_count,
            modules=row.modules,
            reason=row.reason,
        )
        for row in dataflow_result.source_distribution_inputs
    ]
    summary = _summary_records(product, dataflow_result, evidence)
    return evidence, summary


def _summary_records(product: Product, dataflow_result: object, evidence: list[ProductEvidenceRecord]) -> list[ProductSummaryRecord]:
    bucket_counts = Counter(row.source_distribution_bucket for row in evidence)
    records = [
        ProductSummaryRecord(product.product_id, "builder_root_module", product.builder_root_module),
        ProductSummaryRecord(product.product_id, "artifact_description", product.artifact_description),
        ProductSummaryRecord(product.product_id, "distribution_mode", product.distribution_mode),
        ProductSummaryRecord(product.product_id, "project_modules_indexed", str(len(dataflow_result.modules))),
        ProductSummaryRecord(product.product_id, "reachable_modules", str(len(dataflow_result.reachable_modules))),
        ProductSummaryRecord(product.product_id, "file_uses", str(len(dataflow_result.file_uses))),
        ProductSummaryRecord(product.product_id, "file_families", str(len(dataflow_result.file_families))),
        ProductSummaryRecord(product.product_id, "source_distribution_rows", str(len(evidence))),
        ProductSummaryRecord(product.product_id, "unresolved_records", str(len(dataflow_result.unresolved))),
    ]
    records.extend(
        ProductSummaryRecord(product.product_id, f"bucket:{bucket}", str(count))
        for bucket, count in sorted(bucket_counts.items())
    )
    return records

