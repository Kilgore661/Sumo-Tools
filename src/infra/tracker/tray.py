"""
Tracker tray integration.

This module reflects tracker run state in the system tray.

In the current draft implementation, tray updates are represented by simple
console output. The module interface is intentionally small so that a real
tray implementation can later replace the stub without affecting tracker
control flow.

This module defines:
    - set_tray_state(state): reflect the current tracker state
"""

from infra.tracker.types import RunState


def set_tray_state(state: RunState) -> None:
    """
    Reflect the current tracker state.

    Current implementation: console output only.
    """
    print(f"[tray] state -> {state.name}")
