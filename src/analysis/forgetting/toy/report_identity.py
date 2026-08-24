"""Put a compact manifest-derived identity block at the top of HTML reports."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Mapping, Sequence


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/forgetting/toy")
START_MARKER = "<!-- manifest-identity:start -->"
END_MARKER = "<!-- manifest-identity:end -->"


def _display(value: object) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return "[" + ", ".join(_display(item) for item in value) + "]"
    return str(value)


def _identity_items(
    manifest: Mapping[str, object],
    *,
    report_name: str,
    run_directory: Path,
) -> list[tuple[str, str]]:
    items = [
        ("Experiment", _display(manifest.get("experiment", "unknown"))),
        ("Report", report_name),
        ("Run ID", run_directory.name),
    ]
    if manifest.get("run_role") is not None:
        items.append(("Role", _display(manifest["run_role"])))
    if manifest.get("status") is not None:
        items.append(("Status", _display(manifest["status"])))
    if manifest.get("started_at") is not None:
        items.append(("Started", _display(manifest["started_at"])))
    if manifest.get("finished_at") is not None:
        items.append(("Finished", _display(manifest["finished_at"])))

    world = manifest.get("world")
    if isinstance(world, Mapping):
        items.append(
            (
                "World",
                f"players={_display(world.get('player_count', '?'))}; "
                f"latent gap={_display(world.get('latent_gap', '?'))}; "
                f"Q={_display(world.get('q', '?'))}; "
                f"K={_display(world.get('k', '?'))}",
            )
        )

    ensemble = manifest.get("ensemble")
    if isinstance(ensemble, Mapping):
        items.append(
            (
                "Ensemble",
                f"seed={_display(ensemble.get('master_seed', '?'))}; "
                f"replicates={_display(ensemble.get('replicate_count', '?'))}; "
                f"events/replicate="
                f"{_display(ensemble.get('events_per_replicate', '?'))}; "
                f"persistence="
                f"{_display(ensemble.get('persistence_events', 'n/a'))}",
            )
        )

    history = manifest.get("history")
    if isinstance(history, Mapping):
        items.append(
            (
                "History",
                f"seed={_display(history.get('master_seed', '?'))}; "
                f"events={_display(history.get('events', '?'))}; "
                f"bouts={_display(history.get('global_bouts', '?'))}",
            )
        )

    batch = manifest.get("batch")
    if isinstance(batch, Mapping):
        items.append(
            (
                "Batch",
                f"models={_display(batch.get('completed_models', '?'))}/"
                f"{_display(batch.get('requested_models', '?'))}; "
                f"map seed={_display(batch.get('map_master_seed', '?'))}; "
                f"history seed={_display(batch.get('history_master_seed', '?'))}; "
                f"replicates={_display(batch.get('histories_per_model', '?'))}; "
                f"events={_display(batch.get('events_per_history', '?'))}; "
                f"raw half-range={_display(batch.get('half_range', '?'))}",
            )
        )

    initializations = manifest.get("initializations")
    if isinstance(initializations, Mapping):
        for name, ratings in initializations.items():
            items.append((f"Initialization {name}", _display(ratings)))
    return items


def manifest_identity_html(
    manifest: Mapping[str, object],
    *,
    report_name: str,
    run_directory: Path,
) -> str:
    rows = "".join(
        "<tr>"
        f"<th style='padding:.25rem .65rem .25rem 0;text-align:left;"
        f"vertical-align:top;white-space:nowrap'>{html.escape(label)}</th>"
        f"<td style='padding:.25rem 0;overflow-wrap:anywhere'>"
        f"{html.escape(value)}</td>"
        "</tr>"
        for label, value in _identity_items(
            manifest,
            report_name=report_name,
            run_directory=run_directory,
        )
    )
    return f"""
  {START_MARKER}
  <section class="manifest-identity" style="margin:0 0 1.5rem;padding:.8rem 1rem;background:#f3f6fa;border:1px solid #cbd5e1;border-radius:.35rem">
    <h2 style="margin:0 0 .45rem;font-size:1.05rem">Run identity</h2>
    <table style="border-collapse:collapse;width:100%;font-size:.92rem"><tbody>{rows}</tbody></table>
  </section>
  {END_MARKER}
"""


def inject_manifest_identity(
    document: str,
    manifest: Mapping[str, object],
    *,
    report_name: str,
    run_directory: Path,
) -> str:
    document = re.sub(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        "",
        document,
        flags=re.DOTALL,
    )
    heading_end = document.find("</h1>")
    if heading_end < 0:
        raise ValueError(f"HTML report has no h1: {run_directory / report_name}")
    insertion = heading_end + len("</h1>")
    identity = manifest_identity_html(
        manifest,
        report_name=report_name,
        run_directory=run_directory,
    )
    return document[:insertion] + identity + document[insertion:]


def refresh_run_reports(
    run_directory: Path,
    manifest: Mapping[str, object] | None = None,
) -> int:
    if manifest is None:
        manifest = json.loads(
            (run_directory / "manifest.json").read_text(encoding="utf-8")
        )
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping):
        return 0
    report_names = sorted(
        {
            str(value)
            for value in outputs.values()
            if str(value).lower().endswith(".html")
        }
    )
    refreshed = 0
    for report_name in report_names:
        path = run_directory / report_name
        if not path.exists():
            continue
        document = path.read_text(encoding="utf-8")
        path.write_text(
            inject_manifest_identity(
                document,
                manifest,
                report_name=report_name,
                run_directory=run_directory,
            ),
            encoding="utf-8",
        )
        refreshed += 1
    return refreshed


def refresh_report_tree(root: Path = DEFAULT_OUTPUT_ROOT) -> tuple[int, int]:
    runs = 0
    reports = 0
    for manifest_path in sorted(root.rglob("manifest.json")):
        refreshed = refresh_run_reports(manifest_path.parent)
        if refreshed:
            runs += 1
            reports += refreshed
    return runs, reports


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh manifest identity blocks in toy HTML reports."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    runs, reports = refresh_report_tree(args.root)
    print(f"Refreshed {reports} HTML reports across {runs} runs beneath {args.root}")


if __name__ == "__main__":
    main()
