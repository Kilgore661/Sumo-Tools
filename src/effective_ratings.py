import argparse
import math
from dataclasses import dataclass

from src.infra.connect import connect
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import Day, Month, Year
from src.sumo_core.History import Date
from .classes import Ratings

from .helpers import load_ratings


LOG10_OVER_400 = math.log(10.0) / 400.0
DEFAULT_SIGMA = 75.0


@dataclass(frozen=True)
class BoutReplay:
    day: int
    opponent_id: int
    opponent_shikona: str
    opponent_rating: float
    outcome: float
    er_after_bout: float


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare stored rating vs sequential explanatory rating (ER)."
    )
    parser.add_argument("--rik", required=True, help="Shikona in the supplied basho.")
    parser.add_argument(
        "--basho",
        required=True,
        help="Basho in YYYY/MM format, e.g. 2023/07",
    )
    parser.add_argument(
        "--days",
        required=True,
        help="Inclusive day range A-B, anchored at the start of day A.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1958,
        help="History load start year.",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="History load end year. Defaults to the basho year.",
    )
    parser.add_argument("--zip", action="store_true", help="Use zipped history store.")
    parser.add_argument(
        "--sigma",
        type=float,
        default=DEFAULT_SIGMA,
        help="Per-bout volatility parameter for ER replay.",
    )
    return parser.parse_args()


def parse_basho(text: str) -> Date:
    try:
        year_text, month_text = text.split("/")
        return Date(Year(int(year_text)), Month(int(month_text)))
    except Exception as e:
        raise ValueError(f"Invalid --basho value {text!r}; expected YYYY/MM") from e


def parse_day_range(text: str) -> tuple[int, int]:
    try:
        start_text, end_text = text.split("-")
        start_day = int(start_text)
        end_day = int(end_text)
        Day(start_day)
        Day(end_day)
    except Exception as e:
        raise ValueError(f"Invalid --days value {text!r}; expected A-B within 1..15") from e

    if start_day > end_day:
        raise ValueError(f"Invalid --days value {text!r}; start day exceeds end day")

    return start_day, end_day


def win_probability(player_rating: float, opponent_rating: float) -> float:
    exponent = (opponent_rating - player_rating) / 400.0
    return 1.0 / (1.0 + 10.0 ** exponent)


def update_one_bout(current_rating: float, opponent_rating: float, outcome: float, sigma: float) -> float:
    """
    Solve the 1D MAP update from the proposal by bisection on the first derivative.
    """
    if sigma <= 0:
        raise ValueError(f"sigma must be positive, got {sigma}")

    def grad(x: float) -> float:
        p = win_probability(x, opponent_rating)
        return LOG10_OVER_400 * (outcome - p) - (x - current_rating) / (sigma * sigma)

    lo = current_rating - 6.0 * sigma
    hi = current_rating + 6.0 * sigma

    g_lo = grad(lo)
    g_hi = grad(hi)

    if g_lo < 0.0:
        return lo
    if g_hi > 0.0:
        return hi

    for _ in range(80):
        mid = 0.5 * (lo + hi)
        g_mid = grad(mid)
        if g_mid > 0.0:
            lo = mid
        else:
            hi = mid

    return 0.5 * (lo + hi)


def resolve_rikid(basho_state, shikona_text: str):
    target = shikona_text.strip().lower()
    for rid, shik in basho_state.banzuke.rikshik.items():
        if str(shik).strip().lower() == target:
            return rid
    raise KeyError(f"No rikishi named {shikona_text!r} found in the supplied basho")


def find_bout_for_rikishi(daily_results, rikid):
    for pair in daily_results.torikumi:
        if rikid in pair:
            result = daily_results.results_lookup(pair)
            if result is None:
                raise RuntimeError(f"No BoutResult recorded for pair {pair}")
            return pair, result
    return None, None


def outcome_for_rikishi(result, rikid) -> float:
    if result.rikishi1 == rikid:
        outcome = result.outcome1
    elif result.rikishi2 == rikid:
        outcome = result.outcome2
    else:
        raise ValueError(f"RikId {rikid} is not in BoutResult {result}")

    if outcome in (Outcome.W, Outcome.FS):
        return 1.0
    if outcome in (Outcome.L, Outcome.FP):
        return 0.0
    if outcome == Outcome.DRAW:
        return 0.5

    raise ValueError(f"Unsupported outcome: {outcome}")


