"""Site-specific Bet365 next-day sumo odds probe."""

from __future__ import annotations

from argparse import Namespace
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

from src.misc.Betting import download_bet365_sumo_odds as scraper

from .adapters import existing_scraper_adapter
from .cli import COMMON_PLACE_IDS, run_source_cli


DEFAULT_PLACES = ("direct", *COMMON_PLACE_IDS)


def _factory(args, target: date):
    output_dir = args.output_dir or Path("files/output/misc/Betting/bet365")
    profile_dir = args.profile_dir or Path("files/output/misc/Betting/browser_profiles/bet365")
    namespace = Namespace(
        url=scraper.DEFAULT_URL,
        output_dir=output_dir,
        timezone=args.timezone,
        browser_channel=args.browser_channel,
        headed=args.headed,
        profile_dir=profile_dir,
        browser_path=args.browser_path,
        diagnostics=args.diagnostics,
        manual_wait_seconds=args.manual_wait_seconds,
    )
    return existing_scraper_adapter(
        scraper.download_once, namespace, ZoneInfo(args.timezone), target
    )


def main(argv: list[str] | None = None) -> int:
    return run_source_cli("bet365", DEFAULT_PLACES, _factory, argv)


if __name__ == "__main__":
    raise SystemExit(main())
