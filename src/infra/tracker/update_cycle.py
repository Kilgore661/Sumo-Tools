"""
Tracker update-cycle orchestration.

This module coordinates one tracker update cycle.

It owns the concrete sequencing of tracker sub-steps and returns an
UpdateResult describing the overall outcome.

Current structure:

1. retrieval / download
2. conditional rebuild
3. conditional publish
4. conditional cache handling
5. conditional analysis
6. derived-artifact validation

Only the retrieval stage is currently wired to real downloader behaviour.
The downstream stages are present as placeholders so that the orchestration
shape already matches the agreed design.
"""

from .types import RequestedDateDays, RetrievalResult, UpdateResult
from .scraper.downloader import download
from ..parser.parser2 import parse_and_save_history, logger, OUTPUT_DIR


def _rebuild_canonical_history() -> bool:
    """
    Rebuild and publish canonical history.

    Delegates to parser2.parse_and_save_history, including the required
    logger lifecycle that parser2.main() would normally provide.
    """
    try:
        logger.initialise(output_dir=OUTPUT_DIR)

        # TEMP: fixed range for testing - how do we get these numbers from the state/params?
        # Don't use 2026 because I think sumodb have changed the format of the Mz section
        parse_and_save_history(start_year=1958, end_year=2025)

        return True

    except Exception as exc:
        print(f"[update_cycle] rebuild failed: {exc}")
        return False
    logger.close()

def _publish_canonical_history() -> bool:
    """
    Placeholder for canonical-history publication.
    """
    return True


def _refresh_cache() -> bool:
    """
    Placeholder for cache refresh after source change.
    """
    return True


def _ensure_cache() -> bool:
    """
    Placeholder for cache presence when source data is unchanged.
    """
    return True


def _analyse() -> bool:
    """
    Placeholder for required analysis/product generation.
    """
    return True


def _derived_artifacts_exist() -> bool:
    """
    Placeholder for derived-artifact validation.

    Current agreed meaning of validation is existence only.
    """
    return True


def run_update_cycle(requested_date_days: RequestedDateDays) -> UpdateResult:
    """
    Run one update cycle for the requested BashoDayRefs.
    """
    if not requested_date_days:
        return UpdateResult.NO_NEW_DATA

    print(f"[update_cycle] checking {len(requested_date_days)} previous results")

    retrieval_result = download(requested_date_days)

    match retrieval_result:
        case RetrievalResult.FAILURE:
            print("[update_cycle] retrieval failed")
            return UpdateResult.RETRIEVAL_FAILED

        case RetrievalResult.SUCCESS_CHANGED:
            print("[update_cycle] retrieval changed source dataset")

            if not _rebuild_canonical_history():
                print("[update_cycle] rebuild failed")
                return UpdateResult.REBUILD_FAILED

            if not _publish_canonical_history():
                print("[update_cycle] publish failed")
                return UpdateResult.PUBLISH_FAILED

            if not _refresh_cache():
                print("[update_cycle] cache refresh failed")
                return UpdateResult.CACHE_FAILED

            if not _analyse():
                print("[update_cycle] analysis failed")
                return UpdateResult.ANALYSIS_FAILED

            if not _derived_artifacts_exist():
                print("[update_cycle] required derived artifacts are missing")
                return UpdateResult.DERIVED_ARTIFACTS_MISSING

            print("[update_cycle] update cycle succeeded after source change")
            return UpdateResult.SUCCESS

        case RetrievalResult.SUCCESS_UNCHANGED:
            print("[update_cycle] retrieval left source dataset unchanged")

            if not _ensure_cache():
                print("[update_cycle] cache ensure failed")
                return UpdateResult.CACHE_FAILED

            if _derived_artifacts_exist():
                print("[update_cycle] no new data and downstream state already satisfied")
                return UpdateResult.NO_NEW_DATA

            if not _analyse():
                print("[update_cycle] analysis failed while repairing downstream state")
                return UpdateResult.ANALYSIS_FAILED

            if not _derived_artifacts_exist():
                print("[update_cycle] required derived artifacts are still missing")
                return UpdateResult.DERIVED_ARTIFACTS_MISSING

            print("[update_cycle] update cycle succeeded by repairing downstream state")
            return UpdateResult.SUCCESS

        case _:
            raise RuntimeError(f"Unhandled RetrievalResult: {retrieval_result!r}")
