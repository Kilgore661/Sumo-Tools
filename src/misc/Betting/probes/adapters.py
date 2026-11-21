"""Adapt the existing source scrapers to the place runner."""

from __future__ import annotations

import hashlib
import json
from argparse import Namespace
from datetime import date, datetime
from pathlib import Path
from typing import Callable

from .connection import Place
from .runner import AcquisitionResult


def _target_file_state(output_dir: Path, target: date) -> dict[Path, str]:
    state: dict[Path, str] = {}
    for path in output_dir.glob(f"{target.isoformat()}_*.json"):
        try:
            state[path] = hashlib.sha256(path.read_bytes()).hexdigest()
        except FileNotFoundError:
            continue
    return state


def _changed_target_files(
    output_dir: Path, target: date, before: dict[Path, str]
) -> list[Path]:
    paths: list[Path] = []
    for path in output_dir.glob(f"{target.isoformat()}_*.json"):
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if before.get(path) != digest:
                paths.append(path)
        except FileNotFoundError:
            continue
    return sorted(paths)


def _add_provenance(
    paths: list[Path], *, run_id: str, place: Place, exit_ip: str, target: date
) -> None:
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["acquisition"] = {
            "run_id": run_id,
            "target_date": target.isoformat(),
            "place": place.name,
            "location_id": place.location_id,
            "exit_ip": exit_ip,
            "recorded_at": datetime.now().astimezone().isoformat(),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _validate_snapshot(path: Path, target: date) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"Could not read valid JSON from {path.name}: {exc}"
    events = payload.get("events")
    if not isinstance(events, list) or not events:
        return f"{path.name} contains no events"
    for event in events:
        if not isinstance(event, dict):
            return f"{path.name} contains a malformed event"
        try:
            event_date = datetime.fromisoformat(str(event["start"])).date()
        except (KeyError, TypeError, ValueError):
            return f"{path.name} contains an event without a valid start"
        if event_date != target:
            return f"{path.name} contains an event for {event_date}, not {target}"
        competitors = (event.get("competitor_1"), event.get("competitor_2"))
        if not all(isinstance(value, str) and value.strip() for value in competitors):
            return f"{path.name} contains an event without two competitors"
        odds = event.get("odds")
        if not isinstance(odds, list) or len(odds) != 2:
            return f"{path.name} contains an event without two prices"
        outcomes: set[str] = set()
        for odd in odds:
            try:
                outcome = str(odd["outcome"]).strip()
                price = float(odd["price"])
            except (KeyError, TypeError, ValueError):
                return f"{path.name} contains an invalid outcome or price"
            if not outcome or price <= 1:
                return f"{path.name} contains an invalid outcome or price"
            outcomes.add(outcome)
        if len(outcomes) != 2:
            return f"{path.name} contains duplicate outcomes"
    return None


def existing_scraper_adapter(
    download_once: Callable[[Namespace, object], bool],
    namespace: Namespace,
    timezone: object,
    target: date,
) -> Callable[[Place, str, str], AcquisitionResult]:
    def acquire(place: Place, exit_ip: str, run_id: str) -> AcquisitionResult:
        before = _target_file_state(namespace.output_dir, target)
        try:
            wrote_anything = download_once(namespace, timezone)
        except Exception as exc:  # source libraries expose several runtime errors
            detail = str(exc).splitlines()[0]
            if "451" in detail:
                return AcquisitionResult("http_451", detail)
            if "403" in detail:
                return AcquisitionResult("http_rejected", detail)
            if "did not show any bouts with prices" in detail:
                return AcquisitionResult("odds_absent", detail)
            return AcquisitionResult("browser_failed", detail)
        files = _changed_target_files(namespace.output_dir, target, before)
        if files:
            validation_errors = [
                error for path in files if (error := _validate_snapshot(path, target))
            ]
            if validation_errors:
                return AcquisitionResult("validation_failed", "; ".join(validation_errors))
            _add_provenance(
                files, run_id=run_id, place=place, exit_ip=exit_ip, target=target
            )
            return AcquisitionResult(
                "success", files=tuple(str(path.resolve()) for path in files)
            )
        if wrote_anything:
            return AcquisitionResult(
                "target_date_mismatch",
                f"The scraper wrote odds, but none were for {target.isoformat()}",
            )
        return AcquisitionResult("odds_absent", "No priced target-day bouts were written")

    return acquire
