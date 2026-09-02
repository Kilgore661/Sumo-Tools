"""Local-server deployment for make_site89 output."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from .models import BuildOutput


DEFAULT_DEPLOY_TARGETS_PATH = Path("distro/make_site89_targets.json")


@dataclass(frozen=True, kw_only=True)
class DeployTarget:
    name: str
    method: str
    location: str
    url: str = ""


@dataclass(frozen=True, kw_only=True)
class DeploymentPlan:
    default_targets: tuple[str, ...]
    targets: dict[str, DeployTarget]


@dataclass(frozen=True, kw_only=True)
class DeploymentResult:
    target_name: str
    method: str
    source_root: Path
    target_root: Path
    public_url: str
    file_count: int


def build_output_from_existing(output_root: Path) -> BuildOutput:
    entrypoint = output_root / "index.html"
    if not entrypoint.is_file():
        raise FileNotFoundError(f"Build output entrypoint not found: {entrypoint}")
    return BuildOutput(
        root=output_root,
        entrypoint=entrypoint,
        file_count=sum(1 for path in output_root.rglob("*") if path.is_file()),
    )


def load_deployment_plan(
    path: Path = DEFAULT_DEPLOY_TARGETS_PATH,
) -> DeploymentPlan:
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw_targets = raw.get("targets")
    if not isinstance(raw_targets, dict):
        raise ValueError(f"{path} must contain a 'targets' object")
    targets: dict[str, DeployTarget] = {}
    for name, config in raw_targets.items():
        if not isinstance(config, dict):
            raise ValueError(f"{path} target {name!r} must be an object")
        method = config.get("method")
        if method != "win_copy":
            raise ValueError(
                f"{path} target {name!r} must use the win_copy method"
            )
        location = config.get("location")
        if not location:
            raise ValueError(f"{path} target {name!r} needs a location")
        targets[name] = DeployTarget(
            name=name,
            method=method,
            location=str(location),
            url=str(config.get("url") or ""),
        )
    default_targets = tuple(raw.get("default_targets") or targets.keys())
    unknown = [name for name in default_targets if name not in targets]
    if unknown:
        raise ValueError(f"unknown default deploy target(s): {', '.join(unknown)}")
    return DeploymentPlan(default_targets=default_targets, targets=targets)


def select_deploy_targets(
    plan: DeploymentPlan,
    *,
    local_only: bool = False,
) -> tuple[DeployTarget, ...]:
    targets = tuple(plan.targets[name] for name in plan.default_targets)
    if local_only:
        targets = tuple(target for target in targets if target.method == "win_copy")
    if not targets:
        raise ValueError("no deploy targets selected")
    return targets


def deploy_targets(
    build_output: BuildOutput,
    targets: tuple[DeployTarget, ...],
) -> tuple[DeploymentResult, ...]:
    return tuple(
        deploy_win_copy(build_output, target)
        for target in targets
    )


def deploy_win_copy(
    build_output: BuildOutput,
    deploy_target: DeployTarget,
) -> DeploymentResult:
    local_root = Path(deploy_target.location)
    _clear_local_root(local_root)
    for source in build_output.root.rglob("*"):
        if source.is_file():
            target = local_root / source.relative_to(build_output.root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return DeploymentResult(
        target_name=deploy_target.name,
        method=deploy_target.method,
        source_root=build_output.root,
        target_root=local_root,
        public_url=deploy_target.url,
        file_count=build_output.file_count,
    )


def _clear_local_root(local_root: Path) -> None:
    local_root.mkdir(parents=True, exist_ok=True)
    for item in local_root.iterdir():
        if item.name.endswith(".swp"):
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
