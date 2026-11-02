"""Produce, assemble and locally deploy the independent Elo-89 site."""

from __future__ import annotations

from pathlib import Path

from src.analysis.site89.producer import produce_site89_bundle
from src.infra.history_artifacts import POST_1988_START_YEAR, history_from_year
from src.infra.live_store.api import get_history
from src.infra.new_banzuke.api import NEW_BANZUKE_JSON, load_new_banzuke
from src.infra.torikumi import load_future
from src.infra.torikumi.persistence import DEFAULT_FUTURE_PATH
from src.products.make_elo89.__main__ import (
    build_parser,
    main as run_make_elo89,
    reject_conflicting_modes,
)


def main(argv: list[str] | None = None) -> None:
    """Run the live-store-first Elo-89 production and publication workflow."""

    args = build_parser().parse_args(argv)
    reject_conflicting_modes(args)

    if not args.no_build:
        print("[build_elo89] Loading History from the live store...", flush=True)
        full_history = get_history()
        history = history_from_year(full_history, POST_1988_START_YEAR)
        future_path = Path(DEFAULT_FUTURE_PATH)
        new_banzuke_path = Path(NEW_BANZUKE_JSON)
        print("[build_elo89] Producing the Elo-89 site-data bundle...", flush=True)
        produce_site89_bundle(
            history=history,
            output_root=args.data_bundle,
            history_source="live store (selected from 1989/01)",
            future=load_future(future_path) if future_path.is_file() else None,
            new_banzuke=(
                load_new_banzuke(new_banzuke_path)
                if new_banzuke_path.is_file()
                else None
            ),
            progress=lambda message: print(f"[build_elo89] {message}", flush=True),
        )
        print(f"Produced Elo-89 site-data bundle: {args.data_bundle}")

    print("[build_elo89] Assembling and deploying the site...", flush=True)
    run_make_elo89(argv)


if __name__ == "__main__":
    main()
