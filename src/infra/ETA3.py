# File: eta_modified.py
import time
import math
from datetime import datetime, timedelta
from typing import Optional
from collections import deque
import sys

class EtaModule:
    # Single process tracking
    _items_done = 0
    _total_items = 0
    _start_time = 0.0  # Use float for consistency
    _eta_history = None
    _last_tick_time = 0.0 # Added: Store time of the last tick
    _last_tick_duration = 0.0 # Added: Store duration of the last tick

    def __init__(self, total_items: int, history_size: int = 10) -> None:
        """
        Initialize tracking for the process.

        Args:
            total_items: Total number of items to process
            history_size: Number of recent ETAs to track for trend calculation
        """
        self._items_done = 0
        self._total_items = total_items
        self._start_time = time.time()
        self._last_tick_time = self._start_time # Initialize last tick time
        self._last_tick_duration = 0.0 # Initialize duration
        self._eta_history = deque(maxlen=history_size)

    def tick(self) -> str:
        """
        Update progress, calculate tick duration, and return estimated time of completion.

        Returns:
            Formatted string with estimated completion time
        """
        current_time = time.time()

        # Calculate duration of this tick BEFORE updating count/time
        if self._items_done > 0: # Avoid calculating duration for the very first 'tick' start
             self._last_tick_duration = current_time - self._last_tick_time
        else:
             # For the first item, duration is time since init
             self._last_tick_duration = current_time - self._start_time

        # Update process count and time *after* duration calculation
        self._items_done += 1
        self._last_tick_time = current_time # Store current time for the next tick's calculation

        # --- Rest of ETA calculation ---
        if self._items_done == self._total_items:
            # Reset duration on completion? Optional.
            # self._last_tick_duration = current_time - self._last_tick_time
            return "Complete"

        elapsed = current_time - self._start_time # Use current_time for consistency
        if self._items_done == 0: # Should not happen after increment, but good practice
            return "Calculating..."

        items_per_second = self._items_done / elapsed
        remaining_items = self._total_items - self._items_done

        if items_per_second > 0:
            seconds_left = remaining_items / items_per_second
            # Store seconds_left in the history for trend calculation
            self._eta_history.append(seconds_left)
            eta_timestamp = datetime.now() + timedelta(seconds=seconds_left)
            return eta_timestamp.strftime("%H:%M:%S")
        else:
            return "Unknown"

    # --- ADDED METHOD ---
    def display_status(self, eta_time: str) -> None:
        """
        Prints a formatted status line to the console.

        This method encapsulates the complicated print statement, creating a
        single, updating line of progress information. It should be called
        immediately after tick().

        Args:
            eta_time: The ETA string returned by the tick() method.
        """
        percent = self.percent_complete()
        trend = self.eta_trend_str()
        last_duration = self.get_last_tick_duration()

        # Build the output string
        status_line = (f"Processed item {self._items_done}/{self._total_items} ({percent:4.1f}% done). "
                       f"ETA: {eta_time} ({trend}). "
                       f"Last item took: {last_duration:7.3f}s")

        # Write to stdout, using \r to return to the start of the line.
        # Add padding to ensure the previous line is fully overwritten.
        sys.stdout.write(f"{status_line}{' ' * 10}\r")
        sys.stdout.flush()
    # --- END ADDED METHOD ---


    def get_last_tick_duration(self) -> float:
        """
        Get the time taken for the most recently completed tick in seconds.

        Returns:
            Duration of the last tick in seconds.
        """
        return self._last_tick_duration

    def hhmmss(self) -> str:
        """
        Get total time taken for completion in HH:MM:SS format.

        Returns:
            Formatted string with total time taken
        """
        # Use the last tick time if complete, otherwise current time
        end_time = self._last_tick_time if self._items_done == self._total_items else time.time()
        elapsed = end_time - self._start_time

        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def percent_complete(self) -> float:
        """
        Calculate percentage of items completed.

        Returns:
            Percentage complete (0-100)
        """
        if self._total_items == 0:
            return 100.0

        return (self._items_done / self._total_items) * 100

    def eta_trend(self, n: int = 10) -> Optional[float]:
        """
        Calculate the change in ETA over the last n ticks.
        Positive value means the process is slowing down (ETA increasing).
        Negative value means the process is speeding up (ETA decreasing).

        Args:
            n: Number of ticks to look back (defaults to all available)

        Returns:
            Change in seconds per tick, or None if insufficient data
        """
        if len(self._eta_history) < 2:
            return None

        # Use available history but limit to n entries
        available = min(n, len(self._eta_history))

        # Make sure we have at least 2 entries to calculate a trend
        if available < 2:
            return None

        # Calculate change in ETA using first and last available entries
        # within the window of size 'available'
        older_eta = self._eta_history[-available]
        current_eta = self._eta_history[-1]

        # Average change per tick over the specified window
        return (current_eta - older_eta) / (available - 1)

    def eta_trend_str(self) -> str:
        """
        Get a human-readable description of the ETA trend.

        Returns:
            String describing the trend
        """
        trend = self.eta_trend()

        if trend is None:
            return "Calculating..."

        # Use a small threshold to determine 'stable'
        if abs(trend) < 0.01: # Adjust threshold as needed
            return "=" # Stable
        elif trend > 0:
            return f"↓ {trend:4.2f}s/item" # Slowing down (ETA getting later)
        else:
            # Trend is negative, meaning ETA is getting earlier (speeding up)
            return f"↑ {-trend:4.2f}s/item" # Speeding up (ETA getting earlier)

# --- UPDATED EXAMPLE ---
if __name__ == '__main__':
    # --- Example Usage ---
    total_work = 50
    eta = EtaModule( total_work )

    print("Starting processing...")
    for i in range(total_work):
        # Simulate work with varying duration
        sleep_time = 0.1 + (math.sin(i / 5.0) * 0.08) # Make it vary a bit
        time.sleep(sleep_time)

        # Update progress and get ETA string
        eta_time = eta.tick()

        # Use the new method to display the status line
        eta.display_status(eta_time)

    print("\nProcessing complete!")
    print(f"Total time taken: {eta.hhmmss()}")
