"""Create a runnable make_site2 distro zip.

This is an operational packaging helper, not part of the make_site2 product.
Run it from the repository root:

    py distro/package_make_site2.py
"""

from __future__ import annotations

import argparse
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("files/output/distro")
DEFAULT_ROOT_NAME = "Sumo-Tools"

BASIC_PATHS = (
    Path("_boot.ps1"),
    Path("README.md"),
    Path("init_scan.py"),
    Path("package.json"),
    Path("package-lock.json"),
    Path("src"),
    Path("tests"),
    Path("docs"),
    Path("distro/README.md"),
    Path("distro/package_make_site2.py"),
    Path("distro/docs"),
    Path("distro/make_site2_targets.json"),
    Path("files/input/bios.json"),
    Path("files/input/elo_fide.json"),
)

EXTENDED_CACHE_PATHS = (
    Path("files/output/current standings"),
    Path("files/output/HTML results"),
    Path("files/output/infra/get_bios/rikishi"),
    Path("files/output/Equelo/expt2_combined_final.csv"),
)

EXCLUDED_DIR_NAMES = frozenset(
    (
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".venv",
        "venv",
        "node_modules",
    )
)
EXCLUDED_SUFFIXES = frozenset((".pyc", ".pyo", ".swp", ".tmp"))


@dataclass(frozen=True, kw_only=True)
class DistroResult:
    path: Path
    file_count: int
    zip_byte_count: int
    uncompressed_byte_count: int
    missing_optional_paths: tuple[Path, ...]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a zip containing the code, operational config, docs and "
            "input data needed to bootstrap make_site2 from an extracted copy."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to receive the distro zip. Default: {DEFAULT_OUTPUT_DIR}.",
    )
    parser.add_argument(
        "--name",
        help=(
            "Zip filename stem. Default: "
            "sumo-tools-make_site2-{basic|extended}-YYYYMMDD-HHMMSS."
        ),
    )
    parser.add_argument(
        "--root-name",
        default=DEFAULT_ROOT_NAME,
        help=(
            "Top-level folder name inside the zip. "
            f"Default: {DEFAULT_ROOT_NAME}."
        ),
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help=(
            "Also include bulky generated caches that shorten bootstrap time, "
            "such as downloaded SumoDB HTML and the slow Equelo solver output. "
            "The bundled _boot.ps1 will use those caches instead of refreshing "
            "them from scratch."
        ),
    )
    parser.add_argument(
        "--include-extended-cache",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    extended = args.extended or args.include_extended_cache
    output_path = make_output_path(args.output_dir, args.name, extended=extended)
    result = write_distro_zip(
        output_path=output_path,
        root_name=args.root_name,
        extended=extended,
    )
    print(f"Wrote {result.path}")
    print(f"Files: {result.file_count}")
    print(f"Zip size: {format_size(result.zip_byte_count)}")
    print(f"Uncompressed size: {format_size(result.uncompressed_byte_count)}")
    if result.missing_optional_paths:
        print("Optional cache paths not included because they were absent:")
        for path in result.missing_optional_paths:
            print(f"  {path}")


def make_output_path(output_dir: Path, name: str | None, *, extended: bool) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    if name is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        mode = "extended" if extended else "basic"
        name = f"sumo-tools-make_site2-{mode}-{stamp}"
    path = output_dir / name
    return path if path.suffix == ".zip" else path.with_suffix(".zip")


def format_size(byte_count: int) -> str:
    mib = byte_count / (1024 * 1024)
    return f"{mib:.1f} MB ({byte_count:,} bytes)"


def write_distro_zip(
    *,
    output_path: Path,
    root_name: str,
    extended: bool,
) -> DistroResult:
    basic_files = collect_required_files(BASIC_PATHS)
    optional_files: list[Path] = []
    missing_optional_paths: list[Path] = []
    if extended:
        optional_files, missing_optional_paths = collect_optional_files(
            EXTENDED_CACHE_PATHS
        )
    files = sorted(set(basic_files + optional_files), key=path_sort_key)
    manifest = make_manifest(
        files=files,
        extended=extended,
        missing_optional_paths=missing_optional_paths,
    )
    uncompressed_byte_count = sum(path.stat().st_size for path in files)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            if path == Path("_boot.ps1"):
                continue
            zf.write(path, archive_name(root_name, path))
        zf.writestr(
            f"{root_name}/_boot.ps1",
            make_boot_script(extended=extended),
        )
        zf.writestr(
            f"{root_name}/DISTRO_README.txt",
            make_distro_readme(extended=extended),
        )
        zf.writestr(
            f"{root_name}/distro_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )
    return DistroResult(
        path=output_path,
        file_count=len(files) + 2,
        zip_byte_count=output_path.stat().st_size,
        uncompressed_byte_count=uncompressed_byte_count,
        missing_optional_paths=tuple(missing_optional_paths),
    )


def collect_required_files(paths: tuple[Path, ...]) -> list[Path]:
    missing = [path for path in paths if not path.exists()]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"required distro path(s) missing: {names}")
    files: list[Path] = []
    for path in paths:
        files.extend(iter_files(path))
    return files


def collect_optional_files(paths: tuple[Path, ...]) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    missing: list[Path] = []
    for path in paths:
        if not path.exists():
            missing.append(path)
            continue
        files.extend(iter_files(path))
    return files, missing


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if should_include_file(path) else []
    files: list[Path] = []
    for child in path.rglob("*"):
        if child.is_file() and should_include_file(child):
            files.append(child)
    return files


def should_include_file(path: Path) -> bool:
    if set(path.parts).intersection(EXCLUDED_DIR_NAMES):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if path.name.endswith("~"):
        return False
    return True


def archive_name(root_name: str, path: Path) -> str:
    return (Path(root_name) / path).as_posix()


def path_sort_key(path: Path) -> str:
    return path.as_posix().lower()


def make_manifest(
    *,
    files: list[Path],
    extended: bool,
    missing_optional_paths: list[Path],
) -> dict[str, object]:
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "purpose": "make_site2 runnable source distribution",
        "mode": "extended" if extended else "basic",
        "extended": extended,
        "basic_paths": [path.as_posix() for path in BASIC_PATHS],
        "extended_cache_paths": [path.as_posix() for path in EXTENDED_CACHE_PATHS],
        "missing_optional_paths": [
            path.as_posix() for path in missing_optional_paths
        ],
        "file_count": len(files),
        "files": [path.as_posix() for path in files],
    }


