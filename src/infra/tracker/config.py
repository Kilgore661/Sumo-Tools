from dataclasses import dataclass


@dataclass(frozen=True)
class TrackerConfig:
    """
    Configuration for the tracker.

    All values are treated as part of the system contract, not something
    to be dynamically mutated at runtime.
    """

    # Number of days before basho start when tracking becomes active
    pre_basho_days: int = 14

    # Number of days in a basho
    basho_length_days: int = 15

    # Hour of day (local time) when a run may occur
    # e.g. 10 means 10:00
    trigger_hour: int = 10

    # Main loop polling interval in seconds
    poll_interval_seconds: float = 60.0
