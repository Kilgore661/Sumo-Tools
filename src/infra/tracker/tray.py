"""
Tracker tray integration.

This module reflects tracker run state in the system tray.

In the current draft implementation, tray updates are represented by simple
console output. The module interface is intentionally small so that a real
tray implementation can later replace the stub without affecting tracker
control flow.

This module defines:
    - set_tray_state(state, now): reflect the current tracker state
"""

from datetime import datetime
from .types import RunState


def set_tray_state(state: RunState, now: datetime) -> None:
    """
    Reflect the current tracker state.

    Current implementation: console output only.
    """
    timestamp = now.strftime("%Y/%m/%d %H:%M")
    print(f"[tray] {timestamp} state -> {state.name}")
