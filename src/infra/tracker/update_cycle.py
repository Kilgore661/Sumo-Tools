import os
from .types import RequestedDateDays, RetrievalResult, UpdateResult
from .scraper.downloader import download
from ...sumo_core.History import History
from ..parser.parser2 import parse_history, logger, OUTPUT_DIR
from ..persistence.new_sumo_serialiser import save_history_with_annotations
from ..config import EPOCH
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
    try:
        full_path = _canonical_history_path(start_year, end_year)
        save_history_with_annotations(history, full_path)
        return os.path.exists(full_path + ".zip")
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
    requested_date_days: RequestedDateDays,
    live_store: LiveStore,
) -> UpdateResult:
    """
    Run one update cycle for the requested BashoDayRefs.

    Policy:
    - retrieval failure => RETRIEVAL_FAILED
    - source changed => rebuild History, publish canonical zip, refresh live store
    - source unchanged => ensure live store and return NO_NEW_DATA
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

            start_year = EPOCH
            end_year = int(requested_date_days[-1].date.year)

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
