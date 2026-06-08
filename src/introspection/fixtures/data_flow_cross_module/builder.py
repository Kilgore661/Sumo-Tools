"""Builder fixture for cross-module data-flow propagation."""

from __future__ import annotations

from pathlib import Path

from src.introspection.fixtures.data_flow_cross_module.writer import write_index


def build(output_dir: Path) -> None:
    route_data_dir = output_dir / "route" / "data"
    write_index(route_data_dir)
