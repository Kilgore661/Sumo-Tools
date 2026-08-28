import os
from .types import RetrievalPlan, RetrievalResult, UpdateResult
from .scraper.downloader import download
from ...sumo_core.History import History
from ..parser.parser2 import parse_history, logger, OUTPUT_DIR
from ..persistence.new_sumo_serialiser import save_history_with_annotations
from ..config import EPOCH
from ..history_artifacts import POST_1988_START_YEAR, history_from_year
from ..live_store.LiveStore import LiveStore


def _rebuild_canonical_history(start_year: int, end_year: int) -> History | None:
    try:
        logger.initialise(output_dir=OUTPUT_DIR)
        return parse_history(start_year, end_year)
    except Exception as exc:
        print(f"[update_cycle] rebuild failed: {exc}")
        return None
    finally:
        logger.close()


def _canonical_history_path(start_year: int, end_year: int) -> str:
    output_dir = f"{OUTPUT_DIR}/Historys"
    filename = f"{start_year}_01 to {end_year}_11"
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)


def _publish_canonical_history(
    history: History,
    start_year: int,
    end_year: int,
) -> bool:
    """Publish the full History and its synchronized post-1988 derivative."""

    try:
        full_path = _canonical_history_path(start_year, end_year)
        save_history_with_annotations(history, full_path)
        expected_paths = [full_path + ".zip"]

        if start_year < POST_1988_START_YEAR <= end_year:
            post_1988_path = _canonical_history_path(
                POST_1988_START_YEAR, end_year
            )
            save_history_with_annotations(
                history_from_year(history, POST_1988_START_YEAR),
                post_1988_path,
            )
            expected_paths.append(post_1988_path + ".zip")

        return all(os.path.exists(path) for path in expected_paths)
    except Exception as exc:
        print(f"[update_cycle] publish failed: {exc}")
        return False


def _refresh_live_store(live_store: LiveStore, history: History) -> bool:
    """
    Publish the rebuilt History into the already-owned live store.
    """
    return live_store.publish(history)


def _ensure_live_store(live_store: LiveStore) -> bool:
    """
    Return True iff the owned live store currently exists.
    """
    return live_store.exists()


def run_update_cycle(
    retrieval_plan: RetrievalPlan,
    live_store: LiveStore,
) -> UpdateResult:
    """
    Run one update cycle for the requested source artifacts.

    Policy:
    - retrieval failure => RETRIEVAL_FAILED
    - source changed => rebuild History, publish canonical zip, refresh live store
    - source unchanged => ensure live store and return NO_NEW_DATA
    """
    if not retrieval_plan.banzuke_dates and not retrieval_plan.daily_results:
        return UpdateResult.NO_NEW_DATA

    print(
        "[update_cycle] checking "
        f"{len(retrieval_plan.banzuke_dates)} banzuke pages and "
        f"{len(retrieval_plan.daily_results)} previous results"
    )

    retrieval_result = download(retrieval_plan)

    match retrieval_result:
        case RetrievalResult.FAILURE:
            print("[update_cycle] retrieval failed")
            return UpdateResult.RETRIEVAL_FAILED

        case RetrievalResult.SUCCESS_CHANGED:
            print("[update_cycle] retrieval changed source dataset")

            start_year = EPOCH
            if not retrieval_plan.daily_results:
                print("[update_cycle] source changed but no daily results were requested")
                return UpdateResult.NO_NEW_DATA

            end_year = int(retrieval_plan.daily_results[-1].date.year)

            history = _rebuild_canonical_history(start_year, end_year)
            if history is None:
                print("[update_cycle] rebuild failed")
                return UpdateResult.REBUILD_FAILED

            if not _publish_canonical_history(history, start_year, end_year):
                print("[update_cycle] publish failed")
                return UpdateResult.PUBLISH_FAILED

            if not _refresh_live_store(live_store, history):
                print("[update_cycle] live store refresh failed")
                return UpdateResult.LIVE_STORE_FAILED

            print("[update_cycle] update cycle succeeded after source change")
            return UpdateResult.SUCCESS

        case RetrievalResult.SUCCESS_UNCHANGED:
            print("[update_cycle] retrieval left source dataset unchanged")

            if not _ensure_live_store(live_store):
                print("[update_cycle] live store ensure failed")
                return UpdateResult.LIVE_STORE_FAILED

            print("[update_cycle] no new data")
            return UpdateResult.NO_NEW_DATA

        case _:
            raise RuntimeError(f"Unhandled RetrievalResult: {retrieval_result!r}")
