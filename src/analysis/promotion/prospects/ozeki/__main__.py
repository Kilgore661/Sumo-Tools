"""Run the Ozeki promotion-prospects analysis."""

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path

from .run import run_analysis


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/promotion/prospects/ozeki")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260919)
    args = parser.parse_args()

    print("[0/8] Loading one History snapshot...", flush=True)
    if args.history_zip:
        from src.infra.persistence.annotated_serialiser import load_history_with_annotations

        path = args.history_zip.resolve()
        history = load_history_with_annotations(str(path.with_suffix("")))
        source = {
            "kind": "history_zip",
            "path": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    else:
        from src.infra.live_store.api import get_history, published_name_file

        history = get_history()
        source = {
            "kind": "live_store",
            "published_name_file": str(published_name_file()),
        }
    output_dir = args.output_root / datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    run_analysis(
        history, output_dir, source=source,
        bootstrap_samples=args.bootstrap_samples, seed=args.seed,
        progress=lambda message: print(message, flush=True),
    )


if __name__ == "__main__":
    main()

