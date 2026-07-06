from __future__ import annotations

import sys
import time


class ProgressTimer:
    def __init__(self, total: int, *, report_every: int) -> None:
        self.total = total
        self.report_every = report_every
        self.start_time = time.perf_counter()

    def report(self, completed: int) -> None:
        if self.report_every <= 0:
            return
        if completed != 1 and completed % self.report_every != 0 and completed != self.total:
            return

        elapsed = time.perf_counter() - self.start_time
        rate = completed / elapsed if elapsed > 0 else 0.0
        remaining = (self.total - completed) / rate if rate > 0 else 0.0
        print(
            f"runs {completed}/{self.total} "
            f"elapsed {format_duration(elapsed)} "
            f"eta {format_duration(remaining)} "
            f"({rate:.2f} runs/s)",
            file=sys.stderr,
        )


def format_duration(seconds: float) -> str:
    total_seconds = max(0, int(round(seconds)))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{seconds:02d}s"
    if minutes:
        return f"{minutes}m{seconds:02d}s"
    return f"{seconds}s"
