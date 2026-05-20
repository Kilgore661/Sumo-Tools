import pytest

from src.products.make_site2.__main__ import (
    build_parser,
    resolve_basho_results_payload_mode,
)


def payload_mode_for(*args: str) -> str:
    return resolve_basho_results_payload_mode(build_parser().parse_args(args))


def test_make_site2_builds_all_basho_payloads_by_default() -> None:
    assert payload_mode_for() == "all"


def test_make_site2_one_basho_limits_payloads_to_latest() -> None:
    assert payload_mode_for("--one-basho") == "latest"


def test_make_site2_no_basho_disables_payloads() -> None:
    assert payload_mode_for("--no-basho") == "none"


def test_make_site2_rejects_conflicting_basho_payload_flags() -> None:
    with pytest.raises(SystemExit):
        payload_mode_for("--no-basho", "--one-basho")
