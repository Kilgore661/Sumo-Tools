"""Produce, assemble and deploy the Sumo '89 site from the live store."""

from __future__ import annotations

from pathlib import Path

from src.analysis.site89.producer import produce_site89_bundle
from src.infra.history_artifacts import POST_1988_START_YEAR, history_from_year
from src.infra.live_store.api import get_history
from src.infra.torikumi import load_future
from src.infra.torikumi.persistence import DEFAULT_FUTURE_PATH
from src.products.make_site89.__main__ import (
    build_parser,
    main as run_make_site89,
    reject_conflicting_modes,
)


def main(argv: list[str] | None = None) -> None:
    """Run the live-store-first Sumo '89 production and deployment workflow."""

    args = build_parser().parse_args(argv)
    reject_conflicting_modes(args)

    if not args.no_build:
        full_history = get_history()
        history = history_from_year(full_history, POST_1988_START_YEAR)
        future_path = Path(DEFAULT_FUTURE_PATH)
        produce_site89_bundle(
            history=history,
            output_root=args.data_bundle,
            history_source="live store (selected from 1989/01)",
            future=load_future(future_path) if future_path.is_file() else None,
        )
        print(f"Produced site-data bundle: {args.data_bundle}")

    run_make_site89(argv)


if __name__ == "__main__":
    main()