def opponent_id_for_pair(pair, rikid):
    a, b = pair
    if a == rikid:
        return b
    if b == rikid:
        return a
    raise ValueError(f"RikId {rikid} is not in pair {pair}")


def stored_rating_at_start_of_day(ratings, basho_date, day: int, rikid) -> float:
    if day == 1:
        return ratings.basho_start[basho_date][rikid]
    return ratings.day_end[basho_date][Day(day - 1)][rikid]


def stored_rating_at_end_of_day(ratings, basho_date, day: int, rikid) -> float:
    return ratings.day_end[basho_date][Day(day)][rikid]


def replay_er(history, ratings, basho_date, rikid, start_day: int, end_day: int, sigma: float):
    basho_state = history[basho_date]
    summary = basho_state.summary

    current_er = stored_rating_at_start_of_day(ratings, basho_date, start_day, rikid)
    replays: list[BoutReplay] = []

    for day in range(start_day, end_day + 1):
        daily_results = summary(Day(day))
        if daily_results is None:
            continue

        pair, result = find_bout_for_rikishi(daily_results, rikid)
        if pair is None:
            continue

        opp_id = opponent_id_for_pair(pair, rikid)
        opp_rating = stored_rating_at_start_of_day(ratings, basho_date, day, opp_id)
        outcome = outcome_for_rikishi(result, rikid)

        current_er = update_one_bout(current_er, opp_rating, outcome, sigma)

        replays.append(
            BoutReplay(
                day=day,
                opponent_id=int(opp_id),
                opponent_shikona=str(basho_state.banzuke.get_shik(opp_id)),
                opponent_rating=opp_rating,
                outcome=outcome,
                er_after_bout=current_er,
            )
        )

    return current_er, replays


def format_outcome(outcome: float) -> str:
    if outcome == 1.0:
        return "W"
    if outcome == 0.0:
        return "L"
    return "D"


def main():
    args = parse_args()

    basho_date = parse_basho(args.basho)
    start_day, end_day = parse_day_range(args.days)

    history_end = args.end if args.end is not None else int(basho_date.year)

    history = connect(args.start, history_end, use_zip=args.zip)
    ratings = load_ratings()

    if basho_date not in history:
        available = ", ".join(str(d) for d in sorted(history.keys()))
        raise KeyError(f"Basho {basho_date} not found in History. Available basho: {available}")

    basho_state = history[basho_date]
    rikid = resolve_rikid(basho_state, args.rik)

    start_rating = stored_rating_at_start_of_day(ratings, basho_date, start_day, rikid)
    end_rating = stored_rating_at_end_of_day(ratings, basho_date, end_day, rikid)
    end_er, replays = replay_er(
        history=history,
        ratings=ratings,
        basho_date=basho_date,
        rikid=rikid,
        start_day=start_day,
        end_day=end_day,
        sigma=args.sigma,
    )

    chii = basho_state.banzuke.get_chii(rikid)
    shikona = basho_state.banzuke.get_shik(rikid)

    print(f"{shikona} [{rikid}] — {basho_date} — days {start_day}-{end_day}")
    print(f"Rank: {chii}")
    print(f"Stored rating at start of day {start_day}: {start_rating:.3f}")
    print(f"Stored rating at end of day {end_day}:   {end_rating:.3f}")
    print(f"ER at end of day {end_day}:              {end_er:.3f}")
    print(f"Stored delta over window:                {end_rating - start_rating:+.3f}")
    print(f"ER delta over window:                    {end_er - start_rating:+.3f}")

    if replays:
        print()
        print("Replay path:")
        print(f"  start day {start_day}: {start_rating:.3f}")
        for replay in replays:
            print(
                f"  end day {replay.day}: {replay.er_after_bout:.3f}  "
                f"vs {replay.opponent_shikona} [{replay.opponent_id}]  "
                f"opp={replay.opponent_rating:.3f}  result={format_outcome(replay.outcome)}"
            )
    else:
        print()
        print("No bouts found for the rikishi in the requested interval.")


if __name__ == "__main__":
    main()

