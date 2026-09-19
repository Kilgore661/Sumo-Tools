"""Artifact writers for the Ozeki promotion-prospects analysis."""

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


def write_csv(path, rows):
    path = Path(path)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _percentage(value):
    return "—" if value is None else f"{value:.2%}"


def build_report(dataset, tables, *, bootstrap_samples, seed):
    opportunities = dataset["opportunities"]
    promotions = dataset["promotions"]
    resolved = [row for row in opportunities if row["resolved"]]
    complete = [row for row in resolved if row["complete_45_bouts"]]
    rules = sorted(tables["rules"], key=lambda row: (-row["f1"], row["rule"]))
    lines = [
        "# Ozeki promotion prospects analysis",
        "",
        "This is a retrospective statistical description of observed promotion",
        "decisions. It is not a JSA rule and is not public-site annotation data.",
        "",
        "## Coverage",
        "",
        f"- History: {dataset['basho_dates'][0]} to {dataset['basho_dates'][-1]}",
        f"- Retained promotion events: {len(promotions)}",
        f"- Distinct promoted rikishi: {len({r['rikishi_id'] for r in promotions})}",
        f"- Candidate-pool windows: {len(opportunities)}",
        f"- Resolved candidate-pool windows: {len(resolved)}",
        f"- Complete 45-bout resolved windows: {len(complete)}",
        f"- Distinct candidate-pool rikishi: {len({r['rikishi_id'] for r in opportunities})}",
        f"- Excluded immediate ozekiwake reinstatements: {len(dataset['excluded_reinstatements'])}",
        "",
        "The candidate pool has a first basho at maegashira, komusubi or",
        "sekiwake and the following two at komusubi or sekiwake. Promotions",
        "outside that pool remain in the recall denominator.",
        "",
        "## Predeclared rule comparisons",
        "",
        "A requires all three basho at K/S. B permits M in the first basho.",
        "C33 is A33 with at least ten wins in every basho.",
        "",
        "| Rule | TP | FP | FN | Precision | Recall | F1 | Clustered precision 95% | Clustered recall 95% |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rules:
        lines.append(
            f"| {row['rule']} | {row['tp']} | {row['fp']} | {row['fn']} | "
            f"{_percentage(row['precision'])} | {_percentage(row['recall'])} | "
            f"{_percentage(row['f1'])} | "
            f"{_percentage(row['precision_cluster_95_low'])}–"
            f"{_percentage(row['precision_cluster_95_high'])} | "
            f"{_percentage(row['recall_cluster_95_low'])}–"
            f"{_percentage(row['recall_cluster_95_high'])} |"
        )
    lines += [
        "",
        f"Cluster intervals use {bootstrap_samples} deterministic rikishi-cluster "
        f"resamples (seed {seed}). Wilson intervals are retained in `rules.csv`.",
        "Neither interval accounts fully for changing institutional practice.",
        "",
        "## Chronological validation",
        "",
        "For each fold, a rule is selected by training-period F1, then frozen and",
        "evaluated on the later period.",
        "",
        "| Training | Test | Selected | Training P/R/F1 | Test P/R/F1 | Test TP/FP/FN |",
        "|---|---|---|---|---|---|",
    ]
    for row in tables["forward_validation"]:
        lines.append(
            f"| {row['training_period']} | {row['test_period']} | {row['selected_rule']} | "
            f"{_percentage(row['training_precision'])} / {_percentage(row['training_recall'])} / {_percentage(row['training_f1'])} | "
            f"{_percentage(row['test_precision'])} / {_percentage(row['test_recall'])} / {_percentage(row['test_f1'])} | "
            f"{row['test_tp']} / {row['test_fp']} / {row['test_fn']} |"
        )
    lines += [
        "",
        "## Interpretation limits",
        "",
        "- Percentages describe this supplied History and outcome contract.",
        "- Overlapping windows are real decisions but are not independent.",
        "- Sparse categories remain uncertain even when their observed rate is high.",
        "- Fixed time blocks are diagnostics, not data-mined institutional eras.",
        "- Missing historical bouts can undercount a total; descriptive win tables",
        "  therefore use complete 45-bout windows.",
        "- Rank, wins and chronology cannot reconstruct deliberative reasons,",
        "  injuries, banzuke capacity or other unmodelled circumstances.",
        "- Selection on earlier history does not turn the selected candidate into",
        "  an official or deterministic promotion rule.",
        "",
        "See the CSV artifacts for support counts, distinct-rikishi counts, Wilson",
        "intervals, fixed-period results and component-result breakdowns.",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(output_dir, dataset, tables, *, source,
                    bootstrap_samples, seed):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    mappings = {
        "opportunities.csv": dataset["opportunities"],
        "promotions.csv": dataset["promotions"],
        "total_wins.csv": tables["total_wins"],
        "rank_patterns.csv": tables["rank_patterns"],
        "minimum_wins.csv": tables["minimum_wins"],
        "weak_result_position.csv": tables["weak_result_position"],
        "rules.csv": tables["rules"],
        "period_rules.csv": tables["period_rules"],
        "forward_validation.csv": tables["forward_validation"],
    }
    for filename, rows in mappings.items():
        write_csv(output_dir / filename, rows)
    report_path = output_dir / "report.md"
    report_path.write_text(
        build_report(dataset, tables, bootstrap_samples=bootstrap_samples, seed=seed),
        encoding="utf-8",
    )
    artifact_paths = sorted(output_dir.iterdir())
    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Retrospective Ozeki promotion-prospects analysis; not a JSA rule or public-site annotation feed.",
        "source": source,
        "history_first_basho": dataset["basho_dates"][0],
        "history_last_basho": dataset["basho_dates"][-1],
        "history_basho_count": len(dataset["basho_dates"]),
        "first_scored_promotion_banzuke": "1958/07",
        "observation_unit": "Promotion opportunity at a banzuke boundary; overlapping windows count separately.",
        "candidate_pool": "First basho M/K/S; following two basho K/S.",
        "outcome": "Promotion to Ozeki on the immediately following supplied banzuke.",
        "wins": "Regular wins including fusensho and excluding playoff wins.",
        "bootstrap": {
            "unit": "rikishi",
            "samples": bootstrap_samples,
            "seed": seed,
        },
        "fixed_periods": ["1958-1979", "1980-1999", "2000-latest"],
        "counts": {
            "promotions": len(dataset["promotions"]),
            "distinct_promoted_rikishi": len({
                row["rikishi_id"] for row in dataset["promotions"]
            }),
            "opportunities": len(dataset["opportunities"]),
            "resolved_opportunities": sum(row["resolved"] for row in dataset["opportunities"]),
            "distinct_opportunity_rikishi": len({
                row["rikishi_id"] for row in dataset["opportunities"]
            }),
            "excluded_reinstatements": len(dataset["excluded_reinstatements"]),
            "boundary_cases": len(dataset["boundary_cases"]),
        },
        "git_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip(),
        "git_status": subprocess.run(
            ["git", "status", "--short"], capture_output=True, text=True
        ).stdout,
        "artifact_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in artifact_paths
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report_path
