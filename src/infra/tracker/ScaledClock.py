from datetime import datetime, timedelta
import time


class ScaledClock:
    def __init__(
        self,
        simulated_start: datetime,
        simulated_seconds_per_real_second: float,
    ) -> None:
        self._simulated_start = simulated_start
        self._real_start = time.monotonic()
        self._scale = simulated_seconds_per_real_second

    def now(self) -> datetime:
        real_elapsed = time.monotonic() - self._real_start
        simulated_elapsed = timedelta(seconds=real_elapsed * self._scale)
        return self._simulated_start + simulated_elapsed
