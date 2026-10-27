"""Build a provenance-bound P1-WL website inside the Kimarite work package."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from time import perf_counter

from src.products.make_site89.build import build_site
from src.products.make_site89.bundle import load_site_data_bundle


EXPECTED_PRIOR_SHA256 = (
    "6f5a3bc59dcdbd279e150f53ef0848ae658f2ee72b1371174976c6387cb70486"
)
EXPECTED_HISTORY_START = "1989/01"
EXPECTED_HISTORY_END = "2026/09"
DEFAULT_CANDIDATE_BUNDLE = Path(
    "src/validation/elo89-expert-account/Matters Arising/Kimarite/"
    "P1-WL Site Bundle Comparison/output/"
    "site-bundle-comparison-2026-10-27-run3/candidate"
)
DEFAULT_OUTPUT_PARENT = Path(
    "src/validation/elo89-expert-account/Matters Arising/Kimarite/"
    "P1-WL Website Build/output"
)
PREVIEW_PORT = 8766


def build_p1_wl_website(
    *,
    data_bundle: Path,
    output_root: Path,
    cache_mode: str = "dev",
    expected_prior_sha256: str = EXPECTED_PRIOR_SHA256,
    expected_history_start: str = EXPECTED_HISTORY_START,
    expected_history_end: str = EXPECTED_HISTORY_END,
) -> Path:
    """Build one retained site without invoking make_site89 deployment."""

    started = perf_counter()
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite website run: {output_root}")
    if cache_mode not in {"dev", "prod"}:
        raise ValueError(f"Unsupported cache mode: {cache_mode!r}")

    bundle_root = data_bundle.resolve()
    bundle = load_site_data_bundle(bundle_root)
    if bundle.history_start != expected_history_start:
        raise ValueError(
            "P1-WL website History start differs: "
            f"expected {expected_history_start}, received {bundle.history_start}"
        )
    if bundle.history_end != expected_history_end:
        raise ValueError(
            "P1-WL website History end differs: "
            f"expected {expected_history_end}, received {bundle.history_end}"
        )

    bundle_manifest_path = bundle_root / "manifest.json"
    rating_manifest_path = _rating_manifest_path(bundle_root, bundle.manifest)
    rating_manifest = _load_json_object(rating_manifest_path)
    prior = rating_manifest.get("prior")
    if not isinstance(prior, dict):
        raise ValueError("Elo-89 rating-run manifest has no prior object")
    recorded_prior_sha256 = prior.get("source_sha256")
    if recorded_prior_sha256 != expected_prior_sha256:
        raise ValueError(
            "Candidate bundle does not use the accepted P1-WL prior: "
            f"expected {expected_prior_sha256}, received {recorded_prior_sha256!r}"
        )
    copied_prior_path = rating_manifest_path.parent / _required_string(
        prior, "copied_to"
    )
    copied_prior_identity = _file_identity(copied_prior_path)
    copied_prior_pair_count = _validate_copied_prior(
        copied_prior_path, prior.get("pair_count")
    )

    output_root.mkdir(parents=True)
    site_root = output_root / "site"
    manifest = {
        "schema_version": 1,
        "experiment": "Kimarite P1-WL website build",
        "status": "running",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "ownership": {
            "orchestrator": "src.validation.kimarite.p1_wl_website",
            "assembler_dependency": "src.products.make_site89.build.build_site",
            "deployment_invoked": False,
        },
        "input": {
            "bundle_root": str(bundle_root),
            "bundle_manifest": _file_identity(bundle_manifest_path),
            "rating_manifest": _file_identity(rating_manifest_path),
            "copied_prior": copied_prior_identity,
            "copied_prior_pair_count": copied_prior_pair_count,
            "accepted_prior_sha256": expected_prior_sha256,
            "history_start": bundle.history_start,
            "history_end": bundle.history_end,
            "artifact_count": len(bundle.artifacts),
        },
        "build": {
            "cache_mode": cache_mode,
            "site_root": "site",
            "preview_port": PREVIEW_PORT,
            "preview_url": f"http://localhost:{PREVIEW_PORT}/",
        },
    }
    _write_json(output_root / "manifest.json", manifest)

    try:
        result = build_site(
            data_bundle=bundle_root,
            output_root=site_root,
            cache_mode=cache_mode,
        )
        tree_identity = _tree_identity(result.root)
    except BaseException as error:
        manifest["status"] = "failed"
        manifest["failure"] = f"{type(error).__name__}: {error}"
        manifest["runtime_seconds"] = perf_counter() - started
        _write_json(output_root / "manifest.json", manifest)
        raise

    elapsed = perf_counter() - started
    manifest["status"] = "complete"
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["runtime_seconds"] = elapsed
    manifest["output"] = {
        **tree_identity,
        "entrypoint": result.entrypoint.relative_to(output_root).as_posix(),
        "reported_file_count": result.file_count,
    }
    _write_json(output_root / "manifest.json", manifest)

    resolved_site = result.root.resolve()
    print(f"Built P1-WL website: {result.entrypoint.resolve()}", flush=True)
    print(f"Files: {result.file_count}", flush=True)
    print(f"Total wall-clock time: {elapsed:.3f} seconds", flush=True)
    print("Shared preview command:", flush=True)
    print(
        f'py -m http.server {PREVIEW_PORT} --directory "{resolved_site}"',
        flush=True,
    )
    print(f"Shared preview URL: http://localhost:{PREVIEW_PORT}/", flush=True)
    print(f"Evidence: {(output_root / 'manifest.json').resolve()}", flush=True)
    return output_root


def _rating_manifest_path(
    bundle_root: Path, bundle_manifest: dict[str, object]
) -> Path:
    relative = bundle_manifest.get("rating_run")
    if not isinstance(relative, str) or not relative:
        raise ValueError("Site-data bundle has no rating_run manifest path")
    path = bundle_root / relative
    if not path.is_file():
        raise FileNotFoundError(f"Elo-89 rating-run manifest not found: {path}")
    return path


def _load_json_object(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON object: {path}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _required_string(value: dict[str, object], field: str) -> str:
    result = value.get(field)
    if not isinstance(result, str) or not result:
        raise ValueError(f"Expected non-empty {field!r} in Elo-89 prior manifest")
    return result


def _validate_copied_prior(path: Path, recorded_pair_count: object) -> int:
    if not isinstance(recorded_pair_count, int) or recorded_pair_count <= 0:
        raise ValueError("Elo-89 prior manifest has no positive pair_count")
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != ("rank_pair", "ordinal", "rating"):
            raise ValueError(f"Unexpected copied-prior schema: {path}")
        rows = list(reader)
    if len(rows) != recorded_pair_count:
        raise ValueError(
            "Copied-prior row count differs from rating manifest: "
            f"expected {recorded_pair_count}, received {len(rows)}"
        )
    rank_pairs = [row["rank_pair"] for row in rows]
    if len(set(rank_pairs)) != len(rank_pairs) or any(not value for value in rank_pairs):
        raise ValueError("Copied prior contains missing or duplicate rank pairs")
    try:
        for row in rows:
            int(row["ordinal"])
            float(row["rating"])
    except ValueError as error:
        raise ValueError(f"Copied prior contains a non-numeric value: {path}") from error
    return len(rows)


def _file_identity(path: Path) -> dict[str, object]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Input file not found: {resolved}")
    return {
        "path": str(resolved),
        "size": resolved.stat().st_size,
        "sha256": _sha256(resolved),
    }


def _tree_identity(root: Path) -> dict[str, object]:
    resolved = root.resolve()
    files = sorted(path for path in resolved.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    total_bytes = 0
    for path in files:
        relative = path.relative_to(resolved).as_posix()
        size = path.stat().st_size
        total_bytes += size
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha256(path)))
    return {
        "file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-bundle",
        type=Path,
        default=DEFAULT_CANDIDATE_BUNDLE,
        help="Accepted P1-WL site-data bundle.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="New retained run directory; defaults to a timestamped run.",
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Build without development cache-busting query parameters.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output = args.output or DEFAULT_OUTPUT_PARENT / f"p1-wl-website-{stamp}"
    build_p1_wl_website(
        data_bundle=args.data_bundle,
        output_root=output,
        cache_mode="prod" if args.prod else "dev",
    )
    return 0
