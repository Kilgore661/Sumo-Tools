import pytest

from src.products.make_site2.__main__ import (
    build_parser,
    reject_conflicting_modes,
    resolve_cache_mode,
    resolve_basho_results_payload_mode,
)


def payload_mode_for(*args: str) -> str:
    return resolve_basho_results_payload_mode(build_parser().parse_args(args))


def cache_mode_for(*args: str) -> str:
    return resolve_cache_mode(build_parser().parse_args(args))


def test_make_site2_builds_all_basho_payloads_by_default() -> None:
    assert payload_mode_for() == "all"


def test_make_site2_one_basho_limits_payloads_to_latest() -> None:
    assert payload_mode_for("--one-basho") == "latest"


def test_make_site2_no_basho_disables_payloads() -> None:
    assert payload_mode_for("--no-basho") == "none"


def test_make_site2_rejects_conflicting_basho_payload_flags() -> None:
    with pytest.raises(SystemExit):
        payload_mode_for("--no-basho", "--one-basho")


def test_make_site2_uses_development_cache_busting_by_default() -> None:
    assert cache_mode_for() == "dev"


def test_make_site2_prod_disables_development_cache_busting() -> None:
    assert cache_mode_for("--prod") == "prod"


def test_make_site2_accepts_no_build_local_only_deployment() -> None:
    args = build_parser().parse_args(["--no-build", "--local-only"])

    reject_conflicting_modes(args)
    assert args.no_build
    assert args.local_only


def test_make_site2_rejects_no_build_build_only() -> None:
    with pytest.raises(SystemExit):
        reject_conflicting_modes(build_parser().parse_args(["--no-build", "--build-only"]))


def test_make_site2_rejects_build_options_with_no_build() -> None:
    with pytest.raises(SystemExit):
        reject_conflicting_modes(build_parser().parse_args(["--no-build", "--prod"]))