def make_boot_script(*, extended: bool) -> str:
    text = Path("_boot.ps1").read_text(encoding="utf-8")
    if extended:
        return text
    replacements = {
        '# Run "py -m src.infra.bootstrap_sources"': (
            'Run "py -m src.infra.bootstrap_sources"'
        ),
        (
            "# Run \"py -m src.analysis.equelo.expt2.run_all --start 1958 "
            "--end 2026 --modern-end-year 2026 --k-policy divisional "
            "--collapse annotation-only\""
        ): (
            "Run \"py -m src.analysis.equelo.expt2.run_all --start 1958 "
            "--end 2026 --modern-end-year 2026 --k-policy divisional "
            "--collapse annotation-only\""
        ),
        '# Run "py -m src.infra.get_bios"': 'Run "py -m src.infra.get_bios"',
    }
    for old, new in replacements.items():
        if old not in text:
            raise ValueError(f"could not find _boot.ps1 line to rewrite: {old}")
        text = text.replace(old, new)
    text = text.replace(
        "# Slow internet refresh stages and the fixed-point solver are left commented.",
        "# Slow internet refresh stages and the fixed-point solver are enabled.",
    )
    text = text.replace(
        "# Use the commented stages when rebuilding the corresponding cached artifacts\n"
        "# rather than consuming an extended distro/cache.",
        "# This basic distro does not contain the corresponding extended caches.",
    )
    return text


def make_distro_readme(*, extended: bool) -> str:
    cache_note = (
        "This is an extended distro. It includes the cache paths recorded in "
        "distro_manifest.json, and its bundled _boot.ps1 leaves the expensive "
        "refresh stages commented.\n"
        if extended
        else (
            "This zip is a basic distro. It omits bulky generated caches, so "
            "its bundled _boot.ps1 enables the downloader stages and the slow "
            "fixed-point solver.\n"
        )
    )
    return f"""Sumo-Tools make_site2 distro

After extracting:

1. Edit distro/make_site2_targets.json for your local and remote deployment
   destinations.
2. Run _boot.ps1 from the extracted repository root to regenerate the pipeline
   outputs needed by make_site2.
3. Start the live store in a separate terminal when _boot.ps1 tells you to:

   py -m src.infra.tracker.tracker

4. Build/deploy the site:

   py -m src.products.make_site2 --local-only

The true input data included in the basic distro is:

  files/input/bios.json
  files/input/elo_fide.json

{cache_note}The default deployment command:

  py -m src.products.make_site2

builds and deploys to all default targets listed in
distro/make_site2_targets.json. Use --local-only to deploy only filesystem-copy
targets and avoid SFTP credential prompts.
"""


if __name__ == "__main__":
    main()
