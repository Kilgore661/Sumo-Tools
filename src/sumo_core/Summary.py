from typing import Union, Literal
from dataclasses import dataclass
from .BasicPrimitives import Day, Torikumi, Pair, RikId, Pair
from .BasicEnums import Outcome, Symbol
from .Kimarite import Kimarite

################################################################################

class Decision:

    """
    Decision value object for sumo history.

    Represents how a bout result was decided.

    A Decision is one of:
    - a Kimarite (normal bout resolution), or
    - the string "fusen" (win by default), or
    - the string "blank" (no result recorded)

    This is implemented as a constrained value constructor rather than an enum,
    because the domain is a union of an enum (Kimarite) and special string values.
    """

    def __new__(cls, value: Union[Kimarite, Literal["fusen", "blank"]]):
        if not (isinstance(value, Kimarite) or value in ("fusen", "blank")):
            raise TypeError(f"Decision must be Kimarite or special outcome, got {type(value)}")
        return value

################################################################################

@dataclass
class BoutResult:
    """
    BoutResult value object for sumo history.

    Represents the recorded result of a single bout.

    A BoutResult contains:
    - the two participating rikishi
    - the outcome recorded for each
    - the decision mechanism
    - the display symbol

    The two rikishi must be distinct, and the two outcomes must form one of the
    established valid combinations.
    """


    rikishi1: RikId
    outcome1: Outcome
    rikishi2: RikId
    outcome2: Outcome
    decision: Decision
    symbol: Symbol

    def __post_init__(self):
        """
        Validate the structure of the bout result.

        The two rikishi must be distinct, and the two recorded outcomes
        must be mutually consistent.
        """
        _ = Pair(self.rikishi1, self.rikishi2)
        self._validate_outcome_consistency()

    def _validate_outcome_consistency(self):
        """
        Ensure that the pair of outcomes is one of the established valid forms.

        Valid combinations are:
        - {W, L}
        - {FS, FP}
        - {DRAW, DRAW}
        """
        outcome_pair = {self.outcome1, self.outcome2}

        valid_pairs = [
            {Outcome.W, Outcome.L},
            {Outcome.FS, Outcome.FP},
            {Outcome.DRAW, Outcome.DRAW},
        ]

        if outcome_pair not in valid_pairs:
            raise ValueError(
                f"Invalid outcome combination: {self.outcome1}, {self.outcome2}"
            )
################################################################################

class ResultLookup(dict):
    """
    ResultLookup mapping for sumo history.

    Represents a partial function:

        Pair -> BoutResult

    Implemented as a dictionary with function-call syntax.
    """

    DEMOTION = "↓"

    def __call__(self, pair: Pair):
        """
        Return the BoutResult for the given Pair, or None if undefined.
        """
        return self.get(pair)
################################################################################
@dataclass
class DailyResults:
    """
    DailyResults aggregate for sumo history.

    Represents the results recorded for a single day of a basho.

    A DailyResults consists of:
    - torikumi       : the set of scheduled bouts
    - results_lookup : a partial function from Pair to BoutResult

    This class intentionally performs no internal validation.
    In the established model, the relevant consistency constraints are enforced
    at higher aggregate level, not here.
    """


    torikumi: Torikumi
    results_lookup: ResultLookup
################################################################################

class Summary(dict):
    """
    Summary aggregate for sumo history.

    Represents the recorded summary of a basho.

    A Summary consists of:
    - a partial function from Day to DailyResults
    - a partial function from RikId to Performance

    The established structural invariant is that, if any days are recorded,
    they must begin at day 1 and be contiguous with no gaps.
    """

    def __init__(self, daily_results_dict, performances=None):
        super().__init__(daily_results_dict)
        self.performances = performances if performances is not None else Performances()

        days = sorted(self.keys())
        if days and days[0] != 1:
            raise ValueError(
                f"Tournament must start with day 1, found: {days[0]}"
            )

        for i in range(1, len(days)):
            if days[i] != days[i - 1] + 1:
                raise ValueError(
                    f"Gap in daily records between days {days[i - 1]} and {days[i]}"
                )

    def __call__(self, day: Day):
        """
        Return the DailyResults for the given day, or None if undefined.
        """
        return self.get(day)

    def last_defined(self):
        """
        Return the last day with defined results, or None if the summary is empty.
        """
        return Day(max(self.keys())) if self else None
