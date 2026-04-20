"""
Offline publisher for website standings datasets.

Generates the published multiple-basho CSV/JSON pairs required by the
browser application, using fixed project policy and no command-line
parameters.
"""

from time import time

from src.infra.live_store.api import get_history

from src.analysis.standings.helpers import make_run_stamp
from src.analysis.standings.multiple_basho import (
    resolve_date,
    resolve_window_dates,
    get_multiple_basho_core,
)
from src.analysis.standings.multiple_basho_view import (
    get_multiple_basho_view,
)
from src.analysis.standings.multiple_basho_reports import (
    write_multiple_basho_view_csv,
)
from src.analysis.standings.publisher_reports import (
    publisher_run_output_dir,
    publisher_csv_file,
    publisher_json_file,
    publisher_site_config_file,
    write_sidecar_json,
    write_site_config_json,
)


SUPPORTED_NUM_BASHO = (1, 2, 3, 4, 5, 6, 12, 18, 24, 36, 60)
DIRECTION = "BACKWARDS"

DEFAULT_NUM_BASHO = 6
DEFAULT_DIVISION = "makuuchi"


def publish_one_window(
    history,
    run_stamp: str,
    anchor_date,
    num_basho: int,
) -> None:
    selected_dates = resolve_window_dates(
        history=history,
        date=anchor_date,
        direction=DIRECTION,
        num_basho=num_basho,
    )

    core = get_multiple_basho_core(
        history=history,
        selected_dates=selected_dates,
    )

    view = get_multiple_basho_view(
        history=history,
        core=core,
    )

    csv_file = publisher_csv_file(
        run_stamp=run_stamp,
        anchor_date=anchor_date,
        direction=DIRECTION,
        num_basho=num_basho,
    )

    json_file = publisher_json_file(
        run_stamp=run_stamp,
        anchor_date=anchor_date,
        direction=DIRECTION,
        num_basho=num_basho,
    )

    write_multiple_basho_view_csv(view, csv_file)

    write_sidecar_json(
        output_file=json_file,
        anchor_date=anchor_date,
        direction=DIRECTION,
        num_basho=num_basho,
        selected_dates=selected_dates,
    )


def main() -> None:
    t0 = time()

    history = get_history()

    run_stamp = make_run_stamp()

    publisher_run_output_dir(run_stamp).mkdir(
        parents=True,
        exist_ok=True,
    )

    anchor_date = resolve_date(
        history=history,
        direction=DIRECTION,
        requested_date=None,
    )

    config_file = publisher_site_config_file(run_stamp)

    write_site_config_json(
        output_file=config_file,
        anchor_date=anchor_date,
        direction=DIRECTION,
        supported_num_basho=SUPPORTED_NUM_BASHO,
        default_num_basho=DEFAULT_NUM_BASHO,
        default_division=DEFAULT_DIVISION,
    )

    for num_basho in SUPPORTED_NUM_BASHO:
        publish_one_window(
            history=history,
            run_stamp=run_stamp,
            anchor_date=anchor_date,
            num_basho=num_basho,
        )

    print(f"Publisher run complete in {time() - t0:.0f}s")
    print(f"Output: {publisher_run_output_dir(run_stamp)}")


if __name__ == "__main__":
    from time import time
    t0 = time()
    main()
    print( f'Run complete in {time() - t0:.0f} seconds.' )
