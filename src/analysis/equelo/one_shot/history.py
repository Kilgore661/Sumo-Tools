import datetime

from ....infra.connect import connect
from ....sumo_core.History import History

from ..expt1.Oracle import _collapse_annotation, _filter_basho_1989_onward
from .config import MODERN_START_YEAR


def load_modern_history(
    end_year: int | None,
    use_zip: bool,
) -> History:
    raw_history = connect(MODERN_START_YEAR, datetime.datetime.now().year, use_zip=use_zip)

    modern_history = History()
    for date, basho in raw_history.items():
        if date.year < MODERN_START_YEAR:
            continue
        if end_year is not None and date.year > end_year:
            continue

        modern_history[date] = _filter_basho_1989_onward(
            basho=basho,
            collapse_fn=_collapse_annotation,
        )

    return modern_history
