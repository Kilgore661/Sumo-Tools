"""Deployment defaults for the make_site2 static prototype."""

from __future__ import annotations

from pathlib import Path

from src.products.make_site.deploy import HOST, deploy_local, deploy_remote


LOCAL_ROOT = Path("A:/local/html/sumo-tools/make_site2")
REMOTE_ROOT = "/var/www/html/sumo-tools/make_site2"

