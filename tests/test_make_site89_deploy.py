import json
from pathlib import Path

import pytest

from src.products.make_site89.__main__ import build_parser
from src.products.make_site89.deploy import (
    build_output_from_existing,
    deploy_targets,
    load_deployment_plan,
    select_deploy_targets,
)


def test_local_deployment_replaces_old_site_tree(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    server_root = tmp_path / "server" / "sumo-tools89"
    (output_root / "runtime").mkdir(parents=True)
    (output_root / "index.html").write_text("index", encoding="utf-8")
    (output_root / "runtime" / "site.js").write_text("runtime", encoding="utf-8")
    server_root.mkdir(parents=True)
    (server_root / "stale.txt").write_text("stale", encoding="utf-8")
    (server_root / "keep.swp").write_text("keep", encoding="utf-8")
    config_path = tmp_path / "targets.json"
    config_path.write_text(
        json.dumps(
            {
                "default_targets": ["local_apache"],
                "targets": {
                    "local_apache": {
                        "method": "win_copy",
                        "location": str(server_root),
                        "url": "http://server/sumo-tools89/",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    plan = load_deployment_plan(config_path)
    results = deploy_targets(
        build_output_from_existing(output_root),
        select_deploy_targets(plan, local_only=True),
    )

    assert len(results) == 1
    assert results[0].public_url == "http://server/sumo-tools89/"
    assert (server_root / "index.html").read_text(encoding="utf-8") == "index"
    assert (server_root / "runtime" / "site.js").read_text(encoding="utf-8") == "runtime"
    assert not (server_root / "stale.txt").exists()
    assert (server_root / "keep.swp").read_text(encoding="utf-8") == "keep"


def test_existing_build_requires_index(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="index.html"):
        build_output_from_existing(tmp_path)


def test_repository_target_is_separate_from_make_site2() -> None:
    plan = load_deployment_plan(Path("distro/make_site89_targets.json"))

    target = plan.targets["local_apache"]
    assert target.location == "A:/local/html/sumo-tools89"
    assert target.url == "http://192.168.0.146/sumo-tools89/"


def test_cli_accepts_make_site2_style_local_only_mode() -> None:
    args = build_parser().parse_args(["--local-only"])

    assert args.local_only
