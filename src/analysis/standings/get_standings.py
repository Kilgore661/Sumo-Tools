import csv

from src.analysis.standings.config import CACHE_FILE
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.History import Date, History


def date_to_str(date: Date) -> str:
    return str(date)


def build_totals_cache_rows(history: History) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []

    for basho_date, basho_state in sorted(history.items()):
        summary = basho_state.summary
        banzuke = basho_state.banzuke

        rikishi_totals: dict[int, dict[str, int]] = {}

        for _day, daily_results in summary.items():
            for bout in daily_results.results_lookup.values():
                r1 = int(bout.rikishi1)
                r2 = int(bout.rikishi2)

                rikishi_totals.setdefault(r1, {"real_wins": 0, "all_wins": 0, "bout_count": 0})
                rikishi_totals.setdefault(r2, {"real_wins": 0, "all_wins": 0, "bout_count": 0})

                rikishi_totals[r1]["bout_count"] += 1
                rikishi_totals[r2]["bout_count"] += 1

                if bout.outcome1 == Outcome.W:
                    rikishi_totals[r1]["real_wins"] += 1
                    rikishi_totals[r1]["all_wins"] += 1
                elif bout.outcome1 == Outcome.FS:
                    rikishi_totals[r1]["all_wins"] += 1

                if bout.outcome2 == Outcome.W:
                    rikishi_totals[r2]["real_wins"] += 1
                    rikishi_totals[r2]["all_wins"] += 1
                elif bout.outcome2 == Outcome.FS:
                    rikishi_totals[r2]["all_wins"] += 1

        for rid in sorted(banzuke.riks):
            rid_int = int(rid)
            totals = rikishi_totals.get(rid_int, {"real_wins": 0, "all_wins": 0, "bout_count": 0})

            rows.append(
                {
                    "date": date_to_str(basho_date),
                    "rikishi_id": rid_int,
                    "shikona": str(banzuke.get_shik(rid)),
                    "real_wins": totals["real_wins"],
                    "all_wins": totals["all_wins"],
                    "bout_count": totals["bout_count"],
                }
            )

    return rows


def write_totals_cache(
    rows: list[dict[str, int | str]],
    cache_file=CACHE_FILE,
) -> None:
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["date", "rikishi_id", "shikona", "real_wins", "all_wins", "bout_count"]

    with cache_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_totals_cache(cache_file=CACHE_FILE) -> list[dict[str, str]]:
    with cache_file.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_or_create_totals_cache(
    history: History,
    cache_file=CACHE_FILE,
) -> tuple[list[dict[str, str]], str]:
    if cache_file.exists():
        return load_totals_cache(cache_file), "loaded"

    rows = build_totals_cache_rows(history)
    write_totals_cache(rows, cache_file)
    return load_totals_cache(cache_file), "created"


def available_dates(history: History) -> list[str]:
    return [str(date) for date in sorted(history.keys())]


def resolve_date(
    history: History,
    direction: str,
    requested_date: str | None,
) -> str:
    dates = available_dates(history)

    if requested_date is not None:
        if requested_date not in dates:
            raise ValueError(f"Date '{requested_date}' not found in History.")
        return requested_date

    if direction == "BACKWARDS":
        return dates[-1]

    if direction == "FORWARDS":
        return dates[0]

    raise ValueError(f"Unsupported direction: {direction}")


def resolve_window_dates(
    history: History,
    date: str,
    direction: str,
    num_basho: int,
) -> list[str]:
    # TBD:
    # - validate num_basho > 0
    dates = available_dates(history)
    idx = dates.index(date)

    if direction == "BACKWARDS":
        start = max(0, idx - num_basho + 1)
        return dates[start : idx + 1]

    if direction == "FORWARDS":
        end = min(len(dates), idx + num_basho)
        return dates[idx:end]

    raise ValueError(f"Unsupported direction: {direction}")


def compute_standings(
    cache_rows: list[dict[str, str]],
    selected_dates: list[str],
    wins: str,
) -> list[dict]:
    selected = set(selected_dates)
    totals: dict[int, dict[str, int | str]] = {}

    for row in cache_rows:
        if row["date"] not in selected:
            continue

        rid = int(row["rikishi_id"])

        if rid not in totals:
            totals[rid] = {
                "rikishi_id": rid,
                "shikona": row["shikona"],
                "real_wins": 0,
                "all_wins": 0,
                "bout_count": 0,
            }

        totals[rid]["real_wins"] += int(row["real_wins"])
        totals[rid]["all_wins"] += int(row["all_wins"])
        totals[rid]["bout_count"] += int(row.get("bout_count", 0))

    if wins == "real":
        primary = "real_wins"
    elif wins == "all":
        primary = "all_wins"
    else:
        raise ValueError(f"Unsupported wins mode: {wins}")

    ordered = sorted(
        totals.values(),
        key=lambda r: (
            -int(r[primary]),
            -int(r["real_wins"]),
            -int(r["all_wins"]),
            int(r["rikishi_id"]),
        ),
    )

    ranked: list[dict] = []
    prev_value: int | None = None
    prev_position = 0

    for idx, row in enumerate(ordered, start=1):
        current_value = int(row[primary])

        if current_value == prev_value:
            position = prev_position
        else:
            position = idx
            prev_position = position
            prev_value = current_value

        ranked.append(
            {
                "position": position,
                "rikishi_id": row["rikishi_id"],
                "shikona": row["shikona"],
                "real_wins": row["real_wins"],
                "all_wins": row["all_wins"],
                "bout_count": row["bout_count"],
            }
        )

    return ranked
