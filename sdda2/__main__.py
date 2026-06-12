from __future__ import annotations

from .analysis import analyse_product
from .input_actions import perform_input_actions
from .input_worklist import build_input_worklist
from .products import default_product
from .reports import write_product_reports


def main() -> None:
    product = default_product()
    evidence, summary = analyse_product(product)
    input_worklist = build_input_worklist(product, evidence)
    input_actions, producer_search, input_resolutions = perform_input_actions(product, input_worklist)
    write_product_reports(
        product,
        evidence,
        summary,
        input_worklist,
        input_actions,
        producer_search,
        input_resolutions,
    )
    print(f"Product: {product.product_id}")
    print(f"Builder: {product.builder_root_module}")
    print(f"Wrote {product.output_dir}")
    print(f"Evidence rows: {len(evidence)}")
    print(f"Input worklist rows: {len(input_worklist)}")
    print(f"Producer search rows: {len(producer_search)}")


if __name__ == "__main__":
    main()
