"""Public assembly facade for the make_site2 runtime manifest.

The implementation is split under :mod:`.manifest` so this module remains the
stable import boundary used by the build pipeline.
"""

from __future__ import annotations

from .manifest.builder import build_public_site_shell, build_runtime_manifest

__all__ = ["build_public_site_shell", "build_runtime_manifest"]
