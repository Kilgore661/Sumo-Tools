from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def make_run_dir(root: Path, *, seed: int, timestamp: datetime | None = None) -> Path:
    timestamp = timestamp or datetime.now().astimezone()
    stamp = timestamp.strftime("%Y%m%d_%H%M%S")
    run_dir = root / f"{stamp}_seed{seed}"
    suffix = 1
    while run_dir.exists():
        suffix += 1
        run_dir = root / f"{stamp}_seed{seed}_{suffix}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")
