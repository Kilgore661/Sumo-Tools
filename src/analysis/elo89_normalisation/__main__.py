"""Run independent normalisation diagnostics from saved Elo-89 artifacts."""

import argparse
from pathlib import Path

from .inputs import digest, load_inputs, safe_output
from .accounting import reconstruct, reconcile_site
from .summary import build_summaries
from .report import write_outputs

DEFAULT_ELO_ROOT = Path("files/output/analysis/site89_bundle/sources/elo89")
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/elo89_normalisation")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, help="Read annotated ZIP instead of the default live store.")
    parser.add_argument("--elo-root", type=Path, default=DEFAULT_ELO_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--site-changes", type=Path,
                        help="Explicit site rating-change CSV directory to reconcile (auto-detected for a site bundle).")
    return parser


def load_history(args):
    if args.history_zip is None:
        from src.infra.live_store.api import get_history
        return get_history(), {"kind": "live_store"}
    from src.infra.persistence.annotated_serialiser import load_history_with_annotations
    path = args.history_zip.resolve()
    if path.suffix.lower() != ".zip":
        path = path.with_suffix(".zip")
    fingerprint = digest(path)
    history = load_history_with_annotations(str(path.with_suffix("")))
    return history, {"kind": "history_zip", "path": str(path), "sha256": fingerprint}


def main(argv=None):
    args = build_parser().parse_args(argv)
    sources = [args.elo_root]
    if args.history_zip is not None:
        sources.append(args.history_zip if args.history_zip.suffix == ".zip" else args.history_zip.with_suffix(".zip"))
    site = args.site_changes
    if site is None:
        candidate = args.elo_root.parent.parent / "site/current-sumo/rating-changes/data"
        if candidate.is_dir():
            site = candidate
    if site is not None:
        sources.append(site)
    safe_output(args.output_root, sources)
    print("Loading History and validating production artifacts...", flush=True)
    history, source = load_history(args)
    inputs = load_inputs(args.elo_root, history)
    source["represented_history_sha256"] = inputs.history_digest
    print(f"Accounting for {len(inputs.dates)} basho...", flush=True)
    frame, exclusions = reconstruct(inputs)
    site_hashes = ({str(path.resolve()): digest(path) for path in site.glob("*-change.csv")}
                   if site is not None else {})
    checked = reconcile_site(frame, site) if site is not None else None
    print(f"Reconciled {len(frame):,} wrestler-windows; summarising...", flush=True)
    summaries, comparisons, exceptions = build_summaries(frame)
    inputs.verify_unchanged()
    if source["kind"] == "history_zip" and digest(Path(source["path"])) != source["sha256"]:
        raise ValueError("History ZIP changed during analysis")
    write_outputs(args.output_root, inputs, frame, exclusions, summaries, comparisons,
                  exceptions, source, checked, site_hashes)
    inputs.verify_unchanged()
    for path, expected in site_hashes.items():
        if digest(Path(path)) != expected:
            raise ValueError(f"Site input changed during analysis: {path}")
    print(f"Outputs: {args.output_root.resolve()}", flush=True)


if __name__ == "__main__":
    main()
