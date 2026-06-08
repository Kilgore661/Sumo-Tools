"""Entry fixture for cross-module data-flow propagation."""

from __future__ import annotations

from pathlib import Path

from src.introspection.fixtures.data_flow_cross_module.builder import build


OUTPUT_DIR = Path("files/output/introspection/fixtures/cross_module")


def run() -> None:
    build(OUTPUT_DIR)
