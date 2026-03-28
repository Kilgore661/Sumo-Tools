from datetime import datetime, timedelta
import time

class RealClock:
    """
    Real wall-clock time source.
    """

    def now(self) -> datetime:
        return datetime.now()


class ScaledClock:
    """
    Simulated clock.

    Time starts at `simulated_start` and then advances according to
    `real_seconds_per_simulated_day`.

    Example:
        real_seconds_per_simulated_day = 20.0
    means one simulated day passes in twenty real seconds.
    """

    def __init__(
        self,
        simulated_start: datetime,
        real_seconds_per_simulated_day: float,
    ) -> None:
        if real_seconds_per_simulated_day <= 0.0:
            raise ValueError(
                "real_seconds_per_simulated_day must be > 0"
            )

        self._simulated_start = simulated_start
        self._real_start = time.monotonic()
        self._real_seconds_per_simulated_day = real_seconds_per_simulated_day

    def now(self) -> datetime:
        real_elapsed_seconds = time.monotonic() - self._real_start
        simulated_days = real_elapsed_seconds / self._real_seconds_per_simulated_day
        return self._simulated_start + timedelta(days=simulated_days)
