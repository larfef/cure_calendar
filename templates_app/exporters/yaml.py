from pathlib import Path
import yaml


def write_products_to_yaml(products_data, output_path="products_output.yaml"):
    """Write ProductsData structure to YAML file for later reloading.

    Args:
        products_data: ProductsData TypedDict with keys:
            - products: Dict[int, Product] - Django Product instances
            - delays: Dict[int, int] - Delay for each product
            - cortisol_phase: bool - Whether cortisol phase is active
    """
    # Serialize to a format that can be saved and reloaded
    serializable_data = {
        "product_ids": list(products_data["products"].keys()),
        "delays": products_data["delays"],
        "cortisol_phase": products_data["cortisol_phase"],
    }

    output_file = Path(output_path)
    with output_file.open("w", encoding="utf-8") as f:
        yaml.dump(
            serializable_data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    return str(output_file.absolute())
