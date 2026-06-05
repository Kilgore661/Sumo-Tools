# src/infra/get_bios/shikona_normalisation_probe.py

"""
Probe for public shikona disambiguation.

This is prototype/reference code, not production resolver logic.

It investigates whether retired rikishi with non-unique public shikona can be
disambiguated acceptably by an Intai-based suffix scheme, and compares that
with using the full recorded latest shikona as the collision key.

Run from the repository root:

    python -m src.infra.get_bios.shikona_normalisation_probe
    python -m src.infra.get_bios.shikona_normalisation_probe --full-shikona

The first command uses the default first-token shikona key and tries the old
Intai suffix scheme:

    Shikona
    Shikona (YYYY)
    Shikona (YYYY/MM)

Use its summary and unresolved_findings.csv to see why the Intai scheme is not
good enough. In particular, missing Intai values and duplicate Intai year/month
cases show up as findings.

The second command uses the full recorded latest shikona string as the
collision key. Use its summary, proposed_labels.csv, and unresolved_findings.csv
to check that full shikona is the viable public-facing disambiguator.

Outputs are written by default to:

    files/output/infra/get_bios/shikona_normalisation_probe/

The production rule is recorded in "Shikona Resolution.md":

    If History shikona is non-unique and the rikishi is retired,
    use full shikona; otherwise use the History shikona.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.analysis.sumo_history.basho_results.dates import represented_dates
from src.infra.get_bios.shikona_normalisation_probe_analysis import (
    analyse,
    write_finding_csv,
    write_label_csv,
    write_summary,
)
from src.infra.get_bios.shikona_normalisation_probe_intai import try_fix_missing_intai
from src.infra.get_bios.shikona_normalisation_probe_model import (
    normalise_rikid,
    parse_bio_records,
)
from src.infra.live_store.api import get_history
from src.products.make_site2.data_output import load_history_from_zip
from src.sumo_core.History import History


OUTPUT_ROOT = Path("files") / "output" / "infra" / "get_bios"
DEFAULT_INPUT_JSON = OUTPUT_ROOT / "rikishi_bios.json"
DEFAULT_OUTPUT_DIR = OUTPUT_ROOT / "shikona_normalisation_probe"


def load_probe_history(history_zip: Path | None) -> History:
    if history_zip is not None:
        return load_history_from_zip(history_zip)
    return get_history()


def latest_basho_rikids(history: History) -> tuple[str, set[str]]:
    dates = represented_dates(history)
    if not dates:
        raise ValueError("No represented basho dates found")

    latest_date = dates[-1]
    return str(latest_date), {
        normalise_rikid(str(int(rikid)))
        for rikid in history(latest_date).banzuke.riks
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe the proposed get_bios shikona normalisation rule.",
    )
    parser.add_argument(
        "--input-json",
        default=str(DEFAULT_INPUT_JSON),
        help=f"Parsed get_bios JSON input path (default: {DEFAULT_INPUT_JSON})",
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Optional zip-backed History serialisation. If absent, use the live store.",
    )
    parser.add_argument(
        "--full-shikona",
        action="store_true",
        help="Use the full recorded latest shikona string instead of the default first-token key.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_json = Path(args.input_json)
    output_dir = Path(args.output_dir)

    history = load_probe_history(args.history_zip)
    latest_basho, latest_basho_rikids_set = latest_basho_rikids(history)
    print(
        f"Latest represented basho is {latest_basho} "
        f"with {len(latest_basho_rikids_set)} rikishi."
    )

    raw: Any = json.loads(input_json.read_text(encoding="utf-8"))
    records = parse_bio_records(raw, full_shikona=args.full_shikona)
    records, fix_findings = try_fix_missing_intai(
        records,
        output_dir,
        latest_basho=latest_basho,
        latest_basho_rikids_set=latest_basho_rikids_set,
    )
    all_labels, collision_labels, findings = analyse(records)
    findings = [*fix_findings, *findings]

    output_dir.mkdir(parents=True, exist_ok=True)

    write_summary(
        output_dir / "summary.txt",
        records,
        all_labels,
        collision_labels,
        findings,
        latest_basho=latest_basho,
        latest_basho_rikid_count=len(latest_basho_rikids_set),
        full_shikona=args.full_shikona,
    )
    write_label_csv(output_dir / "proposed_labels.csv", all_labels)
    write_label_csv(output_dir / "latest_shikona_collisions.csv", collision_labels)
    write_finding_csv(output_dir / "unresolved_findings.csv", findings)

    print(f"Read {len(records)} bio records from {input_json}")
    print(f"Wrote {output_dir / 'summary.txt'}")
    print(f"Wrote {output_dir / 'proposed_labels.csv'}")
    print(f"Wrote {output_dir / 'latest_shikona_collisions.csv'}")
    print(f"Wrote {output_dir / 'unresolved_findings.csv'}")

    if findings:
        print(f"\nProbe found {len(findings)} unresolved findings.")
    else:
        print("\nProbe found no unresolved findings.")


if __name__ == "__main__":
    main()
