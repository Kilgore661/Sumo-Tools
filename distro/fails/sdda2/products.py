from __future__ import annotations

from pathlib import Path

from .models import Product


LOCAL_SERVER_SITE = Product(
    product_id="local-server-site",
    builder_root_module="src.products.make_site2.__main__",
    import_root=Path("."),
    artifact_description="Local website file set produced by make_site2.",
    distribution_mode="source distribution with internet access",
    output_dir=Path("files") / "output" / "sdda2" / "local-server-site",
)


PRODUCTS = {
    LOCAL_SERVER_SITE.product_id: LOCAL_SERVER_SITE,
}


def default_product() -> Product:
    return LOCAL_SERVER_SITE

