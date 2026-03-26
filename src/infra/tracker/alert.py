"""
Tracker fatal alerting.

This module provides the tracker-side alert used when a fatal condition is
encountered and the tracker is about to terminate.

In the current implementation, alerting means:
- print a message to the console
- emit a Windows beep

This module defines:
    - alert_fatal(message): emit a fatal alert
"""

import winsound


def alert_fatal(message: str) -> None:
    """
    Emit a fatal tracker alert.

    The alert is intended for hard failures such as parser failure on valid
    input, failure to publish a canonical zip, or window-close with unresolved
    recovery work.
    """
    print(f"[alert] FATAL: {message}")
    winsound.Beep(1000, 500)
