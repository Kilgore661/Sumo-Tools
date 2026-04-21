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

from pathlib import Path
import shutil

WEB_ROOT = Path(r"A:/local/html/standings")
WEB_DATA = WEB_ROOT / "data"

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



from pathlib import Path
import shutil

WEB_ROOT = Path(r"A:/local/html/standings")
WEB_DATA = WEB_ROOT / "data"


def deploy_to_local_web(run_dir: Path) -> None:
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)

    static_dir = Path(__file__).resolve().parent / "files"

    # Copy fixed web assets to the site root.
    for name in ["index.html", "standings.css", "standings.js.txt"]:
        source_file = static_dir / name
        target_file = WEB_ROOT / name
        shutil.copy2(source_file, target_file)

    # Remove old published data files so deployed data matches this run exactly.
    for old_file in WEB_DATA.iterdir():
        if old_file.is_file():
            old_file.unlink()

    # Copy all generated publisher artefacts, including site_config.json.
    for item in run_dir.iterdir():
        if item.is_file() and item.suffix.lower() in {".csv", ".json"}:
            shutil.copy2(item, WEB_DATA / item.name)

def main() -> None:
    t0 = time()

    history = get_history()

    run_stamp = make_run_stamp()

    run_dir = publisher_run_output_dir(run_stamp)
    run_dir.mkdir(
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

    deploy_to_local_web(run_dir)

    print(f"Publisher run complete in {time() - t0:.0f}s")
    print(f"Output: {run_dir}")
    print(f"Deployed to: {WEB_ROOT}")

if __name__ == '__main__':
    main()
