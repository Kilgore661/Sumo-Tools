"""
Static asset deployment contract for the Banzuke Change Report.
"""

import shutil

from src.analysis.news.classes import PublicationRequest


STATIC_FILE_NAMES = (
    "banzuke_change_report.html",
    "banzuke_change_report.css",
    "banzuke_change_report.js.txt",
)

COMMON_STATIC_FILE_NAMES = (
    "site-wide.css",
)


def copy_static_assets(request: PublicationRequest) -> None:
    """
    Contract:
        request.static_dir contains the BCR HTML/CSS/JS assets and
        request.common_static_dir contains the shared lab CSS used by the BCR
        HTML.

        Copies the static browser app assets into the output tree.
    """

    request.output_root.mkdir(parents=True, exist_ok=True)
    request.common_output_dir.mkdir(parents=True, exist_ok=True)

    for name in STATIC_FILE_NAMES:
        shutil.copy2(request.static_dir / name, request.output_root / name)

    for name in COMMON_STATIC_FILE_NAMES:
        shutil.copy2(
            request.common_static_dir / name,
            request.common_output_dir / name,
        )
