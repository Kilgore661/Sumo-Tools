"""Append-only records for site-specific acquisition attempts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class AttemptStore:
    def __init__(self, directory: Path, source: str, run_id: str) -> None:
        self.directory = directory
        self.source = source
        self.run_id = run_id
        self.directory.mkdir(parents=True, exist_ok=True)
        self.attempts_path = directory / f"{source}_attempts.jsonl"

    def write_manifest(self, payload: dict[str, Any]) -> Path:
        path = self.directory / f"{self.run_id}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def append(self, payload: dict[str, Any]) -> None:
        row = {"run_id": self.run_id, "source": self.source, **payload}
        with self.attempts_path.open("a", encoding="utf-8", newline="") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def excluded_place_keys(self) -> set[str]:
        """Return places previously refused with HTTP 451 for this source."""

        if not self.attempts_path.exists():
            return set()
        excluded: set[str] = set()
        for line in self.attempts_path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            place = row.get("place") or {}
            if row.get("source") == self.source and row.get("outcome") == "http_451":
                key = place.get("key")
                if key:
                    excluded.add(str(key))
        return excluded
